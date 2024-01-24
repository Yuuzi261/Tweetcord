import discord
import os
import sqlite3

class CustomizeMsgModal(discord.ui.Modal, title='customize message'):
    def __init__(self, user_id: str, username: str, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel = channel
        label = f'customizing message for @{username} in #{channel.name}'
        if len(label) > 45: label = f'customizing message for @{username}'
        if len(label) > 45: label = f'customizing message'
        self.customized_msg = discord.ui.TextInput(label=label, placeholder='enter customized message', max_length=200, style=discord.TextStyle.long, required=True)
        self.add_item(self.customized_msg)

    async def on_submit(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('UPDATE notification SET customized_msg = ? WHERE user_id = ? AND channel_id = ?', (self.customized_msg.value, self.user_id, str(self.channel.id)))
        conn.commit()
        conn.close()
        
        await itn.followup.send('setting successful', ephemeral=True)