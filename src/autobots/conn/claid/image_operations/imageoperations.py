import requests
from loguru import logger
from pydantic import ValidationError
import time
import re

from requests import Response

from src.autobots.conn.claid.claid import ClaidConfig
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidErrorResponse, ClaidResponse, \
    ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel
from typing import Any, Dict


class ClaidImageOperations:
    def __init__(self, claid_config: ClaidConfig):
        self.claid_config = claid_config

    def filter_null_values(self, obj: Any) -> Any:
        """
        Recursively filter out null values from the dictionary.
        """
        if isinstance(obj, dict):
            return {k: self.filter_null_values(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [self.filter_null_values(item) for item in obj]
        else:
            return obj

    async def bulk_edit(self, req: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse | Exception:
        claid_config = ClaidConfig()
        url = claid_config.claid_url + '/v1-beta1/image/edit/batch'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {claid_config.claid_apikey}"
        }

        input = req.input

        # Define a regular expression pattern to extract user_id and uuid
        pattern = r"app-myautobots-public-dev/claid/([^/]+)/([^/]+)/input/([^/]+)\.\w+"
        match = re.match(pattern, url)
        user_id = match.group(1)
        uuid = match.group(2)
        image_name = match.group(3)

        output = claid_config.s3_output_folder_url + user_id + '/' + uuid + '/output/'
        output_image_url = "https://app-myautobots-public-dev/claid/" + user_id + '/' + uuid + '/output/' + image_name
        output_image_url

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
            if response.data.status == 'ACCEPTED' or response.data.status == 'PROCESSING':
                retry_count = 0
                while True:
                    job_res: Response = await self.fetch_results_from_result_url(
                        response.data.result_url)

                    try:
                        job_response = ClaidResponse.model_validate(job_res.json())
                        if job_response.data.status == 'DONE':
                            return job_response

                        elif job_response.data.status == 'PROCESSING' or job_response.data.status == 'ACCEPTED':
                            continue

                    except Exception as e:
                        logger.error(f"Result fetch api is failing with exception: {e} and response : {job_res}")
                        return Exception(job_res)

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

    async def photoshoot(self,
                         req: ClaidPhotoShootInputModel) -> ClaidPhotoShootOutputModel | ClaidErrorResponse | Exception:
        url = self.claid_config.claid_url + '/v1-ea/scene/create'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.claid_config.claid_apikey}"
        }

        output = req.output.model_dump(exclude_none=True)
        object = req.object.model_dump(exclude_none=True)
        scene = req.scene.model_dump(exclude_none=True)
        request_payload = {
            "output": output,
            "object": object,
            "scene": scene
        }

        response: Response = requests.post(url, json=request_payload, headers=headers)
        response_content_json: Dict[str, Any] = response.json()

        result = Exception("Error during photoshoot")

        try:
            claid_error = ClaidErrorResponse(**response_content_json)
            return claid_error
        except ValidationError as e:
            result = Exception(str(e))

        if isinstance(result, Exception):
            try:
                claid_response = ClaidPhotoShootOutputModel(**response_content_json)
                return claid_response
            except ValidationError | TypeError | Exception as e:
                result = Exception(str(e))

        return result

    async def fetch_results_from_result_url(self, url: str) -> Response:
        claid_config = ClaidConfig()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {claid_config.claid_apikey}"
        }

        response: Response = requests.get(url, headers=headers)

        return response
