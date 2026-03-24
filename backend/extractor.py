import os
import json
import re
import time
from google import genai
from openai import OpenAI
from models import Entity, Relationship, Triplet, ExtractionResponse, NIM_MODELS
from prompts import build_prompt

_gemini_client: genai.Client | None = None
_nim_client: OpenAI | None = None


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def get_nim_client() -> OpenAI:
    global _nim_client
    if _nim_client is None:
        use_local_llm = _is_truthy(os.environ.get("USE_LOCAL_LLM"))
        if use_local_llm:
            local_base_url = os.environ.get("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8080/v1").strip()
            local_api_key = os.environ.get("LOCAL_LLM_API_KEY") or "local"
            _nim_client = OpenAI(base_url=local_base_url, api_key=local_api_key)
        else:
            api_key = os.environ.get("NVIDIA_API_KEY")
            if not api_key:
                raise ValueError("NVIDIA_API_KEY environment variable not set")
            _nim_client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
    return _nim_client


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


def _call_gemini(prompt: str, model: str) -> str:
    client = get_gemini_client()
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or ""


def _call_nim(prompt: str, model: str) -> str:
    client = get_nim_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content or ""


def extract(text: str, model: str = "gemini-3.1-flash-lite-preview") -> ExtractionResponse:
    """Call LLM API and extract entities, relationships, and triplets."""
    prompt = build_prompt(text)

    start_ms = time.time()
    if model in NIM_MODELS:
        raw = _call_nim(prompt, model)
    else:
        raw = _call_gemini(prompt, model)
    elapsed_ms = int((time.time() - start_ms) * 1000)
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
            is_novel=e.get("is_novel"),
            ecological_context=e.get("ecological_context"),
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
