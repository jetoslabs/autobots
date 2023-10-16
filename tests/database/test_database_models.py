import uuid

import pytest

from autobots.conn.openai.chat import Message, ChatReq

from autobots.core.utils import gen_uuid
from autobots.database.base import SessionLocal
from autobots.prompts.prompt_orm_model import PromptORM
from autobots.prompts.target_platform import LLMTargetPlatform
from autobots.user.user_orm_model import UserORM


@pytest.mark.asyncio
async def test_database_models_happy_path(set_test_settings):
    session = SessionLocal()
    try:
        # add user
        user1 = UserORM(id=uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37"))
        # session.add(user1)
        # session.commit()

        # add prompt
        prompt_name = "test_random_photo_happy_path" + gen_uuid().hex
        messages = [Message(role="user", content="Act as a expert blog writer")]
        chat_req = ChatReq(messages=messages)
        prompt1 = PromptORM(
            name=prompt_name,
            chat_req=chat_req,
            user_id=user1.id,
            target_platform=LLMTargetPlatform.openai#"openai"
        )
        session.add(prompt1)
        session.commit()

        # query user
        # users = session.query(UserORM)\
        #     .filter_by(id=user1.id)\
        #     .all()
        # assert len(users) > 0
        # assert users[0].id == user1.id

        # query prompt
        prompts = session.query(PromptORM)\
            .filter_by(name=prompt_name)\
            .all()
        assert len(prompts) > 0
        assert prompts[0].user_id == user1.id
        assert prompts[0].name == prompt_name

        # delete user
        # session.delete(users[0])
        # delete prompt
        session.delete(prompts[0])
        # commit delete
        session.commit()

    except Exception as e:
        assert e is None

    finally:
        session.close()
