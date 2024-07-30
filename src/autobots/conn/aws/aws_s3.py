from functools import lru_cache
from io import BytesIO
from typing import List, IO, Optional

import boto3
from botocore.response import StreamingBody
from loguru import logger

from mypy_boto3_s3 import S3ServiceResource
from mypy_boto3_s3.service_resource import ObjectSummary
from mypy_boto3_s3.type_defs import DeletedObjectTypeDef
from pydantic import HttpUrl

from src.autobots.core.settings import Settings, SettingsProvider


class AwsS3:

    def __init__(
            self,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str,
            object_prefix: str = ""
    ):
        s3: S3ServiceResource = boto3.resource(
            service_name="s3",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket = s3.Bucket(bucket_name)
        # self.s3 = s3
        # self.object_prefix = f"{object_prefix}" if object_prefix != "" else object_prefix
        self.object_prefix = None
        self.set_object_prefix(object_prefix)

    def set_object_prefix(self, object_prefix: str) -> None:
        if object_prefix.endswith("/"):
            self.object_prefix = object_prefix
        else:
            self.object_prefix = object_prefix + "/"

    async def put(self, data: str, filename: str) -> int:
        object_path = self.object_prefix + filename
        try:
            file_obj = BytesIO(data.encode('utf-8'))
            self.bucket.upload_fileobj(file_obj, object_path)
            return len(data)
        except Exception as e:
            logger.error(str(e))
        return -1

    async def put_file_obj(self, file_obj: BytesIO, filename: str) -> HttpUrl:
        """ TO BE DEPRECATED, use put_file_obj_v1 instead """
        object_path = self.object_prefix + filename
        try:
            length = len(file_obj.getvalue())
            self.bucket.upload_fileobj(file_obj, object_path)
            object_url = await self.get_https_url(object_path)
            logger.debug(f"File written to s3, filename: {object_url}, size: {length}")
            return object_url
        except Exception as e:
            logger.error(str(e))
        return ""

    async def upload_fileobj(self, file_obj: IO | StreamingBody | StreamingBody, filename: str) -> HttpUrl:
        """
        Uploads any file type
        """
        object_path = f"{self.object_prefix}{filename}"
        try:
            self.bucket.upload_fileobj(file_obj, object_path)
            object_url = await self.get_https_url(object_path)
            logger.debug(f"Fileobj written to s3, filename: {object_url}")
            return object_url
        except Exception as e:
            logger.error(str(e))
        return ""

    async def download_fileobj(self, filename: str, fileobj: IO | StreamingBody | StreamingBody) -> HttpUrl:
        """
        Downloads any file type
        """
        object_path = self.object_prefix + filename
        try:
            self.bucket.download_fileobj(object_path, fileobj)
            object_url = await self.get_https_url(object_path)
            logger.debug(f"Fileobj Downloaded, filename: {object_url}")
            return object_url
        except Exception as e:
            logger.error(str(e))
            raise

    async def get(self, filename: str) -> str:
        object_path = self.object_prefix + filename
        try:
            res_bytes = BytesIO()
            self.bucket.download_fileobj(object_path, res_bytes)
            res_data = res_bytes.getvalue().decode('utf-8')
            return res_data
        except Exception as e:
            logger.error(str(e))

    async def delete(self, filename: str) -> list[DeletedObjectTypeDef]:
        object_path = filename
        if filename and not filename.startswith(self.object_prefix):
            object_path = self.object_prefix + filename
        try:
            delete_res = self.bucket.delete_objects(Delete={
                "Objects": [
                    {
                        "Key": object_path
                    }
                ]
            })
            return delete_res["Deleted"]
        except Exception as e:
            logger.error(str(e))

    async def list(self, prefix: Optional[str] = None, limit: int = 300) -> List[ObjectSummary]:
        try:
            if prefix and not prefix.startswith(self.object_prefix):
                prefix = self.object_prefix + prefix
            else:
                prefix = self.object_prefix
            s3_objects = []
            size = 0
            for s3_object in self.bucket.objects.filter(Prefix=prefix):
                if size >= limit:
                    break
                size = size + 1
                s3_objects.append(s3_object)
            return s3_objects
        except Exception as e:
            logger.error(str(e))

    async def delete_prefix(self, prefix: str) -> List[DeletedObjectTypeDef]:
        if prefix and not prefix.startswith(self.object_prefix):
            prefix = self.object_prefix + prefix
        s3_objects = await self.list(prefix=prefix)
        deleted = []
        for s3_object in s3_objects:
            # partial_key = s3_object.key.replace(self.object_prefix, "")
            deleted_in_this_iter = await self.delete(s3_object.key)
            deleted += deleted_in_this_iter
        return deleted

    async def get_https_url(self, key: str) -> HttpUrl:
        """
        key is the complete object_path
        """
        return HttpUrl(f"https://{self.bucket.name}.s3.amazonaws.com/{key}")

    async def get_s3_uri(self, key: str) -> HttpUrl:
        """
        key is the complete object_path
        """
        return HttpUrl(f"s3://{self.bucket.name}/{key}")

    async def get_filename(self, key: str) -> str:
        """
        key is the s3 object_path
        """
        return key.split("/")[-1]


@lru_cache
def get_aws_s3(
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str,
        object_prefix: str = ""
) -> AwsS3:
    return AwsS3(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        bucket_name=bucket_name,
        object_prefix=object_prefix
    )


@lru_cache
def get_s3(settings: Settings = SettingsProvider.sget(), object_prefix: str = "") -> AwsS3:
    s3 = get_aws_s3(settings.AWS_S3_BUCKET_REGION, settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_BUCKET_NAME,
                    object_prefix)
    return s3


@lru_cache
def get_s3_for_image_upload(settings: Settings = SettingsProvider.sget(), object_prefix: str = "") -> AwsS3:

    s3 = get_aws_s3(settings.AWS_S3_BUCKET_REGION, settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_PUBLIC_BUCKET_NAME,
                    object_prefix)
    return s3


@lru_cache
def get_public_s3(settings: Settings = SettingsProvider.sget(), object_prefix: str = "") -> AwsS3:
    s3 = get_aws_s3(settings.AWS_S3_BUCKET_REGION, settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_PUBLIC_BUCKET_NAME,
                    object_prefix)
    return s3