from typing import Optional, Type

from pydantic import BaseModel, Field
import time
import asyncio
from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.opus.opus import OpusRes, Video2VideoReqModel, get_opus_video
from src.autobots.user.user_orm_model import UserORM


class Video2VideoRunModel(BaseModel):
    url: Optional[str] = Field(default=None, description="")


class ActionCreateVideo2VideoOpus(ActionCreate):
    type: ActionType = ActionType.video2video_opus
    config: Video2VideoReqModel
    input: Optional[Video2VideoRunModel] = None


class ActionVideo2VideoOpus(
    ActionABC[Video2VideoReqModel, Video2VideoReqModel, Video2VideoReqModel, Video2VideoRunModel, OpusRes]
):
    type = ActionType.video2video_opus

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return Video2VideoReqModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return Video2VideoReqModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return Video2VideoReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Video2VideoRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return OpusRes

    def __init__(self, action_config: Video2VideoReqModel, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, action_input: Video2VideoRunModel):
        if action_input.url:
            self.action_config.url = action_input.url
        opus = get_opus_video()
        id_or_err = opus.create_clip(self.action_config)
        if isinstance(id_or_err, Exception):
            return id_or_err
        start_time = time.time()
        total_run_time = 5 * 60
        interval = 10

        while (time.time() - start_time) < total_run_time:
            if opus.query_clip(id_or_err)['stage'] == 'COMPLETED':
                break
        # Wait for the specified interval before the next iteration
            await asyncio.sleep(interval)
        return opus.get_result_clip(id_or_err)
