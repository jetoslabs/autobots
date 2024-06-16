from typing import List

import pytest

from src.autobots import SettingsProvider
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootInputModel, ClaidErrorResponse, ClaidBulkEditRequestModel, Operations, \
    ClaidBulkEditResponse, Resizing


@pytest.mark.asyncio
@pytest.mark.skip(reason="Testing Claid photoshoot as action")
async def test_claid_photoshoot(set_test_settings):
    user_name = "user_test"
    unique = "123"
    uca = get_claid()
    settings = SettingsProvider.sget()
    destination = f"{settings.CLAID_SIDE_S3_BUCKET}{settings.CLAID_PATH_PREFIX}{user_name}/{unique}/output/"

    try:
        claid_request = ClaidPhotoShootInputModel(
            output=PhotoshootOutput(
                destination=destination
            ),
            object=PhotoshootObject(
                image_url="https://upload.wikimedia.org/wikipedia/en/9/9c/Archie_1942_issue_1.jpg",
                # image_url=f"{settings.CLAID_S3_SIDE_STORAGE_PREFIX}user_test/123/input/image1.jpg",
                placement_type="absolute",
                scale=0.4
            ),
            scene=PhotoshootScene(
                prompt="on the wooden table in the dark room"
            )
        )

        res: List[str] | ClaidErrorResponse | Exception = await uca.photoshoot(claid_request)
        assert isinstance(res, List)
        assert len(res) > 0
    except Exception as e:
        assert e is None
    finally:
        deleted = await get_claid().s3.delete_prefix(f"{user_name}/{unique}")
        assert len(deleted) > 0


@pytest.mark.asyncio
async def test_claid_bulkedit(set_test_settings):
    user_name = "user_test"
    unique = "124"
    uca = get_claid()
    settings = SettingsProvider.sget()
    destination = f"{settings.CLAID_SIDE_S3_BUCKET}{settings.CLAID_PATH_PREFIX}{user_name}/{unique}/output/"

    bulk_edit_req = ClaidBulkEditRequestModel(
        input=[
            "https://en.wikipedia.org/wiki/World_Heritage_Site#/media/File:Lince_Ib%C3%A9rico_Do%C3%B1ana.jpg",
            "https://en.wikipedia.org/wiki/World_Heritage_Site#/media/File:Paisaje_en_Punta_Pitt,_isla_de_San_Crist%C3%B3bal,_islas_Gal%C3%A1pagos,_Ecuador,_2015-07-24,_DD_75.JPG"
        ],
        operations=Operations(
            resizing=Resizing(width=128, height=128),
            # background=Background(remove=True),
        ),
        output=destination
    )
    res = await uca.bulk_edit(bulk_edit_req)
    assert not isinstance(res, ClaidErrorResponse)
    assert isinstance(res, ClaidBulkEditResponse) ##//Not seeing in S3
    assert res.data.status == "DONE"
    assert len(res.results) > 0

