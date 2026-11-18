import os
import re
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure project root and test directory are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import conftest  # noqa: F401 - global test isolation for standalone execution
except ImportError:
    pass

from configs.load_configs import configs
from src.notification.account_tracker import AccountTracker


class TestAuthenticateAccount(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tracker = AccountTracker.__new__(AccountTracker)

        self.app = MagicMock()
        self.app.load_cookies = AsyncMock()
        self.app.connect = AsyncMock()
        self.app.load_auth_token = AsyncMock()
        self.app.session.cookies_dict.return_value = {}

    @patch.dict(os.environ, {'DATA_PATH': os.path.join('some', 'data')})
    @patch('src.notification.account_tracker.Twitter')
    async def test_login_with_random_ct0_then_reconnect(self, mock_twitter):
        """Logs in via load_cookies with a random ct0 and reconnects, without calling load_auth_token."""
        mock_twitter.return_value = self.app
        calls = MagicMock()
        calls.attach_mock(self.app.load_cookies, 'load_cookies')
        calls.attach_mock(self.app.connect, 'connect')

        with patch.dict(configs, {'use_existing_sessions_first': False, 'auth_max_attempts': 2}):
            app = await self.tracker._authenticate_account('Main', 'tok')

        self.assertIs(app, self.app)
        mock_twitter.assert_called_once_with(os.path.join('some', 'data', 'Main'))
        self.app.load_auth_token.assert_not_awaited()

        self.assertEqual([c[0] for c in calls.mock_calls], ['load_cookies', 'connect'])
        cookies = self.app.load_cookies.await_args.args[0]
        self.assertEqual(cookies['auth_token'], 'tok')
        self.assertRegex(cookies['ct0'], re.compile(r'^[0-9a-f]{32}$'))

    @patch.dict(os.environ, {'DATA_PATH': os.path.join('some', 'data')})
    @patch('src.notification.account_tracker.Twitter')
    async def test_existing_session_skips_login(self, mock_twitter):
        """A saved, verified session with the same auth_token is reused without logging in again."""
        mock_twitter.return_value = self.app
        self.app.session.cookies_dict.return_value = {'auth_token': 'tok'}
        self.app.session.user = {'username': 'main'}
        self.app.connect.return_value = MagicMock()

        with patch.dict(configs, {'use_existing_sessions_first': True, 'auth_max_attempts': 2}):
            app = await self.tracker._authenticate_account('Main', 'tok')

        self.assertIs(app, self.app)
        self.app.connect.assert_awaited_once()
        self.app.load_cookies.assert_not_awaited()

    @patch.dict(os.environ, {'DATA_PATH': os.path.join('some', 'data')})
    @patch('src.notification.account_tracker.Twitter')
    async def test_unverified_session_without_user_reauthenticates(self, mock_twitter):
        """An unverified session (user is None) must not be reused with a single connect()."""
        mock_twitter.return_value = self.app
        self.app.session.cookies_dict.return_value = {'auth_token': 'tok'}
        self.app.session.user = None

        with patch.dict(configs, {'use_existing_sessions_first': True, 'auth_max_attempts': 2}):
            app = await self.tracker._authenticate_account('Main', 'tok')

        self.assertIs(app, self.app)
        self.app.load_cookies.assert_awaited_once()
        self.app.connect.assert_awaited_once()

    @patch.dict(os.environ, {'DATA_PATH': os.path.join('some', 'data')})
    @patch('src.notification.account_tracker.Twitter')
    async def test_updated_auth_token_reauthenticates(self, mock_twitter):
        """When env auth_token differs from the saved session, it skips connect() reuse and re-authenticates."""
        mock_twitter.return_value = self.app
        self.app.session.cookies_dict.return_value = {'auth_token': 'old_tok'}
        self.app.session.user = {'username': 'main'}

        with patch.dict(configs, {'use_existing_sessions_first': True, 'auth_max_attempts': 2}):
            app = await self.tracker._authenticate_account('Main', 'new_tok')

        self.assertIs(app, self.app)
        self.app.load_cookies.assert_awaited_once()
        self.assertEqual(self.app.load_cookies.await_args.args[0]['auth_token'], 'new_tok')
        self.app.connect.assert_awaited_once()

    @patch.dict(os.environ, {'DATA_PATH': os.path.join('some', 'data')})
    @patch('src.notification.account_tracker.Twitter')
    async def test_existing_session_connect_error_falls_back_to_login(self, mock_twitter):
        """If reusing an existing session raises an error, it falls back to load_cookies + connect()."""
        mock_twitter.return_value = self.app
        self.app.session.cookies_dict.return_value = {'auth_token': 'tok'}
        self.app.session.user = {'username': 'main'}
        self.app.connect.side_effect = [RuntimeError('session expired'), MagicMock()]

        with patch.dict(configs, {'use_existing_sessions_first': True, 'auth_max_attempts': 2}):
            app = await self.tracker._authenticate_account('Main', 'tok')

        self.assertIs(app, self.app)
        self.app.load_cookies.assert_awaited_once()
        self.assertEqual(self.app.connect.await_count, 2)

    @patch('src.notification.account_tracker.asyncio.sleep', new_callable=AsyncMock)
    @patch('src.notification.account_tracker.Twitter')
    async def test_persistent_auth_failure_retries_and_removes_tainted_session(self, mock_twitter, mock_sleep):
        """Persistent login failures retry up to auth_max_attempts, remove any tainted session file, and re-raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_file = os.path.join(tmpdir, 'Main.tw_session')
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write('{"cookies": {"auth_token": "tok", "ct0": "random"}, "user": null}')

            self.app.session.session_file_path = session_file
            self.app.load_cookies.side_effect = RuntimeError('verify failed')
            mock_twitter.return_value = self.app

            with patch.dict(os.environ, {'DATA_PATH': tmpdir}), \
                 patch.dict(configs, {'use_existing_sessions_first': False, 'auth_max_attempts': 3}):
                with self.assertRaises(RuntimeError):
                    await self.tracker._authenticate_account('Main', 'tok')

            self.assertEqual(self.app.load_cookies.await_count, 3)
            self.assertEqual(mock_sleep.await_count, 2)
            self.assertFalse(os.path.exists(session_file))


if __name__ == '__main__':
    unittest.main()
