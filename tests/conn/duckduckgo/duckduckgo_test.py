from typing import List

import pytest

from autobots.conn.duckduckgo.duckduckgo import SearchRes, get_duckduckgo, AnswerRes
from autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams, Safesearch, Timelimit
from autobots.conn.duckduckgo.duckduckgo_region_model import Region


@pytest.mark.asyncio
async def test_search_text_happy_path(set_test_settings):
    search_params = SearchTextParams(
        keywords="where is Arsenal Football club located",
        region=Region.No_Region,
        safesearch=Safesearch.off,
        # timelimit=Timelimit.day,
        max_result=3
    )
    search_res: List[SearchRes] = await get_duckduckgo().search_text(search_params)
    assert len(search_res) > 0
    assert search_res[0].href
    assert search_res[0].title


@pytest.mark.asyncio
async def test_news_happy_path(set_test_settings):
    search_params = SearchTextParams(
        keywords="Latest football news",
        region=Region.United_Kingdom_en,
        safesearch=Safesearch.off,
        timelimit=Timelimit.day,
        max_result=3
    )
    news_res = await get_duckduckgo().news(search_params)
    assert len(news_res) > 0
    assert news_res[0].url
    assert news_res[0].title


@pytest.mark.asyncio
async def test_answer_happy_path(set_test_settings):
    ans_res: List[AnswerRes] = await get_duckduckgo().answer("cricket")
    assert len(ans_res) > 0
    assert ans_res[0].text
    assert ans_res[0].url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_images_happy_path(set_test_settings):
    ans_res = await get_duckduckgo().search_images("Athlete running in the city")
    assert len(ans_res) > 0
    assert ans_res[0].url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_videos_happy_path(set_test_settings):
    ans_res = await get_duckduckgo().search_videos("Athlete running in the city")
    assert len(ans_res) > 0
    assert ans_res[0].embed_url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_map_happy_path(set_test_settings):
    ans_res = await get_duckduckgo().search_map("monuments", city="New Delhi")
    assert len(ans_res) > 0
    assert ans_res[0].url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_translate_happy_path(set_test_settings):
    ans_res = await get_duckduckgo().translate("Going to school", to="hi")
    assert ans_res.original
    assert ans_res.translated


@pytest.mark.asyncio
async def test_suggestions_happy_path(set_test_settings):
    ans_res = await get_duckduckgo().suggestions("arsenal.com")
    assert len(ans_res) > 0
    assert ans_res[0].phrase
