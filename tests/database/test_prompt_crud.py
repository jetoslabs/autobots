import uuid

import pytest
import pytest_asyncio

from autobots.conn.openai.chat import Message, Role, ChatReq
from autobots.core.settings import get_settings
from autobots.core.utils import gen_uuid
from autobots.database.base import get_db
# from autobots.database.database_models import UserORM, PromptORM
from autobots.database.prompt_crud import PromptCRUD
from autobots.database.prompt_orm_model import PromptORM
from autobots.database.target_platform import LLMTargetPlatform
from autobots.database.user_crud import UserCRUD
from autobots.database.user_orm_model import UserORM


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_prompt_crud_happy_path(set_settings):
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    created_prompt = None
    with next(get_db()) as db:
        try:
            # is_user_exist = await UserCRUD.read(user_id, db)
            # if len(is_user_exist) == 0:
            #     # add user
            #     user1 = UserORM(id=user_id)
            #     await UserCRUD.create(user1, db)
            #     db.commit()

            # add prompt
            prompt_name = "test_prompt_crud_happy_path"+ gen_uuid().hex
            message_content = "Be a blog writer"
            chat_req = ChatReq(messages=[Message(role=Role.user, content=message_content)])
            prompt1 = PromptORM(
                name=prompt_name,
                chat_req=chat_req,
                user_id=user_id,
                target_platform=LLMTargetPlatform.openai
            )
            await PromptCRUD.create(prompt=prompt1, db=db)
            db.commit()

            # select prompt
            prompts = await PromptCRUD.read_by_name_version(user_id, prompt_name, db=db)
            assert len(prompts) > 0
            # verify content of 1st message
            created_prompt = prompts[0]
            assert created_prompt.chat_req["messages"][0]["content"] == message_content

        finally:
            # delete prompt
            await PromptCRUD.delete(created_prompt, db)
            db.commit()
            # # delete user if exist (provisioning for other tests)
            # is_user_exist = await UserCRUD.read(user_id, db)
            # if len(is_user_exist) > 0:
            #     await UserCRUD.delete(user1, db)
            #     db.commit()
