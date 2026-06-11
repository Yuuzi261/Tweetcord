import os

import aiosqlite

from src.log import setup_logger
from src.utils import get_utcnow

log = setup_logger(__name__)


async def init_db():
    data_path = os.getenv('DATA_PATH')
    if not os.path.exists(data_path):
        os.mkdir(data_path)

    db_path = os.path.join(data_path, 'tracked_accounts.db')
    db_exists = os.path.exists(db_path)
    
    if db_exists: return

    async with aiosqlite.connect(db_path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, username TEXT, latest_tweet TEXT, client_used TEXT, enabled INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS channel (id TEXT PRIMARY KEY, server_id TEXT);
            CREATE TABLE IF NOT EXISTS notification (user_id TEXT, channel_id TEXT, role_id TEXT, enabled INTEGER DEFAULT 1, enable_type TEXT DEFAULT 11, enable_media_type TEXT DEFAULT 11, customized_msg TEXT DEFAULT NULL, FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (channel_id) REFERENCES channel (id), PRIMARY KEY(user_id, channel_id));
            CREATE TABLE IF NOT EXISTS server_user_config (server_id TEXT, user_id TEXT, translate TEXT, PRIMARY KEY(server_id, user_id), FOREIGN KEY (user_id) REFERENCES user (id));
        """)
        await db.commit()

    log.info('database file not found, a blank database file has been created')


async def init_latest_tweet_on_startup(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('UPDATE user SET latest_tweet = ?', (get_utcnow(),))
        await db.commit()

    log.info('all latest_tweet timestamps have been updated to current time')
