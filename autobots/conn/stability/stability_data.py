from typing import Any, Sequence

from pydantic import BaseModel
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


class StabilityReq(BaseModel):
    prompt: str | list[str] | list
    # init_image: Image | None = None
    # mask_image: Image | None = None
    height: int = 512
    width: int = 512
    start_schedule: float = 1.0
    end_schedule: float = 0.01
    cfg_scale: float = 7.0
    sampler: Any = None
    steps: int | None = 30
    seed: Sequence[int] | int = 0
    samples: int = 1
    safety: bool = True
    classifiers: Any | None = None
    guidance_preset: int = generation.GUIDANCE_PRESET_NONE
    guidance_cuts: int = 0
    guidance_strength: float | None = None
    guidance_prompt: str | None = None
    guidance_models: list[str] | None = None
