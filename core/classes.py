import re

from discord.ext import commands
from bs4 import BeautifulSoup
from tweety.types import Tweet


class Cog_Extension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


class Media():
    def __init__(self, source: Tweet | BeautifulSoup | dict):
        self.is_mixed = False
        if isinstance(source, Tweet):
            if hasattr(source, 'media') and len(source.media) > 0:
                self.type = source.media[0].type
                self.urls = [m.media_url_https for m in source.media]
                self.length = len(self.urls)
                self.video_link = source.media[0].expanded_url if self.type == 'video' else None
            else:
                self.type, self.urls, self.length, self.video_link = None, [], 0, None
            self.mosaic_url = None

        elif isinstance(source, dict):
            tweet_data = source.get('tweet', {})
            media_data = tweet_data.get('media', {})

            if not media_data.get('all') and 'quote' in tweet_data:
                media_data = tweet_data['quote'].get('media', {})

            all_media = media_data.get('all', [])

            if not all_media:
                self.type, self.urls, self.length, self.mosaic_url = None, [], 0, None
                return

            self.length = len(all_media)
            # Use original URL for photos, thumbnail for videos/gifs
            self.urls = [m.get('url') if m.get('type') == 'photo' else m.get('thumbnail_url', m.get('url')) for m in all_media]

            type_map = {'photo': 'photo', 'video': 'video', 'gif': 'animated_gif'}
            self.type = type_map.get(all_media[0].get('type'), 'photo')
            
            media_types = {m.get('type') for m in all_media}
            self.is_mixed = len(media_types) > 1
            
            self.mosaic_url = media_data.get('mosaic', {}).get('type') == 'mosaic_photo' and media_data.get('mosaic', {}).get('formats', {}).get('jpeg')
            if not self.mosaic_url and self.length > 0:
                 self.mosaic_url = self.urls[0]
                 
            try: self.video_link = tweet_data['raw_text']['facets'][0]['replacement']
            except: self.video_link = None

        elif isinstance(source, BeautifulSoup):
            meta_image = source.find('meta', property='og:image')
            
            if not meta_image:
                self.type, self.urls, self.length, self.mosaic_url = None, [], 0, None
                return

            img_url = meta_image.get('content', '')
            self.mosaic_url = img_url
            
            # Determine the media type (video, animated_gif, photo)
            if source.find('meta', property='og:video'):
                self.type = 'video'
            elif 'tweet_video_thumb' in img_url:
                self.type = 'animated_gif'
            else:
                self.type = 'photo'

            # Regex is only needed to decompose images when the URL comes from a mosaic service
            if 'mosaic.fxtwitter.com' in img_url:
                m = re.search(r'/(\d{15,})/(.+)$', img_url)
                if m:
                    base = "https://pbs.twimg.com/media/{}.jpg"
                    self.urls = [base.format(m_id) for m_id in m.group(2).split('/')]
                else:
                    self.urls = [img_url]
            else:
                self.urls = [img_url]
                
            self.length = len(self.urls)
            
            self.video_link = f"{source.find('meta', property='og:url').get('content')}/video/1"

        else:
            raise TypeError('source must be a Tweet, BeautifulSoup, or dict')
