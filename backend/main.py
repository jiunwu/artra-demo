import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load .env if present
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

import json
from models import ExtractionRequest, ExtractionResponse, ALLOWED_MODELS
import extractor
import pmc

# Import metrics calculation if available
try:
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    import calculate_metrics
except ImportError:
    calculate_metrics = None

app = FastAPI(title="ArTra Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Real taxonomic texts from open-access peer-reviewed literature
EXAMPLE_TEXTS = [
    {
        "id": 1,
        "title": "Mahabadphora aesthesphora (Diptera: Phoridae)",
        "source": "PLOS ONE, DOI: 10.1371/journal.pone.0257899",
        "text": (
            "Male holotype: Wing length 1.44 mm. Costal index 0.31. Costal ratios about 5: 1.3: 1. "
            "Frons without median furrow, bearing paired short supra-antennal bristles and four long "
            "bristles per side. Mesopleuron has hairs; scutellum displays one pair of long bristles "
            "and one pair of short hairs. Tergite hairs notably small; ventral surface lacks hairs. "
            "Left epandrial lobe smaller than right; epandrium features strong bristles. Hind tibia "
            "lacks dorsal hair palisade. Very pale wing, basal third of wing exhibits minimal "
            "pigmentation; the single axillary bristle 0.05 mm long. Holotype locality: Iran, West "
            "Azerbaijan Province, Mahabad City (36°34.16'N, 45°41.21'E, 1521 m elevation), collected "
            "July 23, 2018."
        ),
    },
    {
        "id": 2,
        "title": "Tetradonia lizonae & laselvensis (Coleoptera: Staphylinidae)",
        "source": "PLOS ONE, DOI: 10.1371/journal.pone.0165056",
        "text": (
            "Tetradonia lizonae von Beeren & Maruyama sp. nov. Body length 3.9–4.4 mm; fore body "
            "1.9–2.0 mm; head width 0.75–0.76 mm; pronotal length 0.59–0.63 mm; pronotal width "
            "0.75–0.76 mm. Coloration: uniformly reddish brown with blackish-brown head. Small "
            "spineless beetle with extremely large eyes occupying entire head sides. Long antennae "
            "equal to combined head-pronotum-elytra length. Elytra weakly granulate-punctate. "
            "Associated with army ant colonies (Eciton burchellii) in lowland tropical forest. "
            "Tetradonia laselvensis Maruyama & von Beeren sp. nov. Body length 3.8–4.3 mm; fore "
            "body 1.8–2.0 mm; head width 0.66–0.71 mm; pronotal width 0.72–0.81 mm. Coloration: "
            "reddish brown body; head, pronotum, and elytral apical halves darker brown. Small "
            "spineless species with moderate-sized eyes. Elytra strongly granulate-punctate. "
            "Found in association with army ant colonies in La Selva Biological Station, Costa Rica."
        ),
    },
    {
        "id": 3,
        "title": "Ommatoiulus avatar n. sp. (Diplopoda: Julida: Julidae)",
        "source": "PLOS ONE, DOI: 10.1371/journal.pone.0135243",
        "text": (
            "Ommatoiulus avatar n. sp. Males measure body length 25.6–33.2 mm; height 2.1–2.9 mm, "
            "42–46 podous rings. Females: body length 26–38.2 mm; height 2.5–3.5 mm, 46–52 podous "
            "rings. Coloration after preservation: brownish with yellowish and black marbling most "
            "pronounced dorsally. Head chestnut-brown on frontal part with labral margin and "
            "mouthparts bright reddish-brown. Legs light brown with characteristic dark striping on "
            "body segments. The new species most closely resembles Ommatoiulus bavayi but differs "
            "significantly in genital structure: the solenomerite is much broader with a distal "
            "lamella, and the paracoxite is notably more serrated, broader and complex. Distribution: "
            "known exclusively from Spain, Andalusia; specimens collected from pine forests and "
            "mountain locations around Competa and Canillas de Albaida."
        ),
    },
    {
        "id": 4,
        "title": "Multilingual Extraction (Chinese)",
        "source": "Mock Data",
        "text": (
            "新種 Pachybrachis sassii sp. nov. 的體長為 5.6 mm，主要棲息於地中海氣候的灌木叢中。"
        ),
    },
]


@app.get("/api/health")
def health():
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
    return {"status": "ok", "gemini_available": bool(gemini_key), "nvidia_nim_available": bool(nvidia_key)}


@app.get("/api/examples")
def examples():
    return EXAMPLE_TEXTS


@app.get("/api/pmc/mine")
def mine_pmc():
    try:
        result = pmc.mine_pmc_text()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mine PMC text: {str(e)}")


@app.get("/api/pmc/search")
def search_pmc(term: str, limit: int = 10):
    try:
        result = pmc.search_pmc(term, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search PMC: {str(e)}")


@app.get("/api/evaluation/metrics")
def get_evaluation_metrics():
    """Returns the pre-calculated offline evaluation metrics from scripts/predictions.jsonl."""
    if not calculate_metrics:
        raise HTTPException(status_code=500, detail="Metrics module not found.")

    predictions_file = Path(__file__).parent.parent / "scripts" / "predictions.jsonl"
    if not predictions_file.exists():
        return {"status": "pending", "message": "Offline evaluation has not been run yet. Execute scripts/run_inference.py to generate predictions."}

    try:
        total_ner, total_re, total_triplets = calculate_metrics.calculate_all_metrics(str(predictions_file))

        # Calculate F1s
        ner_f1_sum = sum(calculate_metrics.calculate_precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])[2] for counts in total_ner.values())
        re_f1_sum = sum(calculate_metrics.calculate_precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])[2] for counts in total_re.values())

        macro_ner_f1 = ner_f1_sum / max(1, len(total_ner))
        macro_re_f1 = re_f1_sum / max(1, len(total_re))

        # Detailed metrics
        ner_details = {k: calculate_metrics.calculate_precision_recall_f1(v["tp"], v["fp"], v["fn"])[2] for k, v in total_ner.items()}
        re_details = {k: calculate_metrics.calculate_precision_recall_f1(v["tp"], v["fp"], v["fn"])[2] for k, v in total_re.items()}

        return {
            "status": "success",
            "metrics": {
                "ner": {
                    "macro_f1": round(macro_ner_f1, 2),
                    "details": {k: round(v, 2) for k, v in ner_details.items()}
                },
                "re": {
                    "macro_f1": round(macro_re_f1, 2),
                    "details": {k: round(v, 2) for k, v in re_details.items()}
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@app.post("/api/extract", response_model=ExtractionResponse)
def extract(request: ExtractionRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(request.text) > 10000:
        raise HTTPException(status_code=400, detail="Text too long (max 10000 chars)")
    model = request.model or "gemini-3.1-flash-lite-preview"
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Allowed: {', '.join(ALLOWED_MODELS)}")
    try:
        return extractor.extract(request.text, model=model)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


# Serve frontend
@app.get("/")
def serve_index():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
