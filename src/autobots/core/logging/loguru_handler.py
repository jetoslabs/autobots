import logging
from loguru import logger


# Add Loguru handler to root logger
class LoguruHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        # Replace the default Python root logger with Loguru
        logging.root.handlers = [logging.NullHandler()]
        logging.root.setLevel(logging.INFO)
        logging.propagate = False  # Disable propagation to prevent duplicate logs

    def emit(self, record):
        logger.opt(depth=7, exception=record.exc_info).log(record.levelno, record.getMessage())


def replace_logging_with_loguru():
    logging.root.addHandler(LoguruHandler())  # Now the root logger will use Loguru for logging
