from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import httpx
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    TIKTOK_CLIENT_KEY: str
    TIKTOK_CLIENT_SECRET: str
    TIKTOK_ACCESS_TOKEN: str

    class Config:
        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


class TikTokClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.base_url = "https://open.tiktokapis.com/v2"
        self._headers = {
            "Authorization": f"Bearer {self.settings.TIKTOK_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def dep() -> "TikTokClient":
        return TikTokClient()

    def fetch_hashtag_insights(self, tag: str) -> Optional[dict]:
        endpoint = f"{self.base_url}/insights/hashtag/overview/"
        payload = {"hashtag_names": [tag]}
        try:
            response = httpx.post(endpoint, json=payload, headers=self._headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            summary = data.get("data", {}).get("hashtag_insights", [])
            if not summary:
                return None
            insight = summary[0]
            return {
                "hashtag": tag,
                "impressions": insight.get("views"),
                "reach": insight.get("reach"),
                "avg_engagement_rate": insight.get("engagement_rate"),
                "top_posts": insight.get("top_videos", []),
            }
        except httpx.HTTPError as exc:
            logger.warning("TikTok hashtag insights failed: %s", exc)
            return None

    def fetch_creator_videos(self, count: int = 10) -> list[dict]:
        endpoint = f"{self.base_url}/insights/video/list/"
        payload = {"max_count": count}
        try:
            response = httpx.post(endpoint, json=payload, headers=self._headers, timeout=30)
            response.raise_for_status()
            return response.json().get("data", {}).get("videos", [])
        except httpx.HTTPError as exc:
            logger.warning("TikTok videos fetch failed: %s", exc)
            return []
