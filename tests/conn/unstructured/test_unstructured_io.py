import pytest
from fastapi import UploadFile

from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io


@pytest.mark.asyncio
async def test_unstructured_io_whole_file_happy_path(set_test_settings):
    ui_client = get_unstructured_io()
    file_name = "tests/resources/unstructured_io/autobots_api.txt"
    with open(file_name, mode='rb') as file:
        upload_file = UploadFile(filename=file_name, file=file)
        chunks = await ui_client.get_file_chunks(upload_file, 0)
        assert len(chunks) == 1


