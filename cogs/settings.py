import discord
from discord.ext import commands
from discord import app_commands
from core.classes import Cog_Extension
import json

with open('setting.json', 'r', encoding='utf8') as jfile:
	jdata = json.load(jfile)

class Settings(Cog_Extension):
    pass

async def setup(bot):
	await bot.add_cog(Settings(bot))