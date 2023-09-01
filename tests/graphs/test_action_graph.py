import uuid

import pytest
import pytest_asyncio
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_gen_text_llm_chat_openai import ActionCreateGenTextLlmChatOpenai
from autobots.action.user_actions import UserActions
from autobots.conn.openai.chat import ChatReq, Message, Role
from autobots.core.settings import get_settings
from autobots.core.utils import gen_random_str
from autobots.database.mongo_base import get_mongo_db
from autobots.graphs.action_graph import ActionGraph
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_user_graph_run_happy_path(set_settings):
    rand: str = gen_random_str()

    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    user = UserORM(id=user_id)

    db = next(get_mongo_db())

    # create actions
    user_actions = UserActions(user=user)
    action_llm_persona = await create_action_persona(user_actions, db, rand)
    action_llm_manager = await create_action_manager(user_actions, db, rand)
    action_llm_product = await create_action_product(user_actions, db, rand)
    action_llm_creative = await create_action_creative(user_actions, db, rand)
    action_llm_jingle = await create_action_jingle(user_actions, db, rand)

    try:
        # create action graph
        action_graph = {
            str(action_llm_manager.id): [str(action_llm_persona.id), str(action_llm_product.id)],
            str(action_llm_persona.id): [str(action_llm_creative.id), str(action_llm_jingle.id)],
            str(action_llm_product.id): [str(action_llm_creative.id), str(action_llm_jingle.id)]
        }

        # run action graph
        user_input = Input(input="Campaign for Nike shoes during Diwali Festival")
        action_response = await ActionGraph.run(user, user_input, action_graph, db)

        # validate
        assert len(action_response) > 1

    except Exception as e:
        assert e is not None

    finally:
        # cleanup
        await user_actions.delete_action(action_llm_manager.id, db)
        await user_actions.delete_action(action_llm_persona.id, db)
        await user_actions.delete_action(action_llm_product.id, db)
        await user_actions.delete_action(action_llm_creative.id, db)
        await user_actions.delete_action(action_llm_jingle.id, db)


@pytest.mark.asyncio
async def create_action_persona(user_actions: UserActions, db: Database, rand: str) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="persona_" + rand,
        input=ChatReq(messages=[Message(
            role=Role.user,
            content="Generate personas for Marketing this product"
        )])
    )
    action_doc = await user_actions.create_action(
        ActionCreate(**action_create.model_dump()), db
    )
    return action_doc


@pytest.mark.asyncio
async def create_action_manager(user_actions: UserActions, db: Database, rand: str) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="manager_" + rand,
        input=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as market manager, create input for department"
        )])
    )
    action_doc = await user_actions.create_action(
        ActionCreate(**action_create.model_dump()), db
    )
    return action_doc


@pytest.mark.asyncio
async def create_action_product(user_actions: UserActions, db: Database, rand: str) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="market researcher_" + rand,
        input=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as product researcher, create research report for the product"
        )])
    )
    action_doc = await user_actions.create_action(
        ActionCreate(**action_create.model_dump()), db
    )
    return action_doc


@pytest.mark.asyncio
async def create_action_creative(user_actions: UserActions, db: Database, rand: str = gen_random_str()) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="creative_" + rand,
        input=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as a creative editor, generate text creative"
        )])
    )
    action_doc = await user_actions.create_action(
        ActionCreate(**action_create.model_dump()), db
    )
    return action_doc


@pytest.mark.asyncio
async def create_action_jingle(user_actions: UserActions, db: Database, rand: str = gen_random_str()) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="jingle_" + rand,
        input=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as a creative editor, generate jingle for marketing"
        )])
    )
    action_doc = await user_actions.create_action(
        ActionCreate(**action_create.model_dump()), db
    )
    return action_doc


# @pytest.mark.asyncio
# async def create_graph(user_graphs: UserGraphs, graph_map: Dict[str, List[str]], db: Session, rand: str = gen_random_str()) -> GraphORM:
#     user_graph_create_input = UserGraphCreateInput(
#         name="marketing dept_" + rand,
#         graph_map=graph_map
#     )
#     graph = await user_graphs.create(user_graph_create_input, db)
#     return graph
