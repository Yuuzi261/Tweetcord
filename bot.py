import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

load_dotenv()

bot = commands.Bot(command_prefix=os.getenv('PREFIX'), intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.getenv('ACTIVIY_NAME')))
    for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
    print('[INFO] Bot is online')

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
    
    
@bot.command()
@commands.is_owner()
@commands.dm_only()
async def uploadCookies(ctx):
    txtfile = await [attachment for attachment in ctx.message.attachments if attachment.filename[-4:] == '.txt'][0].read()
    raw = json.loads(txtfile)
    needed_cookies = ['guest_id', 'guest_id_marketing', 'guest_id_ads', 'kdt', 'auth_token', 'ct0', 'twid', 'personalization_id']
    cookies = {}
    for cookie in raw:
        name = cookie['name']
        if name in needed_cookies: cookies[name] = cookie['value']
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
        

@bot.event
async def on_command_error(ctx, error):
    embed=discord.Embed(title="ERROR", color=0xb7e0f3)
    
    if isinstance(error, commands.errors.CommandNotFound):
        return
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        embed.add_field(name="No Private Message", value="This command can only be used in private messages", inline=False)
        embed.add_field(name="Error message", value=error, inline=False)
    else:
        embed.add_field(name="ERROR", value="An unexpected error occurred", inline=False)
        embed.add_field(name="Error message", value=error, inline=False)

    await ctx.send(embed=embed)
    
    
if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
