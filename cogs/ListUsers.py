import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os

class ListUsersCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='list_users',
        description='Lists registered Twitter usernames and their associated channels'
    )
    @commands.has_permissions(administrator=True)
    async def list_users(self, itn: discord.Interaction):
        
        server_id = itn.guild_id

        db_path = os.path.join(os.getenv('DATA_PATH', ''), 'tracked_accounts.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user.username, channel.id, notification.role_id, notification.enabled
            FROM user
            JOIN notification
            ON user.id = notification.user_id
            JOIN channel
            ON notification.channel_id = channel.id
            WHERE notification.server_id = ?
        """, (str(server_id),))
        user_channel_role_data = cursor.fetchall()

        conn.close()

        formatted_data = [
            f"{i+1}. ```{username}``` <#{channel_id}> <@&{role_id}> {':arrow_forward:' if enabled == 1 else ':pause_button:'}" if role_id 
            else f"{i+1}. ```{username}``` <#{channel_id}> {':arrow_forward:' if enabled == 1 else ':pause_button:'}"
            for i, (username, channel_id, role_id, enabled) in enumerate(user_channel_role_data)
        ]

        if not formatted_data:
            description = "***No users are registered on this server.***"
        else:
            description = '\n'.join(formatted_data)
            
        embed = discord.Embed(
            title=f'Notification List in __***{itn.guild.name}***__ ',
            description=description,
            color=0x778899
        )

        await itn.response.send_message(embed=embed)




async def setup(bot):
    await bot.add_cog(ListUsersCog(bot))