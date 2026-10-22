import asyncio
import os
import signal
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure project root and test directory are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import conftest  # noqa: F401 - global test isolation for standalone execution
except ImportError:
    pass

from src.utils import close_on_sigterm


class TestCloseOnSigterm(unittest.IsolatedAsyncioTestCase):
    async def test_sigterm_closes_bot(self):
        """SIGTERM registers a handler that closes the bot."""
        bot = MagicMock()
        bot.close = AsyncMock()
        loop = asyncio.get_running_loop()

        with patch.object(loop, 'add_signal_handler') as add_handler:
            close_on_sigterm(bot)

        sig, callback = add_handler.call_args.args
        self.assertEqual(sig, signal.SIGTERM)

        callback()
        await asyncio.sleep(0)
        bot.close.assert_awaited_once()

    async def test_unsupported_loop_is_ignored(self):
        """Event loops without signal support (Windows) do not crash startup."""
        loop = asyncio.get_running_loop()

        with patch.object(loop, 'add_signal_handler', side_effect=NotImplementedError):
            close_on_sigterm(MagicMock())


if __name__ == '__main__':
    unittest.main()
