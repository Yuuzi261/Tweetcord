## English

> [!WARNING]
> Cross-version updates are **NOT SUPPORTED**. For multi-version updates, please iterate through each version to update to the latest version. Before updating, please back up your data using the prefix command `download_data`.

<details>
   <summary><b>⬆️click here to upgrade from 0.4.1 to 0.5</b></summary>

<!-- Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade version` to upgrade. This cog can be removed after the upgrade is completed. -->

\# TODO

```py
import asyncio
import os

import aiosqlite
import dotenv
from src.utils import get_accounts

dotenv.load_dotenv()


async def upgrade():
    # Set the default value of enable_media_type to 11 (both)
    # Set the default value of client_used to the first account in the list of accounts
    first_account = list(get_accounts().keys())[0]
    try:
        async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
            await db.executescript(f"""
                PRAGMA foreign_keys=off;
                
                BEGIN TRANSACTION;
                
                ALTER TABLE notification ADD enable_media_type TEXT DEFAULT 11;
                ALTER TABLE user ADD client_used TEXT DEFAULT '{first_account}';
            
                CREATE TABLE new_user (
                    id TEXT PRIMARY KEY,
                    username TEXT,
                    lastest_tweet TEXT,
                    client_used TEXT,
                    enabled INTEGER DEFAULT 1
                );
                INSERT INTO new_user (id, username, lastest_tweet, client_used, enabled)
                SELECT id, username, lastest_tweet, client_used, enabled
                FROM user;
                DROP TABLE user;
                ALTER TABLE new_user RENAME TO user;
                
                CREATE TABLE new_notification (
                    user_id TEXT,
                    channel_id TEXT,
                    role_id TEXT,
                    enabled INTEGER DEFAULT 1,
                    enable_type TEXT DEFAULT 11,
                    enable_media_type TEXT DEFAULT 11,
                    customized_msg TEXT DEFAULT NULL,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (channel_id) REFERENCES channel (id),
                    PRIMARY KEY(user_id, channel_id)
                );
                INSERT INTO new_notification (user_id, channel_id, role_id, enabled, enable_type, enable_media_type, customized_msg)
                SELECT user_id, channel_id, role_id, enabled, enable_type, enable_media_type, customized_msg
                FROM notification;
                DROP TABLE notification;
                ALTER TABLE new_notification RENAME TO notification;
                
                COMMIT;
                
                PRAGMA foreign_keys=on;
            """)
            await db.commit()
            print('Successfully upgraded to 0.5. You can remove this script and start the bot.')
    except Exception as e:
        print(e)
        print('upgrading to 0.5 failed, please try again or contact the author.')


if __name__ == '__main__':
    asyncio.run(upgrade())
```

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.4 to 0.4.1</b></summary>

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade version` to upgrade. This cog can be removed after the upgrade is completed.

```py
import discord
from discord import app_commands
from core.classes import Cog_Extension
import sqlite3
import os

from src.permission import ADMINISTRATOR

class Upgrade(Cog_Extension):
    
    upgrade_group = app_commands.Group(name='upgrade', description='Upgrade something', default_permissions=ADMINISTRATOR)

    @upgrade_group.command(name='version', description='upgrade to Tweetcord 0.4.1')
    async def upgrade(self, itn: discord.Interaction):
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()

        try:
            cursor.executescript("""
                PRAGMA foreign_keys=off;

                BEGIN TRANSACTION;

                ALTER TABLE notification RENAME TO old_notification;

                CREATE TABLE IF NOT EXISTS notification (
                    user_id TEXT, 
                    channel_id TEXT, 
                    role_id TEXT, 
                    enabled INTEGER DEFAULT 1, 
                    enable_type TEXT DEFAULT '11', 
                    customized_msg TEXT DEFAULT NULL, 
                    FOREIGN KEY (user_id) REFERENCES user (id), 
                    FOREIGN KEY (channel_id) REFERENCES channel (id), 
                    PRIMARY KEY(user_id, channel_id)
                );

                INSERT INTO notification (user_id, channel_id, role_id, enabled, customized_msg)
                SELECT user_id, channel_id, role_id, enabled, customized_msg
                FROM old_notification;

                DROP TABLE old_notification;

                COMMIT;

                PRAGMA foreign_keys=on;
            """)
            await itn.followup.send('Successfully upgraded to 0.4.1. You can remove this cog and reboot the bot.')
        except Exception as e:
            await itn.followup.send(f'Upgrading to 0.4.1 failed. Please try again or contact the author. Error: {str(e)}')
        finally:
            conn.close()


async def setup(bot):
    await bot.add_cog(Upgrade(bot))

```

</details>

<details>
   <summary><b>⬆️click here to upgrade from 0.3.5 to 0.4</b></summary>

⚠️Before everything starts you must upgrade the version of `tweety-ns` to `1.0.9.2` first and download or pull the new code from this repo.

Create a python file in the `cogs` folder and name it `upgrade.py`. Paste the following code and run the bot. Use the slash command `/upgrade version` to upgrade. This cog can be removed after the upgrade is completed.

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
   <summary><b>⬆️click here to upgrade from 0.3.4 to 0.3.5</b></summary>

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
   <summary><b>⬆️click here to upgrade from 0.3.3 to 0.3.4</b></summary>

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

## 繁體中文

> [!WARNING]
> **不支援**跨版本更新，多版本更新請迭代更新至新版本。更新前請先透過前綴指令 `download_data` 進行資料備份。

<details>
   <summary><b>⬆️0.4升級到0.4.1請點這裡</b></summary>

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

    @upgrade_group.command(name='version', description='upgrade to Tweetcord 0.4.1')
    async def upgrade(self, itn: discord.Interaction):
        
        await itn.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(f"{os.getenv('DATA_PATH')}tracked_accounts.db")
        cursor = conn.cursor()

        try:
            cursor.executescript("""
                PRAGMA foreign_keys=off;

                BEGIN TRANSACTION;

                ALTER TABLE notification RENAME TO old_notification;

                CREATE TABLE IF NOT EXISTS notification (
                    user_id TEXT, 
                    channel_id TEXT, 
                    role_id TEXT, 
                    enabled INTEGER DEFAULT 1, 
                    enable_type TEXT DEFAULT '11', 
                    customized_msg TEXT DEFAULT NULL, 
                    FOREIGN KEY (user_id) REFERENCES user (id), 
                    FOREIGN KEY (channel_id) REFERENCES channel (id), 
                    PRIMARY KEY(user_id, channel_id)
                );

                INSERT INTO notification (user_id, channel_id, role_id, enabled, customized_msg)
                SELECT user_id, channel_id, role_id, enabled, customized_msg
                FROM old_notification;

                DROP TABLE old_notification;

                COMMIT;

                PRAGMA foreign_keys=on;
            """)
            await itn.followup.send('Successfully upgraded to 0.4.1. You can remove this cog and reboot the bot.')
        except Exception as e:
            await itn.followup.send(f'Upgrading to 0.4.1 failed. Please try again or contact the author. Error: {str(e)}')
        finally:
            conn.close()


async def setup(bot):
    await bot.add_cog(Upgrade(bot))

```

</details>

<details>
   <summary><b>⬆️0.3.5升級到0.4請點這裡</b></summary>

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
   <summary><b>⬆️0.3.4升級到0.3.5請點這裡</b></summary>

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
   <summary><b>⬆️0.3.3升級到0.3.4請點這裡</b></summary>

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