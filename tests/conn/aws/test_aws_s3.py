import aiofiles.os
import pytest
from fastapi import UploadFile

from src.autobots.conn.aws.aws_s3 import get_s3
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
from src.autobots.core.utils import gen_uuid


@pytest.mark.asyncio
async def test_aws_s3_fileobj_pdf(set_test_settings):
    prefix = "test_"+str(gen_uuid())
    s3 = get_s3(object_prefix=prefix)

    filename = "Meetkiwi Design Documentation for Google Ads.pdf"
    filepath = f"tests/resources/conn/aws/{filename}"
    # Upload to s3
    try:
        with open(filepath, mode='rb') as file:
            upload_file = UploadFile(filename=filename, file=file)
            is_uploaded = await s3.upload_fileobj(upload_file.filename, upload_file.file)
            assert is_uploaded
    except Exception as e:
        assert str(e) is None

    download_file_path = f"tests/resources/conn/aws/downloaded_fileobj_{filename}"
    # Download to file system
    try:
        with open(download_file_path, "wb") as file:
            is_downloaded = await s3.download_fileobj(filename, file)
            ############
            unstructured = get_unstructured_io()
            await unstructured.get_file_chunks()
            ############
            assert is_downloaded
            # Delete from file system
            await aiofiles.os.remove(download_file_path)
    except Exception as e:
        assert str(e) is None

