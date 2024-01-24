from functools import lru_cache
from typing import List, Optional, Any

from fastapi import UploadFile
from pydantic import BaseModel, ValidationError
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
from unstructured_client.models.operations import PartitionResponse

from src.autobots.core.logging.log import Log
from src.autobots.core.settings import Settings, SettingsProvider


class PartitionResponseElementMetadata(BaseModel):
    filename: Optional[str]
    filetype: Optional[str]
    page_number: Optional[int]
    languages: Optional[List[str]] = []
    links: Optional[List[Any]] = None


class PartitionResponseElement(BaseModel):
    type: Optional[str]
    element_id: Optional[str]
    metadata: Optional[PartitionResponseElementMetadata]
    text: Optional[str]


class UnstructuredIO:

    def __init__(self, unstructured_api_key: str):
        self.client = UnstructuredClient(
            api_key_auth=unstructured_api_key,
        )

    async def _build_PartitionParameters(self, file: UploadFile, chunk_size: int = 500) -> shared.PartitionParameters:
        req = shared.PartitionParameters(
            # Note that this currently only supports a single file
            files=shared.Files(
                content=await file.read(),
                file_name=file.filename,
            ),
            # Other partition params
            chunking_strategy="by_title",
            combine_under_n_chars=chunk_size,
            pdf_infer_table_structure=True,
            hi_res_model_name=None,
            strategy="auto",
        )
        return req

    async def _get_PartitionResponse(self, file: UploadFile, req: shared.PartitionParameters) -> PartitionResponse | None:
        res: PartitionResponse | None = None
        try:
            res: PartitionResponse = self.client.general.partition(req)
        except SDKError as e:
            Log.error(str(e))
        except Exception as e:
            Log.error(str(e))
        if not res or res.status_code != 200:
            Log.error(f"Error in extracting data from file {file.filename}")
        return res
        # res_str = ("\n\n".join([str(el) for el in res.elements]))

    async def get_file_partition_elements(self, res: PartitionResponse | None) -> List[PartitionResponseElement]:
        elements = []
        for element_dict in res.elements:
            try:
                element = PartitionResponseElement.model_validate(element_dict)
                elements.append(element)
            except ValidationError as e:
                Log.error(str(e))
            except Exception as e:
                Log.error(str(e))
        return elements

    async def get_file_chunks(self, file: UploadFile, chunk_size: int = 500) -> List[str]:
        req = await self._build_PartitionParameters(file, chunk_size=chunk_size)
        res: PartitionResponse | None = await self._get_PartitionResponse(file, req)
        elements = await self.get_file_partition_elements(res)
        strings = []
        for element in elements:
            strings.append(element.text)
        return strings


@lru_cache
def get_unstructured_io(settings: Settings = SettingsProvider.sget()) -> UnstructuredIO:
    return UnstructuredIO(settings.UNSTRUCTURED_API_KEY)
