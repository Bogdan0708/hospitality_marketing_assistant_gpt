from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from common import HashtagInsights, HealthResponse, MediaItem

from .deps import Base, MetaClient, engine, get_db
from .models import InstagramMedia

app = FastAPI(title="Instagram Analytics")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/healthz", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - diagnostics only
        raise HTTPException(status_code=503, detail={"error": "db_unavailable"}) from exc
    return HealthResponse(service="instagram-server")


@app.get("/oauth/callback")
def oauth_callback(code: str, client: MetaClient = Depends(MetaClient.dep)) -> dict:
    token = client.exchange_code_for_token(code)
    return {"token_saved": bool(token)}


@app.get("/metrics/hashtag", response_model=HashtagInsights)
def hashtag_metrics(
    tag: str = Query(..., min_length=1),
    client: MetaClient = Depends(MetaClient.dep),
) -> HashtagInsights:
    data = client.fetch_hashtag_insights(tag)
    if not data:
        raise HTTPException(status_code=404, detail="No data")

    top_posts = [
        MediaItem(
            id=str(item.get("id")),
            caption=item.get("caption"),
            media_type=item.get("media_type"),
            media_url=item.get("media_url") or item.get("permalink"),
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


@app.get("/metrics/account")
def account_metrics(client: MetaClient = Depends(MetaClient.dep)) -> dict:
    return client.fetch_account_insights()


@app.get("/ingest/recent_media")
def ingest_recent_media(
    limit: int = 50,
    client: MetaClient = Depends(MetaClient.dep),
    db: Session = Depends(get_db),
) -> dict:
    items = client.fetch_recent_media(limit=limit)
    payloads = [InstagramMedia.serialize(item) for item in items]

    if payloads:
        stmt = insert(InstagramMedia).values(payloads)
        update_cols = {
            "caption": stmt.excluded.caption,
            "media_type": stmt.excluded.media_type,
            "media_url": stmt.excluded.media_url,
            "timestamp": stmt.excluded.timestamp,
            "like_count": stmt.excluded.like_count,
            "comments_count": stmt.excluded.comments_count,
        }
        stmt = stmt.on_conflict_do_update(index_elements=[InstagramMedia.id], set_=update_cols)
        try:
            db.execute(stmt)
            db.commit()
        except Exception as exc:  # pragma: no cover - transactional guard
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to persist media") from exc

    media_items = [MediaItem(**payload) for payload in payloads]
    return {"count": len(media_items), "items": media_items}
