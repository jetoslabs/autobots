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
    key: str = Field(default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
                     description="Your API Key used for request authorization.")
    prompt: str = Field(...,
                        description="Text prompt with description of the things you want in the video to be generated.")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the video.")
    scheduler: Text2VideoScheduler = Field(default=Text2VideoScheduler.UniPCMultistepScheduler.value,
                                           description="Use it to set a scheduler for video creation.")
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
