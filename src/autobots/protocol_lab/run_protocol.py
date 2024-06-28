from asyncio import Protocol
from typing import Any

from src.autobots.data_model.context import Context


class ProtocolRun(Protocol):

    @staticmethod
    async def run(ctx: Context, run_param: Any) -> Any: ...
