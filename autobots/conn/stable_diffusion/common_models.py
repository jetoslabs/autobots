from enum import Enum


class StableDiffusionResStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"
    failed = "failed"
