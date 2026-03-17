import json
import re

def parse_sample_texts(filepath="reference/sample_texts.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by "## Example "
    examples_raw = re.split(r"## Example \d+:", content)[1:]

    dataset = []

    for ex in examples_raw:
        # Extract the source text
        text_match = re.search(r"```(?:\w*\n)?(.*?)```", ex, re.DOTALL)
        if not text_match:
            continue
        text = text_match.group(1).strip()

        # Extract the expected JSON
        json_match = re.search(r"\*\*Expected extraction\*\*:\s*```json\n(.*?)\n```", ex, re.DOTALL)
        if not json_match:
            # Let's see if there is a Mini Example format
            json_match = re.search(r"\*\*Output\*\*:\s*```json\n(.*?)\n```", ex, re.DOTALL)
            if not json_match:
                continue

        json_str = json_match.group(1).strip()

        try:
            expected_data = json.loads(json_str)

            # Normalize structure
            if "entities" not in expected_data:
                expected_data["entities"] = []
            if "relationships" not in expected_data:
                expected_data["relationships"] = []
            if "triplets" not in expected_data:
                expected_data["triplets"] = []

            dataset.append({
                "text": text,
                "ground_truth": expected_data
            })
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for example: {e}")
            continue

    # Also check for Mini Examples
    mini_examples = re.split(r"### Mini Example \w+", content)[1:]
    for ex in mini_examples:
        text_match = re.search(r"\*\*Input\*\*:\s*`(.*?)`", ex, re.DOTALL)
        json_match = re.search(r"\*\*Output\*\*:\s*```json\n(.*?)\n```", ex, re.DOTALL)

        if text_match and json_match:
            text = text_match.group(1).strip()
            json_str = json_match.group(1).strip()
            try:
                expected_data = json.loads(json_str)
                # Normalize structure
                if "entities" not in expected_data:
                    expected_data["entities"] = []
                if "relationships" not in expected_data:
                    expected_data["relationships"] = []
                if "triplets" not in expected_data:
                    expected_data["triplets"] = []

                dataset.append({
                    "text": text,
                    "ground_truth": expected_data
                })
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for mini example: {e}")
                continue


    return dataset

def main():
    dataset = parse_sample_texts()
    print(f"Parsed {len(dataset)} examples.")

    output_path = "scripts/evaluation_set.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote dataset to {output_path}")

if __name__ == "__main__":
    main()