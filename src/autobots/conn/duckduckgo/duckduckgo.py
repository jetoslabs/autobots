from functools import lru_cache
from typing import List, Optional, Iterator, AsyncGenerator

from duckduckgo_search import AsyncDDGS
from pydantic import BaseModel, HttpUrl

from src.autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams, SearchMapsParams, SearchImageParams, \
    SearchVideoParams
from src.autobots.core.logging.log import Log
from src.autobots.core.settings import Settings, SettingsProvider


class SearchRes(BaseModel):
    title: str
    href: HttpUrl
    body: str


class NewsRes(BaseModel):
    date: str
    title: str
    body: str
    url: HttpUrl
    image: Optional[HttpUrl]
    source: str


class AnswerRes(BaseModel):
    icon: Optional[str]
    text: str
    topic: Optional[str]
    url: HttpUrl


class ImageRes(BaseModel):
    title: str
    image: HttpUrl
    thumbnail: HttpUrl
    url: HttpUrl
    height: int
    width: int
    source: str


class VideoRes(BaseModel):
    content: HttpUrl
    description: str
    duration: str
    embed_html: str
    embed_url: HttpUrl
    image_token: str
    images: dict
    provider: str
    published: str
    publisher: str
    statistics: dict
    title: str
    uploader: str


class MapRes(BaseModel):
    title: str
    address: str
    country_code: Optional[str] = None
    latitude: float
    longitude: float
    url: HttpUrl | str
    desc: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[HttpUrl] = None
    source: HttpUrl
    links: Optional[str] = None
    hours: dict | str
    category: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None


class TranslateRes(BaseModel):
    detected_language: str
    translated: str
    original: str


class SuggestionRes(BaseModel):
    phrase: str


class DuckDuckGo:

    async def search_text(self, search_params: SearchTextParams) -> List[SearchRes]:
        search_res = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            search_iter: AsyncGenerator[dict[str, str | None]] = ddgs.text(**search_params.model_dump(exclude_none=True))
            async for r in search_iter:
                # if num > search_params.max_results:
                #     break
                # num = num + 1
                res = SearchRes(**r)
                search_res.append(res)
                Log.trace(f"Search for {search_params.keywords}: {r}")
        return search_res

    async def news(self, search_params: SearchTextParams) -> List[NewsRes]:
        news_res = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            async for r in ddgs.news(**search_params.model_dump(exclude_none=True)):
                # if num > num_results:
                #     break
                # num = num + 1
                res = NewsRes(**r)
                news_res.append(res)
        Log.trace(f"News for {search_params.keywords}: {news_res}")
        return news_res

    async def answer(self, keywords: str, num_results: int = 3) -> List[AnswerRes]:
        answer_res = []
        async with AsyncDDGS() as ddgs:
            num = 1
            async for r in ddgs.answers(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = AnswerRes(**r)
                answer_res.append(res)
                Log.trace(f"Answer for {keywords}: {r}")
        return answer_res

    async def search_images(self, search_params: SearchImageParams) -> List[ImageRes]:
        images = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            ddgs_images_gen = ddgs.images(**search_params.model_dump(exclude_none=True))
            async for r in ddgs_images_gen:
                # if num > num_results:
                #     break
                # num = num + 1
                res = ImageRes(**r)
                images.append(res)
                Log.trace(f"Image for {search_params.keywords}: {r}")
        return images

    async def search_videos(self, search_params: SearchVideoParams) -> List[VideoRes]:
        videos = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            ddgs_videos_gen = ddgs.videos(**search_params.model_dump(exclude_none=True))
            async for r in ddgs_videos_gen:
                # if num > num_results:
                #     break
                # num = num + 1
                res = VideoRes(**r)
                videos.append(res)
                Log.trace(f"Video for {search_params.keywords}: {r}")
        return videos

    async def search_maps(self, search_params: SearchMapsParams) -> List[MapRes]:
        maps = []
        # num = 1
        async with AsyncDDGS() as ddgs:
            search_iter = ddgs.maps(**search_params.model_dump())
            async for r in search_iter:
                # if num > num_results:
                #     break
                # num = num + 1
                res = MapRes(**r)
                maps.append(res)
                Log.trace(f"Map search for {search_params.keywords}: {r}")
        return maps

    async def translate(self, keywords: str, from_: Optional[str] = None, to: str = "en") -> TranslateRes:
        translated: TranslateRes
        async with AsyncDDGS() as ddgs:
            r = await ddgs.translate(keywords, to=to)
            res = TranslateRes(**r)
            translated = res
            Log.trace(f"Translated for {keywords}: {r}")
        return translated

    async def suggestions(self, keywords: str, num_results: int = 30):
        suggestions = []
        num = 1
        async with AsyncDDGS() as ddgs:
            async for r in ddgs.suggestions(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = SuggestionRes(**r)
                suggestions.append(res)
                Log.trace(f"Suggestion for {keywords}: {r}")
        return suggestions


@lru_cache
def get_duckduckgo(settings: Settings = SettingsProvider.sget()) -> DuckDuckGo:
    return DuckDuckGo()
