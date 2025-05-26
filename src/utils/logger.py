import logging
from logging.handlers import TimedRotatingFileHandler
import os

# https://docs.python.org/3/library/logging.html
# https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler

""" Wrapper class for logging """
class Logger:
    def __init__(self, name, log_file, level=logging.INFO, when='W0', interval=1, backup_count=7):
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            file_handler = TimedRotatingFileHandler(
                log_file, 
                when=when, 
                interval=interval, 
                backupCount=backup_count
            )
            file_handler.setLevel(level)

            # Console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)
