# import discord
from core.classes import Cog_Extension
from tweety import Twitter
# import json
# import asyncio

from src.log import setup_logger
from src.cookies import get_cookies
from src.notification.account_tracker import AccountTracker

log = setup_logger(__name__)

class Notification(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.account_tracker = AccountTracker(bot)


async def setup(bot):
	await bot.add_cog(Notification(bot))