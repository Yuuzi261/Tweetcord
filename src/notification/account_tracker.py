import discord
from tweety import Twitter
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import sqlite3
import asyncio

from src.log import setup_logger
from src.notification.display_tools import gen_embed, get_action
from src.notification.get_tweets import get_tweets
from src.notification.date_comparator import date_comparator
from src.db_function.db_executor import execute
from configs.load_configs import configs

log = setup_logger(__name__)

load_dotenv()

class AccountTracker():
    def __init__(self, bot):
        self.bot = bot
        self.tasksMonitorLogAt = datetime.utcnow() - timedelta(seconds=configs['tasks_monitor_log_period'])
        bot.loop.create_task(self.setup_tasks())

    async def setup_tasks(self):
        app = Twitter("session")
        app.load_auth_token(os.getenv('TWITTER_TOKEN'))
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()
        
        self.bot.loop.create_task(self.tweetsUpdater(app)).set_name('TweetsUpdater')
        cursor.execute('SELECT username FROM user')
        usernames = []
        for user in cursor:
            username = user[0]
            usernames.append(username)
            self.bot.loop.create_task(self.notification(username)).set_name(username)
        self.bot.loop.create_task(self.tasksMonitor(set(usernames))).set_name('TasksMonitor')
        
        conn.close()


    async def notification(self, username):
        while True:
            await asyncio.sleep(configs['tweets_check_period'])

            task = asyncio.create_task(asyncio.to_thread(get_tweets, self.tweets, username))
            await task
            lastest_tweet = task.result()
            if lastest_tweet == None: continue
            
            conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            user = cursor.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
            if date_comparator(lastest_tweet.created_on, user['lastest_tweet']) == 1:
                execute(conn, 'UPDATE user SET lastest_tweet = ? WHERE username = ?', (str(lastest_tweet.created_on), username), username)
                log.info(f'find a new tweet from {username}')
                for data in cursor.execute('SELECT * FROM notification WHERE user_id = ? AND enabled = 1', (user['id'],)):
                    channel = self.bot.get_channel(int(data['channel_id']))
                    if channel != None:
                        mention = f"{channel.guild.get_role(int(data['role_id'])).mention} " if data['role_id'] != '' else ''
                        await channel.send(f"{mention}**{lastest_tweet.author.name}** just {get_action(lastest_tweet)} here: \n{lastest_tweet.url}", file = discord.File('images/twitter.png', filename='twitter.png'), embeds = gen_embed(lastest_tweet))
                    
            conn.close()


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
                deadTasks = list(users - aliveTasks)
                log.warning(f'dead tasks : {deadTasks}')
                for deadTask in deadTasks:
                    self.bot.loop.create_task(self.notification(deadTask)).set_name(deadTask)
                    log.info(f'restart {deadTask} successfully')
                
            if 'TweetsUpdater' not in taskSet:
                log.warning('tweets updater : dead')
                
            if (datetime.utcnow() - self.tasksMonitorLogAt).total_seconds() >= configs['tasks_monitor_log_period']:
                log.info(f'alive tasks : {list(aliveTasks)}')
                if 'TweetsUpdater' in taskSet: log.info('tweets updater : alive')
                self.tasksMonitorLogAt = datetime.utcnow()
                
            await asyncio.sleep(configs['tasks_monitor_check_period'])
            

    async def addTask(self, username : str):
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()
        
        self.bot.loop.create_task(self.notification(username)).set_name(username)
        log.info(f'new task {username} added successfully')
        
        for task in asyncio.all_tasks():
            if task.get_name() == 'TasksMonitor':
                try: log.info(f'existing TasksMonitor has been closed') if task.cancel() else log.info('existing TasksMonitor failed to close')
                except Exception as e: log.warning(f'addTask : {e}')
        self.bot.loop.create_task(self.tasksMonitor({user[0] for user in cursor.execute('SELECT username FROM user').fetchall()})).set_name('TasksMonitor')
        log.info(f'new TasksMonitor has been started')
        
        conn.close()