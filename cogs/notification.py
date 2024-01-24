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
from src.permission import ADMINISTRATOR
from configs.load_configs import configs

log = setup_logger(__name__)

load_dotenv()

class CustomizeMsgModal(discord.ui.Modal, title='customize message'):
    def __init__(self, user_id: str, username: str, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel = channel
        label = f'customizing message for @{username} in #{channel.name}'
        if len(label) > 45: label = f'customizing message for @{username}'
        if len(label) > 45: label = f'customizing message'
        self.customized_msg = discord.ui.TextInput(label=label, placeholder='enter customized message', max_length=200, style=discord.TextStyle.long, required=True)
        self.add_item(self.customized_msg)

    async def on_submit(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('UPDATE notification SET customized_msg = ? WHERE user_id = ? AND channel_id = ?', (self.customized_msg.value, self.user_id, str(self.channel.id)))
        conn.commit()
        conn.close()
        
        await itn.followup.send('setting successful', ephemeral=True)

class Notification(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.account_tracker = AccountTracker(bot)

    add_group = app_commands.Group(name='add', description='Add something', default_permissions=ADMINISTRATOR)
    remove_group = app_commands.Group(name='remove', description='Remove something', default_permissions=ADMINISTRATOR)
    customize_group = app_commands.Group(name='customize', description='Customize something', default_permissions=ADMINISTRATOR)

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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        match_user = cursor.fetchone()
        
        server_id = str(channel.guild.id)
        roleID = str(mention.id) if mention != None else ''
        if match_user == None or match_user['enabled'] == 0:
            app = Twitter("session")
            app.load_auth_token(os.getenv('TWITTER_TOKEN'))
            try:
                new_user = app.get_user_info(username)
            except:
                await itn.followup.send(f'user {username} not found', ephemeral=True)
                return
            
            if match_user == None:
                cursor.execute('INSERT INTO user VALUES (?, ?, ?)', (str(new_user.id), username, datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')))
                cursor.execute('INSERT OR IGNORE INTO channel VALUES (?, ?)', (str(channel.id), server_id))
                cursor.execute('INSERT INTO notification (user_id, channel_id, role_id) VALUES (?, ?, ?)', (str(new_user.id), str(channel.id), roleID))
            else:
                cursor.execute('INSERT OR IGNORE INTO channel VALUES (?, ?)', (str(channel.id), server_id))
                cursor.execute('REPLACE INTO notification (user_id, channel_id, role_id) VALUES (?, ?, ?)', (match_user['id'], str(channel.id), roleID))
                cursor.execute('UPDATE user SET enabled = 1 WHERE id = ?', (match_user['id'],))
                
            
            app.follow_user(new_user)
            
            if app.enable_user_notification(new_user): log.info(f'successfully turned on notification for {username}')
            else: log.warning(f'unable to turn on notifications for {username}')
        else:
            cursor.execute('INSERT OR IGNORE INTO channel VALUES (?, ?)', (str(channel.id), server_id))
            cursor.execute('REPLACE INTO notification (user_id, channel_id, role_id) VALUES (?, ?, ?)', (match_user['id'], str(channel.id), roleID))
        
        conn.commit()
        conn.close()
            
        if match_user == None or match_user['enabled'] == 0: await self.account_tracker.addTask(username)
            
        await itn.followup.send(f'successfully add notifier of {username}!', ephemeral=True)


    @remove_group.command(name='notifier')
    async def notifier(self, itn : discord.Interaction, username: str, channel: discord.TextChannel):
        """Remove a notifier on your server.

        Parameters
        -----------
        username: str
            The username of the twitter user you want to turn off notifications for.
        channel: discord.TextChannel
            The channel which set to delivers notifications.
        """
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM notification, user WHERE username = ? AND channel_id = ? AND user_id = id AND notification.enabled = 1', (username, str(channel.id)))
        match_notifier = cursor.fetchone()
        if match_notifier != None:
            cursor.execute('UPDATE notification SET enabled = 0 WHERE user_id = ? AND channel_id = ?', (match_notifier['user_id'], str(channel.id)))
            conn.commit()
            await itn.followup.send(f'successfully remove notifier of {username}!', ephemeral=True)
            cursor.execute('SELECT user_id FROM notification WHERE user_id = ? AND enabled = 1', (match_notifier['user_id'],))
            
            if len(cursor.fetchall()) == 0:
                cursor.execute('UPDATE user SET enabled = 0 WHERE id = ?', (match_notifier['user_id'],))
                conn.commit()
                await self.account_tracker.removeTask(username)
                if configs['auto_unfollow'] or configs['auto_turn_off_notification']:
                    app = Twitter("session")
                    app.load_auth_token(os.getenv('TWITTER_TOKEN'))
                    target_user = app.get_user_info(username)
                    
                    if configs['auto_unfollow']: 
                        log.info(f'successfully unfollowed {username}') if app.unfollow_user(target_user) else log.warning(f'unable to unfollow {username}')
                    else:
                        log.info(f'successfully turned off notification for {username}') if app.disable_user_notification(target_user) else log.warning(f'unable to turn off notifications for {username}')
                
        else:
            await itn.followup.send(f'can\'t find notifier {username} in {channel.mention}!', ephemeral=True)
        
        conn.close()
        
        
    @customize_group.command(name='message')
    async def customize_message(self, itn : discord.Interaction, username: str, channel: discord.TextChannel, default: bool = False):
        """Set customized messages for notification.

        Parameters
        -----------
        username: str
            The username of the twitter user you want to set customized message.
        channel: discord.TextChannel
            The channel which set to delivers notifications.
        default: bool
            Whether to use default setting.
        """
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM notification, user WHERE username = ? AND channel_id = ? AND user_id = id AND notification.enabled = 1', (username, str(channel.id)))
        match_notifier = cursor.fetchone()
        if match_notifier != None:
            if default:
                await itn.response.defer(ephemeral=True)
                cursor.execute('UPDATE notification SET customized_msg = ? WHERE user_id = ? AND channel_id = ?', (None, match_notifier['user_id'], str(channel.id)))
                conn.commit()
                await itn.followup.send('successfully restored to default settings', ephemeral=True)
            else:
                modal = CustomizeMsgModal(match_notifier['user_id'], username, channel)
                await itn.response.send_modal(modal)
        else:
            await itn.response.send_message(f'can\'t find notifier {username} in {channel.mention}!', ephemeral=True)
            
        conn.close()


async def setup(bot):
	await bot.add_cog(Notification(bot))