<div align="center">

<img alt="LOGO" src="https://i.imgur.com/WKXJDZL.png" width="300" height="300" />
  
# Tweetcord

Discord的Twitter通知機器人

[**English**](./README.md) | [**繁體中文**](./README_zh.md)

</div>

## 📝簡介

Tweetcord是一個discord機器人，它使用tweety-ns模組讓你在discord上接收特定Twitter用戶的推文更新。你只需要設置想要關注的Twitter用戶和discord頻道，Tweetcord就會自動將推文發送到指定的頻道，這樣你就不會錯過任何重要的消息。🐦

## ✨功能

<details>
   <summary>

### 截圖

   </summary>
👇當你關注的用戶發布了新的推文，你的伺服器也會收到通知。

![](https://i.imgur.com/SXITM0a.png)

</details>

<details>
   <summary>

### 指令

   </summary>

👉 `/add notifier` `username` `channel` | `mention`

| 參數 | 類型 | 描述 |
| --------- | ----- | ----------- |
| `username` | str | 你想要開啟通知的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 機器人發送通知的頻道 |
| `mention` | discord.Role | 通知時提及的身分組 |

👉 `/remove notifier` `username` `channel`

| 參數 | 類型 | 描述 |
| --------- | ----- | ----------- |
| `username` | str | 你想要關閉通知的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 設置為發送通知的頻道 |

👉 `/list users`

- 列出所有當前伺服器開啟通知的Twitter用戶

👉 `/sync` _(0.4版本的新功能)_

- 將新Twitter帳戶的通知與資料庫同步。如果你更改了bot使用的Twitter帳戶，請使用此指令

👉 `/customize message` `username` `channel` | `default` _(0.4版本的新功能)_

| 參數 | 類型 | 描述 |
| --------- | ----- | ----------- |
| `username` | str | 你想要設定自定義通知訊息的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 機器人發送通知的頻道 |
| `default` | bool | 是否要還原至預設的設定 _(預設是false)_ |

目前自定義通知訊息有4種特別的變數可以使用，將在下面說明：

- `{action}` : 發文者的動作, 包括 `tweeted`, `retweeted` 和 `quoted` _(暫不支持中文)_
- `{author}` : 發文者的顯示名稱
- `{mention}` : 發送到discord時提及的身份組
- `{url}` : 推文的連結

</details>

## 📥安裝

在運行機器人之前，你需要安裝必要的模組。

```shell
pip install -r requirements.txt
```

在某些作業系統中，你可能需要使用 `pip3` 而不是 `pip` 來進行安裝。

## ⚡使用

**📢本教學適用於0.3.2或更高版本。（建議：0.3.5或更高版本）**

<details>
   <summary><b>📌0.3.5升級到0.4請點這裡</b></summary>

⚠️在一切開始之前請先更新 `tweety-ns` 至 `1.0.9.2` 版本並且從這個repo下載或拉取新的程式碼。

在 `cogs` 資料夾創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並運行機器人，使用斜線指令 `/upgrade version` 進行升級。升級結束後可以移除這個cog。

```py
import discord
from discord import app_commands
from core.classes import Cog_Extension
import sqlite3
import os

from src.permission import ADMINISTRATOR

class Upgrade(Cog_Extension):
    
    upgrade_group = app_commands.Group(name='upgrade', description='Upgrade something', default_permissions=ADMINISTRATOR)

    @upgrade_group.command(name='version', description='upgrade to Tweetcord 0.4')
    async def upgrade(self, itn: discord.Interaction):
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()

        try:
            cursor.executescript("""
                ALTER TABLE user ADD enabled INTEGER DEFAULT 1;
                ALTER TABLE notification ADD customized_msg TEXT DEFAULT NULL;
            """)
            await itn.followup.send('successfully upgrade to 0.4, you can remove this cog and reboot the bot.')
        except:
            await itn.followup.send('upgrading to 0.4 failed, please try again or contact the author.')


async def setup(bot):
    await bot.add_cog(Upgrade(bot))
```

</details>

<details>
   <summary><b>📌0.3.4升級到0.3.5請點這裡</b></summary>

在 `cogs` 資料夾創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並運行機器人，使用斜線指令 `/upgrade` 進行升級。升級結束後可以移除這個cog。

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
   <summary><b>📌0.3.3升級到0.3.4請點這裡</b></summary>

因為資料庫結構更新因此必須使用以下程式碼更新資料庫結構。

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

### 1. 創建並配置.env文件

```env
BOT_TOKEN=YourDiscordBotToken
TWITTER_TOKEN=YourTwitterAccountAuthToken
DATA_PATH=./data/
```

你可以從cookies中獲取你的token，或是你可以探索其他獲取它的方法。

### 2. 配置configs.yml文件

所有與時間相關的配置都以秒為單位。

```yml
prefix: ''                          # 機器人命令的前綴。
activity_name: ''                   # 機器人顯示的活動名稱。
tweets_check_period: 10             # 檢查推文的頻率（不建議將此值設置得太低，以避免速率限制）。
tweets_updater_retry_delay: 300     # 當Tweets Updater遇到異常（例如速率限制）時的重試間隔。
tasks_monitor_check_period: 60      # 檢查每個任務是否正常運行的間隔，如果某個任務停止了，嘗試重新啟動。
tasks_monitor_log_period: 14400     # 將當前運行中的任務列表輸出到執行日誌的間隔。
auto_turn_off_notification: true    # (v0.4或更新版本) 如果某個使用者的所有通知都已停用，決定是否取消追蹤該使用者。
auto_unfollow: true                 # (v0.4或更新版本) 如果某個使用者的所有通知都已停用，決定是否停用該使用者的通知（Twitter端）。
```

### 3. 運行機器人並邀請至你的伺服器

```shell
python bot.py
```

在某些操作系統中，你可能需要使用 `python3` 而不是 `python`。

🔧機器人權限設定 `2147666944`

- [x] 讀取訊息（Read Messages/View Channels）
- [x] 發送訊息（Send Messages）
- [x] 嵌入連結（Embed Links）
- [x] 附加檔案（Attach Files）
- [x] 提及 @everyone、@here 和所有身分組（Mention Everyone）
- [x] 使用應用程式命令（Use Slash Commands）

> [!NOTE]
> 如果想將機器人架到伺服器上，這裡推薦一個基本免費的服務：[fly.io](https://fly.io).

<details>
   <summary><b>⚙️如果你使用fly.io的話你可能會需要的一些配置檔案</b></summary>

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
app = "你的APP名稱"
primary_region = "你的APP地區"

[env]
  DATA_PATH = "/data/"

[mounts]
  source = "你的APP的VOLUME名稱"
  destination = "/data"
```

</details>

### 4. 玩得開心

現在你可以回到Discord，並使用 `/add notifier` 指令來設置你想要接收更新的Twitter用戶！

## 💪貢獻者

感謝所有貢獻者。

[![](https://contrib.rocks/image?repo=Yuuzi261/Tweetcord)](https://github.com/Yuuzi261/Tweetcord/graphs/contributors)
