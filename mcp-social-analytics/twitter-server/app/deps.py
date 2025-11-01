from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import httpx
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    TWITTER_BEARER_TOKEN: str

    class Config:
        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


class TwitterClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.base = "https://api.twitter.com/2"
        self._headers = {"Authorization": f"Bearer {self.settings.TWITTER_BEARER_TOKEN}"}

    @staticmethod
    def dep() -> "TwitterClient":
        return TwitterClient()

    def fetch_hashtag_insights(self, tag: str, max_results: int = 10) -> Optional[dict]:
        query = f"#{tag.lstrip('#')} lang:en"
        params = {
            "query": query,
            "max_results": max(max_results, 10),
            "tweet.fields": "public_metrics,created_at,author_id",
            "expansions": "author_id",
            "user.fields": "name,username,profile_image_url",
        }
        try:
            response = httpx.get(
                f"{self.base}/tweets/search/recent",
                params=params,
                headers=self._headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Twitter search failed: %s", exc)
            return None

        tweets = data.get("data", [])
        impressions = sum(tweet.get("public_metrics", {}).get("impression_count", 0) for tweet in tweets)
        reach = sum(tweet.get("public_metrics", {}).get("like_count", 0) for tweet in tweets)

        top_posts = []
        for tweet in tweets[:5]:
            metrics = tweet.get("public_metrics", {})
            top_posts.append(
                {
                    "id": tweet.get("id"),
                    "caption": tweet.get("text"),
                    "media_type": "tweet",
                    "media_url": f"https://twitter.com/i/web/status/{tweet.get('id')}",
                    "like_count": metrics.get("like_count"),
                    "comments_count": metrics.get("reply_count"),
                }
            )

        return {
            "hashtag": tag,
            "impressions": impressions,
            "reach": reach,
            "avg_engagement_rate": None,
            "top_posts": top_posts,
        }
