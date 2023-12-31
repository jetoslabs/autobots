from functools import lru_cache
from typing import List, Optional

from duckduckgo_search import DDGS
from pydantic import BaseModel, HttpUrl

from autobots.core.logging.log import Log
from autobots.core.settings import Settings, SettingsProvider


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
    country_code: Optional[str]
    latitude: float
    longitude: float
    url: HttpUrl | str
    desc: Optional[str]
    phone: str
    image: Optional[HttpUrl]
    source: HttpUrl
    links: Optional[str]
    hours: dict


class TranslateRes(BaseModel):
    detected_language: str
    translated: str
    original: str


class SuggestionRes(BaseModel):
    phrase: str


class DuckDuckGo:

    async def search_text(self, text: str, num_results: int = 3) -> List[SearchRes]:
        search_res = []
        with DDGS() as ddgs:
            num = 1
            for r in ddgs.text(text):
                if num > num_results:
                    break
                num = num + 1
                res = SearchRes(**r)
                search_res.append(res)
                Log.trace(f"Search for {text}: {r}")
        return search_res

    async def news(self, keywords: str, num_results: int = 3) -> List[NewsRes]:
        news_res = []
        with DDGS() as ddgs:
            num = 1
            for r in ddgs.news(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = NewsRes(**r)
                news_res.append(res)
                Log.trace(f"News for {keywords}: {r}")
        return news_res

    async def answer(self, keywords: str, num_results: int = 3) -> List[AnswerRes]:
        answer_res = []
        with DDGS() as ddgs:
            num = 1
            for r in ddgs.answers(keywords):
                if num > num_results:
                    break
                num = num + 1
                res = AnswerRes(**r)
                answer_res.append(res)
                Log.trace(f"Answer for {keywords}: {r}")
        return answer_res

    async def search_images(self, keywords: str, num_results: int = 3) -> List[ImageRes]:
        images = []
        with DDGS() as ddgs:
            num = 1
            ddgs_images_gen = ddgs.images(
                keywords,
                region="wt-wt",
                safesearch="Off",
                size=None,
                color="color",
                type_image=None,
                layout=None,
                license_image="ModifyCommercially",
            )
            for r in ddgs_images_gen:
                if num > num_results:
                    break
                num = num + 1
                res = ImageRes(**r)
                images.append(res)
                Log.trace(f"Image for {keywords}: {r}")
        return images

    async def search_videos(self, keywords: str, num_results: int = 3) -> List[VideoRes]:
        videos = []
        with DDGS() as ddgs:
            num = 1
            ddgs_videos_gen = ddgs.videos(
                keywords,
                region="wt-wt",
                safesearch="Off",
                timelimit="w",
                resolution="high",
                duration="medium",
            )
            for r in ddgs_videos_gen:
                if num > num_results:
                    break
                num = num + 1
                res = VideoRes(**r)
                videos.append(res)
                Log.trace(f"Video for {keywords}: {r}")
        return videos

    async def search_map(
            self, keywords: str, place: str = None, street: str = None, city: str = None,
            county: str = None, state: str = None, country: str = None, postalcode: str = None,
            latitude: str = None, longitude: str = None, radius: int = 0, num_results: int = 3
    ) -> List[MapRes]:
        maps = []
        num = 1
        with DDGS() as ddgs:
            for r in ddgs.maps(keywords, place=place, street=street, city=city, county=county, state=state,
                               country=country, postalcode=postalcode, latitude=latitude, longitude=longitude,
                               radius=radius):
                if num > num_results:
                    break
                num = num + 1
                res = MapRes(**r)
                maps.append(res)
                Log.trace(f"Map search for {keywords}: {r}")
        return maps

    async def translate(self, keywords: str, from_: Optional[str] = None, to: str = "en") -> TranslateRes:
        translated: TranslateRes
        with DDGS() as ddgs:
            r = ddgs.translate(keywords, to=to)
            res = TranslateRes(**r)
            translated = res
            Log.trace(f"Translated for {keywords}: {r}")
        return translated

    async def suggestions(self, keywords: str, num_results: int = 30):
        suggestions = []
        num = 1
        with DDGS() as ddgs:
            for r in ddgs.suggestions(keywords):
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
