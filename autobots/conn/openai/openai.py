import openai
from openai.openai_object import OpenAIObject

from autobots.conn.openai.chat import ChatReq, ChatRes
from autobots.core.log import log


class OpenAI:

    def __init__(self, org_id: str, api_key: str):
        # once set, any invocation of openai has state
        # openai here is global
        openai.organization = org_id
        openai.api_key = api_key

    @staticmethod
    async def chat(chat_req: ChatReq) -> ChatRes:
        try:
            log.debug("Starting OpenAI Chat")
            res: OpenAIObject = await openai.ChatCompletion.acreate(**chat_req.dict(), timeout=30)
            log.debug("Completed OpenAI Chat")
            resp: ChatRes = ChatRes(**res.to_dict())
            return resp
        except Exception as e:
            log.error(e)
