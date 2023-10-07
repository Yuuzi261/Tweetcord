import discord
from discord import app_commands
from core.classes import Cog_Extension
from tweety import Twitter
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import sqlite3

from src.log import setup_logger
from src.notification.account_tracker import AccountTracker
from src.permission_check import is_administrator

log = setup_logger(__name__)

load_dotenv()

class Notification(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.account_tracker = AccountTracker(bot)

    add_group = app_commands.Group(name='add', description="Add something")


    @is_administrator()
    @add_group.command(name='notifier')
    async def notifier(self, itn : discord.Interaction, username: str, channel: discord.TextChannel, mention: discord.Role = None):
        """Add a twitter user to specific channel on your server.

        Parameters
        -----------
        username: str
            The username of the twitter user you want to turn on notifications for.
        channel: discord.TextChannel
            The channel to which the bot delivers notifications.
        mention: discord.Role
            The role to mention when notifying.
        """
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM user WHERE username='{username}'")
        match_user = cursor.fetchone()
        
        roleID = str(mention.id) if mention != None else ''
        if match_user == None:
            app = Twitter("session")
            app.load_auth_token(os.getenv('TWITTER_TOKEN'))
            try:
                new_user = app.get_user_info(username)
            except:
                await itn.followup.send(f'user {username} not found', ephemeral=True)
                return
            
            cursor.execute('INSERT INTO user VALUES (?, ?, ?)', (str(new_user.id), username, datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')))
            cursor.execute('INSERT OR IGNORE INTO channel VALUES (?)', (str(channel.id),))
            cursor.execute('INSERT INTO notification VALUES (?, ?, ?)', (str(new_user.id), str(channel.id), roleID))
            
            app.follow_user(new_user)
            
            if app.enable_user_notification(new_user): log.info(f'successfully opened notification for {username}')
            else: log.warning(f'unable to turn on notifications for {username}')
        else:
            cursor.execute('INSERT OR IGNORE INTO channel VALUES (?)', (str(channel.id),))
            cursor.execute('REPLACE INTO notification VALUES (?, ?, ?)', (match_user[0], str(channel.id), roleID))
        
        conn.commit()
        conn.close()
            
        if match_user == None: await self.account_tracker.addTask(username)
            
        await itn.followup.send(f'successfully add notifier of {username}!', ephemeral=True)


async def setup(bot):
	await bot.add_cog(Notification(bot))