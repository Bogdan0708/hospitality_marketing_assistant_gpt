from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import httpx
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    META_PAGE_ID: str
    META_APP_ID: str
    META_APP_SECRET: str
    META_LONG_LIVED_TOKEN: str

    class Config:
        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


class FacebookClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.base = "https://graph.facebook.com/v18.0"
        self.token = self.settings.META_LONG_LIVED_TOKEN
        self.page_id = self.settings.META_PAGE_ID

    @staticmethod
    def dep() -> "FacebookClient":
        return FacebookClient()

    def fetch_page_insights(self) -> dict:
        fields = "followers_count,fan_count,new_like_count,talking_about_count"
        url = f"{self.base}/{self.page_id}?fields={fields}&access_token={self.token}"
        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Facebook page insights failed: %s", exc)
            return {}

    def fetch_hashtag_insights(self, tag: str) -> Optional[dict]:
        search_url = f"{self.base}/ig_hashtag_search"
        params = {
            "user_id": self.page_id,
            "q": tag.lstrip("#"),
            "access_token": self.token,
        }
        try:
            response = httpx.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json().get("data", [])
            if not data:
                return None
            hashtag_id = data[0].get("id")
        except httpx.HTTPError as exc:
            logger.warning("Facebook hashtag search failed: %s", exc)
            return None

        media_url = f"{self.base}/{hashtag_id}/top_media"
        params = {
            "user_id": self.page_id,
            "fields": "id,caption,media_type,media_url,permalink,like_count,comments_count",
            "access_token": self.token,
        }
        try:
            response = httpx.get(media_url, params=params, timeout=30)
            response.raise_for_status()
            top_media = response.json().get("data", [])
        except httpx.HTTPError as exc:
            logger.warning("Facebook top media fetch failed: %s", exc)
            top_media = []

        impressions = sum(item.get("like_count", 0) for item in top_media)
        reach = sum(item.get("comments_count", 0) for item in top_media)
        return {
            "hashtag": tag,
            "impressions": impressions,
            "reach": reach,
            "avg_engagement_rate": None,
            "top_posts": top_media,
        }
