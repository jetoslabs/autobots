from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl

from autobots import SettingsProvider
from autobots.conn.stable_diffusion.common_models import YesNo


class NumInferenceSteps(int, Enum):
    _21 = 21
    _31 = 31
    _41 = 41
    _51 = 51


class Text2ImgReqModel(BaseModel):
    key: str = Field(default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
                     description="Your API Key used for request authorization.")
    prompt: str = Field(..., description="Text prompt with description of the things you want in the image to be generated.")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image.")
    width: int = Field(default=512, ge=0, le=1024, description="Max Height: Width: 1024x1024.")
    height: int = Field(default=512, ge=0, le=1024, description="Max Height: Width: 1024x1024.")
    samples: int = Field(default=1, ge=1, le=4,
                         description="Number of images to be returned in response. The maximum value is 4.")
    num_inference_steps: NumInferenceSteps = Field(default=NumInferenceSteps._31,
                                                   description="Number of denoising steps. Available values: 21, 31, 41, 51.")
    safety_checker: YesNo = Field(default=YesNo.yes.value,
                                  description="A checker for NSFW images. If such an image is detected, it will be replaced by a blank image.")
    enhance_prompt: YesNo = Field(default=YesNo.yes.value,
                                  description="Enhance prompts for better results; default: yes, options: yes/no.")
    seed: Optional[int] = Field(default=None,
                                description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.")
    guidance_scale: float = Field(default=7.5, ge=1, le=20,
                                  description="Scale for classifier-free guidance (minimum: 1; maximum: 20).")
    multi_lingual: str = Field(default="no",
                               description="Allow multi lingual prompt to generate images. Use \"no\" for the default English.")
    panorama: YesNo = Field(default=YesNo.no.value,
                            description="Set this parameter to \"yes\" to generate a panorama image.")
    self_attention: YesNo = Field(default=YesNo.yes.value,
                                  description="If you want a high quality image, set this parameter to \"yes\". In this case the image generation will take more time.")
    upscale: YesNo = Field(default=YesNo.no.value,
                           description="Set this parameter to \"yes\" if you want to upscale the given image resolution two times (2x). If the requested resolution is 512 x 512 px, the generated image will be 1024 x 1024 px.")
    embeddings_model: Optional[str] = Field(default=None,
                                            description="This is used to pass an embeddings model (embeddings_model_id).")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class Text2ImgResMetaData(BaseModel):
    H: int
    W: int
    enable_attention_slicing: str
    file_prefix: str
    guidance_scale: float
    instant_response: Optional[str]
    model: str
    n_samples: int
    negative_prompt: str
    outdir: str
    prompt: str
    revision: str
    safetychecker: str
    seed: int
    steps: int
    vae: str


class Text2ImgResStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"


class Text2ImgResModel(BaseModel):
    status: Text2ImgResStatus
    generationTime: float
    id: int
    output: List[HttpUrl]
    meta: Text2ImgResMetaData


class Text2ImgResProcessingModel(BaseModel):
    status: Text2ImgResStatus
    tip: str
    eta: float
    messege: str
    fetch_result: HttpUrl
    id: int
    output: List[HttpUrl]
    meta: Text2ImgResMetaData


class Text2ImgResError(BaseModel):
    status: Text2ImgResStatus
    message: str
