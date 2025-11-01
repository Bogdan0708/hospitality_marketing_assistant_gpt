from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Sentiment Analyzer")
clf = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")


class TextIn(BaseModel):
    texts: list[str]


@app.post("/analyze")
def analyze(payload: TextIn):
    out = clf(payload.texts)
    return {"results": out}
