from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Form
from gotrue import UserResponse
from starlette.templating import Jinja2Templates

from autobots.action.action_doc_model import ActionDoc, ActionCreate, ActionUpdate, ActionFind
from autobots.action.action_gen_text_llm_chat_openai_v2 import ActionCreateGenTextLlmChatOpenai
from autobots.action.user_actions import UserActions
from autobots.api.ui.ui_most import get_user_from_cookie
from autobots.conn.openai.chat import ChatReq, Message
from autobots.core.settings import get_settings
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM

router = APIRouter()

templates = Jinja2Templates(directory="autobots/ui/templates")


@router.get("/llm_action")
async def page_llm_action_submit(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    if user:
        return templates.TemplateResponse("llm_action.html",
                                          {"request": request, "user": user.user, "version": get_settings().VERSION})
    else:
        return templates.TemplateResponse("index.html", {"request": request})


@router.post("/llm_action")
async def page_llm_action_submit(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    body = await request.body()
    if user:
        return templates.TemplateResponse("llm_action.html",
                                          {"request": request, "user": user.user, "version": get_settings().VERSION})
    else:
        return templates.TemplateResponse("index.html", {"request": request})


@router.get("/search_action")
async def page_search_action(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    if user:
        return templates.TemplateResponse("search_action.html",
                                          {"request": request, "user": user.user, "version": get_settings().VERSION})
    else:
        return templates.TemplateResponse("index.html", {"request": request})


@router.post("/action_search")
async def action_search(
        request: Request,
        user: UserResponse | None = Depends(get_user_from_cookie)
):
    input_action_find = await LlmActionUtil.get_action_find(request, user)
    user_action = UserActions(UserORM(id=UUID(user.user.id)))
    db = next(get_mongo_db())

    action_doc_got = await user_action.list_actions(input_action_find, db)
    return action_doc_got


@router.post("/llm_action_test")
async def llm_action_submit(
        request: Request,
        user: UserResponse | None = Depends(get_user_from_cookie)
):
    try:
        action_doc = await LlmActionUtil.get_action_doc(request, user)
        input = await LlmActionUtil.create_input(request)
        response = await UserActions.test_action(action_doc, input)
        message = Message.model_validate(response)
        return message.content
    except Exception as e:
        raise e


@router.post("/llm_action_save")
async def llm_action_save_update(
        request: Request,
        user: UserResponse | None = Depends(get_user_from_cookie)
):
    input_action_doc = await LlmActionUtil.get_action_doc(request, user)
    user_action = UserActions(UserORM(id=UUID(user.user.id)))
    db = next(get_mongo_db())

    action_doc_got = await user_action.get_action(input_action_doc.id, db)
    if not action_doc_got:
        # create action
        action_doc = await user_action.create_action(ActionCreate(**input_action_doc.model_dump()), db)
        action_id = action_doc.id
        return action_id
    else:
        # update action
        action_doc = await user_action.update_action(action_doc_got.id, ActionUpdate(**input_action_doc.model_dump()), db)
        action_id = action_doc.id
        return action_id


class LlmActionUtil:

    @staticmethod
    async def get_action_find(request: Request, user: UserResponse) -> ActionFind:
        form_data = await request.form()
        action_find = ActionFind()
        return action_find

    @staticmethod
    async def get_action_doc(request: Request, user: UserResponse) -> ActionDoc:
        form_data = await request.form()
        messages = []
        try:
            index = -1
            while True:
                index = index + 1
                role = form_data.get(f"input[messages][{index}][role]")
                content = form_data.get(f"input[messages][{index}][content]")
                if not role or not content:
                    break
                message = Message(role=role, content=content)
                messages.append(message)
        except Exception as e:
            pass

        input = ChatReq(
            model=form_data.get("input[model]"), temperature=form_data.get("input[temperature]"),
            top_p=form_data.get("input[top_p]"), n=form_data.get("input[n]"), stop=form_data.get("input[stop]"),
            max_tokens=form_data.get("input[max_tokens]"), presence_penalty=form_data.get("input[presence_penalty]"),
            frequency_penalty=form_data.get("input[frequency_penalty]"), user=form_data.get("input[user]"),
            messages=messages
        )

        action_id = form_data.get("id")
        if not action_id: action_id = "1"
        action_doc = ActionDoc(
            _id=action_id, user_id=user.user.id, name=form_data.get("name"), version=form_data.get("version"),
            description=form_data.get("description"), user_manual=form_data.get("user_manual"),
            type=form_data.get("type"), input=input.model_dump()
        )
        return action_doc

    @staticmethod
    async def create_input(request: Request) -> Input:
        form_data = await request.form()
        input_data = form_data.get("test[input]")
        input = Input(input=input_data)
        return input
