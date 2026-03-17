import json
import os
import sys

# Add backend to path so we can import extractor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from extractor import extract

def run_inference(input_file="scripts/evaluation_set.jsonl", output_file="scripts/predictions.jsonl"):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Run prepare_dataset.py first.")
        return

    predictions = []

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        data = json.loads(line)
        text = data["text"]
        print(f"Processing example {i+1}/{len(lines)}...")

        try:
            # We are using few-shot via Gemini
            result = extract(text)

            # Convert objects to dicts for JSON serialization
            pred_entities = [e.dict() for e in result.entities]
            pred_relationships = [r.dict() for r in result.relationships]
            pred_triplets = [t.dict() for t in result.triplets]

            predictions.append({
                "text": text,
                "ground_truth": data["ground_truth"],
                "prediction": {
                    "entities": pred_entities,
                    "relationships": pred_relationships,
                    "triplets": pred_triplets,
                    "processing_time_ms": result.processing_time_ms,
                    "model_used": result.model_used
                }
            })
            print(f"  Extracted {len(pred_triplets)} triplets.")
        except Exception as e:
            print(f"Error processing example {i+1}: {e}")
            # Add an empty prediction to keep alignment
            predictions.append({
                "text": text,
                "ground_truth": data["ground_truth"],
                "prediction": {
                    "entities": [],
                    "relationships": [],
                    "triplets": [],
                    "error": str(e)
                }
            })

    with open(output_file, "w", encoding="utf-8") as f:
        for item in predictions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote predictions to {output_file}")

if __name__ == "__main__":
    # Ensure API key is set or mock it for testing script execution if needed.
    # We will just print instructions if the API key is not set.
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("NVIDIA_API_KEY"):
         print("Warning: GEMINI_API_KEY or NVIDIA_API_KEY not set in environment. Inference will fail.")
    run_inference()