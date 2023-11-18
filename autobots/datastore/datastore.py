import random
import string
from typing import List, Dict, Callable, AsyncGenerator

from fastapi import UploadFile
from pinecone import QueryResult
from pydantic import BaseModel, HttpUrl

from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.conn.selenium.selenium import get_selenium, Selenium
from autobots.core.settings import SettingsProvider
from autobots.conn.unstructured_io.unstructured_io import get_unstructured_io, UnstructuredIO
from autobots.core.log import log
from autobots.core.utils import gen_hash
from autobots.datastore.data_provider import DataProvider


class DataModel(BaseModel):
    data: str
    meta: Dict[str, str]


class Datastore:
    """
    DataStore will store data s3 and embedding in pinecone
    Each datastore will have unique path in S3 to store data
    Each datastore will have unique namespace in pinecone
    """

    def __init__(self,
                 s3: S3 = get_s3(),
                 pinecone: Pinecone = get_pinecone(),
                 unstructured: UnstructuredIO = get_unstructured_io(),
                 # web_scraper: Selenium = get_selenium()
                 ):
        self.name = None
        self.trace = None
        self.id = None
        self.s3 = s3
        self.pinecone = pinecone
        self.unstructured = unstructured

    def init(self, name: str):
        self.name = name
        self.trace = ''.join(random.choices(string.hexdigits, k=9))
        # Id for the datastore is unique identifier for the datastore
        self.id = f"{self.name}-{self.trace}"
        return self

    def hydrate(self, datastore_id: str):
        self.id = datastore_id
        # Get Trace from datastore_id
        self.trace = datastore_id.split("-")[-1]
        # Get name from datastore_id
        self.name = datastore_id.replace(f"-{self.trace}", "")
        return self

    def _datastore_identifier(self) -> str:
        return SettingsProvider.sget().DATASTORE_IDENTIFIER

    def _get_s3_basepath(self) -> str:
        return f"{self._datastore_identifier()}/{self.id}"

    def _get_pinecone_namespace(self) -> str:
        return f"{self._datastore_identifier()}/{self.id}"

    async def _put_data(self, data: str):
        await self.s3.put(data=data, filename=f"{self._get_s3_basepath()}/{gen_hash(data)}")

    async def _put_embedding(self, data: str):
        await self.pinecone.upsert_data(
            gen_hash(data),
            data=data, metadata={},
            namespace=self._get_pinecone_namespace()
        )

    async def put_data(
            self,
            data: str,
            chunk_func: Callable[[str], AsyncGenerator[str, None]] = DataProvider.read_data_line_by_line,
            chunk_token_size: int = 512
    ):
        """
        Store data
        :return:
        """
        async for chunk in DataProvider.create_data_chunks(data, chunk_func, chunk_token_size):
            await self._put_data(data=chunk)
            await self._put_embedding(data=chunk)

    # async def put_file(
    #         self,
    #         filename: str,
    #         chunk_func: Callable[[str], AsyncGenerator[str, None]] = DataProvider.read_file_line_by_line,
    #         chunk_token_size: int = 512
    # ):
    #
    #     async for chunk in DataProvider.create_file_chunks(filename, chunk_func, chunk_token_size):
    #         await self._put_data(data=chunk)
    #         await self._put_embedding(data=chunk)

    # TODO: use SpooledTemporaryFile instead of Uploadfile
    async def put_files(self, files: List[UploadFile], chunk_size: int = 500):
        for file in files:
            log.debug(f"Processing file: {file.filename}")
            file_chunks: List[str] = await self.unstructured.get_file_chunks(file, chunk_size=chunk_size)
            log.debug(f"Sum of chunks in file: {file.filename} is {len(file_chunks)}")
            await self._put_file_chunks(file, file_chunks)

    async def put_urls(self,
                       urls: List[HttpUrl],
                       chunk_func: Callable[[str], AsyncGenerator[str, None]] = DataProvider.read_data_line_by_line,
                       chunk_token_size: int = 512
                       ):
        web_scraper: Selenium = get_selenium()
        for url in urls:
            log.debug(f"Processing URL: {url}")
            url_data = await web_scraper.read_url_text(url)
            await self.put_data(url_data, chunk_func, chunk_token_size)

    async def _put_file_chunks(self, file: UploadFile, file_chunks: List[str]):
            loop = 0
            for chunk in file_chunks:
                try:
                    await self._put_data(data=chunk)
                    await self._put_embedding(data=chunk)
                    # housekeeping
                    loop = loop + 1
                    log.debug(f"Processed chunk: {loop}/{len(file_chunks)} of file {file.filename}")
                    log.trace(f"Processed file chunk: {file.filename} - {chunk}")
                except Exception as e:
                    log.exception(str(e))

    # async def get(self):
    #     """
    #     Retrieve data
    #     :return:
    #     """
    #     pass

    async def search(self, query: str, top_k: int = 10) -> List[str]:
        """
        Semantic search data
        :return:
        """
        result = []
        query_results: List[QueryResult] = await self.pinecone.query(
            data=query,
            top_k=top_k,
            namespace=self._get_pinecone_namespace()
        )
        for query_result in query_results:
            data = await self.s3.get(f"{self._get_s3_basepath()}/{query_result.id}")
            result.append(data)
        return result

    async def empty_and_close(self):
        # delete namespace in pinecone
        deleted_embeddings = await self.pinecone.delete_all(namespace=self._get_pinecone_namespace())
        # delete folder in s3
        deleted_objects = await self.s3.delete_prefix(prefix=self._get_s3_basepath())
