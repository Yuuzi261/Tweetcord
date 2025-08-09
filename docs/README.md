<div align="center">

<a href="./AVATAR.md"><img alt="LOGO" src="/images/md/avatar.png" width="300" height="300" /></a>
  
# Tweetcord

A Discord Bot for Twitter Notifications

[![](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
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

![](/images/md/screenshot.png)

</details>

<details>
   <summary>

### Commands

   </summary>

👉 `/add notifier` `username` `channel` | `mention` `type` `media_type` `account_used`

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `username` | str | The username of the twitter user you want to turn on notifications for |
| `channel` | discord.TextChannel | The channel to which the bot delivers notifications |
| `mention` | discord.Role | The role to mention when notifying |
| `type` | str | Whether to enable notifications for retweets & quotes |
| `media_type` | str | Whether to enable notifications that include media, or only enable notifications that include media |
| `account_used` | str | The twitter client used by the bot to monitor the user's tweets |

👉 `/remove notifier` `channel` `username`

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `channel` | str | The channel id which set to delivers notifications |
| `username` | str | The username of the twitter user you want to turn off notifications for |

👉 `/list users` | `account` `channel`

- List all twitter users whose notifications are enabled on the current server

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `account` | str | The client name that you want to filter |
| `channel` | str | The channel name that you want to filter |

👉 `/sync`

- Sync the notification of new Twitter account with database.  If you change the twitter account used by bot, please use this command

👉 `/customize message` `channel` `username` | `default`

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `channel` | str | The channel id which set to delivers notifications |
| `username` | str | The username of the twitter user you want to set customized message |
| `default` | bool | Whether to use default setting _(default is false)_ |

Custom notification messages are in `f-string format`, currently supporting 4 special variables for use, which will be explained below.

- `{action}` : poster's action, include `tweeted`, `retweeted` and `quoted`
- `{author}` : poster's display name
- `{mention}` : the role to mention when sending to discord
- `{url}` : the link of the tweet

Using the default notification as an example, if the message is customized to the following format (supporting Discord's markdown format):

```plaintext
{mention}**{author}** just {action} here: 
{url}
```

The notification will be sent in this format when a tweet is posted (here is a real-world example):

```plaintext
@Ping_SubTweet ﾅﾁｮﾈｺ just tweeted here: 
https://twitter.com/nyachodayo/status/1869000108697960952
```

</details>

## 📥Installation

Before running the bot, you need to install the necessary modules.

```shell
pip install -r requirements.txt
```

## ⚡Usage

**📢This tutorial applies to version 0.5 or higher. For settings of older versions, please refer to the README files of the respective historical versions.**

### [⬆️View Version Upgrade Guides](./UPGRADE_GUIDE.md)

### 1. Create and configure the .env file

```env
BOT_TOKEN=YourDiscordBotToken
TWITTER_TOKEN=NameForYourTwitterToken:YourTwitterAccountAuthToken
DATA_PATH=./data
```

> [!NOTE]  
> The `NameForYourTwitterToken` here can be freely defined. It is only used as an alias to specify the account when entering commands and does not need to match the Twitter account name.

#### Example
```env
BOT_TOKEN=FAKE1234567890ABCDEFGHIJKLMNO.PQRSTUVWXYZ1234567890.ABCDEFGHIJKLMNOPQRSTUVWXYZ123456
TWITTER_TOKEN=Account1:12345abcde67890fghij12345klmnop67890qrstuv,Account2:abcdef123456ghijkl7890mnopqrst123456uvwx
DATA_PATH=./data
```

You can retrieve your auth token from cookies, or you can explore other methods to obtain it.

### 2. Configure the configs.yml file

Create `configs.yml` and copy the contents of `configs.example.yml` into it, and edit it to your liking.

> [!IMPORTANT]
> All configuration instructions here are synchronized with the latest version. For users of the old version, please refer to the old README.

#### Base

| Parameter | Description | Restriction |
|-----------|-------------|-------------|
| `prefix` | The prefix for bot commands, only effective for prefix commands. | None, but recommended to choose a simple and easily identifiable prefix and avoid using empty strings. |
| `activity_name` | The activity name displayed by the bot. | None. |
| `activity_type` | The activity type displayed by the bot. | `playing`, `streaming`, `listening`, `watching` and `competing` only. |
| `users_list_pagination_size` | `list users` command's pagination size. | Only accepts integers, and it is not recommended to use too large or too small values. |
| `users_list_page_counter_position` | `list users` command's pagination counter position. | `title` and `footer` only. |

Custom activity name is in `f-string` format, currently supporting 1 special variable for use, which will be explained below.

- `{count}` : the number of users currently being monitored, it will be updated in real time

#### Timer & Counter

| Parameter | Description | Unit |
|-----------|-------------|------|
| `tweets_check_period` | The check frequency for the posts, it is not recommended to set this value too low to avoid rate limiting. Safety value: `18` [(why is this value?)](https://github.com/mahrtayyab/tweety/wiki/FAQs#twitter-new-limits), tests have shown that setting it to `10` usually doesn't cause rate limiting, not recommended below `10`. If the account controlled by Tweetcord is the same as the account you usually use, please increase the value appropriately to avoid rate limiting. | seconds |
| `tweets_updater_retry_delay` | Retry Interval when Tweets Updater encounters exceptions. | minutes |
| `tasks_monitor_check_period` | Interval at which to check if each tasks is functioning properly, and if a task has stopped, attempt a restart. | minutes |
| `tasks_monitor_log_period` | Interval at which to output the list of currently running tasks to the execution log. | hours |
| `auth_max_attempts` | The maximum number of attempts to log in to the Twitter account, if the number of failures exceeds this number, the bot will be forced to stop running. | times |

#### Control Account Behavior

| Parameter | Description |
|-----------|-------------|
| `auto_change_client` | If a new client is specified for an exisiting user, automatically use the new client to monitor the user. |
| `auto_turn_off_notification` | If all notifications for a user are disabled, decide whether to unfollow the user. |
| `auto_unfollow` | If all notifications for a user is disabled, decide whether to disable notification for the user (twitter side). |

#### Database

| Parameter | Description |
|-----------|-------------|
| `auto_repair_mismatched_clients` | Whether the system should automatically use the first client defined in the current environment variables to replace invalid `client_used` values in the database when they are not defined in the environment variables. |

#### Embed Style

| Parameter | Description |
|-----------|-------------|
| `type` | Determine the type of embed, supported types: `built_in` / `proxy`. |

##### built_in:

| Parameter | Description |
|-----------|-------------|
| `fx_image` | Whether to use FxTwitter's combined image when there are multiple images, friendly for iOS systems that cannot display multiple image embeddings. |
| `video_link_button` | Determine whether to use a link button as a prompt when the media is a video. |
| `legacy_logo` | If set to `true`, the footer will use Twitter's legacy bluebird logo instead of the new X emblem. |

##### proxy:

| Parameter | Description |
|-----------|-------------|
| `service` | The embedding proxy service to use when sending tweet links, can be [`fx`](https://github.com/FxEmbed/FxEmbed) or [`vx`](https://github.com/dylanpdx/BetterTwitFix). |
| `domain_name` | The domain name to be used when sending tweet links. When using the `fx` service, options are `fxtwitter` or `fixupx`. When using the `vx` service, options are `vxtwitter` or `fixvx`. |
| `original_url_button` | Add a link button at the bottom of the message that directs to the original tweet. This can resolve the issue where clicking a proxy service URL does not open the app on certain devices. |
| `auto_translation` | Auto-translation settings when sending tweet links. This is only available when using the `fx` service (it will be automatically disabled for other proxy services). `enabled` indicates whether to enable auto-translation, and `default_language` specifies the default translation language. For details, please refer to [Translate Posts (X/Twitter)](https://github.com/FxEmbed/FxEmbed?tab=readme-ov-file#translate-posts-xtwitter). |

> [!NOTE]
> If you need support for more embedding proxy services, please let us know via an [Issue](https://github.com/Yuuzi261/Tweetcord/issues/new).

#### Message

| Parameter | Description |
|-----------|-------------|
| `default_message` | Set default message format globally, the format is the same as the customized message, use f-string and support 4 special variables. For details, please refer to [Commands](#commands). |
| `emoji_auto_format` | For custom messages, whether to automatically convert short-format emoji codes. If enabled, it allows using codes like `:jerry:` to insert current server's emojis without needing to enter the full name `<:jerry:720576643583836181>`. |

### 3. Run and invite the bot to your server

```shell
python bot.py
```

#### Permissions Setup

🔧Bot Permissions Setup (Permissions Integer): `2147666944`

| Enable | Permissions |
|--------|-------------|
| ✔️ | Read Messages/View Channels |
| ✔️ | Send Messages |
| ✔️ | Embed Links |
| ✔️ | Attach Files |
| ✔️ | Mention Everyone |
| ✔️ | Use Slash Commands |

> [!NOTE]  
> Please generate an invitation link with the default permissions on the [Discord Developer Portal](https://discord.com/developers/applications) rather than inviting the bot first and then manually adjusting its permissions.

#### Privileged Gateway Intents Setup

| Enable | Intents |
|--------|-------------|
| ❌  | Presence Intent |
| ❌ | Server Members Intent |
| ✔️ | Message Content Intent |

> [!NOTE]
> If you want to host the bot on a server, here is a recommended service that is basically free: [fly.io](https://fly.io) _(update: fly.io has stopped offering free plans to new users)_

> [!TIP]
> Alternatively, you can try this virtual hosting service provided by Taiwanese students: [FreeServer](https://freeserver.tw/index.html)

<details>
   <summary><b>⚙️some configuration files you may need if you use fly.io</b></summary>

- dockerfile

```dockerfile
FROM python:3.11.11
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

This project also benefits from the creative contributions of artists who provide our logo.

<a href="./AVATAR.md"><img alt="LOGO" src="/images/md/MarcoDK.png" width="64" height="64" /></a>
