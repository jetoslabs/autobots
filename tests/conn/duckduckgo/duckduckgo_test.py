from typing import List

import pytest

from src.autobots.conn.duckduckgo.duckduckgo import SearchRes, get_duckduckgo, AnswerRes
from src.autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams, Timelimit, SearchMapsParams, \
    SearchImageParams, SearchVideoParams, LicenseImage
from src.autobots.conn.duckduckgo.duckduckgo_region_model import Region


@pytest.mark.asyncio
async def test_search_text_happy_path(set_test_settings):
    search_params = SearchTextParams(
        keywords="where is Arsenal Football club located",
        region=Region.wt_wt,
        safesearch="moderate",
        timelimit=Timelimit.d,
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
        region=Region.uk_en,
        safesearch="moderate",
        timelimit=Timelimit.d,
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


@pytest.mark.asyncio
async def test_search_images_happy_path(set_test_settings):
    search_params = SearchImageParams(
        keywords="Tourism",
        license_image=LicenseImage.Public_Domain,
        timelimit="Month"
    )
    ans_res = await get_duckduckgo().search_images(search_params)
    assert len(ans_res) > 0
    assert ans_res[0].url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_videos_happy_path(set_test_settings):
    search_params = SearchVideoParams(keywords="San Francisco tourism")
    ans_res = await get_duckduckgo().search_videos(search_params)
    assert len(ans_res) > 0
    assert ans_res[0].embed_url
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_map_happy_path(set_test_settings):
    search_params = SearchMapsParams(keywords="coffee", place="San Francisco")
    ans_res = await get_duckduckgo().search_maps(search_params)
    assert len(ans_res) > 0
    assert ans_res[0].address
    assert ans_res[0].title


@pytest.mark.asyncio
async def test_search_map_happy_path_1(set_test_settings):
    search_params = SearchMapsParams(
        keywords="coffee",
        place="New Delhi",
        latitude="28.6139",
        longitude="77.2090",
        radius=50
    )
    ans_res = await get_duckduckgo().search_maps(search_params)
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
