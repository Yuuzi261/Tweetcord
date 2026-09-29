import os
import sqlite3
import asyncio
import unittest
import sys
from unittest.mock import patch, MagicMock, AsyncMock

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sync_db.sync_db import sync_db

# Schema mirrored from src/db_function/init_db.py
USER_SCHEMA = 'CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT, latest_tweet TEXT, client_used TEXT, enabled INTEGER DEFAULT 1)'

# Query used by /sync to build its follow list (cogs/sync.py). Kept in sync with that command.
SYNC_FOLLOW_QUERY = 'SELECT id, client_used FROM user WHERE enabled = 1'


class TestSyncFollowQuery(unittest.TestCase):
    """/sync must skip soft-deleted (enabled = 0) accounts, or it re-follows removed users."""

    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute(USER_SCHEMA)
        self.db.executemany(
            'INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, ?)',
            [
                ('1', 'kept',    'clientA', 1),
                ('2', 'removed', 'clientA', 0),  # soft-deleted via /remove notifier
                ('3', 'kept2',   'clientB', 1),
            ],
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_excludes_disabled_users(self):
        rows = self.db.execute(SYNC_FOLLOW_QUERY).fetchall()
        ids = {r[0] for r in rows}
        self.assertEqual(ids, {'1', '3'})
        self.assertNotIn('2', ids)  # the removed account must not be re-followed


class TestSyncDbUnconfiguredClient(unittest.IsolatedAsyncioTestCase):
    """sync_db must skip users whose client token is no longer configured, not crash the whole sync."""

    async def test_skips_unconfigured_client_and_continues(self):
        follow_list = {'userX': 'known', 'userY': 'gone'}  # 'gone' is not in TWITTER_TOKEN anymore

        app_mock = MagicMock()
        app_mock.connect = AsyncMock()
        app_mock.follow_user = AsyncMock()
        app_mock.enable_user_notification = AsyncMock()

        with patch('src.sync_db.sync_db.get_accounts', return_value={'known': 'token'}), \
             patch('src.sync_db.sync_db.Twitter', return_value=app_mock), \
             patch('src.sync_db.sync_db.asyncio.sleep', new=AsyncMock()):
            # Must not raise KeyError on 'gone'
            await sync_db(follow_list)

        # Known client is synced; unconfigured one is skipped, not fatal.
        app_mock.follow_user.assert_awaited_once_with('userX')
        app_mock.enable_user_notification.assert_awaited_once_with('userX')


if __name__ == '__main__':
    unittest.main()
