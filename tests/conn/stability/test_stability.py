import io

import pytest
import pytest_asyncio
from PIL import Image
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

from autobots.conn.conn import get_conn
from autobots.conn.stability.stability import Stability
from autobots.conn.stability.stability_data import StabilityReq, StabilityUpscaleReq
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')
    # Making test cheaper by using old engine
    get_conn().stability = Stability()#(engine="stable-diffusion-768-v2-0")


@pytest.mark.asyncio
async def test_text_to_image_happy_path(set_settings):
    prompt = "Image of a family wearing Nike shoes"
    stability_req = StabilityReq(prompt=prompt, cfg_scale=9)
    img_bytes = await get_conn().stability.text_to_image(stability_req)
    assert img_bytes is not None


@pytest.mark.asyncio
async def test_image_to_image_happy_path(set_settings):
    prompt = "Steve McCurry photo of a man"
    stability_req = StabilityReq(
        prompt=prompt,
        steps=50,
        cfg_scale=8.0,
        # width=1024,
        # height=1024,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )
    img_bytes = await get_conn().stability.text_to_image(stability_req)
    img = Image.open(io.BytesIO(img_bytes))

    assert img.height > 0
    assert img.width > 0

    ### image to image
    # img = Image.open("resources/conn/stability/2968969163.png")
    prompt = "Image of a family wearing Nike shoes"
    stability_req = StabilityReq(
        prompt=prompt,
        init_image=img,
        start_schedule=0.6,
        end_schedule=0.1,
        steps=50,
        cfg_scale=8.0,
        # width=1024,
        # height=1024,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )
    img_bytes = await get_conn().stability.text_to_image(stability_req)

    assert img.height > 0
    assert img.width > 0


@pytest.mark.asyncio
async def test_upscale_image_happy_path(set_settings):
    prompt = "Image of a model running in Nike shoes"
    width = 1024
    height = 1024

    stability_req = StabilityReq(prompt=prompt, cfg_scale=9, width=width, height=height)
    img_bytes = await get_conn().stability.text_to_image(stability_req)
    img = Image.open(io.BytesIO(img_bytes))

    assert img.width == width
    assert img.height == height

    new_width = 1080#width * 2
    new_height = 1080#(new_width/width) * height
    stability_req = StabilityUpscaleReq(init_image=img, width=new_width)
    img_bytes = await get_conn().stability.upscale_image(stability_req)
    new_img = Image.open(io.BytesIO(img_bytes))

    assert new_img.width == new_width
    assert new_img.height == new_height
