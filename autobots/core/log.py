import sys

import loguru
from loguru import logger

from autobots.core.config import get_config
from autobots.core.settings import SettingsProvider


def setup_logger():
    logger.remove()
    logger.bind().info("Setting up logger")
    settings = SettingsProvider.sget()
    # prod mode
    if settings.ENV == get_config().APP_ENV.prod:
        logger.add(sys.stdout,
                   level=get_config().LOG_LEVEL.debug,
                   serialize=True,
                   enqueue=True)
    # dev mode
    elif settings.ENV == get_config().APP_ENV.dev:
        logger.add(sys.stdout,
                   level=get_config().LOG_LEVEL.debug,
                   format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <yellow>{message}</yellow> - <level>{extra}</level>",
                   colorize=True,
                   serialize=False,
                   enqueue=True)


log = loguru.logger.bind(app="autobots")
# setup_logger()


# async def generate_trace_id() -> uuid.UUID:
#     # This function (uuid4) guarantees the random no. and doesn’t compromise with privacy.
#     trace_id: uuid.UUID = uuid.uuid4()
#     return trace_id
