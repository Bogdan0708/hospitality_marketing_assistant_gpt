from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str
    ok: bool = True
    details: dict[str, Any] | None = None


class MediaItem(BaseModel):
    id: str
    caption: str | None = None
    media_type: str | None = None
    media_url: str | None = None
    timestamp: datetime | None = None
    like_count: int | None = Field(default=None, ge=0)
    comments_count: int | None = Field(default=None, ge=0)


class HashtagInsights(BaseModel):
    hashtag: str
    impressions: int | None = Field(default=None, ge=0)
    reach: int | None = Field(default=None, ge=0)
    avg_engagement_rate: float | None = None
    top_posts: list[MediaItem] = Field(default_factory=list)


__all__ = [
    "HealthResponse",
    "MediaItem",
    "HashtagInsights",
]
