import discord
from discord import app_commands
from core.classes import Cog_Extension
from dotenv import load_dotenv
import os
import sqlite3

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
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user')
        follow_list = cursor.fetchall()
        
        conn.commit()
        conn.close()
        
        self.bot.loop.create_task(sync_db(follow_list))
            
        await itn.followup.send(f'synchronizing in the background', ephemeral=True)


async def setup(bot):
	await bot.add_cog(Sync(bot))