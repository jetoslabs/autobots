import uuid

import pytest
from openai.types.chat import ChatCompletionUserMessageParam

from autobots.action.action.action_crud import ActionCRUD
from autobots.action.action.action_doc_model import ActionDocCreate, ActionDocFind
from autobots.action.action_type.action_factory import ActionFactory
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.conn.openai.openai_chat.chat_model import ChatReq, Role, Message
from autobots.core.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM


@pytest.mark.asyncio
async def test_action_crud_happy_path(set_test_settings):
    db = next(get_mongo_db())
    action_crud = ActionCRUD(db)

    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d39")
    user = UserORM(id=user_id)

    try:
        chat_req = ChatReq(messages=[ChatCompletionUserMessageParam(role="user", content="You are an expert blogger")])
        action_doc_create = ActionDocCreate(
            name="test_action_crud_happy_path",
            type=ActionType.text2text_llm_chat_openai,
            config=chat_req.model_dump(),
            # input=None,
            # output=None,
            user_id=str(user_id)
        )
        inserted = await action_crud.insert_one(action_doc_create)
        assert inserted is not None

        action_find = ActionDocFind(user_id=str(user_id), id=str(inserted.id))
        action_docs = await action_crud.find(action_find)
        assert len(action_docs) == 1
        action_doc = action_docs.pop()

        assert action_doc.type == ActionType.text2text_llm_chat_openai
        user_input = TextObj(input="Blog on San Francisco")
        action_factory = ActionFactory()
        resp: TextObjs = await action_factory.run_action(action_doc, user_input.model_dump())
        assert len(resp.texts) > 0
        assert resp.texts[0] != ""

        delete_result = await action_crud.delete_many(action_find)
        assert delete_result.deleted_count == 1
    except Exception as e:
        assert e is None
    finally:
        find = ActionDocFind(user_id=str(user_id), name="test_action_crud_happy_path")
        deleted = await action_crud.delete_many(find)
        assert deleted.deleted_count == 0
