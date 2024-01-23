<div align="center">

<img alt="LOGO" src="https://i.imgur.com/WKXJDZL.png" width="300" height="300" />
  
# Tweetcord

A Twitter Alert Bot For Discord

[**English**](./README.md) | [**繁體中文**](./README_zh.md)

</div>

## 📝Introduction

Tweetcord is a discord bot that uses the tweety-ns module to let you receive tweet updates from specific Twitter users on discord. You just need to set up the Twitter users and discord channels you want to follow, and Tweetcord will automatically send the tweets to the designated channels, so you won’t miss any important news.🐦

## ✨Features

<details>
   <summary>

### Screenshots

   </summary>
👇When the followed user posts a new tweet, your server will also receive a notification.

![](https://i.imgur.com/SXITM0a.png)

</details>

<details>
   <summary>

### Commands

   </summary>

👉 `/add notifier` `username` `channel` | `mention`

| parameters | types | descriptions |
| --------- | ----- | ----------- |
| `username` | str | The username of the twitter user you want to turn on notifications for |
| `channel` | discord.TextChannel | The channel to which the bot delivers notifications |
| `mention` | discord.Role | The role to mention when notifying |

👉 `/remove notifier` `username` `channel`

| parameters | types | descriptions |
| --------- | ----- | ----------- |
| `username` | str | The username of the twitter user you want to turn off notifications for |
| `channel` | discord.TextChannel | The channel which set to delivers notifications |

👉 `/list users`

- List all twitter users whose notifications are enabled on the current server

👉 `/sync`

- Sync the notification of new Twitter account with database.  If you change the twitter account used by bot, please use this command

</details>

## 📥Installation

Before running the bot, you need to install the necessary modules.

```shell
pip install -r requirements.txt
```

In certain operating systems, you may need to use the command `pip3` instead of `pip` for installation.

## ⚡Usage

**📢This tutorial is suitable for version 0.3.2 or later. (Recommended: 0.3.5 or later)**

<details>
   <summary><b>📌click here to upgrade from 0.3.4 to 0.3.5</b></summary>

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade` to upgrade. This cog can be removed after the upgrade is completed.

```py
import discord
from discord import app_commands
from core.classes import Cog_Extension
import sqlite3
import os

from src.log import setup_logger
from src.permission_check import is_administrator

log = setup_logger(__name__)

class Upgrade(Cog_Extension):

    @is_administrator()
    @app_commands.command(name='upgrade', description='upgrade to Tweetcord 0.3.5')
    async def upgrade(self, itn: discord.Interaction):
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()

        cursor.executescript('ALTER TABLE channel ADD server_id TEXT')
        
        cursor.execute('SELECT id FROM channel')
        channels = cursor.fetchall()
        
        for c in channels:
            try:
                channel = self.bot.get_channel(int(c[0]))
                cursor.execute('UPDATE channel SET server_id = ? WHERE id = ?', (channel.guild.id, channel.id))
            except:
                log.warning(f'the bot cannot obtain channel: {c[0]}, but this will not cause problems with the original features. The new feature can also be used normally on existing servers.')
                

        conn.commit()
        conn.close()

        await itn.followup.send('successfully upgrade to 0.3.5, you can remove this cog.')


async def setup(bot):
    await bot.add_cog(Upgrade(bot))
```

</details>

<details>
   <summary><b>📌click here to upgrade from 0.3.3 to 0.3.4</b></summary>

Because the database structure has been updated, you must use the following code to update the database structure.

```py
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
cursor = conn.cursor()

cursor.execute('ALTER TABLE notification ADD enabled INTEGER DEFAULT 1')

conn.commit()
conn.close()
```

</details>

### 1. Create and configure the .env file

```env
BOT_TOKEN=YourDiscordBotToken
TWITTER_TOKEN=YourTwitterAccountAuthToken
DATA_PATH=./data/
```

You can retrieve your auth token from cookies, or you can explore other methods to obtain it.

### 2. Configure the configs.yml file

All time-related configurations are measured in seconds.

```yml
prefix: ''                          # The prefix for bot commands.
activity_name: ''                   # The activity name displayed by the bot.
tweets_check_period: 10             # The check frequency for the posts (it is not recommended to set this value too low to avoid rate limiting).
tweets_updater_retry_delay: 300     # Retry Interval when Tweets Updater encounters exceptions (e.g., rate limitations).
tasks_monitor_check_period: 60      # Interval at which to check if each tasks is functioning properly, and if a task has stopped, attempt a restart.
tasks_monitor_log_period: 14400     # Interval at which to output the list of currently running tasks to the execution log.
auto_turn_off_notification: true    # (v0.4.0 or later) If all notifications for a user are disabled, decide whether to unfollow the user.
auto_unfollow: true                 # (v0.4.0 or later) If all notifications for a user is disabled, decide whether to disable notification for the user (twitter side).
```

### 3. Run and invite the bot to your server

```shell
python bot.py
```

In certain operating systems, you may need to use `python3` instead of `python`.

🔧Bot Permissions Setup `2147666944`

- [x] Read Messages/View Channels
- [x] Send Messages
- [x] Embed Links
- [x] Attach Files
- [x] Mention Everyone
- [x] Use Slash Commands

> [!NOTE]
> If you want to host the bot on a server, here is a recommended service that is basically free: [fly.io](https://fly.io).

### 4. Have fun

Now you can go back to Discord and use the `/add notifier` command to set up notifications for the Twitter users you wish to receive updates from!

## 💪Contributors

This project exists thanks to all the people who contribute.

[![](https://contrib.rocks/image?repo=Yuuzi261/Tweetcord)](https://github.com/Yuuzi261/Tweetcord/graphs/contributors)
