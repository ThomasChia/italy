import time
import logging
import colorlog
from datetime import timedelta


class ElapsedTimeColoredFormatter(colorlog.ColoredFormatter):
    def __init__(self):
        self.start_time = time.time()
        fmt = '%(log_color)s%(levelname)s:%(name)s: %(message)s'
        super().__init__(fmt)
    
    def formatMessage(self, record: logging.LogRecord) -> str:
        message = super().formatMessage(record)
        elapsed_seconds = record.created - self.start_time
        elapsed = timedelta(seconds = elapsed_seconds)
        return str(elapsed)[:-7] + ' | ' + message

def setup_logs():
    handler = colorlog.StreamHandler()
    handler.setFormatter(ElapsedTimeColoredFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])