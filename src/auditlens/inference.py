"""Load the trusted, frozen CPU transaction model."""

import json
from pathlib import Path

DISCLAIMER = "This project is a prototype and is not financial advice."
REGISTRY = Path(__file__).resolve().parents[2] / "models/registry.json"


def top_results(results, top_k):
    if top_k is not None and (isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1):
        raise ValueError("top_k must be a positive integer")
    ordered = sorted(results, key=lambda r: -r["risk_score"])
    return [dict(r, rank=i + 1) for i, r in enumerate(ordered[:top_k])]


def load_registered_model(model_id, *, registry_path=REGISTRY, threads=2, allow_research=False):
    """Explicit routing; no schema-based guessing or incompatible fallback."""
    path = Path(registry_path)
    entries = json.loads(path.read_text())["models"]
    if model_id not in entries:
        raise ValueError(f"Unknown registered model: {model_id}")
    entry = entries[model_id]
    if not entry.get("servable", False):
        raise ValueError(f"Model is not served: {model_id} ({entry['status']})")
    if entry["status"] != "RECOMMENDED" and not allow_research:
        raise ValueError("Research model requires explicit allow_research=True")
    if entry["dataset"] != "handbook":
        raise ValueError("Only the Handbook transaction model is supported")
    from .handbook import HandbookModel

    model = HandbookModel(path.parent.parent / entry["artifact_directory"], threads=threads)
    if model.metadata["config"]["dataset"] != entry["dataset"]:
        raise ValueError("Registry dataset does not match artifact")
    model.serving_info = entry
    return model
