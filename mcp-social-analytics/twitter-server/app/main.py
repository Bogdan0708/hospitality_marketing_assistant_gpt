from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException, Query

from common import HashtagInsights, HealthResponse, MediaItem

from .deps import TwitterClient

logger = logging.getLogger(__name__)

app = FastAPI(title="Twitter Analytics")


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(service="twitter-server")


@app.get("/metrics/hashtag", response_model=HashtagInsights)
def hashtag_metrics(
    tag: str = Query(..., min_length=1),
    client: TwitterClient = Depends(TwitterClient.dep),
) -> HashtagInsights:
    data = client.fetch_hashtag_insights(tag)
    if not data:
        raise HTTPException(status_code=404, detail="No hashtag insights available")

    top_posts = [
        MediaItem(
            id=str(item.get("id")),
            caption=item.get("caption"),
            media_type=item.get("media_type"),
            media_url=item.get("media_url"),
            like_count=item.get("like_count"),
            comments_count=item.get("comments_count"),
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
