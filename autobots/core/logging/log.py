from typing import Literal, Any

import loguru

from autobots.core.logging.app_code import AppCode


class Log:

    def __init__(self):
        self.logger = loguru.logger.bind(app="autobots")

    def bind(self, **kwargs) -> loguru.Logger:
        return self.logger.bind(**kwargs)

    def with_app_code(self, app_code: AppCode) -> loguru.Logger:
        return self.logger.bind(app_code=app_code.value)

    def info(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.info(__message, *args, **kwargs)

    def debug(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.debug(__message, *args, **kwargs)

    def warning(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.warning(__message, *args, **kwargs)

    def error(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.error(__message, *args, **kwargs)

    def exception(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.exception(__message, *args, **kwargs)

    def critical(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.critical(__message, *args, **kwargs)

    def trace(self, __message: str, *args: Any, **kwargs: Any):
        self.logger.trace(__message, *args, **kwargs)

    def log(
            self,
            __level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"],
            __message: str,
            *args: Any,
            **kwargs: Any
    ):
        self.logger.log(__level, __message, *args, **kwargs)


