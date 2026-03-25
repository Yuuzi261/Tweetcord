import os

import aiosqlite
import discord
from discord import ui

from src.utils import get_lock

lock = get_lock()

class CustomizeSettingsModal(ui.Modal, title='customize settings'):
    def __init__(self, user_id: str, username: str, channel: discord.TextChannel | discord.Thread, enable_type: str, media_type: str, customized_msg: str = None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.username = username
        self.channel = channel
        self.title = f'Editing @{username} in #{channel.name}'
        if len(self.title) > 30:
            self.title = f'@{username} in #{channel.name}'
        if len(self.title) > 30:
            self.title = f'@{username}'

        # Enable Type (Retweet, Quote) - CheckboxGroup
        self.enable_type_checkbox = ui.CheckboxGroup(
            options=[
                discord.CheckboxGroupOption(label='Retweet', value='retweet', default=(enable_type[0] == '1')),
                discord.CheckboxGroupOption(label='Quote', value='quote', default=(enable_type[1] == '1'))
            ],
            min_values=0,
            max_values=2,
            required=False
        )
        self.enable_type_label = ui.Label(text='Enable notifications for:', component=self.enable_type_checkbox)
        self.add_item(self.enable_type_label)

        # Media Type (All, No Media, Media Only) - RadioGroup
        self.media_type_radio = ui.RadioGroup(
            options=[
                discord.RadioGroupOption(label='All', value='11', default=(media_type == '11')),
                discord.RadioGroupOption(label='No Media', value='10', default=(media_type == '10')),
                discord.RadioGroupOption(label='Media Only', value='01', default=(media_type == '01'))
            ]
        )
        self.media_type_label = ui.Label(text='Media settings:', component=self.media_type_radio)
        self.add_item(self.media_type_label)
        
        # Customized Message - TextInput
        self.customized_msg = ui.TextInput(
            placeholder='Leave it empty to use default.',
            default=customized_msg,
            max_length=200,
            style=discord.TextStyle.long,
            required=False
        )
        self.customized_msg_label = ui.Label(text='Customizing message:', component=self.customized_msg)
        self.add_item(self.customized_msg_label)

    async def on_submit(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)

        # Convert checkbox values back to '11', '10', '01', '00'
        selected_types = self.enable_type_checkbox.values
        retweet_bit = '1' if 'retweet' in selected_types else '0'
        quote_bit = '1' if 'quote' in selected_types else '0'
        new_enable_type = retweet_bit + quote_bit
        
        new_media_type = self.media_type_radio.value
        customized_msg = self.customized_msg.value if self.customized_msg.value else None

        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            db.row_factory = aiosqlite.Row
            async with lock:
                await db.execute('UPDATE notification SET enable_type = ?, enable_media_type = ?, customized_msg = ? WHERE user_id = ? AND channel_id = ?', (new_enable_type, new_media_type, customized_msg, self.user_id, str(self.channel.id)))
                await db.commit()

        await itn.followup.send('setting successful', ephemeral=True)
