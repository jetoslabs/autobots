import pytest
from src.autobots.conn.claid.claid import UseClaidAiApi
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, Operations, Output, \
    BackgroundRemove, Background, ClaidResponse, ClaidPhotoShootRequestModel, PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel


@pytest.mark.asyncio
async def test_photoshoot(set_test_settings):
    claid_request = ClaidPhotoShootInputModel(
        output=PhotoshootOutput(
            destination="storage://teststorage/output/"
        ),
        object=PhotoshootObject(
            image_url="storage://teststorage/input/photo1.jpeg",
            placement_type="absolute",
            scale=0.4
        ),
        scene=PhotoshootScene(
            prompt= "on the wooden table in the dark room"
        )
    )
    uca = UseClaidAiApi()
    res : ClaidPhotoShootOutputModel = await uca.photoshoot(claid_request)
    print(res)
    assert (res)




