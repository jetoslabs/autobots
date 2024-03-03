from typing import Optional, Union, Literal, Dict, List
from pydantic import BaseModel


class Adjustments(BaseModel):
    hdr: Union[int, Dict[str, Union[int, bool]]]
    exposure: int
    saturation: int
    contrast: int
    sharpness: int


class BackgroundRemove(BaseModel):
    category: Literal["general", "cars", "products"]
    clipping: Optional[bool]


class BackgroundBlur(BaseModel):
    category: Literal["general", "cars", "products"]
    type: Literal["regular", "lens"]
    level: Literal["low", "medium", "high"]


class Operations(BaseModel):
    decompress: Optional[Literal[None, "moderate", "strong", "auto"]]
    upscale: Optional[Literal[None, "smart_enhance", "smart_resize", "faces", "digital_art", "photo"]]
    resizing: Optional[Dict[str, Union[None, Literal["auto", "150%"], int, Dict[str, Literal["center", "smart"]]]]]
    adjustments: Optional[Adjustments]
    background: Optional[Union[bool, BackgroundRemove, BackgroundBlur, Literal["#ffffff", str]]]
    padding: Optional[Literal[None, "10%", "5% 25%"]]
    privacy: Optional[Dict[str, bool]]


class OutputFormat(BaseModel):
    type: Literal["jpeg", "png", "webp", "avif"]
    quality: Optional[int]
    progressive: Optional[bool]


class OutputCompression(BaseModel):
    type: Literal["lossy", "lossless"]
    quality: int


class Output(BaseModel):
    destination: Optional[str]
    metadata: Optional[Dict[str, Optional[int]]]
    format: Union[Literal["jpeg", "png", "webp", "avif"], OutputFormat, OutputCompression]


class ClaidRequestModel(BaseModel):
    input: Union[Literal[str], Dict[str, str]]
    operations: Operations
    output: Optional[Union[str, Output]]

class ClaidObject(BaseModel):
    ext: str
    mps: float
    mime: str
    format: str
    width: int
    height: int


class ClaidResult(BaseModel):
    input_object: ClaidObject
    output_object: ClaidObject


class ClaidResponseRequestModel(BaseModel):
    input: str
    operations: Dict[str, Union[Dict[str, int], Dict[str, bool]]]
    output: str


class ClaidResponseData(BaseModel):
    id: int
    status: str
    created_at: str
    request: ClaidResponseRequestModel
    errors: List[str]
    results: List[ClaidResult]


class ClaidResponse(BaseModel):
    data: ClaidResponseData

class ErrorDetails(BaseModel):
    name: List[str]
    parameters_credentials_access_key: List[str]


class ClaidErrorResponse(BaseModel):
    error_code: str
    error_type: str
    error_message: str
    error_details: ErrorDetails
