import pytest
from src.autobots.conn.claid.claid import UseClaidAiApi
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, Operations, Output, \
    BackgroundRemove, Background, ClaidResponse, ClaidPhotoShootRequestModel, PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootOutputModel


@pytest.mark.asyncio
async def test_bulkEdit(set_test_settings):
    #todo: change the  bucket before moving to prod
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
    assert (res.status_code == 200)

@pytest.mark.asyncio
async def test_photoshoot(set_test_settings):
    claid_request = ClaidPhotoShootRequestModel(
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




