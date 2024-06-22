from typing import Protocol


class ToolableProtocol(Protocol):

    @staticmethod
    async def get_tool_description() -> str: ...

    @staticmethod
    async def run_tool(**kwargs) -> str | Exception: ...
