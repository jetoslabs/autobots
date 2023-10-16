import pytest

from autobots.conn.stable_diffusion.stable_diffusion import StableDiffusion
from autobots.conn.stable_diffusion.text2img import Text2ImgReqModel, Text2ImgResModel, YesNo, \
    Text2ImgResProcessingModel, Text2ImgResStatus
from autobots.core.settings import SettingsProvider


@pytest.mark.asyncio
async def test_text2img_happy_path(set_test_settings):
    prompt = "Ultra real Sport shoes advertisement"
    req = Text2ImgReqModel(prompt=prompt, self_attestaion=YesNo.no.value, width=512)
    st = StableDiffusion(SettingsProvider.sget().STABLE_DIFFUSION_API_KEY)
    res: Text2ImgResModel | Text2ImgResProcessingModel = await st.text2img(req)

    assert (res.status == Text2ImgResStatus.success.value
            or res.status == Text2ImgResStatus.processing.value)


