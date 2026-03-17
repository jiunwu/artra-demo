# Evaluation Plan: Comparing Gemini to BioBERT+LUKE (Original Paper)

This document outlines the methodology for evaluating the performance of our Gemini-based, few-shot prompt approach against the fine-tuned BioBERT+LUKE models from the original paper (Cornelius et al., 2025).

## 1. Objectives
The primary objective is to calculate **Precision**, **Recall**, and **F1 Scores** for the zero-shot/few-shot extraction pipeline and compare them directly with the baseline scores reported in the original paper.

## 2. Baseline Metrics (Cornelius et al., 2025)
The original paper employed a heavy pipeline: PubMed Central text → NER (Fine-tuned BioBERT) → RE (Fine-tuned LUKE) → Standardization.

Their baseline metrics are as follows:

### NER (Strict Matching)
| Entity Type | Precision | Recall | F1 Score |
|-------------|-----------|--------|----------|
| Arthropod   | 0.78      | 0.78   | 0.78     |
| Trait       | 0.55      | 0.57   | 0.56     |
| Value       | 0.43      | 0.44   | 0.44     |
| **Macro Avg**| **0.63**  | **0.57**| **0.59** |

### Relation Extraction (RE)
| Relation Type | Precision | Recall | F1 Score |
|---------------|-----------|--------|----------|
| hasTrait      | 0.55      | 0.55   | 0.55     |
| hasValue      | 0.60      | 0.69   | 0.64     |
| **Macro Avg** | **0.66**  | **0.69**| **0.65** |

## 3. Evaluation Methodology

To ensure a fair and rigorous comparison, we will evaluate the current Gemini implementation using the exact same metrics (Precision, Recall, F1).

### 3.1. Datasets
- **Original Dataset Strategy**: The original paper used 25 manually annotated PubMed Central documents for training/testing.
- **Our Dataset**: We have prepared a mock evaluation set (`scripts/evaluation_set.jsonl`) mimicking the structure of the taxonomic texts.
- *Note: For a true 1:1 comparison, the model should ideally be evaluated on the original held-out test set if made available by the authors.*

### 3.2. Automated Pipeline
We have developed an automated offline evaluation pipeline (`scripts/calculate_metrics.py`) that strictly mirrors the evaluation approach of the paper:
1. **Prediction**: `run_inference.py` runs the Gemini API over all items in the evaluation set.
2. **Metrics Calculation**: `calculate_metrics.py` iterates over predicted entities and relations, performing strict string-and-type matching against the ground truth.

### 3.3. Definitions of Metrics
- **True Positive (TP)**: The extracted entity/relation perfectly matches the type and text/arguments of the ground truth.
- **False Positive (FP)**: The extracted entity/relation does not exist in the ground truth.
- **False Negative (FN)**: A ground truth entity/relation was missed by the model.

Formulas:
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1 Score** = 2 * (Precision * Recall) / (Precision + Recall)

## 4. Frontend Integration and Presentation
The final evaluated metrics are integrated into the main web interface (`frontend/index.html`).
- **Endpoint**: The backend exposes `/api/evaluation/metrics` which parses the `predictions.jsonl` results.
- **Display**: The UI contains a "Approach Comparison" table. Initially, this table displays placeholder text ("See scripts/calculate_metrics.py") or "not measured". Upon loading, the client fetches the metrics and updates the specific cells corresponding to `NER F1 Arthropod`, `NER F1 Trait`, `RE F1 hasTrait`, etc.
- **Handling UI Mismatches**: A previous iteration of the UI presented aggregated Macro F1 scores (as seen in screenshots), but the table has been updated to explicitly break down F1 scores per entity/relation type, exactly mapping to the baseline tables.

## 5. Next Steps
1. **Run Inference**: Execute `python scripts/run_inference.py` to populate `predictions.jsonl`.
2. **Calculate**: Execute `python scripts/calculate_metrics.py` to verify the logic.
3. **Verify API**: Start the server and verify that the endpoint `/api/evaluation/metrics` accurately serves these metrics.
4. **Verify UI**: Ensure the JavaScript correctly populates the granular metrics (Arthropod, Trait, Value, hasTrait, hasValue) in the comparison table.
