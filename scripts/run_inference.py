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

    import concurrent.futures

    def process_line(i, line):
        data = json.loads(line)
        text = data["text"]
        try:
            result = extract(text)
            pred_entities = [e.dict() for e in result.entities]
            pred_relationships = [r.dict() for r in result.relationships]
            pred_triplets = [t.dict() for t in result.triplets]
            return {
                "idx": i,
                "data": {
                    "text": text,
                    "ground_truth": data["ground_truth"],
                    "prediction": {
                        "entities": pred_entities,
                        "relationships": pred_relationships,
                        "triplets": pred_triplets,
                        "processing_time_ms": result.processing_time_ms,
                        "model_used": result.model_used
                    }
                }
            }
        except Exception as e:
            return {
                "idx": i,
                "data": {
                    "text": text,
                    "ground_truth": data["ground_truth"],
                    "prediction": {
                        "entities": [],
                        "relationships": [],
                        "triplets": [],
                        "error": str(e)
                    }
                }
            }

    predictions = [None] * len(lines)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_line, i, line) for i, line in enumerate(lines)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            predictions[res["idx"]] = res["data"]

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