import uuid

import pytest
from fastapi import UploadFile

from src.autobots.conn.aws.aws_s3 import get_s3
from src.autobots.files.user_files import UserFiles
from src.autobots.user.user_orm_model import UserORM


@pytest.mark.asyncio
async def test_files_happy_path(set_test_settings):
    # unstructured = get_unstructured_io()
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    user = UserORM(id=user_id)
    s3 = get_s3()
    user_files = UserFiles(user, s3)

    filename = "Meetkiwi Design Documentation for Google Ads.pdf"
    filepath = f"tests/resources/files/{filename}"

    try:
        with open(filepath, mode='rb') as file:
            upload_file = UploadFile(filename=filename, file=file)
            await user_files.upload_files([upload_file])
            assert True

        data = await user_files.download_files([filename])
        assert data is not None

        await user_files.delete_files([filename])
        await user_files.delete_downloaded_files([filename])
    except Exception as e:
        assert e is None
