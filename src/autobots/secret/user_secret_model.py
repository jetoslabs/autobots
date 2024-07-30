from typing import Dict, Any

from pydantic import Field, ConfigDict

from src.autobots.data_model.created_at import CreatedAt
from src.autobots.data_model.updated_at import UpdatedAt


class UserSecretDoc(CreatedAt, UpdatedAt):
    __collection__ = "Secret"

    user_id: str = Field(...)
    secret: Dict[str, Any]
    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)
