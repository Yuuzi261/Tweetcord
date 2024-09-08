import os

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from core.classes import Cog_Extension
from src.permission import ADMINISTRATOR
from src.utils import str_to_bool as stb

CHECK = '\u2705'
XMARK = '\u274C'


def symbol(value: str) -> str:
    return CHECK if stb(value) else XMARK


class ListUsers(Cog_Extension):

    list_group = app_commands.Group(name='list', description='List something', default_permissions=ADMINISTRATOR)

    @list_group.command(name='users')
    async def list_users(self, itn: discord.Interaction):
        """Lists all exists notifier on your server."""

        server_id = itn.guild_id

        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            async with db.execute("""
                SELECT user.username, channel.id, notification.role_id, notification.enable_type, notification.enable_media_type, user.client_used
                FROM user
                JOIN notification
                ON user.id = notification.user_id
                JOIN channel
                ON notification.channel_id = channel.id
                WHERE channel.server_id = ? AND notification.enabled = 1
            """, (str(server_id),)) as cursor:
                user_channel_role_data = await cursor.fetchall()

        formatted_data = [
            f"{i + 1}. ```{username}``` <#{channel_id}>{f' <@&{role_id}>' if role_id else ''} {symbol(enable_type[0])}retweet {symbol(enable_type[1])}quote {symbol(enable_media_type[0])}text {symbol(enable_media_type[1])}media, using {client_used}"
            for i, (username, channel_id, role_id, enable_type, enable_media_type, client_used) in enumerate(user_channel_role_data)
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


async def setup(bot: commands.Bot):
    await bot.add_cog(ListUsers(bot))
