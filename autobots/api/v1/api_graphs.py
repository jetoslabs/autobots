# from typing import List, Dict
# from uuid import UUID
#
# import gotrue
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session
#
# from autobots.auth.security import get_user_from_access_token
# from autobots.core.log import log
# from autobots.database.base import get_db
# from autobots.graphs.to_del.user_graphs import UserGraphCreateInput, UserGraphCreateOutput, UserGraphs
# from autobots.prompts.user_prompts import Input
# from autobots.user.user_orm_model import UserORM
#
# router = APIRouter()
#
# 
# @router.post("/")
# async def create_graph(
#         user_graph_create_input: UserGraphCreateInput,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> UserGraphCreateOutput:
#     try:
#         user_orm = UserORM(id=UUID(user_res.user.id))
#         prompt_orm = await UserGraphs(user=user_orm).create(user_graph_create_input, db)
#         output = UserGraphCreateOutput.model_validate(prompt_orm)
#         return output
#     except IntegrityError as ie:
#         log.error(ie)
#         raise HTTPException(400, "Name and version is not unique")
#     except Exception as e:
#         log.error(e)
#         raise HTTPException(500)
#
#
# @router.get("/")
# async def list_graphs(
#         limit: int = 100, offset: int = 0,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> List[UserGraphCreateOutput]:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     graph_orm_s = await UserGraphs(user=user_orm).list(limit, offset, db)
#     output = [UserGraphCreateOutput.model_validate(prompt_orm) for prompt_orm in graph_orm_s]
#     return output
#
#
# @router.get("/{id}")
# async def get_graph(
#         id: str,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> UserGraphCreateOutput:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     graph_orm = await UserGraphs(user=user_orm).read(UUID(id), db)
#     output = UserGraphCreateOutput.model_validate(graph_orm)
#     return output
#
#
# @router.put("/{id}")
# async def replace_graph(
#         id: str,
#         user_prompt_create_input: UserGraphCreateInput,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> UserGraphCreateOutput:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     prompt_orm = await UserGraphs(user=user_orm).upsert(UUID(id), user_prompt_create_input, db)
#     output = UserGraphCreateOutput.model_validate(prompt_orm)
#     return output
#
#
# @router.delete("/{id}")
# async def delete_graph(
#         id: str,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> UserGraphCreateOutput:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     prompt_orm = await UserGraphs(user=user_orm).delete(UUID(id), db)
#     output = UserGraphCreateOutput.model_validate(prompt_orm)
#     return output
#
#
# @router.post("/{id}/run/")
# async def run_graph(
#         id: str,
#         input: Input,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> Dict[str, str]:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     results = await UserGraphs(user=user_orm).run(input, UUID(id), db)
#     return results
#
#
# @router.get("/name/{name}/version/{version}")
# async def get_graph(
#         name: str, version: str = None,
#         limit: int = 100, offset: int = 0,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Session = Depends(get_db)
# ) -> List[UserGraphCreateOutput]:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     graph_orm_s = await UserGraphs(user=user_orm).read_by_name_version(name, version, limit, offset, db)
#     output = [UserGraphCreateOutput.model_validate(graph_orm) for graph_orm in graph_orm_s]
#     return output
