from autobots.conn.openai.chat import ChatReq, Message
from autobots.conn.openai.openai import get_openai
from autobots.prompts.prompt_orm_model import PromptORM
from autobots.prompts.target_platform import LLMTargetPlatform


class PromptFactory:

    @staticmethod
    async def run(prompt_orm: PromptORM, user_message: Message) -> Message | None:
        if prompt_orm.target_platform.lower() == LLMTargetPlatform.openai:
            chat_req = ChatReq.model_validate(**prompt_orm.chat_req)
            chat_req.messages = chat_req.messages + [user_message]
            chat_res = await get_openai().chat(chat_req=chat_req)
            resp = chat_res.choices[0].message
            return resp