import pytest

from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.image_mixer.image_mixer_model import (
    ImageMixerReqModel,
)
from src.autobots.conn.stable_diffusion.img2img.img2img_model import SDImg2ImgReqModel
from src.autobots.conn.stable_diffusion.stable_diffusion import StableDiffusion
from src.autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel
from src.autobots.conn.stable_diffusion.text2video.text2video_model import (
    Text2VideoReqModel,
)
from src.autobots.core.settings import SettingsProvider


@pytest.mark.asyncio
async def test_text2img_happy_path(set_test_settings):
    prompt = "Ultra real Sport shoes advertisement"
    req = Text2ImgReqModel(prompt=prompt, width=512)
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.text2img(req)
    assert len(res.urls) >= 1 or res.fetch_url is not None


@pytest.mark.skip(reason="Stable Diffusion test_image_mixer_happy_path flaky")
@pytest.mark.asyncio
async def test_image_mixer_happy_path(set_test_settings):
    prompt = "Rose head"
    req = ImageMixerReqModel(
        prompt=prompt,
        init_image="https://img.freepik.com/premium-photo/red-roses-rose-petals-white-backgroundvalentines-day-concept_167862-5720.jpg,"
        "https://huggingface.co/datasets/diffusers/test-arrays/resolve/main/stable_diffusion_inpaint/boy.png",
        init_image_weights="1,1",
        width=512,
    )
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.image_mixer(req)
    assert len(res.urls) >= 1 or res.fetch_url is not None


@pytest.mark.asyncio
async def test_img2img_happy_path(set_test_settings):
    prompt = "a cat sitting on a bench"
    negative_prompt = "bad quality"
    init_image = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo.png"
    req = SDImg2ImgReqModel(
        prompt=prompt, negetive_prompt=negative_prompt, init_image=init_image, width=512
    )
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.img2img(req)
    assert len(res.urls) >= 1 or res.fetch_url is not None


# @pytest.mark.skip(reason="Stable Diffusion text 2 video api is broken")
@pytest.mark.asyncio
async def test_text2video_happy_path(set_test_settings):
    prompt = "Ultra real athlete running in urban environment TV quality"
    req = Text2VideoReqModel(prompt=prompt)
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: StableDiffusionRes = await st.text2video(req)
    assert len(res.urls) >= 1 or res.fetch_url is not None
