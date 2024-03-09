from functools import lru_cache

from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidErrorResponse, ClaidResponse
from src.autobots.conn.claid.image_operations.imageoperations import bulkEdit


class UseClaidAiApi:

    async def bulkEdit(self, req: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse:

        res: ClaidResponse | ClaidErrorResponse = await bulkEdit(req)
        return res
@lru_cache
def get_calid_ai() -> UseClaidAiApi:
    return UseClaidAiApi()
