import re
import discord

import aiohttp
from bs4 import BeautifulSoup
from tweety.types import Tweet

from core.classes import ParsedTweet
from configs.load_configs import FX_SETTINGS
from src.log import setup_logger

log = setup_logger(__name__)


async def get_parsed_tweet(tweet: Tweet, session: aiohttp.ClientSession = None, lang: str = None) -> ParsedTweet:
    async def get_fx_data(s: aiohttp.ClientSession):
        api_url = re.sub(r'(?:twitter|x)\.com', r'api.fxtwitter.com', tweet.url)
        if lang: api_url += f"/{lang}"
        try:
            async with s.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return ParsedTweet(data)
                else:
                    log.warning(f'failed to get fx data from {api_url} (status: {response.status}), fallback to HTML scraping')
        except Exception as e:
            log.error(f'error fetching from {api_url}: {e}, fallback to HTML scraping')

        html_url = re.sub(r'(?:twitter|x)\.com', r'fxtwitter.com', tweet.url)
        async with s.get(html_url) as response:
            raw = await response.text()
            soup = BeautifulSoup(raw, 'html.parser')
            return ParsedTweet(soup)

    fx_enhancement_conditions = [
        FX_SETTINGS['media'],
        FX_SETTINGS['rt_text']['enabled'],
        FX_SETTINGS['auto_translation'],
        FX_SETTINGS['mosaic'] and len(tweet.media) > 1,
    ]
    if any(fx_enhancement_conditions):
        if session:
            return await get_fx_data(session)
        else:
            async with aiohttp.ClientSession() as session_internal:
                return await get_fx_data(session_internal)
    else:
        return ParsedTweet(tweet)


def is_match_type(tweet: Tweet, enable_type: str):
    tweet_type = 0 if tweet.is_retweet else 1 if tweet.is_quoted else -1
    return tweet_type == -1 or enable_type[tweet_type] == '1'


def is_match_media_type(source: Tweet | ParsedTweet, media_type: str):
    if isinstance(source, Tweet): return media_type == '11' or (media_type == '10' and len(source.media) == 0) or (media_type == '01' and len(source.media) > 0)
    elif isinstance(source, ParsedTweet): return media_type == '11' or (media_type == '10' and source.length == 0) or (media_type == '01' and source.length > 0)
    else: raise TypeError('source must be a Tweet or Media')


def replace_emoji(match: re.Match, guild: discord.Guild):
    emoji_name = match.group(1)
    emoji = discord.utils.get(guild.emojis, name=emoji_name)
    return str(emoji) if emoji else match.group(0)
