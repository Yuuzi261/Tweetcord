import re

import aiohttp
import discord
from bs4 import BeautifulSoup
from tweety.types import Tweet

from configs.load_configs import configs
from src.i18n import t


class Media():
    def __init__(self, source: Tweet | BeautifulSoup):
        if isinstance(source, Tweet):
            if hasattr(source, 'media') and len(source.media) > 0:
                self.type = source.media[0].type
                self.urls = [m.media_url_https for m in source.media]
                self.length = len(self.urls)
            else:
                self.type, self.urls, self.length = None, [], 0
            self.mosaic_url = None

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

        else:
            raise TypeError('source must be a Tweet or a BeautifulSoup')
        

async def gen_embed(tweet: Tweet, session: aiohttp.ClientSession = None) -> list[discord.Embed]:
    async def get_fx_images(s: aiohttp.ClientSession):
        async with s.get(target_url) as response:
            raw = await response.text()
            
        soup = BeautifulSoup(raw, 'html.parser')
        return Media(soup)
    
    target_url = re.sub(r'twitter', r'fxtwitter', tweet.url)
    
    if any(configs['embed']['built_in']['fx_image'].values()):
        if session:
            media = await get_fx_images(session)
        else:
            async with aiohttp.ClientSession() as session_internal:
                media = await get_fx_images(session_internal)
    else:
        media = Media(tweet)
        
    author = tweet.author
    embed = discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=True)} {get_tweet_type(media)}', description=tweet.text, url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
    embed.set_author(name=f'{author.name} (@{author.username})', icon_url=author.profile_image_url_https, url=f'https://twitter.com/{author.username}')
    embed.set_thumbnail(url=re.sub(r'normal(?=\.jpg$)', '400x400', tweet.author.profile_image_url_https))
    embed.set_footer(text='Twitter' if configs['embed']['built_in']['legacy_logo'] else 'X', icon_url='attachment://footer.png')
    
    if media.length == 1:
        embed.set_image(url=media.urls[0])
        return [embed]
    elif media.length > 1:
        if configs['embed']['built_in']['fx_image']['mosaic']:
            embed.set_image(url=media.mosaic_url)
            return [embed]
        else:
            imgs_embed = [discord.Embed(url=tweet.url).set_image(url=url) for url in media.urls]
            imgs_embed.insert(0, embed)
            return imgs_embed
    return [embed]


def get_action(tweet: Tweet, disable_quoted: bool = False) -> str:
    if tweet.is_retweet:
        return t('display.action.retweeted')
    elif tweet.is_quoted and not disable_quoted:
        return t('display.action.quoted')
    else:
        return t('display.action.tweeted')


def get_tweet_type(media: Media) -> str:
    if media.length > 1:
        return t('display.tweet_type.photos', count=media.length)
    elif media.length == 1:
        map_key = f'display.media_type_map.{media.type}'
        translated = t(map_key)
        # t() returns the key itself when the key is missing; use raw type name as fallback
        media_type = media.type if translated == map_key else translated
        return t('display.tweet_type.media', media_type=media_type)
    else:
        return t('display.tweet_type.status')
