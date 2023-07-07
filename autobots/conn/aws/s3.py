from io import BytesIO
import boto3

from mypy_boto3_s3 import S3ServiceResource
from mypy_boto3_s3.type_defs import DeletedObjectTypeDef

from autobots.core.log import log
from autobots.core.settings import get_settings


class S3:

    def __init__(self):
        s3: S3ServiceResource = boto3.resource(
            service_name="s3",
            region_name=get_settings().AWS_S3_BUCKET_REGION,
            aws_access_key_id=get_settings().AWS_ACCESS_KEY_ID,
            aws_secret_access_key=get_settings().AWS_SECRET_ACCESS_KEY
        )
        self.bucket = s3.Bucket(get_settings().AWS_S3_BUCKET_NAME)

    async def put(self, data: str, filename: str) -> int:
        try:
            file_obj = BytesIO(data.encode('utf-8'))
            self.bucket.upload_fileobj(file_obj, filename)
            return len(data)
        except Exception as e:
            log.error(e)
        return -1

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
