from typing import Union, Literal, Dict, List, Optional, Any
from pydantic import BaseModel


class Intensity(BaseModel):
    intensity: int = 0


class Stitching(BaseModel):
    stitching: bool = False


class Adjustments(BaseModel):
    hdr: Union[int, Intensity, Stitching] = 0
    exposure: int = 1
    saturation: int = 1
    contrast: int = 1
    sharpness: int = 1


class Crop(BaseModel):
    crop: Literal["center", "smart"] = "smart"


class Resizing(BaseModel):
    width: int | None = None
    height: int | None = None
    fit: Union[Literal["bounds", "cover", "canvas", "outpaint"], Crop] = "bounds"


class BackgroundRemove(BaseModel):
    category: Literal["general", "cars", "products"] = "general"
    clipping: bool = True


class BackgroundBlur(BaseModel):
    category: Literal["general", "cars", "products"] = "general"
    type: Literal["regular", "lens"] = "regular"
    level: Literal["low", "medium", "high"] = "low"


class Background(BaseModel):
    remove: Union[bool, BackgroundRemove] | None = None
    blur: Union[bool, BackgroundBlur] | None = None
    color: str | None = "transparent"


class Restorations(BaseModel):
    decompress: str | None = None
    upscale: str | None = None


class Operations(BaseModel):
    restorations: Restorations | None = None
    upscale: str | None = None
    resizing: Resizing | None = None
    adjustments: Adjustments | None = None
    background: Background | None = None
    padding: str | None = None
    privacy: Dict[str, bool] | None = None


class OutputFormat(BaseModel):
    type: Literal["jpeg", "png", "webp", "avif"]
    quality: int | None = None
    progressive: bool | None = None


class OutputCompression(BaseModel):
    type: Literal["lossy", "lossless"]
    quality: int


class Output(BaseModel):
    destination: str | None = None
    metadata: Dict[str, int] | None = None
    format: Union[Literal["jpeg", "png", "webp", "avif"], OutputFormat, OutputCompression] = "png"


class ClaidBulkEditRequestModel(BaseModel):
    input: List[str] | None = None
    operations: Operations | None = None
    output: str


class ClaidInputModel(BaseModel):
    input: List[str]
    operations: Operations | None = None


class ClaidObject(BaseModel):
    ext: str
    mps: float
    mime: str
    format: str
    width: int
    height: int
    tmp_url: Optional[str] | None = None


class ClaidResult(BaseModel):
    input_object: ClaidObject
    output_object: ClaidObject


class ClaidResponseData(BaseModel):
    id: int
    status: str
    created_at: str
    request: ClaidBulkEditRequestModel
    errors: List[str] | None = None
    result_url: str | None = None
    results: List[ClaidResult] | None = None


class ClaidBulkEditResponse(BaseModel):
    data: ClaidResponseData


class ErrorDetails(BaseModel):
    name: List[str]
    parameters_credentials_access_key: List[str]


class ClaidErrorResponse(BaseModel):
    error_code: str = ""
    error_type: str
    error_message: str
    error_details: ErrorDetails | Dict[str, Any] = {}


class PhotoshootPosition(BaseModel):
    x: float = 0.5
    y: float = 0.5


class PhotoshootObject(BaseModel):
    image_url: str
    placement_type: Literal["absolute", "original"] = "original"
    rotation_degree: int | None = None
    scale: float | None = None
    position: PhotoshootPosition | None = None


class PhotoshootScene(BaseModel):  # PhotoshootTemplateBasedScene
    negative_prompt: str | None = None
    template_url: str | None = None
    color: str | None = None
    view: Literal["top", "front"] | None = None
    prompt: str
    template_mode: Literal["transform", "lock"] | None = None
    # error if view is used without template_url


class PhotoshootOutput(BaseModel):
    destination: str
    number_of_images: int = 1
    format: Literal["jpeg", "png", "webp", "avif"] = "jpeg"


class ClaidPhotoShootRequestModel(BaseModel):
    output: PhotoshootOutput


class ClaidPhotoShootInputModel(BaseModel):
    object: PhotoshootObject
    scene: PhotoshootScene
    output: PhotoshootOutput | None = None


class ClaidPhotoShootOutputDataModel(BaseModel):
    input: ClaidObject
    output: List[ClaidObject]


class ClaidPhotoShootOutputModel(BaseModel):
    data: ClaidPhotoShootOutputDataModel
