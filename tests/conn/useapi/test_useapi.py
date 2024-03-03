import pytest
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse
from src.autobots.conn.useapi.useapi import UseApi

@pytest.mark.asyncio
async def test_imagine(set_test_settings)-> KeyError:
    prompt = "Ronaldo wearing adidas"
    req = DiscordReqModel(prompt=prompt)
    ua = UseApi()
    res: DiscordJobsApiResponse = await ua.imagine(req)
    # todo: assert (res.code == 200)



