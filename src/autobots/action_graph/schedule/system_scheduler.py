# from typing import Optional
# from uuid import UUID
#
# from fastapi import BackgroundTasks, Depends
# from loguru import logger
# from pymongo.database import Database
#
# from src.autobots.action.action.common_action_models import TextObj
# from src.autobots.action.action.user_actions import UserActions
# from src.autobots.action.action_market.user_actions_market import UserActionsMarket
# from src.autobots.action_graph.action_graph.user_action_graph import UserActionGraphs
# from src.autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
# from src.autobots.action_graph.schedule.scheduler import Scheduler
# from src.autobots.admin.crud.crud_action_graph import ActionGraphCRUD
# from src.autobots.api.webhook import Webhook
# from src.autobots.core.database.mongo_base import get_mongo_db
# from src.autobots.user.user_orm_model import UserORM
#
#
# class SystemScheduler:
#
#     def __init__(self, db: Database = Depends(get_mongo_db)):
#         self.db = db
#         self.action_graph_crud = ActionGraphCRUD(self.db)
#
#     async def list_action_graph_with_schedule(self, limit: int = 100, offset: int = 0):
#         action_graphs = await self.action_graph_crud.find_action_graph_with_schedule(limit, offset)
#         return action_graphs
#
#     async def run_action_graph(
#             self,
#             id: str,
#             user_id: str,
#             input: TextObj,
#             background_tasks: BackgroundTasks = BackgroundTasks(),
#             action_graph_result_id: Optional[str] = None,
#             webhook: Webhook | None = None,
#             db: Database = next(get_mongo_db())
#     ):
#         user_orm = UserORM(id=UUID(user_id))
#         user_actions = UserActions(user_orm, db)
#         user_actions_market = UserActionsMarket(user_orm, db)
#         user_action_graph_result = UserActionGraphResult(user_orm, db)
#         resp = await UserActionGraphs(user=user_orm, db=db).run_in_background(
#             user_actions,
#             user_actions_market,
#             user_action_graph_result,
#             id,
#             input,
#             action_graph_result_id,
#             background_tasks,
#             webhook
#         )
#         return resp
#
#     async def schedule_action_graphs(self):
#         # 1. Read all schedules of action_graph
#         # 2. For each: Add run_action_graph to Scheduler
#         # Scheduler.add_schedule(...)
#         # func is SystemScheduler.run_action_graph
#         offset = 0
#         while True:
#             action_graphs = await self.list_action_graph_with_schedule(offset=offset)
#             if len(action_graphs) == 0:
#                 break
#             for action_graph in action_graphs:
#                 try:
#                     Scheduler.add_schedule(
#                         func=self.run_action_graph,
#                         kwargs={
#                             "id": action_graph.id,
#                             "user_id": action_graph.user_id,
#                             "input": TextObj(text=""),
#                         },
#                         trigger=action_graph.schedule
#                     )
#                 except Exception as e:
#                     logger.bind(action_graph=action_graph).error(str(e))
#
#                 offset = offset + 1  # next batch

