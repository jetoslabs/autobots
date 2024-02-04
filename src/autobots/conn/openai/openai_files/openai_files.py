from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai._legacy_response import HttpxBinaryResponseContent
from openai.pagination import AsyncPage
from openai.types import FileObject, FileDeleted

from src.autobots.conn.openai.openai_files.openai_files_model import FileList, FileCreate, FileDelete, FileRetrieve, \
    FileContent


class OpenaiFiles():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def list(self, file_list: FileList) -> AsyncPaginator[FileObject, AsyncPage[FileObject]]:
        try:
            return await self.client.files.list(**file_list.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def create(self, file_create: FileCreate) -> FileObject:
        try:
            return await self.client.files.create(**file_create.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def delete(self, file_delete: FileDelete) -> FileDeleted:
        try:
            return await self.client.files.delete(**file_delete.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def retrieve(self, file_retrieve: FileRetrieve) -> FileObject:
        try:
            return await self.client.files.retrieve(**file_retrieve.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def retrieve_content(self, file_content: FileContent) -> HttpxBinaryResponseContent:
        try:
            return await self.client.files.content(**file_content.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

