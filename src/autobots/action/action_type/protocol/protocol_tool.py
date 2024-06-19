from typing import Protocol


class ToolProtocol(Protocol):

    @staticmethod
    def get_description() -> str:
        raise NotImplementedError
