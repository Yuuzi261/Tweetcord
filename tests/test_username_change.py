import os
import sys
import tempfile
import sqlite3
import asyncio
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure project root and test directory are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.i18n import init_i18n
init_i18n()

from src.notification.get_tweets import get_tweets
from cogs.notification import Notification


def create_test_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            username TEXT,
            latest_tweet TEXT,
            client_used TEXT,
            enabled INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS channel (
            id TEXT PRIMARY KEY,
            server_id TEXT
        );
        CREATE TABLE IF NOT EXISTS notification (
            user_id TEXT,
            channel_id TEXT,
            role_id TEXT,
            enabled INTEGER DEFAULT 1,
            enable_type TEXT DEFAULT '11',
            enable_media_type TEXT DEFAULT '11',
            customized_msg TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (channel_id) REFERENCES channel (id),
            PRIMARY KEY(user_id, channel_id)
        );
        CREATE TABLE IF NOT EXISTS server_user_config (
            server_id TEXT,
            user_id TEXT,
            translate TEXT,
            PRIMARY KEY(server_id, user_id),
            FOREIGN KEY (user_id) REFERENCES user (id)
        );
    """)
    conn.commit()
    conn.close()


def make_mock_tweet(user_id: str, username: str, created_on: str = '2026-09-30 00:00:00+00:00'):
    tweet = MagicMock()
    tweet.author = MagicMock()
    tweet.author.id = user_id
    tweet.author.username = username
    tweet.author.profile_image_url_https = 'https://example.com/avatar_normal.jpg'
    tweet.created_on = created_on
    return tweet



class TestGetTweetsUsernameChange(unittest.IsolatedAsyncioTestCase):
    """Verifies tweet filtering using immutable user_id."""

    async def test_get_tweets_matches_by_user_id(self):
        """get_tweets matches by user_id even if username changed on Twitter."""
        mock_tweet = make_mock_tweet(user_id='1001', username='new_handle', created_on='2026-09-30 00:00:00+00:00')
        result = await get_tweets([mock_tweet], user_id='1001', last_tweet_at='2026-09-29 00:00:00+00:00')

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].author.id, '1001')

    async def test_get_tweets_mismatched_user_id_returns_none(self):
        """get_tweets returns None if tweet author ID does not match requested user_id."""
        mock_tweet = make_mock_tweet(user_id='1001', username='new_handle', created_on='2026-09-30 00:00:00+00:00')
        result = await get_tweets([mock_tweet], user_id='9999', last_tweet_at='2026-09-29 00:00:00+00:00')

        self.assertIsNone(result)


class TestNotificationCogUsernameChange(unittest.IsolatedAsyncioTestCase):
    """Verifies /remove notifier and account tracker behavior with user_id."""

    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'tracked_accounts.db')
        create_test_db(self.db_path)
        self.env_patch = patch.dict(os.environ, {
            'DATA_PATH': self.temp_dir.name,
            'TWITTER_TOKEN': 'clientA:tokenA'
        })
        self.env_patch.start()

        # Seed database: user '1001' has old username 'old_handle'
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO user (id, username, latest_tweet, client_used, enabled) VALUES ('1001', 'old_handle', '2026-09-29 00:00:00', 'clientA', 1)")
        conn.execute("INSERT INTO channel (id, server_id) VALUES ('2001', '3001')")
        conn.execute("INSERT INTO notification (user_id, channel_id, role_id, enabled) VALUES ('1001', '2001', '', 1)")
        conn.commit()
        conn.close()

        def mock_create_task(coro):
            if asyncio.iscoroutine(coro):
                coro.close()
            return MagicMock()

        self.bot = MagicMock()
        self.bot.loop.create_task = mock_create_task
        self.bot.change_presence = AsyncMock()
        self.cog = Notification(self.bot)


    async def asyncTearDown(self):
        await self.cog.cog_unload()
        self.env_patch.stop()
        self.temp_dir.cleanup()

    async def test_remove_notifier_unfollows_using_user_id(self):
        """When removing a notifier, it unfollows via Twitter API using user_id directly without extra get_user_info call."""
        itn = MagicMock()
        itn.guild_id = 3001
        itn.response.defer = AsyncMock()
        itn.followup.send = AsyncMock()

        mock_app = MagicMock()
        mock_app.connect = AsyncMock()
        mock_app.unfollow_user = AsyncMock(return_value=True)

        with patch('cogs.notification.Twitter', return_value=mock_app):
            await self.cog.r_notifier.callback(self.cog, itn, channel_id='2001', username='old_handle')

            self.assertTrue(itn.followup.send.called)
            sent_msg = itn.followup.send.call_args[0][0]
            self.assertIn('old_handle', sent_msg)

            # Check notification disabled in DB
            conn = sqlite3.connect(self.db_path)
            user_row = conn.execute("SELECT enabled FROM user WHERE id = '1001'").fetchone()
            notif_row = conn.execute("SELECT enabled FROM notification WHERE user_id = '1001' AND channel_id = '2001'").fetchone()
            conn.close()
            self.assertEqual(user_row[0], 0)
            self.assertEqual(notif_row[0], 0)

            # unfollow_user called directly with user_id '1001'
            mock_app.unfollow_user.assert_called_with('1001')
            self.assertFalse(mock_app.get_user_info.called)

    async def test_remove_notifier_not_found(self):
        """When username is not found in DB, responds with not found message without calling Twitter API."""
        itn = MagicMock()
        itn.guild_id = 3001
        itn.response.defer = AsyncMock()
        itn.followup.send = AsyncMock()

        mock_app = MagicMock()
        mock_app.connect = AsyncMock()

        with patch('cogs.notification.Twitter', return_value=mock_app):
            await self.cog.r_notifier.callback(self.cog, itn, channel_id='2001', username='non_existent')

            self.assertTrue(itn.followup.send.called)
            self.assertFalse(mock_app.connect.called)

    async def test_account_tracker_notification_auto_updates_username_in_db_and_task(self):
        """When a tweet arrives with a new username for a tracked user,

        AccountTracker should automatically update the DB and its tracked username.
        """
        tracker = self.cog.account_tracker
        tracker.latest_tweet_timestamps = {'1001': '2026-09-29 00:00:00+00:00'}
        tracker.tracked_users = {'1001': {'username': 'old_handle', 'client_used': 'clientA'}}
        mock_tweet = make_mock_tweet(user_id='1001', username='new_handle', created_on='2026-09-30 00:00:00+00:00')
        mock_tweet.created_on = datetime.now(timezone.utc)
        mock_tweet.url = 'https://twitter.com/new_handle/status/123'
        mock_tweet.is_retweet = False
        mock_tweet.is_quoted = False
        mock_tweet.media = []
        mock_tweet.text = 'hello world'
        mock_tweet.author.name = 'New Name'

        tracker.tweets = {'clientA': [mock_tweet]}

        # Run one iteration of notification task
        call_count = 0
        async def mock_sleep(sec):
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise asyncio.CancelledError()

        task = asyncio.create_task(tracker.notification('1001', 'old_handle', 'clientA'))
        task.set_name('old_handle')

        with patch('asyncio.sleep', side_effect=mock_sleep), \
             patch.object(tracker, '_send_notification', new_callable=AsyncMock):
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Verify task name updated to new_handle
        self.assertEqual(task.get_name(), 'new_handle')

        # Verify in-memory tracked username updated
        self.assertEqual(tracker.tracked_users['1001']['username'], 'new_handle')

        # Verify database user table updated to new_handle
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT username FROM user WHERE id = '1001'").fetchone()
        conn.close()
        self.assertEqual(row[0], 'new_handle')

    async def test_add_task_and_remove_task_by_user_id(self):
        """addTask starts task and registers cache by user_id; removeTask clears cache and cancels task."""
        tracker = self.cog.account_tracker
        tracker.latest_tweet_timestamps.clear()
        tracker.tracked_users.clear()

        with patch.object(tracker, 'notification', new_callable=AsyncMock):
            await tracker.addTask('2002', 'testuser', 'clientA')
            self.assertIn('2002', tracker.latest_tweet_timestamps)
            self.assertEqual(tracker.tracked_users['2002']['username'], 'testuser')

            dummy_task = asyncio.create_task(asyncio.sleep(100))
            dummy_task.set_name('testuser')

            await tracker.removeTask('2002')
            self.assertNotIn('2002', tracker.latest_tweet_timestamps)
            self.assertNotIn('2002', tracker.tracked_users)
            await asyncio.sleep(0)
            self.assertTrue(dummy_task.cancelled())


