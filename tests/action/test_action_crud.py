import pytest
import pytest_asyncio

from autobots.action.action_crud import ActionCRUD
from autobots.action.action_doc_model import ActionDocCreate, ActionDocFind
from autobots.action.action_manager import ActionManager
from autobots.action.action_type.action_types import ActionType
from autobots.conn.openai.chat import ChatReq, Role, Message
from autobots.core.settings import get_settings
from autobots.core.utils import gen_uuid
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import TextObj


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='.env.local')


@pytest.mark.asyncio
async def test_action_crud_happy_path(set_settings):
    db = next(get_mongo_db())
    action_crud = ActionCRUD(db)

    try:
        chat_req = ChatReq(messages=[Message(role=Role.user, content="You are an expert blogger")])
        action_doc_create = ActionDocCreate(
            name="test_action_crud_happy_path",
            type=ActionType.gen_text_llm_chat_openai,
            config=chat_req.model_dump(),
            input=TextObj().model_dump(),
            output=TextObj().model_dump(),
            user_id=gen_uuid().hex
        )
        inserted = await action_crud.insert_one(action_doc_create)
        assert inserted is not None

        action_find = ActionDocFind(id=str(inserted.id))
        action_docs = await action_crud.find(action_find)
        assert len(action_docs) == 1
        action_doc = action_docs.pop()

        assert action_doc.type == ActionType.gen_text_llm_chat_openai
        user_input = TextObj(input="Blog on San Francisco")
        action_manager = ActionManager()
        resp = await action_manager.run_action(action_doc, user_input)
        assert resp.role == Role.assistant

        delete_result = await action_crud.delete_many(action_find)
        assert delete_result.deleted_count == 1
    except Exception as e:
        assert e is None
    finally:
        find = ActionDocFind(name="test_action_crud_happy_path")
        deleted = await action_crud.delete_many(find)
        assert deleted.deleted_count == 0
