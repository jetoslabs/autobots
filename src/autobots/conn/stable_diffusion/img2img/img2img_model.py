from typing import Optional, Literal, List, Dict, Any

from pydantic import BaseModel, Field, HttpUrl

from src.autobots import SettingsProvider
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus


class SDImg2ImgReqModel(BaseModel):
    key: str = Field(default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
                     description="Your API Key used for request authorization")
    prompt: str = Field(...,
                        description="Text prompt with description of the things you want in the image to be generated")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image")
    init_image: str = Field(..., description="Link to the Initial Image")
    width: int = Field(default=512, ge=1, le=1024, description="Width of the image. Max Height: Width: 1024x1024")
    height: int = Field(default=512, ge=1, le=1024, description="Height of the image. Max Height: Width: 1024x1024")
    samples: int = Field(default=1, ge=1, le=4,
                         description="Number of images to be returned in response. The maximum value is 4.")
    num_inference_steps: Literal["21", "31", "41", "51"] = Field("41", description="Number of denoising steps. Available values: 21, 31, 41, 51.")
    safety_checker: Literal["yes", "no"] = Field("no", description="A checker for NSFW images. If such an image is detected, it will be replaced by a blank image.")
    enhance_prompt: Literal["yes", "no"] = Field("yes", description="Enhance prompts for better results")
    guidance_scale: float = Field(default=10, ge=1, le=20,
                                  description="Scale for classifier-free guidance (minimum: 1; maximum: 20)")
    strength: float = Field(0.7, ge=0.0, le=1.0,
                            description="Prompt strength when using init image. 1.0 corresponds to full destruction of information in the init image.")
    seed: Optional[int] = Field(None,
                                description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.")
    base64: Literal["yes", "no"] = Field("no", description="Get response as base64 string, default: \"no\", options: yes/no")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class SDImg2ImgResError(BaseModel):
    status: StableDiffusionResStatus
    messege: Optional[Dict[str, Any]] = None


class SDImg2ImgMeta(BaseModel):
    H: int
    W: int
    enable_attention_slicing: Literal["true", "false"] = "true"
    file_prefix: str
    guidance_scale: int
    model: str
    n_samples: int
    negative_prompt: str
    outdir: str
    prompt: str
    revision: str
    safety_checker: str
    seed: int
    steps: int
    vae: str


class SDImg2ImgProcessingModel(BaseModel):
    status: StableDiffusionResStatus
    tip: str
    eta: float
    message: Optional[str] = None
    messege: Optional[str] = None
    fetch_result: HttpUrl
    id: int
    output: List[HttpUrl]
    meta: SDImg2ImgMeta


class SDImg2ImgResModel(BaseModel):
    status: StableDiffusionResStatus
    generationTime: float
    id: int
    output: List[str]
    meta: SDImg2ImgMeta

