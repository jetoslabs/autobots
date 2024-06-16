from functools import lru_cache
from typing import List

from pydantic import HttpUrl

from src.autobots.conn.aws.aws_s3 import get_public_s3, AwsS3
from src.autobots.conn.claid.claid_config_model import ClaidConfig
from src.autobots.conn.claid.claid_model import ClaidBulkEditRequestModel, ClaidErrorResponse, ClaidBulkEditResponse, \
    ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel
from src.autobots.conn.claid.image_operations.imageoperations import ClaidImageOperations
from src.autobots.core.settings import Settings, SettingsProvider


class Claid:

    def __init__(self, claid_config: ClaidConfig, s3: AwsS3):
        self.claid_config = claid_config
        self.s3 = s3
        self.image_operations = ClaidImageOperations(claid_config)

    async def photoshoot(self, req: ClaidPhotoShootInputModel) -> List[HttpUrl] | ClaidErrorResponse | Exception:
        res = await self.image_operations.photoshoot(req)
        if isinstance(res, ClaidPhotoShootOutputModel):
            s3_https_output_folder = req.output.destination.replace(self.claid_config.claid_side_s3_bucket, "")
            obj_summaries = await self.s3.list(prefix=s3_https_output_folder)
            output_image_urls = [f"{self.claid_config.https_path_s3_bucket}{obj_summary.key}" for obj_summary in obj_summaries]
            return output_image_urls
        return res

    async def bulk_edit(self, req: ClaidBulkEditRequestModel) -> ClaidBulkEditResponse | ClaidErrorResponse | Exception:
        res = await self.image_operations.bulk_edit(req)
        return res


@lru_cache
def get_claid(settings: Settings = SettingsProvider.sget()) -> Claid:
    claid_config = ClaidConfig(
        claid_apikey=settings.CLAID_API_KEY,
        claid_side_s3_bucket=settings.CLAID_SIDE_S3_BUCKET,
        https_path_s3_bucket=f"https://{settings.AWS_S3_PUBLIC_BUCKET_NAME}.s3.{settings.AWS_S3_BUCKET_REGION}.amazonaws.com/",
        claid_side_folder_url_prefix=settings.CLAID_PATH_PREFIX,
    )
    return Claid(
        claid_config=claid_config,
        s3=get_public_s3(object_prefix=settings.CLAID_PATH_PREFIX),
    )
