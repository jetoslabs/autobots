from typing import Any, Sequence
from pydantic import BaseModel
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


class StabilityReq(BaseModel):
    # https://platform.stability.ai/docs/features/api-parameters
    prompt: str | list[str] | list
    init_image: Any | None = None
    mask_image: Any | None = None
    height: int = 512
    width: int = 512
    start_schedule: float = 0.6
    end_schedule: float = 0.1
    cfg_scale: float = 7.0
    sampler: Any = generation.SAMPLER_K_DPMPP_2M
    steps: int | None = 50
    seed: Sequence[int] | int = 0
    samples: int = 1
    safety: bool = True
    classifiers: Any | None = None
    guidance_preset: int = generation.GUIDANCE_PRESET_FAST_GREEN
    guidance_cuts: int = 0
    guidance_strength: float | None = None
    guidance_prompt: str | None = None
    guidance_models: list[str] | None = None


class StabilityUpscaleReq(BaseModel):
    init_image: Any
    width: int = None
    # prompt: str = None
    # seed: int = None
    # steps: int = 30
    # cfg_scale: int = 7
