import discord
from discord.ext import commands
from tweety import Twitter
import json
import os

with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix=jdata['PREFIX'], intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=jdata['ACTIVIY_NAME']))
    for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
    print(">> Bot is online <<")

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension} done.')


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Un - Loaded {extension} done.')


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    await bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'Re - Loaded {extension} done.')

if __name__ == "__main__":
    bot.run(jdata["TOKEN"])
