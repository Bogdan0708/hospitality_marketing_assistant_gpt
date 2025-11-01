from __future__ import annotations

import logging
from functools import lru_cache
from typing import Generator, Optional

import httpx
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    META_APP_ID: str
    META_APP_SECRET: str
    META_LONG_LIVED_TOKEN: str
    META_IG_BUSINESS_ID: str

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "mitch"
    POSTGRES_PASSWORD: str = "mitchpass"
    POSTGRES_DB: str = "mitch_ai"

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


class MetaClient:
    def __init__(self):
        cfg = settings
        self.base = "https://graph.facebook.com/v18.0"
        self.token = cfg.META_LONG_LIVED_TOKEN
        self.ig_id = cfg.META_IG_BUSINESS_ID

    @staticmethod
    def dep() -> "MetaClient":
        return MetaClient()

    def exchange_code_for_token(self, code: str) -> Optional[str]:
        return None

    def fetch_account_insights(self) -> dict:
        url = (
            f"{self.base}/{self.ig_id}?fields=followers_count,media_count"
            f"&access_token={self.token}"
        )
        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch account insights: %s", exc)
            return {}

    def fetch_hashtag_insights(self, tag: str) -> Optional[dict]:
        hashtag_id = self._resolve_hashtag_id(tag)
        if not hashtag_id:
            return None

        top_media = self._fetch_hashtag_media(hashtag_id, "top_media")
        recent_media = self._fetch_hashtag_media(hashtag_id, "recent_media")

        impressions = sum(item.get("like_count", 0) for item in top_media)
        reach = sum(item.get("comments_count", 0) for item in top_media)
        engagement_denominator = max(1, len(top_media))
        avg_engagement = (impressions + reach) / engagement_denominator

        return {
            "hashtag": tag,
            "impressions": impressions,
            "reach": reach,
            "avg_engagement_rate": round(avg_engagement, 3),
            "top_posts": top_media[:10],
            "recent_posts": recent_media[:10],
        }

    def fetch_recent_media(self, limit: int = 50) -> list[dict]:
        url = (
            f"{self.base}/{self.ig_id}/media"
            "?fields=id,caption,media_type,media_url,timestamp,like_count,comments_count"
            f"&limit={limit}&access_token={self.token}"
        )
        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            payload = response.json()
            return payload.get("data", [])
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch recent media: %s", exc)
            return []

    def _resolve_hashtag_id(self, tag: str) -> Optional[str]:
        normalized = tag.lstrip("#")
        url = (
            f"{self.base}/ig_hashtag_search?user_id={self.ig_id}&q={normalized}"
            f"&access_token={self.token}"
        )
        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            data = response.json().get("data", [])
            if not data:
                return None
            return str(data[0].get("id"))
        except httpx.HTTPError as exc:
            logger.warning("Failed to resolve hashtag '%s': %s", tag, exc)
            return None

    def _fetch_hashtag_media(self, hashtag_id: str, media_type: str) -> list[dict]:
        url = (
            f"{self.base}/{hashtag_id}/{media_type}?user_id={self.ig_id}"
            "&fields=id,caption,media_type,media_url,permalink,like_count,comments_count"
            f"&access_token={self.token}"
        )
        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get("data", [])
        except httpx.HTTPError as exc:
            logger.warning(
                "Failed to fetch hashtag media for %s (%s): %s",
                hashtag_id,
                media_type,
                exc,
            )
            return []


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
