import base64
from typing import Type, List

from loguru import logger
from pydantic import BaseModel

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.IAction import IAction, ActionInputType, ActionOutputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType


class FileParams(BaseModel):
    filename: str
    content: str


class UserInputParams(BaseModel):
    text: str | None = None
    files: List[FileParams] | None = None


class ActionText2textUserInput(IAction[UserInputParams, UserInputParams, TextObjs, UserInputParams, TextObjs]):
    type = ActionType.text2text_user_input

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return UserInputParams

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return UserInputParams

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return TextObjs

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return UserInputParams

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: TextObjs):
        super().__init__(action_config)

    @staticmethod
    async def create_config(config_create: UserInputParams) -> TextObjs:
        text_objs = TextObjs(texts=[])
        if config_create.text:
            text_objs.texts.append(TextObj(text=f"{config_create.text}"))
        if config_create.files:
            for file in config_create.files:
                file_name = file.filename
                # file_text = await ActionText2textUserInput.b64_decode(file.content_base64)
                file_text = file.content
                text_objs.texts.append(TextObj(text=f"file_name: {file_name}\nfile_data: {file_text}"))
        return text_objs

    @staticmethod
    async def update_config(config: TextObjs, config_update: UserInputParams) -> TextObjs:
        text_objs = await ActionText2textUserInput.create_config(config_update)
        return text_objs

    async def run_action(self, action_input: UserInputParams) -> TextObjs:
        text_objs = self.action_config
        if action_input.text:
            text_objs.texts.append(TextObj(text=f"{action_input.text}"))
        if action_input.files:
            for file in action_input.files:
                file_name = file.filename
                # file_text = await ActionText2textUserInput.b64_decode(file.content_base64)
                file_text = file.content
                text_objs.texts.append(TextObj(text=f"file_name: {file_name}\nfile_data: {file_text}"))
        return text_objs

    @staticmethod
    async def b64_decode(b64_str: str) -> str:
        text = ""
        try:
            text = base64.b64decode(b64_str).decode()
        except Exception as e:
            logger.error(str(e))
        return text

    # @staticmethod
    # async def read_file(file: UploadFile) -> str:
    #     try:
    #         content = await file.read()
    #         return str(content)
    #     except Exception as e:
    #         logger.error(str(e))
