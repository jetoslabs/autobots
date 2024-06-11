import pytest

from src.autobots.conn.serp.serp import get_serp
from src.autobots.conn.serp.serp_search_request import SerpGoogleSearchParams


@pytest.mark.asyncio
async def test_serp_google_search_shop_happy_path(set_test_settings):
    search_params = SerpGoogleSearchParams(
        q="buy coffee",
        tbm="shop",
    )
    result = await get_serp().serp_google_search.search(search_params)
    assert not isinstance(result, Exception)


@pytest.mark.asyncio
async def test_serp_google_search_happy_path(set_test_settings):
    search_params = SerpGoogleSearchParams(
        q="buy coffee",
    )
    result = await get_serp().serp_google_search.search(search_params)
    assert not isinstance(result, Exception)
