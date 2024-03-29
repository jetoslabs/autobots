from typing import List

from pydantic import BaseModel

from src.autobots.conn.unsplash.random_photo import Image


class SearchImageList(BaseModel):
    total: int
    total_pages: int
    results: List[Image]
