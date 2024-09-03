import discord
from discord import app_commands
from core.classes import Cog_Extension
import aiosqlite
import os

from src.utils import str_to_bool as stb
from src.permission import ADMINISTRATOR

CHECK = '\u2705'
XMARK = '\u274C'

class ListUsers(Cog_Extension):
    
    list_group = app_commands.Group(name='list', description='List something', default_permissions=ADMINISTRATOR)

    @list_group.command(name='users')
    async def list_users(self, itn: discord.Interaction):
        """Lists all exists notifier on your server."""
        
        server_id = itn.guild_id

        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            async with db.execute("""
                SELECT user.username, channel.id, notification.role_id, notification.enable_type
                FROM user
                JOIN notification
                ON user.id = notification.user_id
                JOIN channel
                ON notification.channel_id = channel.id
                WHERE channel.server_id = ? AND notification.enabled = 1
            """, (str(server_id),)) as cursor:
                user_channel_role_data = await cursor.fetchall()

        formatted_data = [
            f"{i+1}. ```{username}``` <#{channel_id}>{f' <@&{role_id}>' if role_id else ''} {CHECK if stb(enable_type[0]) else XMARK}retweet {CHECK if stb(enable_type[1]) else XMARK}quote"
            for i, (username, channel_id, role_id, enable_type) in enumerate(user_channel_role_data)
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

        await itn.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ListUsers(bot))