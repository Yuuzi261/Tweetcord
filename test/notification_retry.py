import os
import sys
import asyncio
import aiohttp
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call

import discord

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs.load_configs import configs
from src.notification.account_tracker import AccountTracker


class TestNotificationRetry(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create an AccountTracker instance bypassing __init__ to isolate unit tests
        # from real tasks, background loops, and database queries
        self.tracker = AccountTracker.__new__(AccountTracker)
        self.tracker.bot = MagicMock()
        self.tracker.session = AsyncMock()
        self.tracker.sending_retry_tasks = set()
        self.tracker.accounts_data = {}
        self.tracker.latest_tweet_timestamps = {}

        self.channel = MagicMock()
        self.channel.mention = "#test-channel"
        self.channel.send = AsyncMock()

        self.mock_resp_503 = MagicMock(status=503, reason='Service Unavailable')
        self.server_error = discord.DiscordServerError(self.mock_resp_503, 'Service Unavailable')

        self.mock_resp_403 = MagicMock(status=403, reason='Forbidden')
        self.forbidden_error = discord.Forbidden(self.mock_resp_403, 'Missing Access')

    async def asyncTearDown(self):
        for c in self.channel.send.call_args_list:
            f = c.kwargs.get('file')
            if f and hasattr(f, 'close'):
                f.close()

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_retry_success_after_failure(self, mock_sleep, mock_log):
        """Fails with 503 discord.DiscordServerError on first attempt, succeeds on second attempt in built_in mode."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            with patch('src.notification.account_tracker.EMBED_TYPE', 'built_in'):
                # Attempt 1 fails with 503, Attempt 2 succeeds
                self.channel.send.side_effect = [self.server_error, None]

                await self.tracker._retry_send_notification(
                    channel=self.channel,
                    msg="test notification",
                    view=None,
                    embeds=None,
                )

                # Channel send should have been attempted twice
                self.assertEqual(self.channel.send.call_count, 2)
                for c in self.channel.send.call_args_list:
                    self.assertEqual(c.args[0], "test notification")
                    self.assertIsNone(c.kwargs.get('view'))
                    self.assertIsNotNone(c.kwargs.get('file'))

                # Exponential backoff sleeps: initial delay (2), then backoff before second attempt (4)
                self.assertEqual(mock_sleep.call_count, 2)
                mock_sleep.assert_has_calls([call(2), call(4)])

                # Info log should report success after retry
                mock_log.info.assert_called_with(
                    f"successfully sent notification to {self.channel.mention} after retry 2/3"
                )

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_retry_proxy_mode(self, mock_sleep, mock_log):
        """Tests retry in proxy mode (sends without file attachments)."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            with patch('src.notification.account_tracker.EMBED_TYPE', 'proxy'):
                self.channel.send.side_effect = [self.server_error, None]

                await self.tracker._retry_send_notification(
                    channel=self.channel,
                    msg="test notification",
                    view=None,
                    embeds=None,
                )

                self.assertEqual(self.channel.send.call_count, 2)
                self.channel.send.assert_has_calls([
                    call("test notification", view=None),
                    call("test notification", view=None),
                ])
                self.assertEqual(mock_sleep.call_count, 2)
                mock_sleep.assert_has_calls([call(2), call(4)])

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_retry_max_attempts_exceeded(self, mock_sleep, mock_log):
        """Fails with 503 on all attempts, logs error and stops."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            # All attempts fail with 503
            self.channel.send.side_effect = self.server_error

            await self.tracker._retry_send_notification(
                channel=self.channel,
                msg="test notification",
                view=None,
                embeds=None,
            )

            # Channel send should have been called max_retries (3) times
            self.assertEqual(self.channel.send.call_count, 3)

            # Backoff delays: 2, 4, 8
            self.assertEqual(mock_sleep.call_count, 3)
            mock_sleep.assert_has_calls([call(2), call(4), call(8)])

            # Error log should report failure after max retries
            mock_log.error.assert_called_with(
                f"failed to send notification to {self.channel.mention} after 3 retries"
            )

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_non_retryable_error_aborts_immediately(self, mock_sleep, mock_log):
        """Raises discord.Forbidden (403), stops immediately without further retries."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            self.channel.send.side_effect = self.forbidden_error

            await self.tracker._retry_send_notification(
                channel=self.channel,
                msg="test notification",
                view=None,
                embeds=None,
            )

            # Channel send should have been called only once
            self.assertEqual(self.channel.send.call_count, 1)

            # Sleep called only once for the initial attempt
            self.assertEqual(mock_sleep.call_count, 1)
            mock_sleep.assert_called_once_with(2)

            # discord.Forbidden is deliberately suppressed from error log per requirements
            mock_log.error.assert_not_called()

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_non_retryable_general_error_aborts_and_logs(self, mock_sleep, mock_log):
        """Non-retryable general errors abort immediately and log an error."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            general_error = ValueError("Malformed payload")
            self.channel.send.side_effect = general_error

            await self.tracker._retry_send_notification(
                channel=self.channel,
                msg="test notification",
                view=None,
                embeds=None,
            )

            self.assertEqual(self.channel.send.call_count, 1)
            self.assertEqual(mock_sleep.call_count, 1)
            mock_log.error.assert_called_once_with(
                f"non-retryable error occurred at {self.channel.mention} during retry: {general_error}"
            )

    @patch('src.notification.account_tracker.EMBED_TYPE', 'built_in')
    @patch('src.notification.account_tracker.discord.File')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_file_recreated_each_attempt(self, mock_sleep, mock_file_cls):
        """Confirms fresh file creation per attempt if built-in embed footer is used."""
        with patch.dict(configs, {'notification_retry_delay': 2, 'notification_max_retries': 3}):
            mock_f1 = MagicMock(name='file_attempt_1')
            mock_f2 = MagicMock(name='file_attempt_2')
            mock_file_cls.side_effect = [mock_f1, mock_f2]

            self.channel.send.side_effect = [self.server_error, None]
            mock_embed = MagicMock(spec=discord.Embed)

            await self.tracker._retry_send_notification(
                channel=self.channel,
                msg="test notification",
                view=None,
                embeds=[mock_embed],
            )

            # discord.File must be instantiated freshly on each attempt
            self.assertEqual(mock_file_cls.call_count, 2)
            mock_file_cls.assert_has_calls([
                call('images/twitter.png', filename='footer.png'),
                call('images/twitter.png', filename='footer.png'),
            ])

            self.assertEqual(self.channel.send.call_count, 2)
            f1_sent = self.channel.send.call_args_list[0].kwargs['file']
            f2_sent = self.channel.send.call_args_list[1].kwargs['file']
            self.assertIs(f1_sent, mock_f1)
            self.assertIs(f2_sent, mock_f2)
            self.assertIsNot(f1_sent, f2_sent)

    @patch('src.notification.account_tracker.log')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_retry_transient_network_errors(self, mock_sleep, mock_log):
        """Tests that aiohttp.ClientError, asyncio.TimeoutError, and ConnectionResetError trigger retry."""
        transient_errors = [
            aiohttp.ClientError("Client connection dropped"),
            asyncio.TimeoutError("Request timed out"),
            ConnectionResetError("Connection reset by peer"),
        ]

        for err in transient_errors:
            with self.subTest(error_type=type(err).__name__):
                mock_sleep.reset_mock()
                mock_log.reset_mock()
                self.channel.send.reset_mock()

                with patch.dict(configs, {'notification_retry_delay': 1, 'notification_max_retries': 2}):
                    self.channel.send.side_effect = [err, None]

                    await self.tracker._retry_send_notification(
                        channel=self.channel,
                        msg="test msg",
                        view=None,
                        embeds=None,
                    )

                    self.assertEqual(self.channel.send.call_count, 2)
                    self.assertEqual(mock_sleep.call_count, 2)
                    mock_sleep.assert_has_calls([call(1), call(2)])
                    mock_log.warning.assert_called_once_with(
                        f"retry 1/2 failed for {self.channel.mention}: {err}"
                    )
                    mock_log.info.assert_called_once_with(
                        f"successfully sent notification to {self.channel.mention} after retry 2/2"
                    )

    async def test_close_cancels_retry_tasks(self):
        """AccountTracker.close() cancels any active retry tasks and clears the set."""
        async def dummy_coro():
            await asyncio.sleep(100)

        task = asyncio.create_task(dummy_coro())
        self.tracker.sending_retry_tasks.add(task)

        await self.tracker.close()

        self.assertTrue(task.cancelled())
        self.assertEqual(len(self.tracker.sending_retry_tasks), 0)
        self.tracker.session.close.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
