<div align="center">

<img alt="LOGO" src="https://i.imgur.com/WKXJDZL.png" width="300" height="300" />
  
# Tweetcord

A Discord Bot for Twitter Notifications

[![](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![](https://img.shields.io/github/v/release/Yuuzi261/Tweetcord?sort=semver)](https://github.com/Yuuzi261/Tweetcord/releases)
[![](https://img.shields.io/github/release-date/Yuuzi261/Tweetcord)](https://github.com/Yuuzi261/Tweetcord/releases)

[**English**](./README.md) | [**繁體中文**](./README_zh.md)

</div>

## 📝Introduction

Tweetcord is a Discord bot that leverages the [tweety-ns module](https://github.com/mahrtayyab/tweety) to provide real-time tweet updates from specific Twitter users directly to your Discord server. Simply configure the Twitter users and Discord channels you want to monitor, and Tweetcord will automatically forward tweets to the designated channels, ensuring you never miss important updates.🐦

## ✨Features

<details>
   <summary>

### Screenshots

   </summary>
👇Whenever a followed user posts a new tweet, your server will receive an instant notification.

![](https://i.imgur.com/SXITM0a.png)

</details>

<details>
   <summary>

### Commands

   </summary>

👉 `/add notifier` `username` `channel` | `mention` `type`

| parameters | types | descriptions |
| --------- | ----- | ----------- |
| `username` | str | The username of the twitter user you want to turn on notifications for |
| `channel` | discord.TextChannel | The channel to which the bot delivers notifications |
| `mention` | discord.Role | The role to mention when notifying |
| `type` | str | Whether to enable notifications for retweets & quotes |

👉 `/remove notifier` `username` `channel`

| parameters | types | descriptions |
| --------- | ----- | ----------- |
| `username` | str | The username of the twitter user you want to turn off notifications for |
| `channel` | discord.TextChannel | The channel which set to delivers notifications |

👉 `/list users`

- List all twitter users whose notifications are enabled on the current server

👉 `/sync`

- Sync the notification of new Twitter account with database.  If you change the twitter account used by bot, please use this command

👉 `/customize message` `username` `channel` | `default`

| parameters | types | descriptions |
| --------- | ----- | ----------- |
| `username` | str | The username of the twitter user you want to set customized message |
| `channel` | discord.TextChannel | The channel which set to delivers notifications |
| `default` | bool | Whether to use default setting _(default is false)_ |

Custom notification messages are in `f-string format`, currently supporting 4 special variables for use, which will be explained below.

- `{action}` : poster's action, include `tweeted`, `retweeted` and `quoted`
- `{author}` : poster's display name
- `{mention}` : the role to mention when sending to discord
- `{url}` : the link of the tweet

</details>

## 📥Installation

Before running the bot, you need to install the necessary modules.

```shell
pip install -r requirements.txt
```

## ⚡Usage

**📢This tutorial is suitable for version 0.3.2 or later. (Recommended: 0.3.5 or later)**

### [⬆️View Version Upgrade Guides](./UPGRADE_GUIDE.md)

### 1. Create and configure the .env file

```env
BOT_TOKEN=YourDiscordBotToken
TWITTER_TOKEN=YourTwitterAccountAuthToken
DATA_PATH=./data
```

You can retrieve your auth token from cookies, or you can explore other methods to obtain it.

### 2. Configure the configs.yml file

> [!IMPORTANT]
> All configuration instructions here are synchronized with the latest version. For users of the old version, please refer to the old README.

#### Base

- `prefix` : The prefix for bot commands, only effective for prefix commands.
- `activity_name` : The activity name displayed by the bot.

#### Timer

All configurations are measured in seconds.

- `tweets_check_period` : The check frequency for the posts, it is not recommended to set this value too low to avoid rate limiting. Default value: `10`, Safty value: `18`([why is this value?](https://github.com/mahrtayyab/tweety/wiki/FAQs#twitter-new-limits)), not recommended below `10`. If the account controlled by Tweetocrd is the same as the account you usually use, please increase the value appropriately to avoid rate limiting.
- `tweets_updater_retry_delay` : Retry Interval when Tweets Updater encounters exceptions.
- `tasks_monitor_check_period` : Interval at which to check if each tasks is functioning properly, and if a task has stopped, attempt a restart.
- `tasks_monitor_log_period` : Interval at which to output the list of currently running tasks to the execution log.

#### Control Account Behavior

- `auto_turn_off_notification` : If all notifications for a user are disabled, decide whether to unfollow the user.
- `auto_unfollow` : If all notifications for a user is disabled, decide whether to disable notification for the user (twitter side).

#### Embed Style

- `type` : Determine the type of embed, supported types: `built_in` / `fx_twitter`.

built_in:

- `fx_image` : Whether to use FxTwitter's combined image when there are multiple images, friendly for iOS systems that cannot display multiple image embeddings.
- `video_link_button` : #TODO
- `footer_logo` : #TODO

fx_twitter:

- `original_url_button` : #TODO

#### Message

- `default_message` : Set default message format globally, the format is the same as the customized message, use f-string and support 4 special variables. For details, please refer to [Commands](#commands).

### 3. Run and invite the bot to your server

```shell
python bot.py
```

🔧Bot Permissions Setup `2147666944`

- [x] Read Messages/View Channels
- [x] Send Messages
- [x] Embed Links
- [x] Attach Files
- [x] Mention Everyone
- [x] Use Slash Commands

> [!NOTE]
> If you want to host the bot on a server, here is a recommended service that is basically free: [fly.io](https://fly.io). _(update: fly.io has stopped offering free plans to new users)_

> [!TIP]
> Alternatively, you can try this virtual hosting service provided by Taiwanese students: [FreeServer](https://freeserver.tw/index.html)

<details>
   <summary><b>⚙️some configuration files you may need if you use fly.io</b></summary>

- dockerfile

```dockerfile
FROM python:3.10.9
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot/
CMD python bot.py
```

- fly.toml

```toml
app = "YOUR_APP_NAME"
primary_region = "YOUR_APP_REGION"

[env]
  DATA_PATH = "/data"

[mounts]
  source = "YOUR_APP_VOLUME_NAME"
  destination = "/data"
```

</details>

### 4. Have fun

Now you can go back to Discord and use the `/add notifier` command to set up notifications for the Twitter users you wish to receive updates from!

## 💪Contributors

This project exists thanks to all the people who contribute.

[![](https://contrib.rocks/image?repo=Yuuzi261/Tweetcord)](https://github.com/Yuuzi261/Tweetcord/graphs/contributors)
