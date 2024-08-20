import os
import sqlite3

from src.log import setup_logger

log = setup_logger(__name__)

def init_db():
    if not os.path.exists(os.getenv('DATA_PATH')): os.mkdir(os.getenv('DATA_PATH'))
    conn = sqlite3.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db'))
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, username TEXT, lastest_tweet TEXT, enabled INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS channel (id TEXT PRIMARY KEY, server_id TEXT);
        CREATE TABLE IF NOT EXISTS notification (user_id TEXT, channel_id TEXT, role_id TEXT, enabled INTEGER DEFAULT 1, enable_type TEXT DEFAULT 11, customized_msg TEXT DEFAULT NULL, FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (channel_id) REFERENCES channel (id), PRIMARY KEY(user_id, channel_id));
    """)
    conn.commit()
    conn.close()
    log.info('database file not found, a blank database file has been created')