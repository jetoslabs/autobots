from pydantic import Field
from typing import Union, Literal, Dict, List, Optional
from pydantic import BaseModel


class Adjustments(BaseModel):
    hdr: int = 0
    exposure: int = 1
    saturation: int = 1
    contrast: int = 1
    sharpness: int = 1

class Resizing(BaseModel):
    width: str = None
    height: str = None
    fit: Literal["bounds", "cover", "canvas", "outpaint", "crop"] = "bounds"
    crop: str = None


class BackgroundRemove(BaseModel):
    category: Literal["general", "cars", "products"] = "general"
    clipping: bool = True


class BackgroundBlur(BaseModel):
    category: Literal["general", "cars", "products"] = "general"
    type: Literal["regular", "lens"] = "regular"
    level: Literal["low", "medium", "high"] = "low"

class Background(BaseModel):
    remove: BackgroundRemove = None
    blur: BackgroundBlur = None
    color: str = None


class Operations(BaseModel):
    decompress: str = None
    upscale: str = None
    resizing: Resizing = None
    adjustments: Adjustments = None
    background: Background = None
    padding: str = None
    privacy: Dict[str, bool] = None



class OutputFormat(BaseModel):
    type: Literal["jpeg", "png", "webp", "avif"]
    quality: int = None
    progressive: bool = None


class OutputCompression(BaseModel):
    type: Literal["lossy", "lossless"]
    quality: int


class Output(BaseModel):
    destination: str = None
    metadata: Dict[str, int] = None
    format: Union[Literal["jpeg", "png", "webp", "avif"], OutputFormat, OutputCompression] = None


class ClaidRequestModel(BaseModel):
    input: str
    operations: Operations
    output: str

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


