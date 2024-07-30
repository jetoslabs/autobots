from typing import List

from pydantic import BaseModel, HttpUrl

from src.autobots.conn.unstructured_io.unstructured_io import PartitionParametersParams

class FileMeta(BaseModel):
    name: str
    url: HttpUrl

class FileAndProcessingParams(BaseModel):
    filename: str
    processing_params: PartitionParametersParams


class FilesAndProcessingParams(BaseModel):
    files_and_params: List[FileAndProcessingParams]
