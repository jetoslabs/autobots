from typing import Dict, Any

from pydantic import BaseModel


class ActionCreateAPIModel(BaseModel):
    """
    base class to be utilized by action apis to create action
    """

    name: str
    version: float = 0
    description: str = ""
    user_manual: str = ""
    config: Dict[str, Any]
