<div align="center">

<img alt="LOGO" src="https://i.imgur.com/WKXJDZL.png" width="300" height="300" />
  
# Tweetcord

Discord的Twitter通知機器人

[**English**](./README.md) | [**繁體中文**](./README_zh.md)

</div>

## 📝簡介

Tweetcord是一個Discord機器人，它使用[tweety-ns](https://github.com/mahrtayyab/tweety)將指定Twitter用戶的即時推文更新傳送到你的Discord伺服器。只需設置想要關注的Twitter用戶和Discord頻道，Tweetcord就會自動將推文轉發到指定頻道，確保你不會錯過重要的更新。🐦

## ✨功能

<details>
   <summary>

### 截圖

   </summary>
👇每當關注的用戶發布新推文時，你的伺服器也會收到通知。

![](https://i.imgur.com/SXITM0a.png)

</details>

<details>
   <summary>

### 指令

   </summary>

👉 `/add notifier` `username` `channel` | `mention` `type`

| 參數 | 類型 | 描述 |
| --------- | ----- | ----------- |
| `username` | str | 你想要開啟通知的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 機器人發送通知的頻道 |
| `mention` | discord.Role | 通知時提及的身分組 |
| `type` | str | 設定是否啟用轉推和引用的通知 _(0.4.1版本的新功能)_ |

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

自定義通知訊息為 `f-string` 格式，目前支援4種特別的變數可供使用，將在下面說明：

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

## ⚡使用

**📢本教學適用於0.3.2或更高版本。（建議：0.3.5或更高版本）**

### [⬆️查看歷史版本升級指南](./UPGRADE_GUIDE.md)

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
use_fx: false                       # (v0.4.1或更新版本) 是否使用FixTweet來嵌入內容而不是使用內建的嵌入
default_message: |                  # (v0.4.1或更新版本) 全域設定預設的訊息格式
  {mention}**{author}** just {action} here: 
  {url}
```

### 3. 運行機器人並邀請至你的伺服器

```shell
python bot.py
```

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
