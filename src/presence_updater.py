import discord

from discord.ext import commands
from configs.load_configs import configs
from src.db_function.readonly_db import connect_readonly
from configs.paths import get_db_path

RF_COUNT = '{count}'

_static_presence_set = False


async def update_presence(bot: commands.Bot):
    """
    Update the bot's presence according to the configured activity settings.

    When the activity name contains ``{count}``, replace it with the current
    number of enabled accounts. Static activity names are applied only once.
    """
    activity_name: str = configs.get("activity_name")
    activity_type = getattr(discord.ActivityType, configs.get('activity_type').lower())
    
    global _static_presence_set
    if RF_COUNT not in activity_name:
        if _static_presence_set:
            return
        _static_presence_set = True
        presence_message = activity_name
    else:
        async with connect_readonly(get_db_path()) as db:
            async with db.execute('SELECT count(*) FROM user WHERE enabled = 1') as cursor:
                count = (await cursor.fetchone())[0]
                presence_message = activity_name.format(count=str(count))
    
    if activity_type == discord.ActivityType.custom:
        activity = discord.CustomActivity(name=presence_message)
    else:
        activity = discord.Activity(name=presence_message, type=activity_type)
            
    await bot.change_presence(activity=activity)
