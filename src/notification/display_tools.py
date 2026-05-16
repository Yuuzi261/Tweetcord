import re

import discord
from tweety.types import Tweet

from core.classes import Media
from configs.load_configs import configs
from src.i18n import t


def gen_embed(tweet: Tweet, media: Media) -> list[discord.Embed]:
    author = tweet.author
    disable_quoted = not configs['embed']['built_in']['fx_image']['enhancement']
    embed = discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=disable_quoted)} {get_tweet_type(media)}', description=tweet.text, url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
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
        if getattr(media, 'is_mixed', False):
            return t('display.tweet_type.multi_media', count=media.length)
        return t('display.tweet_type.photos', count=media.length)
    elif media.length == 1:
        map_key = f'display.media_type_map.{media.type}'
        translated = t(map_key)
        # t() returns the key itself when the key is missing; use raw type name as fallback
        media_type = media.type if translated == map_key else translated
        return t('display.tweet_type.media', media_type=media_type)
    else:
        return t('display.tweet_type.status')
