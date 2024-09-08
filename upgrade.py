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
    async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        await db.executescript(f"""
            PRAGMA foreign_keys=off;

            BEGIN TRANSACTION;

            ALTER TABLE notification ADD enable_media_type TEXT DEFAULT 11;
            ALTER TABLE user ADD client_used TEXT DEFAULT '{first_account}';

            COMMIT;

            PRAGMA foreign_keys=on;
        """)
        await db.commit()
    print('upgrade done')


if __name__ == '__main__':
    asyncio.run(upgrade())
