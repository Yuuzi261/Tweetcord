import discord
from discord import app_commands
from core.classes import Cog_Extension
from dotenv import load_dotenv
import os
import aiosqlite

from src.log import setup_logger
from src.sync_db.sync_db import sync_db

log = setup_logger(__name__)

load_dotenv()

class Sync(Cog_Extension):

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='sync')
    async def sync(self, itn : discord.Interaction):
        """To sync the notification of new Twitter account with database, use this command.
        """
        
        await itn.response.defer(ephemeral=True)
        
        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM user') as cursor:
                follow_list = await cursor.fetchall()
        
        self.bot.loop.create_task(sync_db(follow_list))
        
        await itn.followup.send(f'synchronizing in the background', ephemeral=True)


async def setup(bot):
	await bot.add_cog(Sync(bot))