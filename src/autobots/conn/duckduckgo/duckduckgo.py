from functools import lru_cache
from typing import List, Optional

from duckduckgo_search import AsyncDDGS
from loguru import logger
from pydantic import BaseModel, HttpUrl
from retry import retry

from src.autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams, SearchMapsParams, SearchImageParams, \
    SearchVideoParams
from src.autobots.core.settings import Settings, SettingsProvider


class SearchRes(BaseModel):
    title: Optional[str] = None
    href: Optional[HttpUrl] = None
    body: Optional[str] = None


class NewsRes(BaseModel):
    date: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    source: Optional[str] = None


class AnswerRes(BaseModel):
    icon: Optional[str] = None
    text: Optional[str] = None
    topic: Optional[str] = None
    url: Optional[HttpUrl] = None


class ImageRes(BaseModel):
    title: Optional[str] = None
    image: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None
    url: Optional[HttpUrl] = None
    height: Optional[int] = None
    width: Optional[int] = None
    source: Optional[str] = None


class VideoRes(BaseModel):
    content: Optional[HttpUrl] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    embed_html: Optional[str] = None
    embed_url: Optional[HttpUrl] = None
    image_token: Optional[str] = None
    images: Optional[dict] = None
    provider: Optional[str] = None
    published: Optional[str] = None
    publisher: Optional[str] = None
    statistics: Optional[dict] = None
    title: Optional[str] = None
    uploader: Optional[str] = None


class MapRes(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    url: Optional[HttpUrl | str] = None
    desc: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[HttpUrl] | str = None
    source: Optional[HttpUrl] = None
    links: Optional[str] = None
    hours: Optional[dict | str] = None
    category: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None


class TranslateRes(BaseModel):
    detected_language: Optional[str] = None
    translated: Optional[str] = None
    original: Optional[str] = None


class SuggestionRes(BaseModel):
    phrase: Optional[str] = None


class DuckDuckGo:

    @retry(tries=5, delay=5, backoff=10)
    async def search_text(self, search_params: SearchTextParams) -> List[SearchRes]:
        search_res = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            search_iter: List[dict[str, str | None]] = ddgs.text(**search_params.model_dump(exclude_none=True))
            for r in search_iter:
                # if num > search_params.max_results:
                #     break
                # num = num + 1
                res = SearchRes(**r)
                search_res.append(res)
                logger.trace(f"Search for {search_params.keywords}: {r}")
        return search_res

    @retry(tries=5, delay=5, backoff=10)
    async def news(self, search_params: SearchTextParams) -> List[NewsRes]:
        news_res = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            for r in ddgs.news(**search_params.model_dump(exclude_none=True)):
                # if num > num_results:
                #     break
                # num = num + 1
                res = NewsRes(**r)
                news_res.append(res)
        logger.trace(f"News for {search_params.keywords}: {news_res}")
        return news_res

    @retry(tries=5, delay=5, backoff=10)
    async def answer(self, keywords: str, num_results: int = 3) -> List[AnswerRes]:
        answer_res = []
        async with AsyncDDGS() as ddgs:
            num = 1
            for r in ddgs.answers(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = AnswerRes(**r)
                answer_res.append(res)
                logger.trace(f"Answer for {keywords}: {r}")
        return answer_res

    @retry(tries=5, delay=5, backoff=10)
    async def search_images(self, search_params: SearchImageParams) -> List[ImageRes]:
        images = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            ddgs_images_gen = ddgs.images(**search_params.model_dump(exclude_none=True))
            for r in ddgs_images_gen:
                # if num > num_results:
                #     break
                # num = num + 1
                res = ImageRes(**r)
                images.append(res)
                logger.trace(f"Image for {search_params.keywords}: {r}")
        return images

    @retry(tries=5, delay=5, backoff=10)
    async def search_videos(self, search_params: SearchVideoParams) -> List[VideoRes]:
        videos = []
        async with AsyncDDGS() as ddgs:
            # num = 1
            ddgs_videos_gen = ddgs.videos(**search_params.model_dump(exclude_none=True))
            for r in ddgs_videos_gen:
                # if num > num_results:
                #     break
                # num = num + 1
                res = VideoRes(**r)
                videos.append(res)
                logger.trace(f"Video for {search_params.keywords}: {r}")
        return videos

    @retry(tries=5, delay=5, backoff=10)
    async def search_maps(self, search_params: SearchMapsParams) -> List[MapRes]:
        maps = []
        # num = 1
        async with AsyncDDGS() as ddgs:
            search_iter = ddgs.maps(**search_params.model_dump())
            for r in search_iter:
                # if num > num_results:
                #     break
                # num = num + 1
                res = MapRes(**r)
                maps.append(res)
                logger.trace(f"Map search for {search_params.keywords}: {r}")
        return maps

    @retry(tries=5, delay=5, backoff=10)
    async def translate(self, keywords: str, from_: Optional[str] = None, to: str = "en") -> TranslateRes:
        translated: TranslateRes
        async with AsyncDDGS() as ddgs:
            for r in ddgs.translate(keywords, to=to):
                res = TranslateRes(**r)
                translated = res
                logger.trace(f"Translated for {keywords}: {r}")
                return translated

    @retry(tries=5, delay=5, backoff=10)
    async def suggestions(self, keywords: str, num_results: int = 30):
        suggestions = []
        num = 1
        async with AsyncDDGS() as ddgs:
            for r in ddgs.suggestions(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = SuggestionRes(**r)
                suggestions.append(res)
                logger.trace(f"Suggestion for {keywords}: {r}")
        return suggestions


@lru_cache
def get_duckduckgo(settings: Settings = SettingsProvider.sget()) -> DuckDuckGo:
    return DuckDuckGo()
