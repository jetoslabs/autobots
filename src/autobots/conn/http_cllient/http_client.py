from aiohttp import ClientSession
from pydantic import HttpUrl


class HttpClient:
    @staticmethod
    async def download_from_url(url: HttpUrl):
        async with ClientSession() as session:
            async with session.get(url=url.unicode_string()) as response:
                body = await response.read()
                return body
