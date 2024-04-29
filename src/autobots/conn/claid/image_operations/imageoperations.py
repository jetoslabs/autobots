import requests
from loguru import logger
from pydantic import ValidationError
import time

from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidErrorResponse, ClaidResponse, \
    ClaidPhotoShootRequestModel, ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel
from typing import Optional, Any, Union
from pydantic import BaseModel, Field
from src.autobots.core.settings import SettingsProvider

class ClaidConfig(BaseModel):
    claid_apikey: Optional[str] = Field(default=SettingsProvider.sget().CLAID_API_KEY,
                                             description="Claid apikey used for request authorization.")
    claid_url: Optional[str] = Field(default="http://api.claid.ai",
                                             description="Claid URL used for request authorization.")
    s3_input_folder_url: str = Field(default=SettingsProvider.sget().CLAID_INPUT_FOLDER_S3_URI,
                                     description="S3 folder for input images")
    s3_output_folder_url: str = Field(default=SettingsProvider.sget().CLAID_OUTPUT_FOLDER_S3_URI,
                                     description="S3 folder for output images")
    s3_input_file_url: str = Field(default=SettingsProvider.sget().CLAID_INPUT_FILE_S3_URI,
                                     description="S3 folder for input image file")

def filterNullValues(obj: Any) -> Any:
    """
    Recursively filter out null values from the dictionary.
    """
    if isinstance(obj, dict):
        return {k: filterNullValues(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [filterNullValues(item) for item in obj]
    else:
        return obj

async def bulkEdit(req: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse:
    claidConfig = ClaidConfig()
    url = claidConfig.claid_url + '/v1-beta1/image/edit/batch'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {claidConfig.claid_apikey}"
    }

    input = claidConfig.s3_input_folder_url
    output = claidConfig.s3_output_folder_url


    operations = req.operations.dict(exclude_none=True)
    request_payload = {
        "input": input,
        "output": output,
        "operations": operations
    }


    response = requests.post(url, json=request_payload, headers=headers)
    response_json = response.json()
    try:
        response = ClaidResponse.model_validate(response_json)
        if(response.data.status == 'ACCEPTED' or response.data.status == 'PROCESSING' ):
            retry_count = 0
            while True:
                job_res: Union[ClaidResponse, ClaidErrorResponse] = await fetchResultsFromResultUrl(response.data.result_url)

                try:
                    job_response = ClaidResponse.model_validate(job_res.json())
                    if job_response.data.status == 'DONE':
                        return job_res

                    elif job_response.data.status == 'PROCESSING' or job_response.data.status == 'ACCEPTED':
                        continue

                except Exception as e:
                    logger.error(f"Result fetch api is failing with exception: {e} and response : {job_response}")
                    return job_response

                retry_count += 1
                if retry_count >= 15:  # Maximum of 5 retries
                    logger.error("Maximum retry limit reached")
                    break  # Exit the loop if maximum retry limit is reached
                logger.warning(f"Retrying fetchResultsFromResultUrl[Claid], attempt {retry_count}")
                time.sleep(15)

        else:
            logger.error(f"Claid bulkedit error: {response.status}")
            return response

    except (ValidationError, TypeError) as e:
        logger.error(f"Claid validation error for response: {response_json} : {e}")

    return response

async def photoshoot(req : ClaidPhotoShootInputModel) -> ClaidPhotoShootOutputModel| ClaidErrorResponse:
    claidConfig = ClaidConfig()
    url = claidConfig.claid_url + '/v1-ea/scene/create'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {claidConfig.claid_apikey}"
    }
    # Hardcoding input and output URLs for now
    if req.output is not None:
        req.output.destination = claidConfig.s3_output_folder_url
        req.output.format = "jpeg"

    if req.object is not None:
        req.object.image_url = claidConfig.s3_input_file_url

    output = req.output.dict(exclude_none=True)
    object = req.object.dict(exclude_none=True)
    scene = req.scene.dict(exclude_none=True)
    request_payload = {
        "output": output,
        "object": object,
        "scene": scene
    }

    response = requests.post(url, json=request_payload, headers=headers)

    try:
        response : ClaidPhotoShootOutputModel = ClaidPhotoShootOutputModel.model_validate(response.json())
        return response

    except ValidationError or TypeError as e:
        logger.error(f"Claid validtion error for response: {response} : {e}")

    return response


async def fetchResultsFromResultUrl(url: str) -> ClaidResponse | ClaidErrorResponse:
    claidConfig = ClaidConfig()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {claidConfig.claid_apikey}"
    }

    response : ClaidResponse | ClaidErrorResponse = requests.get(url, headers=headers)
    return response











