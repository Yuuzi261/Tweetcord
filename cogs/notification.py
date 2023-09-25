import discord
from discord import app_commands
from core.classes import Cog_Extension
from tweety import Twitter
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json

from src.log import setup_logger
from src.get_cookies import get_cookies
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
    @add_group.command(name='notifier', description="Add a twitter user to specific channel on your server.")
    async def notifier(self, itn : discord.Interaction, username: str, channel: discord.TextChannel, mention: discord.Role = None):
        await itn.response.defer(ephemeral=True)
        with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'r', encoding='utf8') as jfile:
            users = json.load(jfile)
        match_user = list(filter(lambda item: item[1]["username"] == username, users.items()))
        if match_user == []:
            cookies = get_cookies()
            app = Twitter("session")
            app.load_cookies(cookies)
            try:
                new_user = app.get_user_info(username)
            except:
                await itn.followup.send(f'user {username} not found', ephemeral=True)
                return
            roleID = str(mention.id) if mention != None else ''
            users[str(new_user.id)] = {'username': username, 'channels': {str(channel.id): roleID}, 'lastest_tweet': datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')}
        else:
            user = match_user[0][1]
            user['channel'][str(channel.id)] = str(mention.id) if mention != None else ''
            
        with open(f"{os.getenv('DATA_PATH')}tracked_accounts.json", 'w', encoding='utf8') as jfile:
            json.dump(users, jfile)
        
        app.follow_user(new_user)
            
        if app.enable_user_notification(new_user): log.info(f'successfully opened notification for {username}')
        else: log.warning(f'unable to turn on notifications for {username}')
        
        await self.account_tracker.addTask(username)
        
        await itn.followup.send(f'successfully add notifier of {username}!', ephemeral=True)


async def setup(bot):
	await bot.add_cog(Notification(bot))