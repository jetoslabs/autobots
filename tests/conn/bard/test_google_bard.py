import pytest

from autobots.conn.google.bard.google_bard import get_google_bard


@pytest.mark.asyncio
async def test_bard(set_test_settings):
    bard = get_google_bard()
    result = bard.client.ask(
        text="top competitors for neemans.com in India"
    )

    # result = bard.get_answer(
    #     input_text="TCS stock price on 4th January 2024"
    # )

    assert result