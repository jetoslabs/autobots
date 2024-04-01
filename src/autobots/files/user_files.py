import os
from typing import List, Optional

from fastapi import UploadFile
from loguru import logger
from pydantic import HttpUrl

from src.autobots.conn.aws.aws_s3 import AwsS3
from src.autobots.core.settings import Settings, SettingsProvider
from src.autobots.user.user_orm_model import UserORM


class UserFiles:

    def __init__(self, user: UserORM, s3: AwsS3, settings: Settings = SettingsProvider.sget()):
        self._user = user
        self._s3 = s3
        _s3_obj_prefix = f"{settings.AWS_S3_FILES_FOLDER}/{str(user.id)}/"
        self._s3.set_object_prefix(_s3_obj_prefix)
        self._download_path = f"{settings.TEMPORARY_DIR}/{_s3_obj_prefix}"

    async def upload_files(self, files: List[UploadFile]) -> List[HttpUrl]:
        assert str(self._user.id) in self._s3.object_prefix
        uploaded_files = []
        for upload_file in files:
            uploaded_file = await self._s3.upload_fileobj(upload_file.file, upload_file.filename)
            uploaded_files.append(uploaded_file)
        return uploaded_files

    async def download_files(self, filenames: List[str]) -> list[str]:
        assert str(self._user.id) in self._s3.object_prefix
        assert str(self._user.id) in self._download_path

        if not os.path.exists(f"{self._download_path}"):
            os.makedirs(f"{self._download_path}")

        download_path_filenames = []
        for filename in filenames:
            try:
                download_path_filename = f"{self._download_path}{filename}"
                with open(download_path_filename, "wb") as file:
                    downloaded = await self._s3.download_fileobj(filename, file)
                    assert downloaded
                    download_path_filenames.append(download_path_filename)
            except Exception as e:
                logger.error(str(e))
        return download_path_filenames

    async def list_files(self, prefix: Optional[str] = None) -> List[str]:
        assert str(self._user.id) in self._s3.object_prefix
        files = []
        object_summaries = await self._s3.list(prefix)
        for object_summary in object_summaries:
            files.append(object_summary.key)
        return files

    async def delete_files(self, filenames: List[str]) -> List[str]:
        assert str(self._user.id) in self._s3.object_prefix
        objects = []
        for filename in filenames:
            deleted = await self._s3.delete(filename)
            for deleted_object in deleted:
                objects.append(deleted_object.get("Key"))
        logger.info(f"Deleted files from S3: {objects}")
        return objects

    async def delete_downloaded_files(self, filenames: List[str]) -> List[str]:
        assert str(self._user.id) in self._download_path
        objects = []
        for filename in filenames:
            filepath = f"{self._download_path}{filename}"
            if os.path.isfile(filepath):
                os.remove(filepath)
                objects.append(filepath)
        logger.info(f"Deleted files from file system: {objects}")
        return objects

