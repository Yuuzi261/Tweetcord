import os
import discord
from discord.ext import commands
import aiosqlite
from configs.load_configs import configs

async def update_presence(bot: commands.Bot):
    """
    Updates the bot's presence based on the number of enabled accounts in the database.
    """
    async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        async with db.execute('SELECT username FROM user WHERE enabled = 1') as cursor:
            count = len(await cursor.fetchall())
            presence_message = configs["activity_name"].format(count=str(count))
    await bot.change_presence(activity=discord.Activity(name=presence_message, type=getattr(discord.ActivityType, configs['activity_type'])))
