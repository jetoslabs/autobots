import pytest
from fastapi import UploadFile

from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io, PartitionParametersParams


@pytest.mark.asyncio
async def test_unstructured_io_whole_file_happy_path(set_test_settings):
    ui_client = get_unstructured_io()
    file_name = "tests/resources/unstructured_io/Meetkiwi Design Documentation for Google Ads.pdf"
    with open(file_name, mode='rb') as file:
        upload_file = UploadFile(filename=file_name, file=file)
        partition_parameters_params = PartitionParametersParams(
            combine_under_n_chars=0,
            strategy="hi_res",
            hi_res_model_name="chipper",
            pdf_infer_table_structure=True
        )
        chunks = await ui_client.get_file_chunks(
            upload_file,
            partition_parameters_params
        )
        assert len(chunks) == 1
