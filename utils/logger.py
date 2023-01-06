import logging
import logging.handlers
from datetime import datetime
import os

timestamped_log = "logs/" + datetime.utcnow().strftime('%Y-%m-%d_%H-%M.log')


class ColourFormatter(logging.Formatter):
    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[32m%(name)s\x1b[0m \x1b[37m%(message)s\x1b[0m ',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'
        output = formatter.format(record)
        record.exc_text = None
        return output


class Logger:
    def __init__(self, name="PyBot", level=logging.INFO):
        formatter = logging.Formatter(
            '[{asctime}] [{levelname:<8}] {name}: {message}',
            '%Y-%m-%d %H:%M:%S',
            style='{'
        )
        self.delete_log('logs/latest.log')
        self.delete_log('logs/debug.log')
        self.delete_log(timestamped_log)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.latest_handler = logging.handlers.RotatingFileHandler(
            'logs/latest.log',
            encoding='utf-8',
            maxBytes=33554432,
            backupCount=5
        )
        self.latest_handler.setFormatter(formatter)
        self.latest_handler.setLevel(logging.INFO)
        self.logger.addHandler(self.latest_handler)
        self.debug_handler = logging.handlers.RotatingFileHandler(
            'logs/debug.log',
            encoding='utf-8',
            maxBytes=33554432,
            backupCount=5
        )
        self.debug_handler.setFormatter(formatter)
        self.debug_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.debug_handler)
        self.timestamped_handler = logging.handlers.RotatingFileHandler(
            timestamped_log,
            encoding='utf-8',
            maxBytes=33554432,
            backupCount=5
        )
        self.timestamped_handler.setFormatter(formatter)
        self.timestamped_handler.setLevel(logging.INFO)
        self.logger.addHandler(self.timestamped_handler)
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(ColourFormatter())
        self.logger.addHandler(self.stream_handler)

    def delete_log(self, filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
