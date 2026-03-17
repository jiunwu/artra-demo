import json
import os
from typing import List, Dict, Tuple

def calculate_precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def evaluate_ner(ground_truth: List[Dict], prediction: List[Dict]) -> Dict:
    metrics = {
        "Arthropod": {"tp": 0, "fp": 0, "fn": 0},
        "Trait": {"tp": 0, "fp": 0, "fn": 0},
        "Value": {"tp": 0, "fp": 0, "fn": 0}
    }

    # We match strictly by text and type
    def normalize_entity(e):
        return (str(e.get("text", "")).lower().strip(), str(e.get("type", "")).capitalize())

    gt_entities = [normalize_entity(e) for e in ground_truth]
    pred_entities = [normalize_entity(e) for e in prediction]

    # Calculate TP, FP
    for p in pred_entities:
        e_type = p[1]
        if e_type in metrics:
            if p in gt_entities:
                metrics[e_type]["tp"] += 1
                gt_entities.remove(p) # Remove to handle duplicates properly
            else:
                metrics[e_type]["fp"] += 1

    # Calculate FN (remaining gt_entities)
    for g in gt_entities:
        e_type = g[1]
        if e_type in metrics:
            metrics[e_type]["fn"] += 1

    return metrics

def evaluate_re(ground_truth: List[Dict], prediction: List[Dict]) -> Dict:
    metrics = {
        "hasTrait": {"tp": 0, "fp": 0, "fn": 0},
        "hasValue": {"tp": 0, "fp": 0, "fn": 0}
    }

    def normalize_rel(r):
        return (
            str(r.get("subject", "")).lower().strip(),
            str(r.get("predicate", "")),
            str(r.get("object", "")).lower().strip()
        )

    gt_rels = [normalize_rel(r) for r in ground_truth]
    pred_rels = [normalize_rel(r) for r in prediction]

    for p in pred_rels:
        r_type = p[1]
        if r_type in metrics:
            if p in gt_rels:
                metrics[r_type]["tp"] += 1
                gt_rels.remove(p)
            else:
                metrics[r_type]["fp"] += 1

    for g in gt_rels:
        r_type = g[1]
        if r_type in metrics:
            metrics[r_type]["fn"] += 1

    return metrics

def evaluate_triplets(ground_truth: List[Dict], prediction: List[Dict]) -> Dict:
    metrics = {"tp": 0, "fp": 0, "fn": 0}

    def normalize_trip(t):
        return (
            str(t.get("arthropod", "")).lower().strip(),
            str(t.get("trait", "")).lower().strip(),
            str(t.get("value", "")).lower().strip()
        )

    gt_trips = [normalize_trip(t) for t in ground_truth]
    pred_trips = [normalize_trip(t) for t in prediction]

    for p in pred_trips:
        if p in gt_trips:
            metrics["tp"] += 1
            gt_trips.remove(p)
        else:
            metrics["fp"] += 1

    for g in gt_trips:
        metrics["fn"] += 1

    return metrics

def calculate_all_metrics(predictions_file="scripts/predictions.jsonl"):
    if not os.path.exists(predictions_file):
        print(f"Predictions file {predictions_file} not found. Run run_inference.py first.")
        return None, None, None

    total_ner = {
        "Arthropod": {"tp": 0, "fp": 0, "fn": 0},
        "Trait": {"tp": 0, "fp": 0, "fn": 0},
        "Value": {"tp": 0, "fp": 0, "fn": 0}
    }
    total_re = {
        "hasTrait": {"tp": 0, "fp": 0, "fn": 0},
        "hasValue": {"tp": 0, "fp": 0, "fn": 0}
    }
    total_triplets = {"tp": 0, "fp": 0, "fn": 0}

    with open(predictions_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            gt = data.get("ground_truth", {})
            pred = data.get("prediction", {})

            # Entities
            ner_metrics = evaluate_ner(gt.get("entities", []), pred.get("entities", []))
            for k, v in ner_metrics.items():
                total_ner[k]["tp"] += v["tp"]
                total_ner[k]["fp"] += v["fp"]
                total_ner[k]["fn"] += v["fn"]

            # Relationships
            re_metrics = evaluate_re(gt.get("relationships", []), pred.get("relationships", []))
            for k, v in re_metrics.items():
                total_re[k]["tp"] += v["tp"]
                total_re[k]["fp"] += v["fp"]
                total_re[k]["fn"] += v["fn"]

            # Triplets
            trip_metrics = evaluate_triplets(gt.get("triplets", []), pred.get("triplets", []))
            total_triplets["tp"] += trip_metrics["tp"]
            total_triplets["fp"] += trip_metrics["fp"]
            total_triplets["fn"] += trip_metrics["fn"]


    print("=== Evaluation Results ===\n")

    print("--- Named Entity Recognition (NER) ---")
    print(f"{'Type':<15} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 55)
    f1_sum = 0
    for e_type, counts in total_ner.items():
        p, r, f1 = calculate_precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])
        f1_sum += f1
        print(f"{e_type:<15} | {p:<10.2f} | {r:<10.2f} | {f1:<10.2f}")
    print(f"{'Macro Avg':<15} | {'-':<10} | {'-':<10} | {f1_sum/3:<10.2f}")
    print("\n")

    print("--- Relation Extraction (RE) ---")
    print(f"{'Type':<15} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 55)
    f1_sum = 0
    for r_type, counts in total_re.items():
        p, r, f1 = calculate_precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])
        f1_sum += f1
        print(f"{r_type:<15} | {p:<10.2f} | {r:<10.2f} | {f1:<10.2f}")
    print(f"{'Macro Avg':<15} | {'-':<10} | {'-':<10} | {f1_sum/2:<10.2f}")
    print("\n")

    print("--- Triplet Extraction (End-to-End) ---")
    print(f"{'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 35)
    p, r, f1 = calculate_precision_recall_f1(total_triplets["tp"], total_triplets["fp"], total_triplets["fn"])
    print(f"{p:<10.2f} | {r:<10.2f} | {f1:<10.2f}")
    print("\n")

    return total_ner, total_re, total_triplets

if __name__ == "__main__":
    calculate_all_metrics()