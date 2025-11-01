from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException, Query

from common import HashtagInsights, HealthResponse, MediaItem

from .deps import TikTokClient

logger = logging.getLogger(__name__)

app = FastAPI(title="TikTok Analytics")


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(service="tiktok-server")


@app.get("/metrics/hashtag", response_model=HashtagInsights)
def hashtag_metrics(
    tag: str = Query(..., min_length=1),
    client: TikTokClient = Depends(TikTokClient.dep),
) -> HashtagInsights:
    data = client.fetch_hashtag_insights(tag)
    if not data:
        raise HTTPException(status_code=404, detail="No hashtag insights available")

    top_posts = [
        MediaItem(
            id=str(item.get("id") or item.get("video_id")),
            caption=item.get("caption") or item.get("title"),
            media_type=item.get("media_type") or "video",
            media_url=item.get("media_url") or item.get("share_url"),
            like_count=item.get("like_count") or item.get("likes"),
            comments_count=item.get("comments_count") or item.get("comments"),
        )
        for item in data.get("top_posts", [])
    ]

    return HashtagInsights(
        hashtag=data.get("hashtag", tag),
        impressions=data.get("impressions"),
        reach=data.get("reach"),
        avg_engagement_rate=data.get("avg_engagement_rate"),
        top_posts=top_posts,
    )


@app.get("/videos/recent")
def recent_videos(
    client: TikTokClient = Depends(TikTokClient.dep),
    count: int = 10,
) -> dict:
    videos = client.fetch_creator_videos(count=count)
    items = [
        MediaItem(
            id=str(item.get("id") or item.get("video_id")),
            caption=item.get("caption") or item.get("title"),
            media_type="video",
            media_url=item.get("video_url") or item.get("share_url"),
            like_count=item.get("likes"),
            comments_count=item.get("comments"),
        )
        for item in videos
    ]
    return {"count": len(items), "items": items}
