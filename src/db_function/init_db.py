import os

import aiosqlite

from src.log import setup_logger

log = setup_logger(__name__)


async def init_db():
    if not os.path.exists(os.getenv('DATA_PATH')):
        os.mkdir(os.getenv('DATA_PATH'))

    async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, username TEXT, lastest_tweet TEXT, client_used TEXT, enabled INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS channel (id TEXT PRIMARY KEY, server_id TEXT);
            CREATE TABLE IF NOT EXISTS notification (user_id TEXT, channel_id TEXT, role_id TEXT, enabled INTEGER DEFAULT 1, enable_type TEXT DEFAULT 11, enable_media_type TEXT DEFAULT 11, customized_msg TEXT DEFAULT NULL, FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (channel_id) REFERENCES channel (id), PRIMARY KEY(user_id, channel_id));
        """)
        await db.commit()

    log.info('database file not found, a blank database file has been created')
