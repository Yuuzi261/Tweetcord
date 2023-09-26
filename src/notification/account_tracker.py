import discord
from tweety import Twitter
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json
import asyncio

from src.log import setup_logger
from src.get_cookies import get_cookies
from src.notification.display_tools import gen_embed, get_action
from src.notification.get_tweets import get_tweets
from src.notification.date_comparator import date_comparator
from configs.load_configs import configs

log = setup_logger(__name__)

load_dotenv()

class AccountTracker():
    def __init__(self, bot):
        self.bot = bot
        self.tasksMonitorLogAt = datetime.utcnow() - timedelta(seconds=configs['tasks_monitor_log_period'])
        bot.loop.create_task(self.setup_tasks())

    async def setup_tasks(self):
        while True:
            try:
                cookies = get_cookies()
                break
            except:
                log.warning('failed to read cookies, please upload cookies')
                await asyncio.sleep(10)
                
        app = Twitter("session")
        app.load_cookies(cookies)
            
        with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'r', encoding='utf8') as jfile:
            users = json.load(jfile)
        self.bot.loop.create_task(self.tweetsUpdater(app)).set_name('TweetsUpdater')
        usernames = []
        for user in users.values():
            username = user['username']
            usernames.append(username)
            self.bot.loop.create_task(self.notification(username)).set_name(username)
        self.bot.loop.create_task(self.tasksMonitor(set(usernames))).set_name('TasksMonitor')


    async def notification(self, username):
        while True:
            await asyncio.sleep(configs['tweets_check_period'])

            task = asyncio.create_task(asyncio.to_thread(get_tweets, self.tweets, username))
            await task
            lastest_tweet = task.result()
            if lastest_tweet == None: continue

            with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'r', encoding='utf8') as jfile:
                users = json.load(jfile)

            user = list(filter(lambda item: item[1]["username"] == username, users.items()))[0][1]
            if date_comparator(lastest_tweet.created_on, user['lastest_tweet']) == 1:
                user['lastest_tweet'] = str(lastest_tweet.created_on)
                log.info(f'find a new tweet from {username}')
                with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'w', encoding='utf8') as jfile:
                    json.dump(users, jfile, sort_keys=True, indent=4)
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
            taskSet = {task.get_name() for task in asyncio.all_tasks()}
            aliveTasks = taskSet & users
            
            if aliveTasks != users:
                log.warning(f'dead tasks : {list(users - aliveTasks)}')
                
            if 'TweetsUpdater' not in taskSet:
                log.warning('tweets updater : dead')
                
            if (datetime.utcnow() - self.tasksMonitorLogAt).total_seconds() >= configs['tasks_monitor_log_period']:
                log.info(f'alive tasks : {list(aliveTasks)}')
                if 'TweetsUpdater' in taskSet: log.info('tweets updater : alive')
                self.tasksMonitorLogAt = datetime.utcnow()
                
            await asyncio.sleep(configs['tasks_monitor_check_period'])
            

    async def addTask(self, username : str):
        with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'r', encoding='utf8') as jfile:
            users = json.load(jfile)
        self.bot.loop.create_task(self.notification(username)).set_name(username)
        log.info(f'new task {username} added successfully')
        
        for task in asyncio.all_tasks():
            if task.get_name() == 'TasksMonitor':
                try: log.info(f'existing TasksMonitor has been closed') if task.cancel() else log.info('existing TasksMonitor failed to close')
                except Exception as e: log.warning(f'addTask : {e}')
        self.bot.loop.create_task(self.tasksMonitor(set([user['username'] for user in users.values()]))).set_name('TasksMonitor')
        log.info(f'new TasksMonitor has been started')