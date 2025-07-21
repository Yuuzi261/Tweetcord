import asyncio
import os
import sys
import re
from datetime import datetime, timezone, timedelta

import aiosqlite
import discord
from discord.ext import commands
from tweety import Twitter

from configs.load_configs import configs
from src.log import setup_logger
from src.notification.display_tools import gen_embed, get_action
from src.notification.get_tweets import get_tweets
from src.notification.utils import is_match_media_type, is_match_type, replace_emoji
from src.utils import get_accounts, get_lock
from src.db_function.readonly_db import connect_readonly

EMBED_TYPE = configs['embed']['type'] if configs['embed']['type'] in ['built_in', 'fx_twitter'] else 'built_in'
DOMAIN_NAME = configs['embed']['fx_twitter']['domain_name'] if configs['embed']['fx_twitter']['domain_name'] in ['fxtwitter', 'fixupx'] else 'fxtwitter'

log = setup_logger(__name__)
lock = get_lock()

class AccountTracker():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts_data = get_accounts()
        self.db_path = os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')
        self.tweets = {account_name: [] for account_name in self.accounts_data.keys()}
        # Responsible for processing queries and writing timestamps
        self.db_write_queue = asyncio.Queue()
        self.latest_tweet_timestamps = {}
        self.timestamps_ready = asyncio.Event()

        self.tasksMonitorLogAt = datetime.now(timezone.utc) - timedelta(hours=configs['tasks_monitor_log_period'])
        bot.loop.create_task(self.setup_tasks())

    async def setup_tasks(self):
        # Start the core database workers first
        self.bot.loop.create_task(self.timestamp_updater()).set_name('TimestampUpdater')
        self.bot.loop.create_task(self.db_writer()).set_name('DBWriter')

        # Wait for the initial timestamp load
        await self.timestamps_ready.wait()

        async def authenticate_account(account_name, account_token):
            app = Twitter(account_name)
            max_attempts = configs['auth_max_attempts']
            for attempt in range(max_attempts):
                try:
                    await app.load_auth_token(account_token)
                    return app
                except Exception as e:
                    log.error(f"Authentication failed for account: {account_name} [Attempt {attempt + 1}/{max_attempts}]")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(5)
                    else:
                        log.error(f"Persistent authentication failure for account {account_name}")
                        raise
        
        for account_name, account_token in self.accounts_data.items():
            try:
                app = await authenticate_account(account_name, account_token)
                self.bot.loop.create_task(self.tweetsUpdater(app)).set_name(f'TweetsUpdater_{account_name}')
            except Exception:
                sys.exit(1)

        # Initial user list for notification tasks
        for (username, client_used), _ in self.latest_tweet_timestamps.items():
            self.bot.loop.create_task(self.notification(username, client_used)).set_name(username)
        
        self.bot.loop.create_task(self.tasksMonitor()).set_name('TasksMonitor')

    async def timestamp_updater(self):
        """Periodically reads all user timestamps from the DB into a shared dictionary."""
        while True:
            try:
                async with connect_readonly(self.db_path) as db:
                    async with db.execute('SELECT username, client_used, lastest_tweet FROM user WHERE enabled = 1') as cursor:
                        new_timestamps = {}
                        async for row in cursor:
                            new_timestamps[(row[0], row[1])] = row[2]
                        self.latest_tweet_timestamps = new_timestamps
                
                if not self.timestamps_ready.is_set():
                    self.timestamps_ready.set()
                    log.info("Initial tweet timestamps loaded.")

            except Exception as e:
                log.error(f"Error in timestamp_updater: {e}")

            await asyncio.sleep(60) # Update every 60 seconds

    async def db_writer(self):
        """Singleton task to handle all database write operations."""
        while True:
            try:
                username, new_timestamp = await self.db_write_queue.get()
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('UPDATE user SET lastest_tweet = ? WHERE username = ?', (str(new_timestamp), username))
                    await db.commit()
                self.db_write_queue.task_done()
            except Exception as e:
                log.error(f"Error in db_writer: {e}")

    async def notification(self, username: str, client_used: str):
        while True:
            await asyncio.sleep(configs['tweets_check_period'])

            last_tweet_at = self.latest_tweet_timestamps.get((username, client_used))
            if not last_tweet_at:
                # This can happen if a user is removed right after the sleep.
                log.warning(f"No timestamp for {username}, task will terminate.")
                break

            lastest_tweets = await get_tweets(self.tweets[client_used], username, last_tweet_at)
            if not lastest_tweets:
                continue
            
            newest_timestamp = lastest_tweets[-1].created_on
            # Update local cache immediately to prevent re-notification
            self.latest_tweet_timestamps[(username, client_used)] = str(newest_timestamp)
            # Queue the database update
            await self.db_write_queue.put((username, newest_timestamp))

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.cursor() as cursor:
                    await cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
                    user = await cursor.fetchone()
                    if not user: continue

                    for tweet in lastest_tweets:
                        log.info(f'find a new tweet from {username}')
                        url = re.sub('twitter', DOMAIN_NAME, tweet.url) if EMBED_TYPE == 'fx_twitter' else tweet.url
                        
                        view, create_view = None, False
                        if bool(tweet.media) and tweet.media[0].type == 'video' and EMBED_TYPE == 'built_in' and configs['embed']['built_in']['video_link_button']:
                            create_view = True
                            button_label, button_url = 'View Video', tweet.media[0].expanded_url
                        elif EMBED_TYPE == 'fx_twitter' and configs['embed']['fx_twitter']['original_url_button']:
                            create_view = True
                            button_label, button_url = 'View Original', tweet.url

                        if create_view:
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(label=button_label, style=discord.ButtonStyle.link, url=button_url))
                        
                        await cursor.execute('SELECT * FROM notification WHERE user_id = ? AND enabled = 1', (user['id'],))
                        notifications = await cursor.fetchall()
                        for data in notifications:
                            channel = self.bot.get_channel(int(data['channel_id']))
                            if channel is not None and is_match_type(tweet, data['enable_type']) and is_match_media_type(tweet, data['enable_media_type']):
                                try:
                                    mention = f"{channel.guild.get_role(int(data['role_id'])).mention} " if data['role_id'] else ''
                                    author, action = tweet.author.name, get_action(tweet)
                                    
                                    if not data['customized_msg']: msg = configs['default_message']
                                    else: msg = re.sub(r":(\w+):", lambda match: replace_emoji(match, channel.guild), data['customized_msg']) if configs['emoji_auto_format'] else data['customized_msg']
                                    msg = msg.format(mention=mention, author=author, action=action, url=url)

                                    if EMBED_TYPE == 'fx_twitter':
                                        await channel.send(msg, view=view)
                                    else:
                                        footer = 'twitter.png' if configs['embed']['built_in']['legacy_logo'] else 'x.png'
                                        file = discord.File(f'images/{footer}', filename='footer.png')
                                        await channel.send(msg, file=file, embeds=await gen_embed(tweet), view=view)

                                except Exception as e:
                                    if not isinstance(e, discord.errors.Forbidden):
                                        log.error(f'an error occurred at {channel.mention} while sending notification: {e}')

    async def tweetsUpdater(self, app: Twitter):
        updater_name = asyncio.current_task().get_name().split('_', 1)[1]
        while True:
            try:
                self.tweets[updater_name] = await app.get_tweet_notifications()
                await asyncio.sleep(configs['tweets_check_period'])
            except Exception as e:
                log.error(f'{e} (task : tweets updater {updater_name})')
                log.error(f"an unexpected error occurred, try again in {configs['tweets_updater_retry_delay']} minutes")
                await asyncio.sleep(configs['tweets_updater_retry_delay'] * 60)

    async def tasksMonitor(self):
        """Dynamically monitors tasks based on the live timestamp cache."""
        while True:
            await asyncio.sleep(configs['tasks_monitor_check_period'] * 60)

            running_tasks = {task.get_name() for task in asyncio.all_tasks()}
            users_in_cache = {username for username, _ in self.latest_tweet_timestamps.keys()}
            
            alive_tasks = running_tasks & users_in_cache

            if alive_tasks != users_in_cache:
                dead_tasks = list(users_in_cache - alive_tasks)
                if dead_tasks:
                    log.warning(f'dead tasks : {dead_tasks}')
                    for dead_task_username in dead_tasks:
                        # Find the corresponding client_used from the cache
                        client_used = None
                        for u, c in self.latest_tweet_timestamps.keys():
                            if u == dead_task_username:
                                client_used = c
                                break
                        
                        if client_used:
                            self.bot.loop.create_task(self.notification(dead_task_username, client_used)).set_name(dead_task_username)
                            log.info(f'restart {dead_task_username} successfully using {client_used}')

            for client in self.accounts_data.keys():
                if f'TweetsUpdater_{client}' not in running_tasks:
                    log.warning(f'tweets updater {client} : dead')

            if (datetime.now(timezone.utc) - self.tasksMonitorLogAt).total_seconds() / 3600 >= configs['tasks_monitor_log_period']:
                log.info(f'alive tasks : {list(alive_tasks)}')
                for client in self.accounts_data.keys():
                    if f'TweetsUpdater_{client}' in running_tasks:
                        log.info(f'tweets updater {client} : alive')
                self.tasksMonitorLogAt = datetime.now(timezone.utc)


    async def addTask(self, username: str, client_used: str):
        """Adds a new user to the live cache and starts their notification task."""
        # Add to live cache first
        self.latest_tweet_timestamps[(username, client_used)] = str(datetime.now(timezone.utc))
        
        # Start the task
        self.bot.loop.create_task(self.notification(username, client_used)).set_name(username)
        log.info(f'new task {username} added successfully using {client_used}')

    async def removeTask(self, username: str):
        """Removes a user from the live cache and cancels their notification task."""
        key_to_remove = None
        # Create a copy of keys for safe iteration
        for u, c in list(self.latest_tweet_timestamps.keys()):
            if u == username:
                key_to_remove = (u, c)
                break
        
        # Remove from cache so the monitor doesn't restart it
        if key_to_remove and key_to_remove in self.latest_tweet_timestamps:
            del self.latest_tweet_timestamps[key_to_remove]

        # Cancel the running task
        for task in asyncio.all_tasks():
            if task.get_name() == username:
                task.cancel()
                log.info(f'task {username} has been cancelled')
                break
