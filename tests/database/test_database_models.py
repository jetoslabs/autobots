import uuid

import pytest
import pytest_asyncio

from autobots.conn.openai.chat import Message
from autobots.core.settings import get_settings, Settings
from autobots.database.base import Session
from autobots.database.database_models import UserORM, PromptORM


@pytest_asyncio.fixture
async def set_settings() -> Settings:
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_database_models_happy_path(set_settings):
    session = Session()
    try:
        # add user
        user1 = UserORM(id=uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37"))
        session.add(user1)
        session.commit()

        # add prompt
        prompt_name = "test_random_photo_happy_path"
        prompt = [Message(role="user", content="Act as a expert blog writer")]
        prompt1 = PromptORM(
            name=prompt_name,
            prompt=prompt,
            user_id=user1.id,
            target_platform="openai"
        )
        session.add(prompt1)
        session.commit()

        # query user
        users = session.query(UserORM)\
            .filter_by(id=user1.id)\
            .all()
        assert len(users) > 0
        assert users[0].id == user1.id

        # query prompt
        prompts = session.query(PromptORM)\
            .filter_by(name=prompt_name)\
            .all()
        assert len(prompts) > 0
        assert prompts[0].user_id == user1.id
        assert prompts[0].name == prompt_name

        # delete user
        session.delete(users[0])
        # delete prompt
        session.delete(prompts[0])
        # commit delete
        session.commit()

    except Exception as e:
        assert e is None

    finally:
        session.close()
