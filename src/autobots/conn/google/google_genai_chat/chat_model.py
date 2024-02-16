import dataclasses
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Optional, get_type_hints

from google.generativeai.types import (
    ContentDict,
    GenerationConfigType,
)
from pydantic import BaseModel, create_model


# TODO: Migrate both of these classes elsewhere
def dataclass_to_pydantic(dc):
    dc_fields = {
        field.name: (field.type, field.default) for field in fields(dc) if field.init
    }
    dc_annotations = get_type_hints(dc)
    # Update types for fields without a default (required fields)
    for name, type_ in dc_annotations.items():
        if name not in dc_fields or dc_fields[name][1] == dataclasses.MISSING:
            dc_fields[name] = (type_, ...)
    return create_model(dc.__name__ + "Pydantic", **dc_fields)


def dataclass_schema_json(dc, indent=None):
    if not is_dataclass(dc):
        raise ValueError("Provided object is not a dataclass")

    schema = {"title": dc.__name__, "type": "object", "properties": {}}
    annotations = get_type_hints(dc)

    for field in fields(dc):
        field_type = annotations[field.name]
        schema["properties"][field.name] = {
            "type": str(field_type).replace("typing.", ""),
        }
        if not isinstance(field.default, dataclasses._MISSING_TYPE):
            schema["properties"][field.name]["default"] = field.default

    return schema


class Role(str, Enum):
    user = "user"
    model = "model"


class ModelName(str, Enum):
    GEMINI_1_0_PRO = "models/gemini-1.0-pro"
    GEMINI_1_0_PRO_001 = "models/gemini-1.0-pro-001"
    GEMINI_1_0_PRO_LATEST = "models/gemini-1.0-pro-latest"
    GEMINI_1_0_PRO_VISION_LATEST = "models/gemini-1.0-pro-vision-latest"
    GEMINI_PRO = "models/gemini-pro"
    GEMINI_PRO_VISION = "models/gemini-pro-vision"


class ChatReq(BaseModel):
    contents: list[ContentDict]
    generation_config: Optional[GenerationConfigType] = None
    stream: bool = False

    class Config:
        arbitrary_types_allowed = True
