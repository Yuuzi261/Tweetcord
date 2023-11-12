import discord
from discord import app_commands
from core.classes import Cog_Extension
import sqlite3
import os

from src.permission_check import is_administrator

class ListUsers(Cog_Extension):
    
    list_group = app_commands.Group(name='list', description="List something")

    @is_administrator()
    @list_group.command(name='users')
    async def list_users(self, itn: discord.Interaction):
        """Lists all exists notifier on your server."""
        
        server_id = itn.guild_id

        db_path = os.path.join(os.getenv('DATA_PATH', ''), 'tracked_accounts.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user.username, channel.id, notification.role_id
            FROM user
            JOIN notification
            ON user.id = notification.user_id
            JOIN channel
            ON notification.channel_id = channel.id
            WHERE channel.server_id = ? AND notification.enabled = 1
        """, (str(server_id),))
        user_channel_role_data = cursor.fetchall()

        conn.close()

        formatted_data = [
            f"{i+1}. ```{username}``` <#{channel_id}> <@&{role_id}>" if role_id else f"{i+1}. ```{username}``` <#{channel_id}>"
            for i, (username, channel_id, role_id) in enumerate(user_channel_role_data)
        ]
        
        if not formatted_data:
            description = "***No users are registered on this server.***"
        else:
            description = '\n'.join(formatted_data)
            
        embed = discord.Embed(
            title=f'Notification List in __***{itn.guild.name}***__ ',
            description=description,
            color=0x778899
        )

        await itn.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ListUsers(bot))