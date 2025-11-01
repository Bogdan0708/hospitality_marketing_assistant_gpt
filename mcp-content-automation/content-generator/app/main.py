from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Content Generator")


class GenReq(BaseModel):
    platform: str
    topic: str
    brand_voice: str = "Playful Dracula, witty, hospitality-forward"
    n_variants: int = 3


@app.post("/captions")
def captions(req: GenReq):
    prompt = f"""Write {req.n_variants} short {req.platform} captions
in the voice: {req.brand_voice}. Topic: {req.topic}.
Add 5-8 trending, relevant hashtags at the end of each variant."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=60,
    )
    message = response.json()["choices"][0]["message"]["content"]
    variants = [variant.strip() for variant in message.split("\n\n") if variant.strip()]
    return {"variants": variants[: req.n_variants]}
