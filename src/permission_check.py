import discord
from discord import app_commands


def is_owner():
    async def predicate(itn : discord.Interaction):
        info = await itn.client.application_info()
        return itn.user == info.owner
    return app_commands.check(predicate)


def is_administrator():
    def predicate(itn : discord.Interaction):
        return itn.user.guild_permissions.administrator
    return app_commands.check(predicate)