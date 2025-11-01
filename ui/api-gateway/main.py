from fastapi import FastAPI
import httpx

app = FastAPI(title="API Gateway")


@app.get("/trends/instagram")
def ig_trends():
    with httpx.Client(timeout=30) as client:
        data = client.post(
            "http://insights-engine:8000/weekly",
            json={"platform": "instagram", "k_clusters": 5},
        ).json()
    return data


@app.post("/posts/generate")
def gen_post(topic: str):
    with httpx.Client(timeout=60) as client:
        data = client.post(
            "http://content-generator:8000/captions",
            json={"platform": "instagram", "topic": topic, "n_variants": 3},
        ).json()
    return data


@app.post("/posts/publish")
def publish(caption: str, image_url: str):
    with httpx.Client(timeout=60) as client:
        data = client.post(
            "http://publisher:8000/publish",
            json={"platform": "instagram", "caption": caption, "image_url": image_url},
        ).json()
    return data
