from typing import Optional


class AppException(Exception):
    """
    General app exception class
    """
    def __init__(
            self,
            detail: Optional[str] = None,
            http_status: Optional[int] = None
    ):
        super().__init__(detail, http_status)
        self.detail = detail if detail is not None else ""
        self.http_status = http_status
