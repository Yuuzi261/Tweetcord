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
    async def list_users(self, itn: discord.Interaction, account: str = '', channel: str = '') -> None:
        """Lists all exists notifier on your server.

        Parameters:
        account: str, optional
            The client name that you want to filter.
        channel: str, optional
            The channel name that you want to filter.
        """

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
                AND (user.client_used = ? OR '' = ?)
                AND (channel.id = ? OR '' = ?)
            """, (str(server_id), account, account, channel, channel)) as cursor:
                user_channel_role_data = await cursor.fetchall()

        formatted_data = [
            f"{i + 1}. ```{username}``` <#{channel_id}>{f' <@&{role_id}>' if role_id else ''} {symbol(enable_type[0])}retweet {symbol(enable_type[1])}quote {symbol(enable_media_type[0])}text {symbol(enable_media_type[1])}media, using {client_used}"
            for i, (username, channel_id, role_id, enable_type, enable_media_type, client_used) in enumerate(user_channel_role_data)
        ]

        if not formatted_data:
            descriptions = ["***No users are registered on this server.***"]
        else:
            descriptions = ["\n".join(formatted_data[i:i + 20]) for i in range(0, len(formatted_data), 20)]  # Prevent cutting off the message

        for index, description in enumerate(descriptions):
            embed = discord.Embed(
                title=f'Notification List in __***{itn.guild.name}***__  Page [{descriptions.index(description) + 1}/{len(descriptions)}]',
                description=description,
                color=0x778899
            )

            if index == 0:
                await itn.response.send_message(embed=embed, ephemeral=True)
            else:
                await itn.followup.send(embed=embed, ephemeral=True)

    @list_users.autocomplete('account')
    async def get_clients(self, itn: discord.Interaction, account: str) -> list[app_commands.Choice[str]]:
        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            db.row_factory = aiosqlite.Row
            async with db.cursor() as cursor:
                await cursor.execute('SELECT client_used FROM user WHERE enabled = 1')
                client_used = list(set([row['client_used'] async for row in cursor]))
                return [app_commands.Choice(name=row, value=row) for row in client_used if account.lower() in row.lower()]

    @list_users.autocomplete('channel')
    async def get_channel(self, itn: discord.Interaction, input_channel: str) -> list[app_commands.Choice[str]]:
        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            db.row_factory = aiosqlite.Row
            async with db.cursor() as cursor:
                await cursor.execute('SELECT id FROM channel WHERE server_id = ?', (str(itn.guild_id),))
                channel_list = [itn.guild.get_channel(int(row['id'])) async for row in cursor]
                return [app_commands.Choice(name=f'#{channel.name}', value=str(channel.id)) for channel in channel_list if input_channel.lower() in channel.name.lower()]


async def setup(bot: commands.Bot):
    await bot.add_cog(ListUsers(bot))
