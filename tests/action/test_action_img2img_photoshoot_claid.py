import pytest

from src.autobots.action.action_type.action_img2img.action_img2img_photoshoot_claid import ActionImg2ImgPhotoshootClaid, \
    ActionConfigPhotoshootClaid, ActionInputPhotoshootClaid
from src.autobots.conn.claid.claid_model import PhotoshootObject, PhotoshootScene


@pytest.mark.asyncio
async def test_action_img2img_photoshoot_claid_happy_path(set_test_settings):
    action_config = ActionConfigPhotoshootClaid()
    action = ActionImg2ImgPhotoshootClaid(action_config)
    action_input = ActionInputPhotoshootClaid(
        object=PhotoshootObject(
            image_url="https://upload.wikimedia.org/wikipedia/en/9/9c/Archie_1942_issue_1.jpg",
        ),
        scene=PhotoshootScene(
            prompt="Make it Black and White"
        )
    )
    action_output = await action.run_action(action_input)
    assert len(action_output.data) == 1
