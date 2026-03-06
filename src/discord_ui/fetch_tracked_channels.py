import os

import discord
from discord import app_commands
import aiosqlite

from src.db_function.readonly_db import connect_readonly

async def fetch_tracked_channels(itn: discord.Integration, input_channel: str, include_unknown: bool) -> list[app_commands.Choice[str]]:
    input_channel = input_channel.lower().replace("#", "")

    async with connect_readonly(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        db.row_factory = aiosqlite.Row
        async with db.cursor() as cursor:
            # Don't show channels that no longer have any notifiers
            await cursor.execute('''
                SELECT c.id
                FROM channel AS c
                WHERE c.server_id = ?
                AND EXISTS (
                    SELECT 1
                    FROM notification AS n
                    WHERE n.channel_id = c.id
                    AND n.enabled = 1
                )
            ''', (str(itn.guild_id),))
            result = []
            async for row in cursor:
                channel_id = row['id']
                channel = itn.guild.get_channel_or_thread(int(channel_id))

                if (channel is None and input_channel) or (channel is not None and input_channel not in channel.name.lower()):
                    continue

                if isinstance(channel, discord.TextChannel): name = f'# {channel.name}'
                elif isinstance(channel, discord.Thread): name = f'🧵 {channel.name}'
                elif not include_unknown: continue
                else: name = f'# unknown ({channel_id})'

                result.append(app_commands.Choice(name=name, value=channel_id))
            return result
