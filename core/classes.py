import re

from discord.ext import commands
from bs4 import BeautifulSoup
from tweety.types import Tweet


class Cog_Extension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


class ParsedTweet():
    class Media():
        def __init__(self, type: str = None, urls: list[str] = None, length: int = None, video_link: str = None, mosaic_url: str = None):
            self.type = type
            self.urls = urls
            self.length = length
            self.video_link = video_link
            self.mosaic_url = mosaic_url
    
    def __init__(self, source: Tweet | BeautifulSoup | dict):
        self.media = self.Media()
        
        self.is_mixed = False
        self.quote_text = None
        
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
            media_data = tweet_data.get('media', {})

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
            
            self.text = tweet_data.get('raw_text', {}).get('text', None)
            self.quote_text = tweet_data.get('quote', {}).get('raw_text', {}).get('text', None)

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
        
    def get_quote_text(self, include_main_text: bool = False) -> str | None:
        if not self.quote_text:
            return None
        
        quote_text = '\n'.join(f"> {line}" for line in self.quote_text.split('\n'))    
        return f"{self.text}\n\n{quote_text}" if include_main_text else quote_text
