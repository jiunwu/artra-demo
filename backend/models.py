from pydantic import BaseModel
from typing import Optional, List


class Entity(BaseModel):
    text: str
    type: str  # "Arthropod" | "Trait" | "Value"
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: Optional[float] = None


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
    model: Optional[str] = "gemini-2.5-flash"


class ExtractionResponse(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]
    triplets: List[Triplet]
    processing_time_ms: int
    model_used: str
