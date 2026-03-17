## English

> [!WARNING]
> Cross-version updates are **NOT SUPPORTED**. For multi-version updates, please iterate through each version to update to the latest version. Before updating, please back up your data using the prefix command `download_data`.

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.6 to 0.6.1</b></summary>

This update involves upgrading the versions of dependency packages, please make sure to update:

```bash
pip install --upgrade -r requirements.txt
```

Since the parameters in configs have been adjusted, please refer to `configs.example.yml` to update the configs (added `init_lastest_tweet_on_startup` setting).

Since this update involves a database update, please create a Python file named `upgrade.py` in the project's root directory, paste the following code, and run the script: `python upgrade.py`, or simply start the bot, which will check for the update script and automatically update. Please remove this script after the upgrade is complete to avoid repeated updates.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=28a0ff2839df9dd07fbe486680177664)](https://gist.github.com/Yuuzi261/28a0ff2839df9dd07fbe486680177664)

</details>

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.5.5 to 0.6</b></summary>

This update does not involve any changes to the database structure, so there is no need to use an upgrade script. Simply pull the updated code to complete the update.

Since the parameters in configs have been adjusted, please refer to `configs.example.yml` to update the configs accordingly.

</details>

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.5.4 to 0.5.5</b></summary>

Version 0.5.5 is a hotfix for version 0.5.4, mainly addressing issue [#55](https://github.com/Yuuzi261/Tweetcord/issues/55).

This update does not involve any changes to the database structure, so there is no need to use an upgrade script. Simply pull the updated code to complete the update.

</details>

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.5.3 to 0.5.4</b></summary>

This update does not involve any changes to the database structure, so there is no need to use an upgrade script. Simply pull the updated code to complete the update.

Since the parameters in configs have been adjusted, please refer to `configs.example.yml` to update the configs accordingly.

📢Due to this update removing unnecessary Discord intents, it is recommended to go to [Discord Developer Portal](https://discord.com/developers/applications) and disable unnecessary privileged gateway intents.

</details>

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.5.2 to 0.5.3</b></summary>

This update does not involve any changes to the database structure, so there is no need to use an upgrade script. Simply pull the updated code and upgrade the environment to complete the update.

```bash
pip install --upgrade -r requirements.txt
```

Because configs has added more parameters, please refer to `configs.example.yml` to fill in the necessary parameters.

</details>

<details>
   <summary><b>⬆️Click Here to Upgrade from 0.5.1 to 0.5.2</b></summary>

This update does not involve any changes to the database structure, so there is no need to use an upgrade script. Simply pull the updated code and upgrade the environment to complete the update.

```bash
pip install --upgrade -r requirements.txt
```

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.4.1 to 0.5.1</b></summary>

**📢Version 0.5.1 involves changes to dependency packages. Please ensure that all required packages are correctly installed in your environment.**

**📢This update includes significant changes to environment variables and configuration files. Please refer to the [README](./README.md) for details to ensure proper operation.**

Create a Python file named `upgrade.py` in the root directory of the project, paste the following code, and run the script using `python upgrade.py`. Alternatively, you can directly start the bot, which will check for the existence of the update script and automatically update. After the upgrade is complete, please remove this script to avoid repeated updates.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=aadbd934efe8a36fd23b307d14683e41)](https://gist.github.com/Yuuzi261/aadbd934efe8a36fd23b307d14683e41)

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.4 to 0.4.1</b></summary>

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade version` to upgrade. This cog can be removed after the upgrade is completed.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=8457699053db8f4410f9288f37e49970)](https://gist.github.com/Yuuzi261/8457699053db8f4410f9288f37e49970)

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.3.5 to 0.4</b></summary>

⚠️Before everything starts you must upgrade the version of `tweety-ns` to `1.0.9.2` first and download or pull the new code from this repo.

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade version` to upgrade. This cog can be removed after the upgrade is completed.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=b68b61dc1f6cf5abf267395620e77756)](https://gist.github.com/Yuuzi261/b68b61dc1f6cf5abf267395620e77756)

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.3.4 to 0.3.5</b></summary>

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade` to upgrade. This cog can be removed after the upgrade is completed.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=3b77c801fae0d2ffe3f9dde66f448535)](https://gist.github.com/Yuuzi261/3b77c801fae0d2ffe3f9dde66f448535)

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.3.3 to 0.3.4</b></summary>

Because the database structure has been updated, you must use the following code to update the database structure.

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=978cfca7589719112b504e759f5c48b6)](https://gist.github.com/Yuuzi261/978cfca7589719112b504e759f5c48b6)

</details>

## 繁體中文

> [!WARNING]
> **不支援**跨版本更新，多版本更新請迭代更新至新版本。更新前請先透過前綴指令 `download_data` 進行資料備份。

<details>
   <summary><b>⬆️0.6升級到0.6.1請點這裡</b></summary>

本次更新對依賴套件的版本進行了升級，請務必進行更新：

```bash
pip install --upgrade -r requirements.txt
```

因為configs的參數有進行調整，請參考 `configs.example.yml` 對configs進行更新（新增 `init_lastest_tweet_on_startup` 設定）。

因本次更新涉及資料庫更新，請在專案根目錄創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並執行該腳本：`python upgrade.py`，或是直接啟動機器人，會檢查是否存在更新腳本並自動更新。升級結束後請移除這個腳本避免重複更新。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=28a0ff2839df9dd07fbe486680177664)](https://gist.github.com/Yuuzi261/28a0ff2839df9dd07fbe486680177664)

</details>

<details>
   <summary><b>⬆️0.5.5升級到0.6請點這裡</b></summary>

本次更新不涉及資料庫結構更新，因此不用使用升級腳本來完成升級，請直接拉取程式碼即可完成更新。

因為configs的參數有進行調整，請參考`configs.example.yml`對configs進行更新。

</details>

<details>
   <summary><b>⬆️0.5.4升級到0.5.5請點這裡</b></summary>

0.5.5為0.5.4的修補版本，主要對 issue [#55](https://github.com/Yuuzi261/Tweetcord/issues/55) 進行了修正。

本次更新不涉及資料庫結構更新，因此不用使用升級腳本來完成升級，請直接拉取程式碼即可完成更新。

</details>

<details>
   <summary><b>⬆️0.5.3升級到0.5.4請點這裡</b></summary>

本次更新不涉及資料庫結構更新，因此不用使用升級腳本來完成升級，請直接拉取程式碼即可完成更新。

因為configs的參數有進行調整，請參考`configs.example.yml`對configs進行更新。

📢由於這次更新移除了非必要的Discord意圖，因此建議到[Discord Developer Portal](https://discord.com/developers/applications)關閉不必要的特權意圖。

</details>

<details>
   <summary><b>⬆️0.5.2升級到0.5.3請點這裡</b></summary>

本次更新不涉及資料庫結構更新，因此不用使用升級腳本來完成升級，請直接拉取程式碼並升級環境即可完成更新。

```bash
pip install --upgrade -r requirements.txt
```

因為configs新增了更多參數，更新後請參考 `configs.example.yml` 補上必要的參數。

</details>

<details>
   <summary><b>⬆️0.5.1升級到0.5.2請點這裡</b></summary>

本次更新不涉及資料庫結構更新，因此不用使用升級腳本來完成升級，請直接拉取程式碼並升級環境即可完成更新。

```bash
pip install --upgrade -r requirements.txt
```

</details>

<details>
   <summary><b>⬆️0.4.1升級到0.5.1請點這裡</b></summary>

**📢0.5.1版本涉及依賴套件更動，請確定環境正確安裝所有所需的套件**

**📢本次更新對環境變數、設定檔進行了大量改動，詳情請見[README](./README_zh.md)以確保運作正常**

在專案根目錄創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並執行該腳本：`python upgrade.py`，或是直接啟動機器人，會檢查是否存在更新腳本並自動更新。升級結束後請移除這個腳本避免重複更新。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=aadbd934efe8a36fd23b307d14683e41)](https://gist.github.com/Yuuzi261/aadbd934efe8a36fd23b307d14683e41)

</details>

<details>
   <summary><b>⬆️0.4升級到0.4.1請點這裡</b></summary>

在 `cogs` 資料夾創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並運行機器人，使用斜線指令 `/upgrade version` 進行升級。升級結束後可以移除這個cog。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=8457699053db8f4410f9288f37e49970)](https://gist.github.com/Yuuzi261/8457699053db8f4410f9288f37e49970)

</details>

<details>
   <summary><b>⬆️0.3.5升級到0.4請點這裡</b></summary>

⚠️在一切開始之前請先更新 `tweety-ns` 至 `1.0.9.2` 版本並且從這個repo下載或拉取新的程式碼。

在 `cogs` 資料夾創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並運行機器人，使用斜線指令 `/upgrade version` 進行升級。升級結束後可以移除這個cog。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=b68b61dc1f6cf5abf267395620e77756)](https://gist.github.com/Yuuzi261/b68b61dc1f6cf5abf267395620e77756)

</details>

<details>
   <summary><b>⬆️0.3.4升級到0.3.5請點這裡</b></summary>

在 `cogs` 資料夾創建一個python檔案並命名為 `upgrade.py`，貼上下面的程式碼並運行機器人，使用斜線指令 `/upgrade` 進行升級。升級結束後可以移除這個cog。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=3b77c801fae0d2ffe3f9dde66f448535)](https://gist.github.com/Yuuzi261/3b77c801fae0d2ffe3f9dde66f448535)

</details>

<details>
   <summary><b>⬆️0.3.3升級到0.3.4請點這裡</b></summary>

因為資料庫結構更新因此必須使用以下程式碼更新資料庫結構。

[![Gist Card](https://github-readme-stats-yuuzi261s-projects.vercel.app/api/gist?id=978cfca7589719112b504e759f5c48b6)](https://gist.github.com/Yuuzi261/978cfca7589719112b504e759f5c48b6)

</details>