from typing import List

import pytest

from src.autobots import SettingsProvider
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootInputModel, ClaidErrorResponse


@pytest.mark.asyncio
@pytest.mark.skip(reason="Claid is very costly")
async def test_claid_photoshoot(set_test_settings):
    user_name = "user_test"
    unique = "123"
    uca = get_claid()
    settings = SettingsProvider.sget()

    try:
        claid_request = ClaidPhotoShootInputModel(
            output=PhotoshootOutput(
                destination=f"{settings.CLAID_SIDE_S3_BUCKET}{settings.CLAID_PATH_PREFIX}{user_name}/{unique}/output/"
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
