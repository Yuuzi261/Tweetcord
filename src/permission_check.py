import discord
from discord import app_commands

def is_administrator():
    def predicate(itn : discord.Interaction):
        return itn.user.guild_permissions.administrator
    return app_commands.check(predicate)