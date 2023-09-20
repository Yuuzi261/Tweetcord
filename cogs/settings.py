import discord
from discord.ext import commands
from discord import app_commands
from core.classes import Cog_Extension
import json

class Settings(Cog_Extension):
    pass

async def setup(bot):
	await bot.add_cog(Settings(bot))