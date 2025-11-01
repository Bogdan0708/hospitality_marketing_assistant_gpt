from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .deps import Base


class InstagramMedia(Base):
    __tablename__ = "instagram_media"

    id = Column(String, primary_key=True)
    caption = Column(String)
    media_type = Column(String(32))
    media_url = Column(String)
    timestamp = Column(DateTime(timezone=True))
    like_count = Column(Integer)
    comments_count = Column(Integer)
    inserted_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def serialize(payload: dict) -> dict:
        ts = payload.get("timestamp")
        timestamp = None
        if isinstance(ts, str):
            timestamp = _parse_timestamp(ts)
        return {
            "id": str(payload.get("id")),
            "caption": payload.get("caption"),
            "media_type": payload.get("media_type"),
            "media_url": payload.get("media_url"),
            "timestamp": timestamp,
            "like_count": payload.get("like_count"),
            "comments_count": payload.get("comments_count"),
        }


def _parse_timestamp(value: str) -> datetime | None:
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        return None
