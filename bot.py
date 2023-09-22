import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import json

from src import log

logger = log.setup_logger(__name__)

load_dotenv()

bot = commands.Bot(command_prefix=os.getenv('PREFIX'), intents=discord.Intents.all())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.getenv('ACTIVIY_NAME')))
    await bot.tree.sync()
    slash = await bot.tree.sync()
    logger.info(f'loading {len(slash)} slash commands')
    bot.tree.on_error = on_tree_error
    for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
    logger.info(f'{bot.user} is online')


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


@commands.is_owner()
@bot.tree.command(name = 'upload_cookies', description = 'upload necessary cookies')
async def upload_cookies(itn : discord.Interaction, cookies : discord.Attachment):
    info = await bot.application_info()
    if itn.user != info.owner: raise commands.errors.NotOwner('only the owner can upload cookies')
    cookies = await cookies.read()
    raw = json.loads(cookies)
    needed_cookies = ['guest_id', 'guest_id_marketing', 'guest_id_ads', 'kdt', 'auth_token', 'ct0', 'twid', 'personalization_id']
    cookies = {}
    for cookie in raw:
        name = cookie['name']
        if name in needed_cookies: cookies[name] = cookie['value']
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
    await itn.response.send_message('successfully uploaded cookies', ephemeral = True)
    logger.info('successfully uploaded cookies')
        

@bot.event
async def on_tree_error(interaction : discord.Interaction, error : app_commands.AppCommandError):
    await interaction.response.send_message(error.__context__, ephemeral = True)
    logger.warning(f'an error occurred but was handled by the tree error handler, error message : {error}')
    
    
@bot.event
async def on_command_error(ctx : commands.context.Context, error : commands.errors.CommandError):
    if isinstance(error, commands.errors.CommandNotFound): return
    else: await ctx.send(error)
    logger.warning(f'an error occurred but was handled by the command error handler, error message : {error}')
    
    
if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
