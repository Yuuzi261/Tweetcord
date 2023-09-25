import discord
from discord import app_commands
from core.classes import Cog_Extension
import json

from src.log import setup_logger
from src.permission_check import is_owner

log = setup_logger(__name__)


class Cookies(Cog_Extension):
    upload_group = app_commands.Group(name='upload', description="Upload something")
    
    @is_owner()
    @upload_group.command(name = 'cookies', description = 'upload necessary cookies.')
    async def upload_cookies(self, itn : discord.Interaction, cookies : discord.Attachment):
        await itn.response.defer(ephemeral=True)
        cookies = await cookies.read()
        raw = json.loads(cookies)
        needed_cookies = ['guest_id', 'guest_id_marketing', 'guest_id_ads', 'kdt', 'auth_token', 'ct0', 'twid', 'personalization_id']
        cookies = {}
        for cookie in raw:
            name = cookie['name']
            if name in needed_cookies: cookies[name] = cookie['value']
        with open('cookies.json', 'w') as f:
            json.dump(cookies, f)
        await itn.followup.send('successfully uploaded cookies', ephemeral = True)
        log.info('successfully uploaded cookies')


async def setup(bot):
	await bot.add_cog(Cookies(bot))