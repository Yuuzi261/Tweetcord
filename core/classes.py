import re

from discord.ext import commands
from bs4 import BeautifulSoup
from tweety.types import Tweet

from src.i18n import t
from src.utils import get_visible_length, safe_truncate, escape_markdown


class Cog_Extension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


class ParsedTweet():
    SIMPLIFIED_THRESHOLD = 400
    MAX_DESCRIPTION_LENGTH = 650
    DCOS_ICON = '\ud83d\udcd1'
    
    class Media():
        def __init__(self, type: str = None, urls: list[str] = None, length: int = None, video_link: str = None, mosaic_url: str = None, external_url: str = None):
            self.type = type
            self.urls = urls
            self.length = length
            self.video_link = video_link
            self.mosaic_url = mosaic_url
            self.external_url = external_url
            
    class Quote():
        def __init__(self, text: str = None, name: str = None, screen_name: str = None, url: str = None, profile_link: str = None, trans_text: str = None):
            self.text = text
            self.name = name
            self.screen_name = screen_name
            self.url = url
            self.profile_link = profile_link
            self.trans_text = trans_text
    
    def __init__(self, source: Tweet | BeautifulSoup | dict):
        self.media = self.Media()
        self.quote = self.Quote()
        
        self.text, self.trans_text, self.trans_lang = None, None, None
        self.is_mixed = False
        
        if isinstance(source, Tweet):
            if hasattr(source, 'media') and len(source.media) > 0:
                self.media.type = source.media[0].type
                self.media.urls = [m.media_url_https for m in source.media]
                self.media.length = len(self.media.urls)
                self.media.video_link = source.media[0].expanded_url if self.media.type == 'video' else None
            else:
                self.media.type, self.media.urls, self.media.length, self.media.video_link = None, [], 0, None
            self.media.mosaic_url = None

        elif isinstance(source, dict):
            tweet_data = source.get('tweet', {})
            quote_data = tweet_data.get('quote', {})
            trans_data = tweet_data.get('translation', {})
            media_data = tweet_data.get('media', {})
            
            self.text = self._handle_raw_text(tweet_data.get('raw_text', {}))
            self.trans_text = escape_markdown(trans_data.get('text', None))
            self.trans_lang = trans_data.get('source_lang', None)
            
            self.quote.text = self._handle_raw_text(quote_data.get('raw_text', {}))
            self.quote.name = quote_data.get('author', {}).get('name', None)
            self.quote.screen_name = quote_data.get('author', {}).get('screen_name', None)
            self.quote.url = quote_data.get('url', None)
            self.quote.profile_link = quote_data.get('author', {}).get('url', None)
            self.quote.trans_text = escape_markdown(quote_data.get('translation', {}).get('text', None))
            
            if tweet_data.get('reposted_by', {}):
                author_name = tweet_data.get('author', {}).get('screen_name', None)
                self.text = f"RT @{author_name}: {self.text}"
                if self.trans_text: self.trans_text = f"RT @{author_name}: {self.trans_text}"

            if not media_data.get('all') and 'quote' in tweet_data:
                media_data = tweet_data['quote'].get('media', {})

            all_media = media_data.get('all', [])

            if not all_media:
                self.media.type, self.media.urls, self.media.length, self.media.mosaic_url = None, [], 0, None
                
                # External link preview images do not affect tweet media type, treat as sending a regular tweet
                ex_media = media_data.get('external', None)
                if ex_media:
                    self.media.external_url = ex_media.get('url', None) if ex_media.get('type', None) == 'photo' else ex_media.get('thumbnail_url')
                    
                return

            self.media.length = len(all_media)
            # Use original URL for photos, thumbnail for videos/gifs
            self.media.urls = [m.get('url') if m.get('type') == 'photo' else m.get('thumbnail_url', m.get('url')) for m in all_media]

            type_map = {'photo': 'photo', 'video': 'video', 'gif': 'animated_gif'}
            self.media.type = type_map.get(all_media[0].get('type'), 'photo')
            
            media_types = {m.get('type') for m in all_media}
            self.is_mixed = len(media_types) > 1
            
            self.media.mosaic_url = media_data.get('mosaic', {}).get('type') == 'mosaic_photo' and media_data.get('mosaic', {}).get('formats', {}).get('jpeg')
            if not self.media.mosaic_url and self.media.length > 0:
                 self.media.mosaic_url = self.media.urls[0]
                 
            try: self.media.video_link = tweet_data['raw_text']['facets'][0]['replacement']
            except: self.media.video_link = None
            
        elif isinstance(source, BeautifulSoup):
            meta_image = source.find('meta', property='og:image')
            
            if not meta_image:
                self.media.type, self.media.urls, self.media.length, self.media.mosaic_url = None, [], 0, None
                return

            img_url = meta_image.get('content', '')
            self.media.mosaic_url = img_url
            
            # Determine the media type (video, animated_gif, photo)
            if source.find('meta', property='og:video'):
                self.media.type = 'video'
            elif 'tweet_video_thumb' in img_url:
                self.media.type = 'animated_gif'
            else:
                self.media.type = 'photo'

            # Regex is only needed to decompose images when the URL comes from a mosaic service
            if 'mosaic.fxtwitter.com' in img_url:
                m = re.search(r'/(\d{15,})/(.+)$', img_url)
                if m:
                    base = "https://pbs.twimg.com/media/{}.jpg"
                    self.media.urls = [base.format(m_id) for m_id in m.group(2).split('/')]
                else:
                    self.media.urls = [img_url]
            else:
                self.media.urls = [img_url]
                
            self.media.length = len(self.media.urls)
            
            self.media.video_link = f"{source.find('meta', property='og:url').get('content')}/video/1"

        else:
            raise TypeError('source must be a Tweet, BeautifulSoup, or dict')
        
    @staticmethod
    def _wrap_quote(text: str) -> str:
        return "\n".join([f"> {line}" for line in text.splitlines()]) if text else ""
    
    @staticmethod
    def _handle_raw_text(raw_text: dict) -> str | None:
        text = raw_text.get('text', None)
        facets = raw_text.get('facets', [])
        if not text:
            return None
        if not facets or not all('indices' in f for f in facets):
            return escape_markdown(text)

        # Sort facets: back-to-front, prioritizing non-media if indices overlap
        def facet_sort_key(f):
            priority = 0 if f.get('type') == 'media' else 1
            return (f['indices'][0], f['indices'][1], priority)

        sorted_facets = sorted(facets, key=facet_sort_key, reverse=True)
        placeholders = {}
        last_processed_start = float('inf')

        for i, facet in enumerate(sorted_facets):
            start, end = facet['indices']
            if end > last_processed_start:
                continue
            
            f_type = facet.get('type')
            if f_type not in ['url', 'media', 'mention', 'hashtag', 'bold']:
                continue
            
            original = facet.get('original')
            facet_text = text[start:end]
            
            if f_type == 'url':
                display = facet.get('display', original)
                replacement = facet.get('replacement', original)
                md_link = f"[{display}]({replacement})"
            elif f_type == 'media':
                md_link = ""
            elif f_type in ['mention', 'hashtag']:
                url = f"https://twitter.com/{original}" if f_type == 'mention' else f"https://twitter.com/hashtag/{original}"
                md_link = f"[{facet_text}]({url})"
            elif f_type == 'bold':
                md_link = f"**{escape_markdown(facet_text)}**"
            
            ph = f"\x01{i}\x02"
            placeholders[ph] = md_link
            text = text[:start] + ph + text[end:]
            last_processed_start = start
        
        # Escape the remaining plain text safely in one go
        text = escape_markdown(text)
        
        # Restore all placeholders to true Markdown links
        return re.sub(r'\x01(\d+)\x02', lambda m: placeholders[m.group(0)], text)
    
    def _simplified_content(self, content: str) -> tuple[str, bool] | None:
        if not content:
            return None
        
        is_simplified = get_visible_length(content) > self.SIMPLIFIED_THRESHOLD
        truncated_content, _ = safe_truncate(content, self.MAX_DESCRIPTION_LENGTH)
        return (truncated_content, is_simplified)
    
    def get_text(self, simplified_content: bool = False) -> tuple[str, bool] | None:        
        content = self.get_translated_text() or self.text
        if not content:
            return None
        
        if simplified_content:
            return self._simplified_content(content)
        return (content, False)

    def get_translated_text(self) -> str | None:
        if not self.trans_text:
            return None
            
        trans_info = f'**{self.DCOS_ICON} {t("class.parsed_tweet.trans_text", lang=self.trans_lang.upper())}**'
        original_text = f"**{t('class.parsed_tweet.original_text')}**\n{self.text}"
        
        return '\n\n'.join([trans_info, self.trans_text, self._wrap_quote(original_text)])
        
    def get_quote_text(self, include_main_text: bool = True, include_quote_info: bool = True, simplified_content: bool = False) -> tuple[str, bool] | None:
        if not self.quote or not self.quote.text:
            return None
        
        quote_inner = []
        if include_quote_info:
            quote_info = t(
                'class.parsed_tweet.quote_info',
                url=self.quote.url, 
                name=self.quote.name, 
                screen_name=self.quote.screen_name, 
                profile_link=self.quote.profile_link
            )
            quote_inner.append(f"**{quote_info}**")
            
        quote_inner.append(self.quote.trans_text or self.quote.text)
        raw_quote_text = '\n\n'.join(quote_inner)
        quote_block = self._wrap_quote(raw_quote_text)
        
        if include_main_text and getattr(self, 'text', None):
            content = f"{self.get_text()[0]}\n\n{quote_block}"
        else:
            content = quote_block
            
        if simplified_content:
            full_content = self._simplified_content(content)
        else:
            full_content = (content, False)
            
        return full_content
