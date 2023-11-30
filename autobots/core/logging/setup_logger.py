import sys

from loguru import logger

from autobots.core.config import get_config
from autobots.core.settings import SettingsProvider


def setup_logger(level: str = get_config().LOG_LEVEL.debug):
    logger.remove()
    logger.bind().info("Setting up logger")
    settings = SettingsProvider.sget()
    # deployment mode
    if (
            settings.ENV == get_config().APP_ENV.prod
            or settings.ENV == get_config().APP_ENV.stage
            or settings.ENV == get_config().APP_ENV.qa
            or settings.ENV == get_config().APP_ENV.dev
    ):
        logger.add(sys.stdout,
                   level=level,
                   serialize=True,
                   enqueue=True)
    # local mode ot test mode
    elif settings.ENV == get_config().APP_ENV.test or settings.ENV == get_config().APP_ENV.local:
        logger.add(sys.stdout,
                   level=level,
                   format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <yellow>{message}</yellow> - <level>{extra}</level>",
                   colorize=True,
                   serialize=False,
                   enqueue=True)
    else:
        raise RuntimeError(f"Unknown environment: {settings.ENV}, Exiting...")

# log = loguru.logger.bind(app="autobots")
