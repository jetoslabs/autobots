import uuid

import pytest
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_type.action_gen_text_llm_chat_openai_v2 import ActionCreateGenTextLlmChatOpenai
from autobots.action.user_actions import UserActions
from autobots.conn.openai.chat import ChatReq, Message, Role
from autobots.core.utils import gen_random_str
from autobots.database.mongo_base import get_mongo_db
from autobots.graphs.action_graph import ActionGraph
from autobots.graphs.action_graph_doc_model import ActionGraphCreate
from autobots.graphs.user_action_graph import UserActionGraphs
from autobots.prompts.user_prompts import TextObj
from autobots.user.user_orm_model import UserORM


@pytest.mark.asyncio
async def test_user_graph_run_happy_path(set_test_settings):
    rand: str = gen_random_str()

    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    user = UserORM(id=user_id)

    db = next(get_mongo_db())

    user_actions = UserActions(user=user)
    user_action_graph = UserActionGraphs(user=user)

    # create actions
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

        # run action graph on fly
        user_input = TextObj(input="Campaign for Nike shoes during Diwali Festival")
        action_graph_response = await ActionGraph.run(user, user_input, action_graph, db)
        assert len(action_graph_response) > 1

        # save action graph
        action_graph_create = ActionGraphCreate(
            name="Marketing Dept", graph=action_graph
        )
        action_graph_doc = await user_action_graph.create(action_graph_create, db)

        # run saved action graph
        input = TextObj(input="Create ad for sports shoes")
        action_graph_resp = await user_action_graph.run(action_graph_doc.id, input, db)
        assert len(action_graph_resp) > 1

        # cleanup action graph
        await user_action_graph.delete(action_graph_doc.id, db)

    except Exception as e:
        assert e is not None

    finally:
        # cleanup actions
        await user_actions.delete_action(action_llm_manager.id, db)
        await user_actions.delete_action(action_llm_persona.id, db)
        await user_actions.delete_action(action_llm_product.id, db)
        await user_actions.delete_action(action_llm_creative.id, db)
        await user_actions.delete_action(action_llm_jingle.id, db)


@pytest.mark.asyncio
async def create_action_persona(user_actions: UserActions, db: Database, rand: str) -> ActionDoc:
    action_create = ActionCreateGenTextLlmChatOpenai(
        name="persona_" + rand,
        config=ChatReq(messages=[Message(
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
        config=ChatReq(messages=[Message(
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
        config=ChatReq(messages=[Message(
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
        config=ChatReq(messages=[Message(
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
        config=ChatReq(messages=[Message(
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
