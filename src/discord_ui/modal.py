import os

import aiosqlite
import discord

from src.i18n import t
from src.utils import get_lock

lock = get_lock()

class CustomizeMsgModal(discord.ui.Modal):
    def __init__(self, user_id: str, username: str, channel: discord.TextChannel | discord.Thread):
        super().__init__(title=t('modal.customize_message.title'), timeout=None)
        self.user_id = user_id
        self.channel = channel
        label = t('modal.customize_message.label_full', username=username, channel_name=channel.name)
        if len(label) > 45:
            label = t('modal.customize_message.label_short', username=username)
        if len(label) > 45:
            label = t('modal.customize_message.label_fallback')
        self.customized_msg = discord.ui.TextInput(label=label, placeholder=t('modal.customize_message.placeholder'), max_length=200, style=discord.TextStyle.long, required=True)
        self.add_item(self.customized_msg)

    async def on_submit(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)

        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            db.row_factory = aiosqlite.Row
            async with lock:
                await db.execute('UPDATE notification SET customized_msg = ? WHERE user_id = ? AND channel_id = ?', (self.customized_msg.value, self.user_id, str(self.channel.id)))
                await db.commit()

        await itn.followup.send(t('modal.customize_message.success'), ephemeral=True)
