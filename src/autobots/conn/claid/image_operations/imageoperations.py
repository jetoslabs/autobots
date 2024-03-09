import requests
from loguru import logger
from pydantic import ValidationError

from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidErrorResponse, ClaidResponse
from typing import Optional, Any
from pydantic import BaseModel, Field
from src.autobots.core.settings import SettingsProvider

class ClaidConfig(BaseModel):
    claid_apikey: Optional[str] = Field(default=SettingsProvider.sget().CLAID_API_KEY,
                                             description="Claid apikey used for request authorization.")
    claid_url: Optional[str] = Field(default="http://api.claid.ai",
                                             description="Claid URL used for request authorization.")

def filter_null_values(obj: Any) -> Any:
    """
    Recursively filter out null values from the dictionary.
    """
    if isinstance(obj, dict):
        return {k: filter_null_values(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [filter_null_values(item) for item in obj]
    else:
        return obj

async def bulkEdit(req: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse:
    claidConfig = ClaidConfig()
    url = claidConfig.claid_url + '/v1-beta1/image/edit/batch'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {claidConfig.claid_apikey}"
    }

    # Hardcoding input and output URLs for now
    input_url = 'storage://mystorage/input/'
    output_url = 'storage://mystorage/output/'

    operations = req.operations.dict(exclude_none=True)
    request_payload = {
        "input": input_url,
        "operations": operations,
        "output": output_url
    }

    response = requests.post(url, json=request_payload, headers=headers)
    response_json = response.json()
    try:
        err = ClaidResponse.model_validate(response_json)
        return err
    except ValidationError or TypeError as e:
        logger.error(f"Claid validtion error for response: {response_json} : {e}")

    return response









