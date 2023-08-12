import uuid
from typing import Dict, List

import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from autobots.conn.openai.chat import ChatReq, Message, Role
from autobots.core.settings import get_settings
from autobots.database.base import get_db
from autobots.graphs.graph_orm_model import GraphORM
from autobots.graphs.user_graphs import UserGraphCreateInput, UserGraphs
from autobots.prompts.prompt_orm_model import PromptORM
from autobots.prompts.target_platform import LLMTargetPlatform
from autobots.prompts.user_prompts import UserPrompts, UserPromptCreateInput, Input
from autobots.user.user_orm_model import UserORM


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_user_graphs_run_graph_happy_path(set_settings):
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    user = UserORM(id=user_id)

    try:
        with next(get_db()) as db:
            # create prompts
            user_prompts = UserPrompts(user=user)
            prompt_persona = await create_prompt_persona(user_prompts, db)
            prompt_manager = await create_prompt_manager(user_prompts, db)
            prompt_product = await create_prompt_product(user_prompts, db)
            prompt_creative = await create_prompt_creative(user_prompts, db)
            prompt_jingle = await create_prompt_jingle(user_prompts, db)

            # create graph
            graph_map = {
                str(prompt_manager.id): [str(prompt_persona.id), str(prompt_product.id)],
                str(prompt_persona.id): [str(prompt_creative.id), str(prompt_jingle.id)],
                str(prompt_product.id): [str(prompt_creative.id), str(prompt_jingle.id)]
            }

        with next(get_db()) as db1:
            user_graphs = UserGraphs(user=user)
            # graph = await create_graph(user_graphs, graph_map, db1)

            # run graph
            input = Input(input="Campaign for Nike shoes during Diwali Festival")
            # results = await user_graphs.run(input, graph.id, db1)
            results = await user_graphs.run_graph(input, graph_map, db1)
            assert len(results) == 5

    finally:
        pass
        with next(get_db()) as db:
            await user_prompts.delete(prompt_persona.id, db)
            await user_prompts.delete(prompt_manager.id, db)
            await user_prompts.delete(prompt_product.id, db)
            await user_prompts.delete(prompt_creative.id, db)
            await user_prompts.delete(prompt_jingle.id, db)
        #
        #     await user_graphs.delete(graph.id, db1)


@pytest.mark.asyncio
async def create_prompt_persona(user_prompts: UserPrompts, db: Session) -> PromptORM:
    user_prompt_create_input = UserPromptCreateInput(
        name="persona",
        chat_req=ChatReq(messages=[Message(
            role=Role.user,
            content="Generate personas for Marketing this product"
        )]),
        target_platform=LLMTargetPlatform.openai
    )
    prompt = await user_prompts.create(user_prompt_create_input, db)
    return prompt


@pytest.mark.asyncio
async def create_prompt_manager(user_prompts: UserPrompts, db: Session) -> PromptORM:
    user_prompt_create_input = UserPromptCreateInput(
        name="manager",
        chat_req=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as market manager, create input for department"
        )]),
        target_platform=LLMTargetPlatform.openai
    )
    prompt = await user_prompts.create(user_prompt_create_input, db)
    return prompt


@pytest.mark.asyncio
async def create_prompt_product(user_prompts: UserPrompts, db: Session) -> PromptORM:
    user_prompt_create_input = UserPromptCreateInput(
        name="market researcher",
        chat_req=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as product researcher, create research report for the product"
        )]),
        target_platform=LLMTargetPlatform.openai
    )
    prompt = await user_prompts.create(user_prompt_create_input, db)
    return prompt


@pytest.mark.asyncio
async def create_prompt_creative(user_prompts: UserPrompts, db: Session) -> PromptORM:
    user_prompt_create_input = UserPromptCreateInput(
        name="creative",
        chat_req=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as a creative editor, generate text creative"
        )]),
        target_platform=LLMTargetPlatform.openai
    )
    prompt = await user_prompts.create(user_prompt_create_input, db)
    return prompt


@pytest.mark.asyncio
async def create_prompt_jingle(user_prompts: UserPrompts, db: Session) -> PromptORM:
    user_prompt_create_input = UserPromptCreateInput(
        name="jingle",
        chat_req=ChatReq(messages=[Message(
            role=Role.user,
            content="Act as a creative editor, generate jingle for marketing"
        )]),
        target_platform=LLMTargetPlatform.openai
    )
    prompt = await user_prompts.create(user_prompt_create_input, db)
    return prompt


@pytest.mark.asyncio
async def create_graph(user_graphs: UserGraphs, graph_map: Dict[str, List[str]], db: Session) -> GraphORM:
    user_graph_create_input = UserGraphCreateInput(
        name="marketing dept",
        graph_map=graph_map
    )
    graph = await user_graphs.create(user_graph_create_input, db)
    return graph
