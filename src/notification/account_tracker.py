import discord
from tweety import Twitter
import json
import asyncio

from src.log import setup_logger
from src.cookies import get_cookies
from src.notification.display_tools import gen_embed, get_action
from src.notification.get_tweets import get_tweets
from src.notification.date_comparator import date_comparator
from configs.load_configs import configs

log = setup_logger(__name__)

class AccountTracker():
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.setup_tasks())
    
    async def setup_tasks(self):
        cookies = get_cookies()
        app = Twitter("session")
        app.load_cookies(cookies)
        with open('tracked_accounts.json', 'r', encoding='utf8') as jfile:
            users = json.load(jfile)
        self.bot.loop.create_task(self.tweetsUpdater(app)).set_name('TweetsUpdater')
        for user in users.keys():
            self.bot.loop.create_task(self.notification(user)).set_name(user)
        self.bot.loop.create_task(self.tasksMonitor(set(users)))


    async def notification(self, username):
        while True:
            await asyncio.sleep(configs['tweets_check_period'])
            try:
                task = asyncio.create_task(asyncio.to_thread(get_tweets, self.tweets, username))
                await task
                lastest_tweet = task.result()
            except Exception as e:
                log.error(f'{e} (task : {username})')
                continue
            
            with open('tracked_accounts.json', 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
                
            user = jdata[username]
            if date_comparator(lastest_tweet.created_on, user['lastest_tweet']):
                user['lastest_tweet'] = str(lastest_tweet.created_on)
                log.info(f'find a new tweet from {username}')
                with open('tracked_accounts.json', 'w') as jfile:
                    json.dump(jdata, jfile)
                for chnl in user['channels'].keys():
                    channel = self.bot.get_channel(int(chnl))
                    mention = f"{channel.guild.get_role(int(user['channels'][chnl])).mention} " if user['channels'][chnl] != '' else ''
                    await channel.send(f"{mention}**{lastest_tweet.author.name}** just {get_action(lastest_tweet)} here: \n{lastest_tweet.url}", file = discord.File('images/twitter.png', filename='twitter.png'), embeds = gen_embed(lastest_tweet))


    async def tweetsUpdater(self, app):
        while True:
            try: self.tweets = app.get_tweet_notifications()
            except Exception as e:
                log.error(f'{e} (task : tweets updater)')
                log.error(f"an unexpected error occurred, try again in {configs['tweets_updater_retry_delay'] / 60} minutes")
                await asyncio.sleep(configs['tweets_updater_retry_delay'])
            await asyncio.sleep(configs['tweets_check_period'])

            
    async def tasksMonitor(self, users : set):
        while True:
            taskSet = set([task.get_name() for task in asyncio.all_tasks()])
            aliveTasks = list(taskSet & users)
            log.info(f'alive tasks : {aliveTasks}')
            log.info('tweets updater : alive') if 'TweetsUpdater' in taskSet else log.warning('tweets updater : dead')
            await asyncio.sleep(configs['tasks_monitor_check_period'])