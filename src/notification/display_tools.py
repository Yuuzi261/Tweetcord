import discord
import re

def gen_embed(tweet):
    author = tweet.author
    embed = discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=True)} {get_tweet_type(tweet)}', description=tweet.text, url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
    embed.set_author(name=f'{author.name} (@{author.username})', icon_url=author.profile_image_url_https, url=f'https://twitter.com/{author.username}')
    embed.set_thumbnail(url=re.sub(r'normal(?=\.jpg$)', '400x400', tweet.author.profile_image_url_https))
    embed.set_footer(text='Twitter', icon_url='attachment://twitter.png')
    if len(tweet.media) == 1:
        embed.set_image(url=tweet.media[0].media_url_https)
        return [embed]
    else:
        imgs_embed = [discord.Embed(url=tweet.url).set_image(url=media.media_url_https) for media in tweet.media]
        imgs_embed.insert(0, embed)
        return imgs_embed

  
def get_action(tweet, disable_quoted = False):
    if tweet.is_retweet: return 'retweeted'
    elif tweet.is_quoted and not disable_quoted: return 'quoted'
    else: return 'tweeted'


def get_tweet_type(tweet):
    media = tweet.media
    if len(media) > 1: return f'{len(media)} photos'
    elif len(media) == 1: return f'a {media[0].type}'
    else: return 'a status'