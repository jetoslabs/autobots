import requests
import time
from pydantic import ValidationError

from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, ClaidErrorResponse
from loguru import logger
from typing import Optional
from pydantic import BaseModel, Field
from src.autobots.core.settings import SettingsProvider

class ClaidConfig(BaseModel):
    claid_apikey: Optional[str] = Field(default=SettingsProvider.sget().CLAID_API_KEY,
                                             description="Claid apikey used for request authorization.")
    claid_url: Optional[str] = Field(default="http://api.claid.ai",
                                             description="Claid URL used for request authorization.")

async def bulkImaginEdit(req: ClaidRequestModel) -> ClaidResponseData | ClaidErrorResponse:
    claidConfig = ClaidConfig()
    url = claidConfig.useapi_net_endpoint_url + '/v1-beta1/image/edit/batch'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {claidConfig.claid_apikey}"
    }

    # hardcoding a input s3 bucket we will chage it to pass client specific buckets later on
    req.input = 's3://akhil-bucket1/input/'
    response = requests.post(url, json=req.json())
    return response









