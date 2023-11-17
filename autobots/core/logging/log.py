from typing import Literal

import loguru

from autobots.core.logging.app_code import AppCode


class Log:

    def __init__(self, **kwargs):
        self.logger = loguru.logger.bind(app="autobots")
        self.logger.bind(**kwargs)

    def bind(self, **kwargs):
        return self.logger.bind(**kwargs)

    def with_app_code(self, app_code: AppCode):
        return self.logger.bind(app_code=app_code.value)

    async def info(self, msg: str):
        self.logger.info(msg)

    async def debug(self, msg: str):
        self.logger.debug(msg)

    async def warning(self, msg: str):
        self.logger.warning(msg)

    async def error(self, msg: str):
        self.logger.error(msg)

    async def exception(self, msg: str):
        self.logger.exception(msg)

    async def critical(self, msg: str):
        self.logger.critical(msg)

    async def log(self, level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"], msg: str):
        self.logger.log(level, msg)


