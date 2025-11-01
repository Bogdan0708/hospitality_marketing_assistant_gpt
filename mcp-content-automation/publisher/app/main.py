from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx

META_PAGE_ID = os.getenv("META_PAGE_ID")
META_IG_BUSINESS_ID = os.getenv("META_IG_BUSINESS_ID")
META_TOKEN = os.getenv("META_LONG_LIVED_TOKEN")
BASE = "https://graph.facebook.com/v18.0"

app = FastAPI(title="Publisher")


class PublishReq(BaseModel):
    platform: str
    caption: str
    image_url: str | None = None
    video_url: str | None = None


@app.post("/publish")
def publish(req: PublishReq):
    if req.platform == "instagram":
        media_create = f"{BASE}/{META_IG_BUSINESS_ID}/media"
        create_res = httpx.post(
            media_create,
            data={
                "caption": req.caption,
                "image_url": req.image_url,
                "access_token": META_TOKEN,
            },
            timeout=60,
        ).json()
        creation_id = create_res.get("id")
        publish_res = httpx.post(
            f"{BASE}/{META_IG_BUSINESS_ID}/media_publish",
            data={"creation_id": creation_id, "access_token": META_TOKEN},
            timeout=60,
        ).json()
        return {"platform": "instagram", "result": publish_res}

    return {"platform": req.platform, "status": "stub"}
