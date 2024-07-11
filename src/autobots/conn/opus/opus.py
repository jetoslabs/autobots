import requests
from fastapi import APIRouter
from loguru import logger
from pydantic import HttpUrl, BaseModel, Field

import json
from typing import Optional, Any
from src.autobots.core.settings import Settings, SettingsProvider
from functools import lru_cache

from src.autobots.exception.app_exception import AppException

router = APIRouter()


class Video2VideoReqModel(BaseModel):
    url: Optional[str] = Field(default=None, description="")


class OpusRes(BaseModel):
    url: HttpUrl


# Replace with your actual API key
class Opus:
    CREATE_CLIP_URL = 'https://api.opus.pro/api/ClipProject'
    RETRIEVE_CLIP_URL = 'https://api.opus.pro/api/ExportableClip'

    def __init__(self, key: str):
        self.key = key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}'
        }

    # API endpoint for creating a clip
    def create_clip(self, req: Video2VideoReqModel) -> Any | Exception:
        try:
            # Example payload data
            payload = {
                'videoUrl': req.url,
                "brandTemplateId": "your_brand_template_id_here",  # Replace with your actual brand template ID
                "conclusionActions": [
                    {
                        "type": "WEBHOOK",
                        "notifyFailure": True,
                        "url": ""
                        # TODO Pass correct url for webhook to work
                    }
                ],
                "curationPref": {
                    "rangeZ": {
                        "startSec": 30,
                        "endSec": 60
                    },
                    "clipDurations": [
                        [30, 60]
                    ],
                    "topicKeywords": ["example_keyword1", "example_keyword2"]
                }
            }

            # Set the self.headers, including the API key for authentication

            # Make the POST request to create a new clip
            response = requests.post(Opus.CREATE_CLIP_URL, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()

            # Check the response status code
            if response.status_code == 200:
                # Parse and print the response JSON data
                logger.info("Clip created successfully:")
                # print(json.dumps(response_data, indent=4))
                return response_data['id']
            else:
                # Print an error message if the request failed
                raise AppException(detail=response_data, http_status=response.status_code)
        except Exception as e:
            logger.error(str(e))
            return e

    def query_clip(self, project_id: str):

        # Define the API endpoint and token
        url = f"https://api.opus.pro/api/ClipProject/{project_id}"

        # Make the GET request
        response = requests.get(url, headers=self.headers)

        # Handle the response
        return response.json()

    def get_result_clip(self, project_id: str) -> OpusRes | Exception:
        # API endpoint for retrieving a clip
        params = {'projectId': project_id}
        # Make the GET request to retrieve the clip details
        response = requests.get(Opus.RETRIEVE_CLIP_URL, headers=self.headers, params=params)
        response_data = response.json()
        # Check the response status code
        if response.status_code == 200:
            # Parse and print the response JSON data
            if len(response_data) == 0:
                logger.error(f"Failed to retrieve clip. Response is empty. Status code: {response.status_code}")
                return AppException(detail="Failed to retrieve clip. Response is empty.", http_status=response.status_code)
            logger.info("Clip details retrieved successfully:")
            return OpusRes(url=response_data[0]['uriForPreview'])
        else:
            # Print an error message if the request failed
            logger.error(f"Failed to retrieve clip. Status code: {response.status_code}")
            return AppException(detail="Failed to retrieve clip.", http_status=response.status_code)


# @router.post("/opus")
# async def handle_conclusion_actions_callback(request: Request):
#     try:
#         payload = await request.json()
#     # Extract ClipProjectStage
#         clip_project_stage = payload.get("stage")
#         project_id = payload.get("id")

#         # Check if ClipProjectStage is COMPLETE
#         if clip_project_stage == "COMPLETE":
#             # Call Get Result Clip API
#             result = get_result_clip(project_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
@lru_cache
def get_opus_video(settings: Settings = SettingsProvider.sget()) -> Opus:
    return Opus(settings.OPUS_API_KEY)
