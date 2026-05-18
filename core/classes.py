import re

from discord.ext import commands
from bs4 import BeautifulSoup
from tweety.types import Tweet

from src.i18n import t


class Cog_Extension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


class ParsedTweet():
    MAX_DESCRIPTION_LENGTH = 450
    DCOS_ICON = '\ud83d\udcd1'
    
    class Media():
        def __init__(self, type: str = None, urls: list[str] = None, length: int = None, video_link: str = None, mosaic_url: str = None):
            self.type = type
            self.urls = urls
            self.length = length
            self.video_link = video_link
            self.mosaic_url = mosaic_url
            
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
            
            self.text = tweet_data.get('raw_text', {}).get('text', None)
            self.trans_text = trans_data.get('text', None)
            self.trans_lang = trans_data.get('source_lang', None)
            self.quote.text = quote_data.get('raw_text', {}).get('text', None)
            self.quote.name = quote_data.get('author', {}).get('name', None)
            self.quote.screen_name = quote_data.get('author', {}).get('screen_name', None)
            self.quote.url = quote_data.get('url', None)
            self.quote.profile_link = quote_data.get('author', {}).get('url', None)
            self.quote.trans_text = quote_data.get('translation', {}).get('text', None)
            
            self.text = f"RT @{tweet_data.get('author', {}).get('screen_name', None)}: {self.text}" if tweet_data.get('reposted_by', {}) else self.text

            if not media_data.get('all') and 'quote' in tweet_data:
                media_data = tweet_data['quote'].get('media', {})

            all_media = media_data.get('all', [])

            if not all_media:
                self.media.type, self.media.urls, self.media.length, self.media.mosaic_url = None, [], 0, None
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
            full_content = f"{self.get_translated_text() or self.text}\n\n{quote_block}"
        else:
            full_content = quote_block
            
        if simplified_content:
            full_content = (full_content[:self.MAX_DESCRIPTION_LENGTH - 3] + '...', True) if len(full_content) > self.MAX_DESCRIPTION_LENGTH else (full_content, False)
        else:
            full_content = (full_content, False)
            
        return full_content
