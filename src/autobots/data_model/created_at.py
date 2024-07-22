from datetime import datetime

from pydantic import BaseModel


class CreatedAt(BaseModel):
    created_at: datetime = datetime.now()

