from functools import lru_cache
from typing import List

import aiohttp
import copy

from src.autobots.conn.unsplash.random_photo import Image
from src.autobots.conn.unsplash.search_photo import SearchImageList
from src.autobots.core.settings import Settings, SettingsProvider


class Unsplash:
    URL: str = "https://api.unsplash.com"
    ACCEPT_VERSION_HEADER: str = "v1"

    RANDOM_PHOTO = {"path": "/photos/random", "method": "GET"}
    SEARCH_PHOTO = {"path": "/search/photos", "method": "GET"}

    def __init__(self, access_key: str):
        self.params = {"client_id": access_key}
        self.headers = {"Accept-Version": Unsplash.ACCEPT_VERSION_HEADER}

    async def get_random_photo(self, count: int = 1) -> List[Image]:
        params = copy.deepcopy(self.params)
        params["count"] = f"{count}"
        url = f"{Unsplash.URL}{Unsplash.RANDOM_PHOTO.get('path')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url=url, params=params) as r:
                json_body = await r.json()
                img_list: List[Image] = [Image(**image_json_body) for image_json_body in json_body]
                # List[Image](json_body)]ImageList.parse_obj(json_body)
                return img_list

    async def search_photo(self, query: str):
        params = copy.deepcopy(self.params)
        params["query"] = f"{query}"
        url = f"{Unsplash.URL}{Unsplash.SEARCH_PHOTO.get('path')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url=url, params=params) as r:
                json_body = await r.json()
                img_list = SearchImageList.model_validate(json_body)
                return img_list


@lru_cache
def get_unsplash(settings: Settings = SettingsProvider.sget()) -> Unsplash:
    return Unsplash(access_key=settings.UNSPLASH_ACCESS_KEY)

