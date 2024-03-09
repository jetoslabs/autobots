import pytest

from src.autobots.conn.claid.claid import UseClaidAiApi
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, Operations, Output, \
    BackgroundRemove, Background, ClaidResponse
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse
from src.autobots.conn.useapi.useapi import UseApi

@pytest.mark.asyncio
async def test_bulkEdit(set_test_settings)-> KeyError:
    req = ClaidRequestModel(
        input={"path": "storage://teststorage/input/photo1.jpeg"},
        operations=Operations(
            background=Background(
                remove = BackgroundRemove(
                category="general",  # Choose appropriate category here
                clipping=True  # Or set to False if not needed
                )

            ),
            decompress = None,
            upscale = None,
            resizing = None,
            adjustments = None,
            padding = None,
            privacy = None
        ),
        output=Output(
            destination="storage://teststorage/output/",
            metadata = None,
            format = None
        )
    )

    uca = UseClaidAiApi()
    res: ClaidResponse = await uca.bulkEdit(req)
    print(res)
    assert (res.dict().get('data').get('status') == 'ACCEPTED')



