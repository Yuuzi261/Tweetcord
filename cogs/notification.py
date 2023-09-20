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
                if user['lastest_tweet'] != lastest_tweet[0]:
                    user['lastest_tweet'] = lastest_tweet[0]
                    with open('following.json', 'w') as jfile:
                        json.dump(jdata, jfile)
                    for chnl in user['channels']:
                        channel = self.bot.get_channel(chnl)
                        await channel.send(f"**{lastest_tweet[1]['author'].name}** just tweeted here: \nhttps://twitter.com/{username}/status/{lastest_tweet[0]}")
                
            print(f'alive : {username}')
            
def get_tweets(app, username):
    tweets = app.get_tweet_notifications()
    tweets_dict = {tweet.id : {'author' : tweet.author, 'created_on' : tweet.created_on} for tweet in tweets if tweet.author.username == username}
    lastest_tweet = sorted(tweets_dict.items(), key=lambda x: x[1]['created_on'], reverse=True)[0]
    return lastest_tweet

def get_cookies():
    with open('cookies.json') as jfile:
        jcookies = json.load(jfile)
        needed_cookies = ['guest_id', 'guest_id_marketing', 'guest_id_ads', 'kdt', 'auth_token', 'ct0', 'twid', 'personalization_id']
        cookies = {}
        for cookie in jcookies:
            name = cookie['name']
            if name in needed_cookies:
                cookies[name] = cookie['value']
                
    return cookies

async def setup(bot):
	await bot.add_cog(Notification(bot))