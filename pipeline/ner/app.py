from fastapi import FastAPI
from pydantic import BaseModel
from gliner import GLiNER
from typing import List

app = FastAPI(title="GLiNER NER API")

# Load model once at startup
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")


class NERRequest(BaseModel):
    text: str
    labels: List[str]
    threshold: float = 0.5


class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    score: float


@app.get("/")
async def root():
    return {"status": "ok", "service": "GLiNER NER API"}


@app.post("/extract", response_model=List[Entity])
async def extract_entities(request: NERRequest):
    entities = model.predict_entities(
        request.text, 
        request.labels, 
        threshold=request.threshold
    )
    return entities

