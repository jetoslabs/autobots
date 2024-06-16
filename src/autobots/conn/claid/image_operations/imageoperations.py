import asyncio

import requests
from loguru import logger
from pydantic import ValidationError

from requests import Response

from src.autobots.conn.claid.claid import ClaidConfig
from src.autobots.conn.claid.claid_model import ClaidBulkEditRequestModel, ClaidErrorResponse, ClaidBulkEditResponse, \
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

    async def bulk_edit(self, req: ClaidBulkEditRequestModel) -> ClaidBulkEditResponse | ClaidErrorResponse | Exception:
        url = self.claid_config.claid_url + '/v1-beta1/image/edit/batch'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.claid_config.claid_apikey}"
        }

        request = req.model_dump(exclude_none=True)
        response = requests.post(url, json=request, headers=headers)
        response_json = response.json()
        if response.status_code == 200:
            try:
                response = ClaidBulkEditResponse.model_validate(response_json)
                job_res: Response = await self.fetch_results_from_result_url(response.data.result_url)
                job_response = ClaidBulkEditResponse.model_validate(job_res.json())
                while job_response.data.status == 'ACCEPTED' or job_response.data.status == 'PROCESSING':
                    job_res: Response = await self.fetch_results_from_result_url(response.data.result_url)
                    job_response = ClaidBulkEditResponse.model_validate(job_res.json())
                    await asyncio.sleep(5)
                return job_response
            except Exception as e:
                logger.error(e)
                return e
        else:
            response = ClaidErrorResponse.model_validate(response_json)
            return response

    async def photoshoot(self,
                         req: ClaidPhotoShootInputModel) -> ClaidPhotoShootOutputModel | ClaidErrorResponse | Exception:
        url = self.claid_config.claid_url + '/v1-ea/scene/create'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.claid_config.claid_apikey}"
        }

        request_payload = {}
        if req.output:
            output_dict = req.output.model_dump(exclude_none=True)
            request_payload['output'] = output_dict
        if req.object:
            object_dict = req.object.model_dump(exclude_none=True)
            request_payload['object'] = object_dict
        if req.scene:
            scene_dict = req.scene.model_dump(exclude_none=True)
            request_payload['scene'] = scene_dict

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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.claid_config.claid_apikey}"
        }

        response: Response = requests.get(url, headers=headers)

        return response
