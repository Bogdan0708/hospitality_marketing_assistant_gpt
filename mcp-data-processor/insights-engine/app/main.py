from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import httpx


class Settings(BaseSettings):
    instagram_server_url: str = "http://instagram-server:8000"
    sentiment_analyzer_url: str = "http://sentiment-analyzer:8000"
    trend_detector_url: str = "http://trend-detector:8000"


settings = Settings()
app = FastAPI(title="Insights Engine")


class InsightReq(BaseModel):
    platform: str
    hashtag: str | None = None


@app.post("/weekly")
def weekly(req: InsightReq):
    with httpx.Client(timeout=30) as client:
        try:
            media_response = client.get(
                f"{settings.instagram_server_url}/ingest/recent_media?limit=100"
            )
            media_response.raise_for_status()
            media = media_response.json()

            payload: list[dict] = []
            if isinstance(media, dict):
                payload = (
                    media.get("items")
                    or media.get("ingested")
                    or media.get("data")
                    or []
                )

            captions = [item.get("caption", "") for item in payload]

            sent_response = client.post(
                f"{settings.sentiment_analyzer_url}/analyze",
                json={"texts": captions},
            )
            sent_response.raise_for_status()
            sent = sent_response.json()

            clusters_response = client.post(
                f"{settings.trend_detector_url}/clusters",
                json={"texts": captions},
            )
            clusters_response.raise_for_status()
            clusters = clusters_response.json()

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    results = sent.get("results", []) if isinstance(sent, dict) else []
    positives = sum(1 for r in results if r.get("label") == "POSITIVE")
    avg_pos = positives / max(1, len(results))

    return {
        "summary": {
            "platform": req.platform,
            "period": "last_7_days",
            "avg_positive": round(avg_pos, 3),
        },
        "clusters": clusters.get("clusters", []) if isinstance(clusters, dict) else [],
    }
