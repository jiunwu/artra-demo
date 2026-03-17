# ArTra Demo - Evaluation Plan

## 1. Objective

To rigorously evaluate the performance of Large Language Models (LLMs), primarily Google Gemini (via few-shot learning), on the task of extracting arthropod traits from taxonomic literature, and to compare this performance against the baseline established by Cornelius et al. (2025) using fine-tuned BioBERT and LUKE models.

## 2. Methodology

### 2.1 Dataset Preparation
We need a ground truth dataset to measure against. Ideally, this should be the same evaluation set used in the original paper, or a representative subset.
1.  **Sourcing**: Obtain the manually annotated test set (from the 25 papers annotated by experts mentioned in `paper_context.md`) from the ArTraDB project, if publicly available.
2.  **Formatting**: Convert the original IOB2/standoff annotations into the target JSON format expected by our LLM pipeline (Entities, Relationships, Triplets).
3.  **Stratification**: Ensure the test set contains a balanced mix of:
    *   Simple descriptions (single species).
    *   Comparative descriptions (multiple species).
    *   Complex taxonomic treatments (nested hierarchies, varied contexts).

### 2.2 LLM Configuration & Inference
*   **Model**: Primarily `gemini-2.0-flash` (or newer/alternative models as specified in the UI/backend).
*   **Prompting Strategy**: Use the few-shot prompt defined in `backend/prompts.py`. Ensure the prompt remains consistent across all evaluation runs.
*   **Execution**: Run the `extract` function on every document in the test set. Log the exact raw JSON output, processing time, and the specific model version used.

### 2.3 Metric Calculation
Evaluation will be performed at three levels, matching the original paper's methodology where possible to ensure a fair comparison.

#### 2.3.1 Named Entity Recognition (NER)
Evaluate the extraction of `Arthropod`, `Trait`, and `Value` entities.
*   **Criteria**:
    *   **Strict Match**: The extracted entity text and type must exactly match the ground truth. (Consider character offsets if available, but string matching is often more robust for LLMs that might slightly alter boundaries).
    *   **Relaxed/Partial Match (Optional)**: The extracted entity overlaps with the ground truth or is a synonym (useful for qualitative analysis, but strict match is needed for baseline comparison).
*   **Metrics per Entity Type**:
    *   **True Positives (TP)**: LLM correctly identifies an entity.
    *   **False Positives (FP)**: LLM identifies an entity not in ground truth.
    *   **False Negatives (FN)**: LLM misses an entity present in ground truth.
    *   $Precision = \frac{TP}{TP + FP}$
    *   $Recall = \frac{TP}{TP + FN}$
    *   $F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$
*   **Macro-average**: Calculate the unweighted mean of Precision, Recall, and F1 across all three entity types.

#### 2.3.2 Relation Extraction (RE)
Evaluate the extraction of `hasTrait` (Arthropod $\rightarrow$ Trait) and `hasValue` (Trait $\rightarrow$ Value) relationships.
*   **Criteria**: A relationship is considered correct (TP) if and only if both the subject and object entities are correctly identified (Strict Match) AND the relationship type is correct.
*   **Metrics per Relation Type**: Precision, Recall, and F1.
*   **Macro-average**: Calculate the unweighted mean across the two relationship types.

#### 2.3.3 Triplet Extraction (End-to-End)
This is the most crucial metric for the application's actual utility: successfully extracting the complete (Arthropod $\rightarrow$ Trait $\rightarrow$ Value) triplet.
*   **Criteria**: A triplet is correct (TP) if the Arthropod, Trait, and Value strings all match a valid triplet in the ground truth.
*   **Metrics**: Precision, Recall, F1 for the overall triplet extraction.

## 3. Comparison to Baseline

The computed metrics will be directly compared against the baseline figures provided in `paper_context.md`:

| Metric Level | Target Type | Baseline F1 | LLM F1 (Expected) |
| :--- | :--- | :--- | :--- |
| NER | Arthropod | 0.78 (Strict) | To be determined |
| NER | Trait | 0.56 (Strict) | To be determined |
| NER | Value | 0.44 (Strict) | To be determined |
| NER | Macro avg | 0.59 (Strict) | To be determined |
| RE | hasTrait | 0.55 | To be determined |
| RE | hasValue | 0.64 | To be determined |
| RE | Macro avg | 0.65 | To be determined |

## 4. Technical Implementation Steps for Evaluation

To automate this evaluation, the following scripts should be developed in a `scripts/` or `eval/` directory:

1.  **`prepare_dataset.py`**:
    *   Downloads or reads raw annotated data.
    *   Parses the original format and outputs a standard `evaluation_set.jsonl` where each line is `{"text": "...", "ground_truth": {"entities": [...], "relationships": [...], "triplets": [...]}}`.
2.  **`run_inference.py`**:
    *   Reads `evaluation_set.jsonl`.
    *   Calls `backend.extractor.extract()` for each text.
    *   Saves the predictions to `predictions.jsonl`.
3.  **`calculate_metrics.py`**:
    *   Takes `evaluation_set.jsonl` and `predictions.jsonl` as input.
    *   Implements the logic to calculate TP, FP, FN for NER, RE, and Triplets.
    *   Calculates Precision, Recall, F1.
    *   Outputs a formatted report (e.g., Markdown table) comparing the results against the baseline.

## 5. Error Analysis
Beyond quantitative metrics, a qualitative error analysis should be conducted on a sample of FP and FN cases to understand *why* the LLM failed. Common failure modes to look for:
*   **Boundary errors**: Including surrounding punctuation or adjectives in entity spans.
*   **Implicit relations**: Failing to link a trait to an arthropod mentioned several sentences prior.
*   **Hallucinations**: Inventing traits or values not present in the text (rare in this extraction setup, but possible).
*   **Formatting failures**: LLM failing to return valid JSON, resulting in a zero score for that document.