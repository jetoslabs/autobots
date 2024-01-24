from functools import lru_cache
from io import BytesIO
from typing import List

import boto3

from mypy_boto3_s3 import S3ServiceResource
from mypy_boto3_s3.service_resource import ObjectSummary
from mypy_boto3_s3.type_defs import DeletedObjectTypeDef
from pydantic import HttpUrl

from src.autobots.core.logging.log import Log
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
        self.object_prefix = f"{object_prefix}/" if object_prefix != "" else object_prefix
        self.bucket = s3.Bucket(bucket_name)

    async def put(self, data: str, filename: str) -> int:
        object_path = self.object_prefix + filename
        try:
            file_obj = BytesIO(data.encode('utf-8'))
            self.bucket.upload_fileobj(file_obj, object_path)
            return len(data)
        except Exception as e:
            Log.error(str(e))
        return -1

    async def put_file_obj(self, file_obj: BytesIO, filename: str) -> HttpUrl:
        object_path = self.object_prefix + filename
        try:
            length = len(file_obj.getvalue())
            self.bucket.upload_fileobj(file_obj, object_path)
            object_url = await self.get_object_url(object_path)
            Log.debug(f"File written to s3, filename: {object_url}, size: {length}")
            return object_url
        except Exception as e:
            Log.error(str(e))
        return ""

    async def get(self, filename: str) -> str:
        object_path = self.object_prefix + filename
        try:
            res_bytes = BytesIO()
            self.bucket.download_fileobj(object_path, res_bytes)
            res_data = res_bytes.getvalue().decode('utf-8')
            return res_data
        except Exception as e:
            Log.error(str(e))

    async def delete(self, filename: str) -> list[DeletedObjectTypeDef]:
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
            Log.error(str(e))

    async def list(self, prefix: str, limit: int = 300) -> List[ObjectSummary]:
        prefix = self.object_prefix + prefix
        s3_objects = []
        size = 0
        for s3_object in self.bucket.objects.filter(Prefix=prefix):
            if size >= limit:
                break
            size = size + 1
            s3_objects.append(s3_object)
        return s3_objects

    async def delete_prefix(self, prefix: str):
        prefix = self.object_prefix + prefix
        s3_objects = await self.list(prefix=prefix)
        for s3_object in s3_objects:
            await self.delete(s3_object.key)

    async def get_object_url(self, key: str) -> HttpUrl:
        """
        key is the complete object_path
        """
        return HttpUrl(f"https://{self.bucket.name}.s3.amazonaws.com/{key}")


@lru_cache
def get_aws_s3(
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str
) -> AwsS3:
    return AwsS3(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        bucket_name=bucket_name
    )

@lru_cache
def get_public_s3(settings: Settings = SettingsProvider.sget()) -> AwsS3:
    s3 = get_aws_s3(settings.AWS_S3_BUCKET_REGION, settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_PUBLIC_BUCKET_NAME)
    return s3

