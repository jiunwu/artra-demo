SYSTEM_PROMPT = """You are a biodiversity literature expert. Extract arthropod traits from taxonomic text.

Extract three entity types:
- Arthropod: taxonomic names (species, genus, family, order) e.g. Drosophila melanogaster, Coleoptera
- Trait: biological characteristics e.g. body length, habitat, feeding ecology, coloration
- Value: specific values/descriptions for traits e.g. 5.6 mm, tropical forest, herbivorous

And produce triplets in the form: {arthropod, trait, value}

Return ONLY valid JSON with this exact structure:
{
  "entities": [
    {"text": "...", "type": "Arthropod|Trait|Value"}
  ],
  "relationships": [
    {"subject": "...", "predicate": "hasTrait|hasValue", "object": "..."}
  ],
  "triplets": [
    {"arthropod": "...", "trait": "...", "value": "..."}
  ]
}"""

FEW_SHOT_EXAMPLES = [
    {
        "input": "Aedes aegypti (Diptera, Culicidae) has a body length of 4–7 mm and is found in tropical urban areas worldwide. The species is a blood-feeding ectoparasite, primarily active during daytime.",
        "output": """{
  "entities": [
    {"text": "Aedes aegypti", "type": "Arthropod"},
    {"text": "Diptera", "type": "Arthropod"},
    {"text": "Culicidae", "type": "Arthropod"},
    {"text": "body length", "type": "Trait"},
    {"text": "4–7 mm", "type": "Value"},
    {"text": "habitat", "type": "Trait"},
    {"text": "tropical urban areas", "type": "Value"},
    {"text": "distribution", "type": "Trait"},
    {"text": "worldwide", "type": "Value"},
    {"text": "feeding ecology", "type": "Trait"},
    {"text": "blood-feeding ectoparasite", "type": "Value"},
    {"text": "activity pattern", "type": "Trait"},
    {"text": "daytime", "type": "Value"}
  ],
  "relationships": [
    {"subject": "Aedes aegypti", "predicate": "hasTrait", "object": "body length"},
    {"subject": "body length", "predicate": "hasValue", "object": "4–7 mm"},
    {"subject": "Aedes aegypti", "predicate": "hasTrait", "object": "habitat"},
    {"subject": "habitat", "predicate": "hasValue", "object": "tropical urban areas"},
    {"subject": "Aedes aegypti", "predicate": "hasTrait", "object": "distribution"},
    {"subject": "distribution", "predicate": "hasValue", "object": "worldwide"},
    {"subject": "Aedes aegypti", "predicate": "hasTrait", "object": "feeding ecology"},
    {"subject": "feeding ecology", "predicate": "hasValue", "object": "blood-feeding ectoparasite"},
    {"subject": "Aedes aegypti", "predicate": "hasTrait", "object": "activity pattern"},
    {"subject": "activity pattern", "predicate": "hasValue", "object": "daytime"}
  ],
  "triplets": [
    {"arthropod": "Aedes aegypti", "trait": "body length", "value": "4–7 mm"},
    {"arthropod": "Aedes aegypti", "trait": "habitat", "value": "tropical urban areas"},
    {"arthropod": "Aedes aegypti", "trait": "distribution", "value": "worldwide"},
    {"arthropod": "Aedes aegypti", "trait": "feeding ecology", "value": "blood-feeding ectoparasite"},
    {"arthropod": "Aedes aegypti", "trait": "activity pattern", "value": "daytime"}
  ]
}"""
    },
    {
        "input": "The spider Argiope bruennichi (Araneae, Araneidae) constructs orb webs in grassland habitats across Europe and Asia. Females have a body length of 15–25 mm with distinctive yellow and black banding on the abdomen. Males are significantly smaller at 4–6 mm.",
        "output": """{
  "entities": [
    {"text": "Argiope bruennichi", "type": "Arthropod"},
    {"text": "Araneae", "type": "Arthropod"},
    {"text": "Araneidae", "type": "Arthropod"},
    {"text": "web type", "type": "Trait"},
    {"text": "orb webs", "type": "Value"},
    {"text": "habitat", "type": "Trait"},
    {"text": "grassland", "type": "Value"},
    {"text": "distribution", "type": "Trait"},
    {"text": "Europe and Asia", "type": "Value"},
    {"text": "body length (female)", "type": "Trait"},
    {"text": "15–25 mm", "type": "Value"},
    {"text": "coloration", "type": "Trait"},
    {"text": "yellow and black banding on the abdomen", "type": "Value"},
    {"text": "body length (male)", "type": "Trait"},
    {"text": "4–6 mm", "type": "Value"}
  ],
  "relationships": [
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "web type"},
    {"subject": "web type", "predicate": "hasValue", "object": "orb webs"},
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "habitat"},
    {"subject": "habitat", "predicate": "hasValue", "object": "grassland"},
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "distribution"},
    {"subject": "distribution", "predicate": "hasValue", "object": "Europe and Asia"},
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "body length (female)"},
    {"subject": "body length (female)", "predicate": "hasValue", "object": "15–25 mm"},
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "coloration"},
    {"subject": "coloration", "predicate": "hasValue", "object": "yellow and black banding on the abdomen"},
    {"subject": "Argiope bruennichi", "predicate": "hasTrait", "object": "body length (male)"},
    {"subject": "body length (male)", "predicate": "hasValue", "object": "4–6 mm"}
  ],
  "triplets": [
    {"arthropod": "Argiope bruennichi", "trait": "web type", "value": "orb webs"},
    {"arthropod": "Argiope bruennichi", "trait": "habitat", "value": "grassland"},
    {"arthropod": "Argiope bruennichi", "trait": "distribution", "value": "Europe and Asia"},
    {"arthropod": "Argiope bruennichi", "trait": "body length (female)", "value": "15–25 mm"},
    {"arthropod": "Argiope bruennichi", "trait": "coloration", "value": "yellow and black banding on the abdomen"},
    {"arthropod": "Argiope bruennichi", "trait": "body length (male)", "value": "4–6 mm"}
  ]
}"""
    }
]


def build_prompt(text: str) -> str:
    """Build the full few-shot prompt for a given input text."""
    parts = [SYSTEM_PROMPT, ""]

    for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
        parts.append(f"[Example {i}]")
        parts.append(f"Input: {example['input']}")
        parts.append(f"Output: {example['output']}")
        parts.append("")

    parts.append("[Now extract from this text]")
    parts.append(f"Input: {text}")
    parts.append("Output:")

    return "\n".join(parts)
