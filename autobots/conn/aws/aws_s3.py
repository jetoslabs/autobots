from functools import lru_cache
from io import BytesIO
from typing import List

import boto3

from mypy_boto3_s3 import S3ServiceResource
from mypy_boto3_s3.service_resource import ObjectSummary
from mypy_boto3_s3.type_defs import DeletedObjectTypeDef
from pydantic import HttpUrl

from autobots.core.log import log


class AwsS3:

    def __init__(
            self,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str
    ):
        s3: S3ServiceResource = boto3.resource(
            service_name="s3",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket = s3.Bucket(bucket_name)

    async def put(self, data: str, filename: str) -> int:
        try:
            file_obj = BytesIO(data.encode('utf-8'))
            self.bucket.upload_fileobj(file_obj, filename)
            return len(data)
        except Exception as e:
            log.error(e)
        return -1

    async def put_file_obj(self, file_obj: BytesIO, filename: str) -> HttpUrl:
        try:
            length = len(file_obj.getvalue())
            self.bucket.upload_fileobj(file_obj, filename)
            object_url = await self.get_object_url(filename)
            log.debug(f"File written to s3, filename: {object_url}, size: {length}")
            return object_url
        except Exception as e:
            log.error(e)
        return ""

    async def get(self, filename: str) -> str:
        try:
            res_bytes = BytesIO()
            self.bucket.download_fileobj(filename, res_bytes)
            res_data = res_bytes.getvalue().decode('utf-8')
            return res_data
        except Exception as e:
            log.error(e)

    async def delete(self, filename: str) -> list[DeletedObjectTypeDef]:
        try:
            delete_res = self.bucket.delete_objects(Delete={
                "Objects": [
                    {
                        "Key": filename
                    }
                ]
            })
            return delete_res["Deleted"]
        except Exception as e:
            log.error(e)

    async def list(self, prefix: str, limit: int = 300) -> List[ObjectSummary]:
        s3_objects = []
        size = 0
        for s3_object in self.bucket.objects.filter(Prefix=prefix):
            if size >= limit:
                break
            size = size + 1
            s3_objects.append(s3_object)
        return s3_objects

    async def delete_prefix(self, prefix: str):
        s3_objects = await self.list(prefix=prefix)
        for s3_object in s3_objects:
            await self.delete(s3_object.key)

    async def get_object_url(self, key: str) -> HttpUrl:
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
