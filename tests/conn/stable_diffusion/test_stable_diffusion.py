import time

import pytest

from autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus, StableDiffusionRes
from autobots.conn.stable_diffusion.image_mixer import ImageMixerReqModel
from autobots.conn.stable_diffusion.stable_diffusion import StableDiffusion
from autobots.conn.stable_diffusion.text2img import Text2ImgReqModel, Text2ImgResModel, YesNo, \
    Text2ImgResProcessingModel, Text2ImgResStatus
from autobots.conn.stable_diffusion.text2video import Text2VideoReqModel, Text2VideoResModel, \
    Text2VideoProcessingResModel
from autobots.core.settings import SettingsProvider


@pytest.mark.asyncio
async def test_text2img_happy_path(set_test_settings):
    prompt = "Ultra real Sport shoes advertisement"
    req = Text2ImgReqModel(prompt=prompt, self_attestaion=YesNo.no.value, width=512)
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.text2img(req)
    assert (len(res.urls) >= 1 or res.fetch_url is not None)


@pytest.mark.asyncio
async def test_image_mixer_happy_path(set_test_settings):
    prompt = "Rose head"
    req = ImageMixerReqModel(
        prompt=prompt,
        init_image="https://img.freepik.com/premium-photo/red-roses-rose-petals-white-backgroundvalentines-day-concept_167862-5720.jpg,"
                   "https://huggingface.co/datasets/diffusers/test-arrays/resolve/main/stable_diffusion_inpaint/boy.png",
        init_image_weights="1,1",
        width=512
    )
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.image_mixer(req)
    assert (len(res.urls) >= 1 or res.fetch_url is not None)


@pytest.mark.asyncio
async def test_text2video_happy_path(set_test_settings):
    prompt = "Ultra real Sport shoes advertisement"
    req = Text2VideoReqModel(prompt=prompt)
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.text2video(req)
    assert (len(res.urls) >= 1 or res.fetch_url is not None)