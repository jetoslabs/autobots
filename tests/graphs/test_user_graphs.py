# import uuid
# from typing import Dict, List
#
# import pytest
# from sqlalchemy.orm import Session
#
# from autobots.action_graph.user_action_graph import UserActionGraphs
# from autobots.conn.openai.chat import ChatReq, Message, Role
# from autobots.core.utils import gen_random_str
# from autobots.database.base import get_db
# from autobots.prompts.prompt_orm_model import PromptORM
# from autobots.prompts.target_platform import LLMTargetPlatform
# from autobots.prompts.user_prompts import UserPrompts, UserPromptCreateInput, TextObj
# from autobots.user.user_orm_model import UserORM
#
#
# @pytest.mark.skip(reason="Moved to to_del folder")
# @pytest.mark.asyncio
# async def test_user_graph_run_happy_path(set_test_settings):
#     rand: str = gen_random_str()
#
#     user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
#     user = UserORM(id=user_id)
#
#     prompt_persona = None
#     prompt_manager = None
#     prompt_product = None
#     prompt_creative = None
#     prompt_jingle = None
#
#     try:
#         with next(get_db()) as db:
#             # create prompts
#             user_prompts = UserPrompts(user=user)
#             prompt_persona = await create_prompt_persona(user_prompts, db, rand)
#             prompt_manager = await create_prompt_manager(user_prompts, db, rand)
#             prompt_product = await create_prompt_product(user_prompts, db, rand)
#             prompt_creative = await create_prompt_creative(user_prompts, db, rand)
#             prompt_jingle = await create_prompt_jingle(user_prompts, db, rand)
#
#             # create graph
#             graph_map = {
#                 str(prompt_manager.id): [str(prompt_persona.id), str(prompt_product.id)],
#                 str(prompt_persona.id): [str(prompt_creative.id), str(prompt_jingle.id)],
#                 str(prompt_product.id): [str(prompt_creative.id), str(prompt_jingle.id)]
#             }
#
#         with next(get_db()) as db1:
#             # testing run_graph
#             user_graphs = UserActionGraphs(user=user)
#             input1 = TextObj(input="Campaign for Nike shoes during Diwali Festival")
#             results1 = await user_graphs.test(input1, graph_map, db1)
#             assert len(results1) == 5
#
#             # testing run (involves creating record in graphs table)
#             input2 = TextObj(input="Campaign for Nike shoes during Diwali Festival")
#             # create graph in table
#             graph = await create_graph(user_graphs, graph_map, db1, rand)
#             # run stored graph
#             results2 = await user_graphs.run(input2, graph.id, db1)
#             assert len(results2) == 5
#     except Exception as e:
#         assert e is not None
#     finally:
#         with next(get_db()) as db:
#             await user_prompts.delete(prompt_persona.id, db)
#             await user_prompts.delete(prompt_manager.id, db)
#             await user_prompts.delete(prompt_product.id, db)
#             await user_prompts.delete(prompt_creative.id, db)
#             await user_prompts.delete(prompt_jingle.id, db)
#         with next(get_db()) as db1:
#             await user_graphs.delete(graph.id, db1)
#
#
# @pytest.mark.asyncio
# async def create_prompt_persona(user_prompts: UserPrompts, db: Session, rand: str) -> PromptORM:
#     user_prompt_create_input = UserPromptCreateInput(
#         name="persona_" + rand,
#         chat_req=ChatReq(messages=[Message(
#             role=Role.user,
#             content="Generate personas for Marketing this product"
#         )]),
#         target_platform=LLMTargetPlatform.openai
#     )
#     prompt = await user_prompts.create(user_prompt_create_input, db)
#     return prompt
#
#
# @pytest.mark.asyncio
# async def create_prompt_manager(user_prompts: UserPrompts, db: Session, rand: str = gen_random_str()) -> PromptORM:
#     user_prompt_create_input = UserPromptCreateInput(
#         name="manager_" + rand,
#         chat_req=ChatReq(messages=[Message(
#             role=Role.user,
#             content="Act as market manager, create input for department"
#         )]),
#         target_platform=LLMTargetPlatform.openai
#     )
#     prompt = await user_prompts.create(user_prompt_create_input, db)
#     return prompt
#
#
# @pytest.mark.asyncio
# async def create_prompt_product(user_prompts: UserPrompts, db: Session, rand: str = gen_random_str()) -> PromptORM:
#     user_prompt_create_input = UserPromptCreateInput(
#         name="market researcher_" + rand,
#         chat_req=ChatReq(messages=[Message(
#             role=Role.user,
#             content="Act as product researcher, create research report for the product"
#         )]),
#         target_platform=LLMTargetPlatform.openai
#     )
#     prompt = await user_prompts.create(user_prompt_create_input, db)
#     return prompt
#
#
# @pytest.mark.asyncio
# async def create_prompt_creative(user_prompts: UserPrompts, db: Session, rand: str = gen_random_str()) -> PromptORM:
#     user_prompt_create_input = UserPromptCreateInput(
#         name="creative_" + rand,
#         chat_req=ChatReq(messages=[Message(
#             role=Role.user,
#             content="Act as a creative editor, generate text creative"
#         )]),
#         target_platform=LLMTargetPlatform.openai
#     )
#     prompt = await user_prompts.create(user_prompt_create_input, db)
#     return prompt
#
#
# @pytest.mark.asyncio
# async def create_prompt_jingle(user_prompts: UserPrompts, db: Session, rand: str = gen_random_str()) -> PromptORM:
#     user_prompt_create_input = UserPromptCreateInput(
#         name="jingle_" + rand,
#         chat_req=ChatReq(messages=[Message(
#             role=Role.user,
#             content="Act as a creative editor, generate jingle for marketing"
#         )]),
#         target_platform=LLMTargetPlatform.openai
#     )
#     prompt = await user_prompts.create(user_prompt_create_input, db)
#     return prompt
#
#
# @pytest.mark.asyncio
# async def create_graph(user_graphs: UserGraphs, graph_map: Dict[str, List[str]], db: Session, rand: str = gen_random_str()) -> GraphORM:
#     user_graph_create_input = UserGraphCreateInput(
#         name="marketing dept_" + rand,
#         graph_map=graph_map
#     )
#     graph = await user_graphs.create(user_graph_create_input, db)
#     return graph
