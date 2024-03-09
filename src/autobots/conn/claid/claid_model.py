from typing import Optional, Union, Literal, Dict, List
from pydantic import BaseModel


class Adjustments(BaseModel):
    hdr: Union[int, Dict[str, Union[int, bool]]]
    exposure: int
    saturation: int
    contrast: int
    sharpness: int


class BackgroundRemove(BaseModel):
    category: Optional[Literal["general", "cars", "products"]] = None
    clipping: Optional[bool] = None


class BackgroundBlur(BaseModel):
    category: Literal["general", "cars", "products"] = "general"
    type: Literal["regular", "lens"] = "general"
    level: Literal["low", "medium", "high"] = "low"

class Background(BaseModel):
    remove: Optional[BackgroundRemove] = None
    blur: Optional[BackgroundBlur] = None
    color: Optional[Literal["#ffffff", str]] = None


class Operations(BaseModel):
    decompress: Optional[Literal[None, "moderate", "strong", "auto"]] = None
    upscale: Optional[Literal[None, "smart_enhance", "smart_resize", "faces", "digital_art", "photo"]] = None
    resizing: Optional[Dict[str, Union[None, Literal["auto", "150%"], int, Dict[str, Literal["center", "smart"]]]]] = None
    adjustments: Optional[Adjustments] = None
    background: Optional[Union[bool, Background]] = None
    padding: Optional[Literal[None, "10%", "5% 25%"]] = None
    privacy: Optional[Dict[str, bool]] = None



class OutputFormat(BaseModel):
    type: Literal["jpeg", "png", "webp", "avif"]
    quality: Optional[int] = None
    progressive: Optional[bool] = None


class OutputCompression(BaseModel):
    type: Literal["lossy", "lossless"]
    quality: int


class Output(BaseModel):
    destination: Optional[str] = None
    metadata: Optional[Dict[str, Optional[int]]] = None
    format: Optional[Union[Literal["jpeg", "png", "webp", "avif"], OutputFormat, OutputCompression]] = None


class ClaidRequestModel(BaseModel):
    input: Optional[Union[str, Dict[str, str]]] = None
    operations: Operations
    output: Optional[Union[str, Output]] = None

class ClaidObject(BaseModel):
    ext: str
    mps: float
    mime: str
    format: str
    width: int
    height: int
    tmp_url: Optional[str] = None


class ClaidResult(BaseModel):
    input_object: ClaidObject
    output_object: ClaidObject



class ClaidResponseData(BaseModel):
    id: int
    status: str
    created_at: str
    request: ClaidRequestModel
    errors: List[str] = None
    result_url : str = None
    results: List[ClaidResult] = None


class ClaidResponse(BaseModel):
    data: ClaidResponseData

class ErrorDetails(BaseModel):
    name: List[str]
    parameters_credentials_access_key: List[str]


class ClaidErrorResponse(BaseModel):
    error_code: str
    error_type: str
    error_message: str
    error_details: ErrorDetails = None

class PhotoshootPosition(BaseModel):
    x: float = 0.5
    y: float = 0.5


class PhotoshootObject(BaseModel):
    image_url: str
    placement_type: Literal["absolute", "original"] = "original"
    rotation_degree: int = 0
    scale: float = 1.0
    position: PhotoshootPosition = None


class PhotoshootScene(BaseModel):
    template_url: str = None
    template_mode: Literal["transform" ,  "lock"] = None
    color: str = None
    view: Literal["top" ,  "front"] = None
    prompt: str = None
    negative_prompt: str = None


class PhotoshootOutput(BaseModel):
    destination: str
    number_of_images: int = None
    format: str = None


class ClaidPhotoShootRequestModel(BaseModel):
    output: PhotoshootOutput
    object: PhotoshootObject
    scene: PhotoshootScene

class ClaidPhotoShootOutputDataModel(BaseModel):
    input: ClaidObject
    output: List[ClaidObject]
class ClaidPhotoShootOutputModel(BaseModel):
    data: ClaidPhotoShootOutputDataModel


