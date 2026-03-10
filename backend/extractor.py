import os
import json
import re
import time
from google import genai
from models import Entity, Relationship, Triplet, ExtractionResponse
from prompts import build_prompt

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _parse_json(raw: str) -> dict:
    """Parse JSON from Gemini response with fallback strategies."""
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from markdown code fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding the first { ... } block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Return empty structure as last resort
    return {"entities": [], "relationships": [], "triplets": []}


def _find_entity_positions(text: str, entity_text: str) -> tuple[int | None, int | None]:
    """Find the start and end positions of an entity in the original text (case-insensitive)."""
    idx = text.lower().find(entity_text.lower())
    if idx == -1:
        return None, None
    return idx, idx + len(entity_text)


def extract(text: str, model: str = "gemini-3.1-flash-lite-preview") -> ExtractionResponse:
    """Call Gemini API and extract entities, relationships, and triplets."""
    client = get_client()
    prompt = build_prompt(text)

    start_ms = time.time()
    response = client.models.generate_content(model=model, contents=prompt)
    elapsed_ms = int((time.time() - start_ms) * 1000)

    raw = response.text or ""
    data = _parse_json(raw)

    # Parse entities, adding position info from original text where missing
    entities = []
    for e in data.get("entities", []):
        entity_text = e.get("text", "")
        start = e.get("start")
        end = e.get("end")
        if start is None or end is None:
            start, end = _find_entity_positions(text, entity_text)
        entities.append(Entity(
            text=entity_text,
            type=e.get("type", ""),
            start=start,
            end=end,
            confidence=e.get("confidence"),
        ))

    relationships = [
        Relationship(
            subject=r.get("subject", ""),
            predicate=r.get("predicate", ""),
            object=r.get("object", ""),
        )
        for r in data.get("relationships", [])
    ]

    triplets = [
        Triplet(
            arthropod=t.get("arthropod", ""),
            trait=t.get("trait", ""),
            value=t.get("value", ""),
        )
        for t in data.get("triplets", [])
    ]

    return ExtractionResponse(
        entities=entities,
        relationships=relationships,
        triplets=triplets,
        processing_time_ms=elapsed_ms,
        model_used=model,
    )
