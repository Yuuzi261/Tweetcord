import discord
from core.classes import Cog_Extension
import json
from tweety import Twitter
import asyncio

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
        self.bot.loop.create_task(self.tweetsUpdater(app)).set_name('TweetsUpdater')
        for user in users.keys():
            self.bot.loop.create_task(self.notification(user)).set_name(user)
        self.bot.loop.create_task(self.tasksMonitor(set(users)))
                
    async def notification(self, username):
        while True:
            await asyncio.sleep(20)
            try:
                task = asyncio.create_task(asyncio.to_thread(get_tweets, self.tweets, username))
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
                    
    async def tweetsUpdater(self, app):
        while True:
            self.tweets = app.get_tweet_notifications()
            await asyncio.sleep(20)
            
    async def tasksMonitor(self, users : set):
        while True:
            taskSet = set([task.get_name() for task in asyncio.all_tasks()])
            aliveTasks = list(taskSet & users)
            print(f'[INFO] Alive Tasks : {aliveTasks}')
            print('[INFO] TweetsUpdater : Alive') if 'TweetsUpdater' in taskSet else print('[WARNING] TweetsUpdater : Dead')
            await asyncio.sleep(600)
            
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
    elif len(media) == 1: return f'a {media[0].type}'
    else: return 'a status'
            
def get_tweets(tweets, username):
    tweets = [tweet for tweet in tweets if tweet.author.username == username]
    lastest_tweet = sorted(tweets, key=lambda x: x.created_on, reverse=True)[0]
    return lastest_tweet

def get_cookies():
    with open('cookies.json') as jfile:
        cookies = json.load(jfile)        
    return cookies

async def setup(bot):
	await bot.add_cog(Notification(bot))