# Tweetcord

Tweetcord is a discord bot that uses the tweety module to let you receive tweet updates from specific Twitter users on discord. You just need to set up the Twitter users and discord channels you want to follow, and Tweetcord will automatically send the tweets to the designated channels, so you won’t miss any important news.🐦

## Features

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

</details>

## Installation

Before running the bot, you need to install the necessary modules.

```shell
pip install -r requirements.txt
```

In certain operating systems, you may need to use the command `pip3` instead of `pip` for installation.

## Usage

**📢This tutorial is suitable for version 0.3.2 or higher.**

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
```

### 3. Run the bot

```shell
python bot.py
```

In certain operating systems, you may need to use `python3` instead of `python`.

### 4. Have fun

Now you can go back to Discord and use the `/add notifier` command to set up notifications for the Twitter users you wish to receive updates from!
