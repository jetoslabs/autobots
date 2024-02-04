from typing import Literal, Any

import loguru

from src.autobots.core.logging.app_code import AppCode


async def get_bind_dict():
    return {"app": "autobots"}

# class Log:
#
#     logger = loguru.logger.bind(app="autobots")
#
#     @staticmethod
#     def bind(**kwargs):
#         return Log.logger.bind(**kwargs)
#
#     @staticmethod
#     def with_app_code(app_code: AppCode):
#         return Log.logger.bind(app_code=app_code.value)
#
#     @staticmethod
#     def info(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.info(__message, *args, **kwargs)
#
#     @staticmethod
#     def debug(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.debug(__message, *args, **kwargs)
#
#     @staticmethod
#     def warning(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.warning(__message, *args, **kwargs)
#
#     @staticmethod
#     def error(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.error(__message, *args, **kwargs)
#
#     @staticmethod
#     def exception(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.exception(__message, *args, **kwargs)
#
#     @staticmethod
#     def critical(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.critical(__message, *args, **kwargs)
#
#     @staticmethod
#     def trace(__message: str, *args: Any, **kwargs: Any):
#         Log.logger.trace(__message, *args, **kwargs)
#
#     @staticmethod
#     def log(
#             __level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"],
#             __message: str,
#             *args: Any,
#             **kwargs: Any
#     ):
#         Log.logger.log(__level, __message, *args, **kwargs)
