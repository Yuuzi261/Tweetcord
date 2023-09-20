import discord
from core.classes import Cog_Extension
import json
from tweety import Twitter
import asyncio
from random import randint

class Notification(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(self.setup_tasks())
    
    async def setup_tasks(self):
        cookies = get_cookies()
        app = Twitter("session")
        app.load_cookies(cookies)
        with open('following.json', 'r', encoding='utf8') as jfile:
            users = json.load(jfile)
        for user in users.keys():
            self.bot.loop.create_task(self.notification(app, user))
                
    async def notification(self, app, username):
        while True:
            await asyncio.sleep(randint(30, 60))
            try:
                task = asyncio.create_task(asyncio.to_thread(get_tweets, app, username))
                await task
                lastest_tweet = task.result()
            except Exception as e:
                print(f'[ERROR] : {e}')
                continue
            
            with open('following.json', 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
                
            user = jdata[username]
            if user['lastest_tweet'] != lastest_tweet.id:
                user['lastest_tweet'] = lastest_tweet.id
                with open('following.json', 'w') as jfile:
                    json.dump(jdata, jfile)
                for chnl in user['channels'].keys():
                    channel = self.bot.get_channel(int(chnl))
                    mention = f"{channel.guild.get_role(int(user['channels'][chnl])).mention} " if user['channels'][chnl] != '' else ''
                    await channel.send(f"{mention}**{lastest_tweet.author.name}** just {get_action(lastest_tweet)} here: \n{lastest_tweet.url}", embeds=gen_embed(lastest_tweet))
                
            print(f'alive : {username}')
            
def gen_embed(tweet):
    author = tweet.author
    embed=discord.Embed(title=f'{author.name} {get_action(tweet, disable_quoted=True)} {get_tweet_type(tweet)}', url=tweet.url, color=0x1da0f2, timestamp=tweet.created_on)
    embed.set_author(name=f'{author.name} (@{author.username})', icon_url=author.profile_image_url_https, url=f'https://twitter.com/{author.username}')
    embed.set_thumbnail(url=author.profile_image_url_https[:-10]+'400x400.jpg')
    embed.add_field(name='', value=tweet.text, inline=False)
    embed.set_footer(text='Twitter', icon_url='https://images-ext-2.discordapp.net/external/krcaH4psq2u8hROno0il7FE05UYL18EcpWwIekh0Vys/https/pingcord.xyz/assets/twitter-footer.png')
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
    elif len(media) == 1:
        if media[0].type == 'image': return 'a photo'
        else: return 'a video'
    else: return 'a status'
            
def get_tweets(app, username):
    tweets = app.get_tweet_notifications()
    tweets = [tweet for tweet in tweets if tweet.author.username == username]
    lastest_tweet = sorted(tweets, key=lambda x: x.created_on, reverse=True)[0]
    return lastest_tweet

def get_cookies():
    with open('cookies.json') as jfile:
        jcookies = json.load(jfile)
    needed_cookies = ['guest_id', 'guest_id_marketing', 'guest_id_ads', 'kdt', 'auth_token', 'ct0', 'twid', 'personalization_id']
    cookies = {}
    for cookie in jcookies:
        name = cookie['name']
        if name in needed_cookies: cookies[name] = cookie['value']
                
    return cookies

async def setup(bot):
	await bot.add_cog(Notification(bot))