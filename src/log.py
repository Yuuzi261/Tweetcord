import logging
import logging.handlers
import os


class LogFormatter(logging.Formatter):

    LEVEL_COLORS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    def setFORMATS(self, is_exc_info_colored):
        if is_exc_info_colored:
            self.FORMATS = {
                level: logging.Formatter(
                    f'\x1b[30;1m%(asctime)s\x1b[0m {color}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m -> %(message)s',
                    '%Y-%m-%d %H:%M:%S'
                )
                for level, color in self.LEVEL_COLORS
            }
        else:
            self.FORMATS = {
                item[0]: logging.Formatter(
                    '%(asctime)s %(levelname)-8s %(name)s -> %(message)s',
                    '%Y-%m-%d %H:%M:%S'
                )
                for item in self.LEVEL_COLORS
            }

    def format(self, record, is_exc_info_colored=False):
        self.setFORMATS(is_exc_info_colored)
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red (if is_exc_info_colored is True)
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            if is_exc_info_colored:
                record.exc_text = f'\x1b[31m{text}\x1b[0m'
            else:
                record.exc_text = text

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


class ConsoleFormatter(LogFormatter):

    def format(self, record):
        return super().format(record, is_exc_info_colored=True)


def setup_logger(module_name: str) -> logging.Logger:

    # create logger
    library, _, _ = module_name.partition('.py')
    logger = logging.getLogger(library)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ConsoleFormatter())

        # specify that the log file path is the same as `main.py` file path
        grandparent_dir = os.path.abspath(__file__ + "/../../")
        log_name = 'console.log'
        log_path = os.path.join(grandparent_dir, log_name)

        # create local log handler
        log_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=2,  # Rotate through 5 files
        )
        log_handler.setFormatter(LogFormatter())

        # Add handlers to logger
        logger.addHandler(log_handler)
        logger.addHandler(console_handler)

    return logger
