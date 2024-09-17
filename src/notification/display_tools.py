import re

import aiohttp
import discord
from bs4 import BeautifulSoup
from tweety.types import Tweet

from configs.load_configs import configs


async def gen_embed(tweet: Tweet) -> list[discord.Embed]:
    author = tweet.author
    embed = discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=True)} {get_tweet_type(tweet)}', description=tweet.text, url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
    embed.set_author(name=f'{author.name} (@{author.username})', icon_url=author.profile_image_url_https, url=f'https://twitter.com/{author.username}')
    embed.set_thumbnail(url=re.sub(r'normal(?=\.jpg$)', '400x400', tweet.author.profile_image_url_https))
    embed.set_footer(text='Twitter', icon_url='attachment://twitter.png')
    if len(tweet.media) == 1:
        embed.set_image(url=tweet.media[0].media_url_https)
        return [embed]
    elif len(tweet.media) > 1:
        if configs['embed']['built_in']['fx_image']:
            async with aiohttp.ClientSession() as session:
                async with session.get(re.sub(r'twitter', r'fxtwitter', tweet.url)) as response:
                    raw = await response.text()
            fximage_url = BeautifulSoup(raw, 'html.parser').find('meta', property='og:image')['content']
            embed.set_image(url=fximage_url)
            return [embed]
        else:
            imgs_embed = [discord.Embed(url=tweet.url).set_image(url=media.media_url_https) for media in tweet.media]
            imgs_embed.insert(0, embed)
            return imgs_embed
    return [embed]


def get_action(tweet: Tweet, disable_quoted: bool = False) -> str:
    if tweet.is_retweet:
        return 'retweeted'
    elif tweet.is_quoted and not disable_quoted:
        return 'quoted'
    else:
        return 'tweeted'


def get_tweet_type(tweet: Tweet) -> str:
    media = tweet.media
    if len(media) > 1:
        return f'{len(media)} photos'
    elif len(media) == 1:
        return f'a {media[0].type}'
    else:
        return 'a status'
