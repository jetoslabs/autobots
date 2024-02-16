from typing import Dict, Any

import httpx
from pydantic import BaseModel, HttpUrl, Field


class Webhook(BaseModel):
    url: HttpUrl
    track_id: str = Field("")

    async def send(self, data: Dict[str, Any]) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.url}/{self.track_id}", json=data, timeout=1)
        except Exception:
            pass
