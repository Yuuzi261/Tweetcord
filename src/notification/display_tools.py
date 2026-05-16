import re

import discord
from tweety.types import Tweet

from core.classes import ParsedTweet
from configs.load_configs import configs
from src.i18n import t


def gen_embed(tweet: Tweet, parsed_tweet: ParsedTweet) -> list[discord.Embed]:
    author = tweet.author
    disable_quoted = not configs['embed']['built_in']['fx']['enhancement']['media']
    embed = discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=disable_quoted)} {get_tweet_type(parsed_tweet)}', 
                          description=f"{tweet.text}\n\n{parsed_tweet.get_quote_text()}" if parsed_tweet.quote_text else tweet.text,
                          url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
    embed.set_author(name=f'{author.name} (@{author.username})', icon_url=author.profile_image_url_https, url=f'https://twitter.com/{author.username}')
    embed.set_thumbnail(url=re.sub(r'normal(?=\.jpg$)', '400x400', tweet.author.profile_image_url_https))
    embed.set_footer(text='Twitter' if configs['embed']['built_in']['legacy_logo'] else 'X', icon_url='attachment://footer.png')
    
    if parsed_tweet.media.length == 1:
        embed.set_image(url=parsed_tweet.media.urls[0])
        return [embed]
    elif parsed_tweet.media.length > 1:
        if configs['embed']['built_in']['fx']['mosaic']:
            embed.set_image(url=parsed_tweet.media.mosaic_url)
            return [embed]
        else:
            imgs_embed = [discord.Embed(url=tweet.url).set_image(url=url) for url in parsed_tweet.media.urls]
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


def get_tweet_type(parsed_tweet: ParsedTweet) -> str:
    if parsed_tweet.media.length > 1:
        if getattr(parsed_tweet, 'is_mixed', False):
            return t('display.tweet_type.multi_media', count=parsed_tweet.media.length)
        return t('display.tweet_type.photos', count=parsed_tweet.media.length)
    elif parsed_tweet.media.length == 1:
        map_key = f'display.media_type_map.{parsed_tweet.media.type}'
        translated = t(map_key)
        # t() returns the key itself when the key is missing; use raw type name as fallback
        media_type = parsed_tweet.media.type if translated == map_key else translated
        return t('display.tweet_type.media', media_type=media_type)
    else:
        return t('display.tweet_type.status')
