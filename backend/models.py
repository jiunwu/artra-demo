from pydantic import BaseModel
from typing import Optional, List

ALLOWED_MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "qwen",
    "z-ai/glm4.7",
    "moonshotai/kimi-k2-instruct-0905",
    "minimaxai/minimax-m2.1",
]

NIM_MODELS = {m for m in ALLOWED_MODELS if (("/" in m) or m == "qwen") and not m.startswith("gemini")}


class Entity(BaseModel):
    text: str
    type: str  # "Arthropod" | "Trait" | "Value"
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: Optional[float] = None
    is_novel: Optional[bool] = None
    ecological_context: Optional[str] = None


class Relationship(BaseModel):
    subject: str
    predicate: str  # "hasTrait" | "hasValue"
    object: str


class Triplet(BaseModel):
    arthropod: str
    trait: str
    value: str


class ExtractionRequest(BaseModel):
    text: str
    model: Optional[str] = "gemini-3.1-flash-lite-preview"


class ExtractionResponse(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]
    triplets: List[Triplet]
    processing_time_ms: int
    model_used: str
