from enum import Enum

from pydantic import BaseModel


class StableDiffusionResStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"


class StableDiffusionResError(BaseModel):
    status: StableDiffusionResStatus
    message: str
