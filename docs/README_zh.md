<div align="center">

<a href="./AVATAR.md"><img alt="LOGO" src="/images/md/avatar.png" width="300" height="300" /><a>
  
# Tweetcord

Discord的Twitter通知機器人

[![](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
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

👉 `/remove notifier` `channel` `username`

| 參數 | 類型 | 描述 |
|------|------|-----|
| `channel` | str | 設置為發送通知的頻道 |
| `username` | str | 你想要關閉通知的Twitter用戶的用戶名 |

👉 `/list users` | `account` `channel`

- 列出所有當前伺服器開啟通知的Twitter用戶

| 參數 | 類型 | 描述 |
|------|------|-----|
| `account` | str | 你想要篩選的客戶端名稱（用來追蹤的帳號） |
| `channel` | str | 你想要篩選的頻道名稱 |

👉 `/sync`

- 將新Twitter帳戶的通知與資料庫同步。如果你更改了bot使用的Twitter帳戶，請使用此指令

👉 `/customize message` `channel` `username` | `default`

| 參數 | 類型 | 描述 |
|------|------|-----|
| `channel` | str | 機器人發送通知的頻道 |
| `username` | str | 你想要設定自定義通知訊息的Twitter用戶的用戶名 |
| `default` | bool | 是否要還原至預設的設定 _(預設是false)_ |

自定義通知訊息為 `f-string` 格式，目前支援4種特別的變數可供使用，將在下面說明：

- `{action}` : 發文者的動作，包括 `tweeted`、`retweeted` 和 `quoted` _（暫不支持中文）_
- `{author}` : 發文者的顯示名稱
- `{mention}` : 發送到discord時提及的身份組
- `{url}` : 推文的連結

以預設通知為例，如果將訊息自定義為以下格式（支援Discord的markdown格式）：

```plaintext
{mention}**{author}** just {action} here: 
{url}
```

則會在推文發送時會以此格式發出通知（這裡舉一個實際例子）：

```plaintext
@Ping_SubTweet ﾅﾁｮﾈｺ just tweeted here: 
https://twitter.com/nyachodayo/status/1869000108697960952
```

</details>

## 📥安裝

在運行機器人之前，你需要安裝必要的模組。

```shell
pip install -r requirements.txt
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

> [!NOTE]
> 這裡的 `NameForYourTwitterToken` 是可以隨意定義的，僅用來作為輸入指令時指定帳戶用的代號，不一定要和Twitter帳號名稱一致。

#### 範例
```env
BOT_TOKEN=FAKE1234567890ABCDEFGHIJKLMNO.PQRSTUVWXYZ1234567890.ABCDEFGHIJKLMNOPQRSTUVWXYZ123456
TWITTER_TOKEN=Account1:12345abcde67890fghij12345klmnop67890qrstuv,Account2:abcdef123456ghijkl7890mnopqrst123456uvwx
DATA_PATH=./data
```

你可以從cookies中獲取你的token，或是你可以探索其他獲取它的方法。

### 2. 配置configs.yml文件

建立 `configs.yml` 並將 `configs.example.yml` 的內容複製過去，並依照自己的喜好編輯它。

> [!IMPORTANT]
> 這裡的所有配置說明和最新版本同步，舊版用戶請參考舊版README。

#### 基本

| 參數 | 描述 | 限制 |
|------|------|-----|
| `prefix` | 機器人命令的前綴，只會對前綴指令生效。 | 無，但建議選擇簡單且易於識別的前綴，並避免使用空字串。 |
| `activity_name` | 機器人顯示的活動名稱。 | 無。 |
| `activity_type` | 機器人顯示的活動類型。 | 僅限 `playing`、`streaming`、`listening`、`watching` 和 `competing`。 |
| `users_list_pagination_size` | `list users` 指令的分頁大小。 | 只接受整數，不宜使用過大或過小的值。 |
| `users_list_page_counter_position` | `list users` 指令的分頁計數器位置。 | 僅限 `title` 和 `footer` 。 |

自定義活動名稱為 `f-string` 格式，目前支援1種特別的變數可供使用，將在下面說明：

- `{count}` : 目前被機器人追蹤的使用者數量，會即時更新

#### 計時器 & 計數器

| 參數 | 描述 | 單位 |
|------|------|-----|
| `tweets_check_period` | 檢查推文的頻率，不建議將此值設置得太低，以避免速率限制。安全值：`18`[（為什麼是這個數值？）](https://github.com/mahrtayyab/tweety/wiki/FAQs#twitter-new-limits)，經過測試設置在 `10` 通常不會遇到速率限制，不推薦低於 `10`。如果Tweetcord控制的帳號和你平常在使用的帳號相同，請適當提高這個數值以避免速率限制。 | 秒 |
| `tweets_updater_retry_delay` | 當Tweets Updater遇到異常時的重試間隔。 | 分鐘 |
| `tasks_monitor_check_period` | 檢查每個任務是否正常運行的間隔，如果某個任務停止了，嘗試重新啟動。 | 分鐘 |
| `tasks_monitor_log_period` | 將當前運行中的任務列表輸出到執行日誌的間隔。 | 小時 |
| `auth_max_attempts` | 登入Twitter帳號時的最大嘗試次數，失敗超過此次數將會強制停止機器人運行。 | 次 |

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
| `type` | 決定嵌入內容的類型，支援的類型有: `built_in` / `proxy`。 |

##### built_in:

| 參數 | 描述 |
|------|------|
| `fx_image` | 當有多張圖片時是否使用FxTwitter的組合圖片，對於無法顯示多張圖片嵌入的iOS系統友善。 |
| `video_link_button` | 當多媒體為影片時，決定是否使用一個連結按鈕做為提示。 |
| `legacy_logo` | 設為`true`的話會使用推特以前的藍鳥logo做為footer而不是新的X標誌。 |

##### proxy:

| 參數 | 描述 |
|------|------|
| `service` | 傳送推文連結時的嵌入代理服務，可以是 [`fx`](https://github.com/FxEmbed/FxEmbed) 或 [`vx`](https://github.com/dylanpdx/BetterTwitFix)。 |
| `domain_name` | 傳送推文連結時的域名，使用 `fx` 服務時可選 `fxtwitter` 或 `fixupx`，使用 `vx` 服務時可選 `vxtwitter` 或 `fixvx`。 |
| `original_url_button` | 在訊息最下方加入連結按鈕，導向原始推文連結，可以解決某些裝置點擊嵌入服務代理網址不會開啟APP的問題。 |
| `auto_translation` | 傳送推文連結時的自動翻譯設定，僅有使用 `fx` 時可以啟用（使用其他嵌入代理服務時會自動關閉），`enabled` 表示是否啟用自動翻譯，`default_language` 表示預設翻譯的語言，詳細請參考 [Translate Posts (X/Twitter)](https://github.com/FxEmbed/FxEmbed?tab=readme-ov-file#translate-posts-xtwitter)。 |

> [!NOTE]
> 如果需要支援更多嵌入代理服務，請透過 [Issue](https://github.com/Yuuzi261/Tweetcord/issues/new) 告訴我們。

#### 訊息

| 參數 | 描述 |
|------|------|
| `default_message` | 全域設定預設的訊息格式，格式和自定義訊息相同，使用f-字串並支援4個特殊變數。相關細節請參考[指令](#指令)。 |
| `emoji_auto_format` | 對於自定義訊息，是否自動轉換短格式的表情符號，若是啟用，則支援使用如 `:jerry:` 的格式來使用當前伺服器的表情符號而不需要輸入完整名稱 `<:jerry:720576643583836181>`。 | 

### 3. 運行機器人並邀請至你的伺服器

```shell
python bot.py
```

#### 權限設定

🔧機器人權限設定（Permissions Integer）：`2147666944`

| 啟用 | 權限 |
|--------|-------------|
| ✔️ | 讀取訊息 (Read Messages/View Channels) |
| ✔️ | 發送訊息 (Send Messages) |
| ✔️ | 嵌入連結 (Embed Links) |
| ✔️ | 附加檔案 (Attach Files) |
| ✔️ | 提及 @everyone、@here 和所有身分組 (Mention Everyone) |
| ✔️ | 使用應用程式命令 (Use Slash Commands) |

> [!NOTE]
> 請在 [Discord Developer Portal](https://discord.com/developers/applications) 生成帶有預設權限的邀請連結，而不是邀請機器人進伺服器後才手動調整權限。

#### 特權意圖設定

| 啟用 | 意圖 |
|--------|-------------|
| ❌  | 成員狀態意圖 (Presence Intent) |
| ❌ | 伺服器成員意圖 (Server Members Intent) |
| ✔️ | 訊息內容意圖 (Message Content Intent) |

> [!NOTE]
> 如果想將機器人架到伺服器上，這裡推薦一個基本免費的服務：[fly.io](https://fly.io)。 _(更新：fly.io已停止向新用戶提供免費的方案)_

> [!TIP]
> 或是你可以試試這個由台灣學生提供的虛擬主機服務： [FreeServer](https://freeserver.tw/index.html)

<details>
   <summary><b>⚙️如果你使用fly.io的話你可能會需要的一些配置檔案</b></summary>

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
