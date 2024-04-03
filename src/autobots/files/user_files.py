import os
from typing import List, Optional, AsyncIterator

import werkzeug
from fastapi import UploadFile, HTTPException
from loguru import logger

from src.autobots.conn.aws.aws_s3 import AwsS3
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
from src.autobots.core.settings import Settings, SettingsProvider
from src.autobots.files.user_files_model import FilesAndProcessingParams
from src.autobots.user.user_orm_model import UserORM


class UserFiles:

    def __init__(self, user: UserORM, s3: AwsS3, setting: Settings = SettingsProvider.sget()):
        self._user = user
        self._s3 = s3
        _s3_obj_prefix = f"{setting.AWS_S3_FILES_FOLDER}/{str(user.id)}/"
        self._s3.set_object_prefix(_s3_obj_prefix)
        self._download_path = f"{setting.TEMPORARY_DIR}/{_s3_obj_prefix}"
        self.unstructured = get_unstructured_io()

    async def upload_files(self, files: List[UploadFile]) -> List[str]:
        assert str(self._user.id) in self._s3.object_prefix
        uploaded_files = []
        for upload_file in files:
            secure_filename = await self.secure_filename(upload_file.filename)
            uploaded_file = await self._s3.upload_fileobj(upload_file.file, secure_filename)
            if uploaded_file:
                uploaded_files.append(secure_filename)
        return uploaded_files

    async def list_files(self, prefix: Optional[str] = None) -> List[str]:
        assert str(self._user.id) in self._s3.object_prefix
        secure_prefix = await self.secure_filename(prefix)
        files = []
        object_summaries = await self._s3.list(secure_prefix)
        for object_summary in object_summaries:
            filename = await self._s3.get_filename(object_summary.key)
            files.append(filename)
        return files

    async def delete_files(self, filenames: List[str]) -> List[str]:
        assert str(self._user.id) in self._s3.object_prefix
        objects = []
        for filename in filenames:
            secure_filename = await self.secure_filename(filename)
            deleted = await self._s3.delete(secure_filename)
            for deleted_object in deleted:
                deleted_key = deleted_object.get("Key")
                deleted_filename = await self._s3.get_filename(deleted_key)
                objects.append(deleted_filename)
        logger.info(f"Deleted files from S3: {objects}")
        return objects

    async def processed_file_and_yield(self, files_and_processing_params: FilesAndProcessingParams) -> AsyncIterator[
        str]:
        for file_and_params in files_and_processing_params.files_and_params:
            async for download_path_filename in self.download_file_and_yield([file_and_params.filename]):
                with open(download_path_filename, "rb") as downloaded_file:
                    secure_filename = await self.secure_filename(downloaded_file.name)
                    file = UploadFile(filename=secure_filename, file=downloaded_file)
                    chunks = await self.unstructured.get_file_chunks(file, file_and_params.processing_params)
                    processed = f"########\nFilename: {secure_filename}\nContent:\n" + " ".join(chunks) + "\n\n"
                    logger.info(f"Processed file: {secure_filename}")
                    yield processed

    async def download_file_and_yield(self, filenames: List[str]) -> AsyncIterator[str]:
        assert str(self._user.id) in self._s3.object_prefix
        assert str(self._user.id) in self._download_path

        if not os.path.exists(f"{self._download_path}"):
            os.makedirs(f"{self._download_path}")

        for filename in filenames:
            secure_filename = await self.secure_filename(filename)
            try:
                download_path_filename = f"{self._download_path}{secure_filename}"
                with open(download_path_filename, "wb") as file:
                    downloaded = await self._s3.download_fileobj(secure_filename, file)
                    assert downloaded
                    logger.info(f"Downloaded file to file system: {download_path_filename}")
                    yield download_path_filename

                await self.delete_downloaded_files([secure_filename])
            except Exception as e:
                logger.error(str(e))

    async def delete_downloaded_files(self, filenames: List[str]) -> List[str]:
        assert str(self._user.id) in self._download_path
        objects = []
        for filename in filenames:
            secure_filename = await self.secure_filename(filename)
            filepath = f"{self._download_path}{secure_filename}"
            if os.path.isfile(filepath):
                os.remove(filepath)
                objects.append(filepath)
            logger.info(f"Deleted file from file system: {filepath}")
        return objects

    async def secure_filename(self, filename: str | None) -> str | None:
        try:
            if filename:
                assert "/" not in filename or "\\" not in filename
                assert ".." not in filename
                filename_parts = filename.split(".")
                assert len(filename_parts) == 2
                secure_filename = werkzeug.utils.secure_filename(filename)
                return secure_filename
        except Exception:
            logger.error(f"Assertion Error while checking if filename is secure, filename: {filename}")
            raise HTTPException(status_code=400, detail="Filename cannot have / or \\ or .. or .")
