import os
import io
import logging
import logging.handlers
import sys
import unittest
from unittest.mock import patch

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.log
from src.log import (
    LOG_BUFFER,
    RingBufferHandler,
    LogFormatter,
    setup_logger,
    _get_shared_handlers,
)


class TestRingBufferHandler(unittest.TestCase):
    def setUp(self):
        LOG_BUFFER.clear()
        self.handler = RingBufferHandler()
        self.handler.setFormatter(LogFormatter())
        self.logger = logging.getLogger("test_ring_buffer")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.handlers.clear()
        logging.Logger.manager.loggerDict.pop("test_ring_buffer", None)
        LOG_BUFFER.clear()

    def test_log_appended_to_buffer(self):
        self.logger.info("hello ring buffer")
        self.assertEqual(len(LOG_BUFFER), 1)
        self.assertIn("hello ring buffer", LOG_BUFFER[0])
        self.assertIn("INFO", LOG_BUFFER[0])
        self.assertIn("test_ring_buffer", LOG_BUFFER[0])

    def test_buffer_maxlen_eviction(self):
        # Temporarily test with a small custom deque or fill beyond limit
        with patch.object(src.log, 'LOG_BUFFER', src.log.deque(maxlen=5)):
            handler = RingBufferHandler()
            handler.setFormatter(LogFormatter())
            test_logger = logging.getLogger("test_eviction")
            test_logger.setLevel(logging.INFO)
            test_logger.handlers = [handler]

            for i in range(10):
                test_logger.info(f"message {i}")

            self.assertEqual(len(src.log.LOG_BUFFER), 5)
            self.assertIn("message 5", src.log.LOG_BUFFER[0])
            self.assertIn("message 9", src.log.LOG_BUFFER[-1])
            logging.Logger.manager.loggerDict.pop("test_eviction", None)

    def test_buffer_formatting_without_ansi(self):
        self.logger.warning("plain warning message")
        entry = LOG_BUFFER[0]
        # Should not contain ANSI color escape codes
        self.assertNotIn("\x1b[", entry)
        self.assertIn("WARNING", entry)
        self.assertIn("plain warning message", entry)

    def test_exception_in_buffer(self):
        try:
            raise ValueError("test exception for buffer")
        except ValueError:
            self.logger.error("error occurred", exc_info=True)

        self.assertEqual(len(LOG_BUFFER), 1)
        entry = LOG_BUFFER[0]
        self.assertIn("test exception for buffer", entry)
        self.assertIn("Traceback", entry)


class TestSharedHandlers(unittest.TestCase):
    def setUp(self):
        LOG_BUFFER.clear()
        self.orig_shared = src.log._SHARED_HANDLERS
        self.orig_enable = src.log.ENABLE_FILE_LOG

        # Isolate from user environment: disable file logging during handler-sharing tests
        # so tests never touch the local filesystem or depend on env vars
        src.log.ENABLE_FILE_LOG = False
        src.log._SHARED_HANDLERS = None
        self.test_loggers = ["module_alpha", "module_beta", "module_repeat", "module_first", "module_second"]

    def tearDown(self):
        src.log._SHARED_HANDLERS = self.orig_shared
        src.log.ENABLE_FILE_LOG = self.orig_enable
        LOG_BUFFER.clear()
        for name in self.test_loggers:
            logging.Logger.manager.loggerDict.pop(name, None)

    def test_handlers_are_singletons_across_loggers(self):
        logger_a = setup_logger("module_alpha.py")
        logger_b = setup_logger("module_beta.py")

        self.assertEqual(len(logger_a.handlers), len(logger_b.handlers))
        self.assertGreater(len(logger_a.handlers), 0)
        for h_a, h_b in zip(logger_a.handlers, logger_b.handlers):
            self.assertIs(h_a, h_b, "Handlers must be identical singleton instances")

    def test_no_duplicate_handlers_on_repeated_setup(self):
        logger_1 = setup_logger("module_repeat.py")
        count_1 = len(logger_1.handlers)
        logger_2 = setup_logger("module_repeat.py")
        count_2 = len(logger_2.handlers)

        self.assertEqual(count_1, count_2)

    def test_both_loggers_write_to_same_buffer(self):
        logger_a = setup_logger("module_first.py")
        logger_b = setup_logger("module_second.py")

        logger_a.info("from first")
        logger_b.info("from second")

        self.assertEqual(len(LOG_BUFFER), 2)
        self.assertIn("module_first", LOG_BUFFER[0])
        self.assertIn("from first", LOG_BUFFER[0])
        self.assertIn("module_second", LOG_BUFFER[1])
        self.assertIn("from second", LOG_BUFFER[1])


class TestFileLoggingToggle(unittest.TestCase):
    """Verify that file logging is strictly controlled by ENABLE_FILE_LOG without touching disk."""

    def setUp(self):
        self.orig_shared = src.log._SHARED_HANDLERS
        self.orig_enable = src.log.ENABLE_FILE_LOG

    def tearDown(self):
        src.log._SHARED_HANDLERS = self.orig_shared
        src.log.ENABLE_FILE_LOG = self.orig_enable

    def test_file_logging_enabled(self):
        src.log.ENABLE_FILE_LOG = True
        src.log._SHARED_HANDLERS = None

        with patch('logging.handlers.RotatingFileHandler') as mock_rfh:
            handlers = _get_shared_handlers()

            mock_rfh.assert_called_once()
            _, kwargs = mock_rfh.call_args
            self.assertEqual(kwargs.get('maxBytes'), 5 * 1024 * 1024)
            self.assertEqual(kwargs.get('backupCount'), 1)
            self.assertEqual(kwargs.get('encoding'), 'utf-8')
            self.assertIn(mock_rfh.return_value, handlers)

    def test_file_logging_disabled(self):
        src.log.ENABLE_FILE_LOG = False
        src.log._SHARED_HANDLERS = None

        with patch('logging.handlers.RotatingFileHandler') as mock_rfh:
            handlers = _get_shared_handlers()
            mock_rfh.assert_not_called()

            types = [type(h) for h in handlers]
            self.assertIn(logging.StreamHandler, types)
            self.assertIn(RingBufferHandler, types)
            self.assertNotIn(logging.handlers.RotatingFileHandler, types)


class TestDownloadLogFallback(unittest.TestCase):
    """Test the in-memory stream logic used by bot.py download_log command."""

    def setUp(self):
        LOG_BUFFER.clear()

    def tearDown(self):
        LOG_BUFFER.clear()

    def test_memory_buffer_to_bytes_io(self):
        LOG_BUFFER.append("2026-09-29 12:00:00 INFO bot -> line 1")
        LOG_BUFFER.append("2026-09-29 12:00:01 INFO bot -> line 2")

        log_content = "\n".join(LOG_BUFFER)
        file_bytes = io.BytesIO(log_content.encode('utf-8'))

        # Verify stream is readable from beginning
        content = file_bytes.read().decode('utf-8')
        self.assertIn("line 1", content)
        self.assertIn("line 2", content)


if __name__ == '__main__':
    unittest.main()
