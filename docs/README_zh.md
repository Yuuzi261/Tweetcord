<div align="center">

<a href="./AVATAR.md"><img alt="LOGO" src="/images/md/avatar.png" width="300" height="300" /><a>
  
# Tweetcord

Discord的Twitter通知機器人

[![](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![](https://img.shields.io/github/v/release/Yuuzi261/Tweetcord?sort=semver)](https://github.com/Yuuzi261/Tweetcord/releases)
[![](https://img.shields.io/github/release-date/Yuuzi261/Tweetcord)](https://github.com/Yuuzi261/Tweetcord/releases)

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

![](/images/md/screenshot.png)

</details>

<details>
   <summary>

### 指令

   </summary>

👉 `/add notifier` `username` `channel` | `mention` `type` `media_type` `account_used`

| 參數 | 類型 | 描述 |
|------|------|-----|
| `username` | str | 你想要開啟通知的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 機器人發送通知的頻道 |
| `mention` | discord.Role | 通知時提及的身分組 |
| `type` | str | 設定是否啟用轉推和引用的通知 |
| `media_type` | str | 設定是否啟用包含多媒體的通知，或僅啟用包含多媒體的通知 |
| `account_used` | str | 用來追蹤用戶推文的Twitter客戶端 |

👉 `/remove notifier` `username` `channel`

| 參數 | 類型 | 描述 |
|------|------|-----|
| `username` | str | 你想要關閉通知的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 設置為發送通知的頻道 |

👉 `/list users`

- 列出所有當前伺服器開啟通知的Twitter用戶

👉 `/sync`

- 將新Twitter帳戶的通知與資料庫同步。如果你更改了bot使用的Twitter帳戶，請使用此指令

👉 `/customize message` `username` `channel` | `default`

| 參數 | 類型 | 描述 |
|------|------|-----|
| `username` | str | 你想要設定自定義通知訊息的Twitter用戶的用戶名 |
| `channel` | discord.TextChannel | 機器人發送通知的頻道 |
| `default` | bool | 是否要還原至預設的設定 _(預設是false)_ |

自定義通知訊息為 `f-string` 格式，目前支援4種特別的變數可供使用，將在下面說明：

- `{action}` : 發文者的動作，包括 `tweeted`、`retweeted` 和 `quoted` _（暫不支持中文）_
- `{author}` : 發文者的顯示名稱
- `{mention}` : 發送到discord時提及的身份組
- `{url}` : 推文的連結

</details>

## 📥安裝

在運行機器人之前，你需要安裝必要的模組。

```shell
pip install -r requirements.txt
pip install https://github.com/mahrtayyab/tweety/archive/main.zip --upgrade
```

## ⚡使用

**📢本教學適用於0.5或更高版本，舊版設定請參考各個歷史版本的README。**

### [⬆️查看歷史版本升級指南](./UPGRADE_GUIDE.md)

### 1. 創建並配置.env文件

```env
BOT_TOKEN=YourDiscordBotToken
TWITTER_TOKEN=NameForYourTwitterToken:YourTwitterAccountAuthToken
DATA_PATH=./data
```

#### 範例
```env
BOT_TOKEN=FAKE1234567890ABCDEFGHIJKLMNO.PQRSTUVWXYZ1234567890.ABCDEFGHIJKLMNOPQRSTUVWXYZ123456
TWITTER_TOKEN=MyTwitterToken:12345abcde67890fghij12345klmnop67890qrstuv,MyTwitterToken2:abcdef123456ghijkl7890mnopqrst123456uvwx
DATA_PATH=./data
```

你可以從cookies中獲取你的token，或是你可以探索其他獲取它的方法。

### 2. 配置configs.yml文件

建立`configs.yml`並將`configs.example.yml`的內容複製過去，並依照自己的喜好編輯它。

> [!IMPORTANT]
> 這裡的所有配置說明和最新版本同步，舊版用戶請參考舊版README。

#### 基本

| 參數 | 描述 | 限制 |
|------|------|-----|
| `prefix` | 機器人命令的前綴，只會對前綴指令生效。 | 無，但建議選擇簡單且易於識別的前綴，並避免使用空字串。 |
| `activity_name` | 機器人顯示的活動名稱。 | 無。 |
| `activity_type` | 機器人顯示的活動類型。 | 僅限 `playing`、`streaming`、`listening`、`watching` 和 `competing`。 |

自定義活動訊息為 `f-string` 格式，目前支援1種特別的變數可供使用，將在下面說明：

- `{count}` : 目前被機器人追蹤的使用者數量

#### 計時器

| 參數 | 描述 | 單位 |
|------|------|-----|
| `tweets_check_period` | 檢查推文的頻率，不建議將此值設置得太低，以避免速率限制。預設值：`10`，安全值：`18`[（為什麼是這個數值？）](https://github.com/mahrtayyab/tweety/wiki/FAQs#twitter-new-limits)，不推薦低於 `10`。如果Tweetcord控制的帳號和你平常在使用的帳號相同，請適當提高這個數值以避免速率限制。 | 秒 |
| `tweets_updater_retry_delay` | 當Tweets Updater遇到異常時的重試間隔。 | 分鐘 |
| `tasks_monitor_check_period` | 檢查每個任務是否正常運行的間隔，如果某個任務停止了，嘗試重新啟動。 | 分鐘 |
| `tasks_monitor_log_period` | 將當前運行中的任務列表輸出到執行日誌的間隔。 | 小時 |

#### 控制帳戶行為

| 參數 | 描述 |
|------|------|
| `auto_change_client` | 如果為現有使用者指定新用戶端，則自動使用新用戶端對該使用者進行追蹤。 |
| `auto_turn_off_notification` | 如果某個使用者的所有通知都已停用，決定是否取消追蹤該使用者。 |
| `auto_unfollow` | 如果某個使用者的所有通知都已停用，決定是否停用該使用者的通知（Twitter端）。 |

#### 資料庫

| 參數 | 描述 |
|------|------|
| `auto_repair_mismatched_clients` | 當資料庫中含有環境變數未定義的`client_used`的話，是否自動使用目前環境變數所定義的第一個客戶端取代這些無效的客戶端名稱。 |

#### 嵌入內容風格

| 參數 | 描述 |
|------|------|
| `type` | 決定嵌入內容的類型，支援的類型有: `built_in` / `fx_twitter`。 |

##### built_in:

| 參數 | 描述 |
|------|------|
| `fx_image` | 當有多張圖片時是否使用FxTwitter的組合圖片，對於無法顯示多張圖片嵌入的iOS系統友善。 |
| `video_link_button` | _即將推出_ |
| `footer_logo` | _即將推出_ |

##### fx_twitter:

| 參數 | 描述 |
|------|------|
| `original_url_button` | _即將推出_ |

#### 訊息

| 參數 | 描述 |
|------|------|
| `default_message` | 全域設定預設的訊息格式，格式和自定義訊息相同，使用f-字串並支援4個特殊變數。相關細節請參考[指令](#指令)。 |

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
> 如果想將機器人架到伺服器上，這裡推薦一個基本免費的服務：[fly.io](https://fly.io)。 _(更新：fly.io已停止向新用戶提供免費的方案)_

> [!TIP]
> 或是你可以試試這個由台灣學生提供的虛擬主機服務： [FreeServer](https://freeserver.tw/index.html)

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
  DATA_PATH = "/data"

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

這個專案也受益於為我們提供標誌的藝術家的創意貢獻。

<a href="./AVATAR.md"><img alt="LOGO" src="/images/md/MarcoDK.png" width="64" height="64" /></a>
