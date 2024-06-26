import os
import random
import string
from typing import List, Dict, Callable, AsyncGenerator

from fastapi import UploadFile
from loguru import logger
from pinecone import QueryResponse
from pydantic import BaseModel, HttpUrl
from retry import retry

from src.autobots.conn.aws.s3 import S3
from src.autobots.conn.pinecone.pinecone import Pinecone
from src.autobots.conn.selenium.selenium import get_selenium, Selenium
from src.autobots.core.settings import SettingsProvider
from src.autobots.conn.unstructured_io.unstructured_io import UnstructuredIO, PartitionParametersParams
from src.autobots.core.utils import gen_hash, gen_random_str
from src.autobots.datastore.data_provider import DataProvider
from src.autobots.event_result.event_result_model import EventResultStatus


class DataModel(BaseModel):
    data: str
    meta: Dict[str, str]


class DatastoreResult(BaseModel):
    resource: str
    status: EventResultStatus


class Datastore:
    """
    DataStore will store data s3 and embedding in pinecone
    Each datastore will have unique path in S3 to store data
    Each datastore will have unique namespace in pinecone
    """

    def __init__(self,
                 s3: S3,
                 pinecone: Pinecone,
                 unstructured: UnstructuredIO,
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
    ) -> List[DatastoreResult]:
        """
        Store data
        :return:
        """
        result = []
        try:
            async for chunk in DataProvider.create_data_chunks(data, chunk_func, chunk_token_size):
                await self._put_data(data=chunk)
                await self._put_embedding(data=chunk)
            result.append(DatastoreResult(resource=data, status=EventResultStatus.success))
        except Exception as e:
            logger.error(f"Error processing data {str(e)}")
            result.append(DatastoreResult(resource=data, status=EventResultStatus.error))
        return result

    async def put_files(self, files: List[UploadFile], partition_parameters_params: PartitionParametersParams) -> List[DatastoreResult]:
        result = []
        for file in files:
            datastore_result = await self.put_file(file, partition_parameters_params)
            result.append(datastore_result)
            # try:
            #     logger.debug(f"Processing file: {file.filename}")
            #     file_chunks: List[str] = await self.unstructured.get_file_chunks(file, chunk_size=chunk_size)
            #     logger.debug(f"Total chunks in file: {file.filename} is {len(file_chunks)}")
            #     await self._put_file_chunks(file, file_chunks)
            #     result.append(DatastoreResult(resource=file.filename, status=EventResultStatus.success))
            # except Exception as e:
            #     logger.error(f"Error: {str(e)} while putting file: {file.filename}")
            #     result.append(DatastoreResult(resource=file.filename, status=EventResultStatus.error))
        return result

    @retry(exceptions=Exception, tries=3, delay=30)
    async def put_file(self, file: UploadFile, partition_parameters_params: PartitionParametersParams) -> DatastoreResult:
        datastore_result: DatastoreResult
        try:
            logger.debug(f"Processing file: {file.filename}")
            file_chunks: List[str] = await self.unstructured.get_file_chunks(file, partition_parameters_params)
            logger.debug(f"Total chunks in file: {file.filename} is {len(file_chunks)}")
            await self._put_file_chunks(file, file_chunks)
            datastore_result = DatastoreResult(resource=file.filename, status=EventResultStatus.success)
        except Exception as e:
            logger.error(f"Error: {str(e)} while putting file: {file.filename}")
            datastore_result = DatastoreResult(resource=file.filename, status=EventResultStatus.error)
            raise
        return datastore_result

    async def put_urls(self,
                       urls: List[HttpUrl],
                       partition_parameters_params: PartitionParametersParams,
                       chunk_func: Callable[[str], AsyncGenerator[str, None]] = DataProvider.read_data_line_by_line,
                       ) -> List[DatastoreResult]:
        result = []
        # create new temp directory
        path = "./to_del"
        if not os.path.exists(path):
            os.mkdir(path)
        web_scraper: Selenium = get_selenium()
        # fetch html for each url
        for url in urls:
            # build filename
            full_path_name = f"{path}/{url.path.replace('/', '_')}_{gen_random_str(5)}.html"
            try:
                logger.debug(f"Processing URL: {url}")
                # web scrape html data
                html_data = await web_scraper.read_url(url)
                # write html to file
                with open(full_path_name, "w+b") as file:
                    # Write str to file
                    file.write(bytes(html_data, encoding='utf-8'))
                # put file in datastore
                with open(full_path_name, "rb") as file:
                    await self.put_files(
                        files=[UploadFile(filename=full_path_name, file=file)],
                        partition_parameters_params=partition_parameters_params
                    )
                result.append(DatastoreResult(resource=str(url), status=EventResultStatus.success))
            except Exception as e:
                logger.error(f"Error: processing URL: {str(url)}, error: {str(e)}")
                result.append(DatastoreResult(resource=str(url), status=EventResultStatus.error))
            finally:
                # delete file
                os.remove(full_path_name)
        return result

    async def _put_file_chunks(self, file: UploadFile, file_chunks: List[str]):
        loop = 0
        for chunk in file_chunks:
            try:
                await self._put_data(data=chunk)
                await self._put_embedding(data=chunk)
                # housekeeping
                loop = loop + 1
                logger.debug(f"Processed chunk: {loop}/{len(file_chunks)} of file {file.filename}")
                logger.trace(f"Processed file chunk: {file.filename} - {chunk}")
            except Exception as e:
                logger.error(str(e))

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
        query_res: QueryResponse = await self.pinecone.query(
            data=query,
            top_k=top_k,
            namespace=self._get_pinecone_namespace()
        )
        query_results = query_res.get("matches")
        for query_result in query_results:
            data = await self.s3.get(f"{self._get_s3_basepath()}/{query_result.id}")
            result.append(data)
        return result

    async def empty_and_close(self):
        # delete namespace in pinecone
        deleted_embeddings = await self.pinecone.delete_all(namespace=self._get_pinecone_namespace())  # noqa: F841
        # delete folder in s3
        deleted_objects = await self.s3.delete_prefix(prefix=self._get_s3_basepath())  # noqa: F841
