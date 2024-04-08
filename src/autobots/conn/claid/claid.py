from functools import lru_cache
from typing import  Union
import json
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidErrorResponse, ClaidResponse, \
    ClaidPhotoShootRequestModel, ClaidPhotoShootOutputModel
from src.autobots.conn.claid.image_operations.imageoperations import bulkEdit, photoshoot


class UseClaidAiApi:

    async def bulkEdit(self, req: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse:

        res: ClaidResponse | ClaidErrorResponse = await bulkEdit(req)
        response = ClaidResponse.model_validate(json.loads(res.text))
        return response

    async def photoshoot(self, req: ClaidPhotoShootRequestModel) -> ClaidPhotoShootOutputModel | ClaidErrorResponse :

        res: Union[ClaidPhotoShootOutputModel | ClaidErrorResponse] = await photoshoot(req)
        return res
@lru_cache
def get_calid_ai() -> UseClaidAiApi:
    return UseClaidAiApi()
