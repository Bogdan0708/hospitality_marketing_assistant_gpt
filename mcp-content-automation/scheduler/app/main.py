from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import time
import redis

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
)

app = FastAPI(title="Scheduler")


class ScheduleReq(BaseModel):
    platform: str
    when_epoch: int
    payload: dict


@app.post("/enqueue")
def enqueue(req: ScheduleReq):
    key = f"queue:{req.platform}"
    r.zadd(key, {json.dumps(req.payload): req.when_epoch})
    return {"queued": True}


@app.post("/tick")
def tick():
    now = int(time.time())
    for platform in ["instagram", "facebook", "twitter", "tiktok"]:
        key = f"queue:{platform}"
        items = r.zrangebyscore(key, 0, now)
        for item in items:
            r.zrem(key, item)
            # TODO: forward to publisher service asynchronously
    return {"ok": True}
