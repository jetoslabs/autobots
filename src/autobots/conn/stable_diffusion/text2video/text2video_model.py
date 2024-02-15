from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl

from src.autobots import SettingsProvider
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus


class Text2VideoScheduler(str, Enum):
    DDPMScheduler = "DDPMScheduler"
    DDIMScheduler = "DDIMScheduler"
    PNDMScheduler = "PNDMScheduler"
    LMSDiscreteScheduler = "LMSDiscreteScheduler"
    EulerDiscreteScheduler = "EulerDiscreteScheduler"
    EulerAncestralDiscreteScheduler = "EulerAncestralDiscreteScheduler"
    DPMSolverMultistepScheduler = "DPMSolverMultistepScheduler"
    HeunDiscreteScheduler = "HeunDiscreteScheduler"
    KDPM2DiscreteScheduler = "KDPM2DiscreteScheduler"
    DPMSolverSinglestepScheduler = "DPMSolverSinglestepScheduler"
    KDPM2AncestralDiscreteScheduler = "KDPM2AncestralDiscreteScheduler"
    UniPCMultistepScheduler = "UniPCMultistepScheduler"
    DDIMInverseScheduler = "DDIMInverseScheduler"
    DEISMultistepScheduler = "DEISMultistepScheduler"
    IPNDMScheduler = "IPNDMScheduler"
    KarrasVeScheduler = "KarrasVeScheduler"
    ScoreSdeVeScheduler = "ScoreSdeVeScheduler"


class Text2VideoReqModel(BaseModel):
    key: str = Field(
        default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
        description="Your API Key used for request authorization.",
    )
    # model_id: str = Field(default="zeroscope",
    #                       description="The ID of the model to use. Can be zeroscope or one of the models present here https://modelslab.com/models/category/stable-diffusion")
    prompt: str = Field(
        ...,
        description="Text prompt with description of the things you want in the video to be generated.",
    )
    negative_prompt: Optional[str] = Field(
        default="low quality", description="Items you don't want in the video."
    )
    seed: Optional[int] = Field(
        default=None,
        description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.",
    )
    width: int = Field(
        default=1024, ge=0, le=1024, description="Max Height: Width: 1024x1024."
    )
    height: int = Field(
        default=1024, ge=0, le=1024, description="Max Height: Width: 1024x1024."
    )
    # num_frames: int = Field(default=25, ge=16, le=25,
    #                         description="Number of frames in generated video. Max: 25. Defaults to 16.")
    # num_inference_steps: int = Field(default=20, ge=20, le=50,
    #                                  description="Number of denoising steps. Max: 50. Defaults to 20.")
    # guidance_scale: float = Field(default=10, ge=1, le=20,
    #                               description="Scale for classifier-free guidance (minimum: 1; maximum: 20)")
    # clip_skip: Optional[float] = Field(default=2, ge=0, le=5,
    #                                    description="Number of CLIP layers to skip. 2 leads to more aesthetic defaults. Defauls to null.")
    # use_improved_sampling: Optional[bool] = Field(default=True,
    #                                               description="Whether or not you want to use improved sampling technique. Leads to better results with higher temporal consistency at the cost of being slow.")
    # improved_sampling_seed: Optional[int] = Field(default=None,
    #                                               description="Seed for consistent video generation when using improved sampling technique.")
    # fps: Optional[int] = Field(default=None, description="Frames per second rate of generated video.")
    # output_type: Literal["mp4", "gif", "base64"] = Field(default="mp4", description="The output type could be mp4,gif, base64")
    # instant_response: Optional[bool] = Field(default=False,
    #                                          description="queue response instantly before processing finishes instead of waiting a minimum amount of time, default: false, options: true or false")
    # temp: Optional[bool] = Field(default=False, description="true if you want to store your generations on our temporary storage. Temporary files are cleaned every 24 hours. Defaults to false.")
    # base64: Optional[bool] = Field(default=False,
    #                                description="true if you'd like your generated video as a base64 string of an mp4 file. Defaults to false.")
    # webhook: Optional[str] = Field(default=None,
    #                                description="Set an URL to get a POST API call once the image generation is complete.")
    # track_id: Optional[str] = Field(default=None,
    #                                 description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")
    scheduler: Text2VideoScheduler = Field(
        default=Text2VideoScheduler.UniPCMultistepScheduler.value,
        description="Use it to set a scheduler for video creation.",
    )
    seconds: int = Field(default=3, description="Duration of the video in seconds.")


class Text2VideoResModel(BaseModel):
    status: StableDiffusionResStatus
    generationTime: float
    id: int
    output: List[HttpUrl]


class Text2VideoResMetaData(BaseModel):
    H: int
    W: int
    file_prefix: str
    guidance_scale: int
    image_guidance_scale: int
    instant_response: Optional[str] = None
    n_samples: int
    negative_prompt: str
    num_frames: int
    outdir: str
    prompt: str
    safetychecker: str
    scheduler: Text2VideoScheduler
    seconds: int
    seed: int
    steps: int


class Text2VideoProcessingResModel(BaseModel):
    status: StableDiffusionResStatus
    tip: str
    eta: float
    message: Optional[str] = None
    messege: Optional[str] = None
    fetch_result: HttpUrl
    id: int
    output: HttpUrl | str
    meta: Text2VideoResMetaData


class Text2VideoResError(BaseModel):
    status: StableDiffusionResStatus
    message: str
