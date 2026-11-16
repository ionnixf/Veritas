"""Thin integration over the existing frozen Handbook pipeline."""

import json
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

from auditlens.inference import REGISTRY, load_registered_model

from .errors import APIError

ROOT = REGISTRY.parent.parent
BENCHMARK = ROOT / "models/handbook-xgboost-v1/benchmark.json"
ASSETS = Path(__file__).parent / "assets"
LIMITATIONS = [
    "All historical Handbook results are from synthetic data; no demonstrated real-bank effectiveness.",
    "September test was opened before the history-alignment correction; this is not a pristine independent holdout.",
    "The model practically does not detect terminal compromise (scenario 2).",
    "Scores are uncalibrated review priorities, not fraud probabilities or proof of wrongdoing.",
    "Explanations describe observed history, not causal or SHAP model attributions.",
    "Arbitrary bank statements are unsupported; exact schema, stable IDs and compatible history are required.",
]


def metric_summary(metrics):
    return {
        **{
            key: metrics[key]
            for key in ("n", "positives", "precision", "recall", "average_precision", "f1", "threshold")
        },
        "precision_at_1000": metrics["ranking"]["1000"]["precision"],
        "positives_at_1000": metrics["ranking"]["1000"]["expected_positives"],
    }


class HandbookService:
    def __init__(self, settings):
        self.settings = settings
        report = json.loads(BENCHMARK.read_text())
        self.candidate = report["candidate"]
        entries = json.loads(REGISTRY.read_text())["models"]
        matches = [
            (key, entry)
            for key, entry in entries.items()
            if entry["dataset"] == "handbook"
            and entry["model_version"] == self.candidate["id"]
            and entry.get("servable")
        ]
        if len(matches) != 1:
            raise RuntimeError("Expected one registered selected Handbook XGBoost route")
        self.model_id, self.entry = matches[0]
        metadata = json.loads((ROOT / self.entry["artifact_directory"] / "metadata.json").read_text())
        self.split_periods = {
            split: metadata[key]
            for split, key in (
                ("train", "training_period"),
                ("validation", "validation_period"),
                ("test", "test_period"),
            )
        }
        self.baselines = report["baselines"]
        self.report_date = report["date"]
        self.model = None

    def load(self):
        self.model = load_registered_model(self.model_id, threads=self.settings.threads, allow_research=True)

    def health(self):
        return dict(
            status="ready" if self.model is not None else "unavailable",
            model_available=self.model is not None,
            model_id=self.model_id,
            model_version=self.entry["model_version"],
            device="cpu",
        )

    def describe(self):
        return dict(
            model_id=self.model_id,
            name="Handbook XGBoost",
            version=self.entry["model_version"],
            available=self.model is not None,
            research_status=self.entry["status"],
            recommended_for_live_detection=False,
            score_kind=self.entry["score_kind"],
            input_schema=self.entry["input_schema"],
            file_types=["csv", "xlsx"],
            history_requirements={
                "required_for_acceptance": False,
                "customer_pair_complete_calendar_days": 30,
                "terminal_days": 7,
                "same_schema": True,
                "strictly_before_earliest_transaction": True,
                "disjoint_record_ids": True,
                "completeness_verifiable": False,
                "cold_start": "Accepted with warnings; earlier batch rows build history; simultaneous rows excluded.",
            },
            limits=asdict(self.settings),
            limitations=list(dict.fromkeys(LIMITATIONS + self.entry["limitations"])),
            benchmark={split: metric_summary(self.candidate[split]) for split in ("validation", "test")},
            baselines={name: metric_summary(metrics) for name, metrics in self.baselines.items()},
            benchmark_provenance={
                "source": "models/handbook-xgboost-v1/benchmark.json",
                "narrative": "README.md",
                "date": self.report_date,
                "synthetic": True,
                "dataset_rows": 1_754_155,
                "test_period": "September",
                "split_periods": self.split_periods,
                "test_previously_opened": True,
                "history_alignment_corrected": True,
                "test_caveat": self.candidate["test_caveat"],
                "ranking_policy": self.candidate["test"]["ranking_policy"],
                "terminal_compromise_recall": self.candidate["test"]["scenarios"]["2"]["recall_at_threshold"],
                "metrics_recomputed": False,
            },
        )

    def analyze(self, current, history, top_k):
        if self.model is None:
            raise APIError(503, "model_unavailable", "Registered Handbook model could not be loaded.")
        history_count = 0 if history is None else history.height
        if current.height + history_count > self.settings.max_combined_rows:
            raise APIError(413, "row_limit", "Combined transaction and history row limit exceeded.")
        coverage = [
            "History completeness cannot be verified; supply all relevant transactions in the preceding windows."
        ]
        first_day = current["timestamp"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        if history is None:
            coverage.append(
                "No history supplied: initial rows may have customer/terminal cold starts and incomplete windows."
            )
        elif first_day - history["timestamp"].min() < timedelta(days=30):
            coverage.append(
                "Insufficient history coverage: fewer than 30 preceding complete calendar days; customer/pair windows may be incomplete."
            )
        try:
            # Analyze the whole batch to include warnings for rows outside the chosen queue.
            rows = self.model.analyze(current, history=history)
        except ValueError as exc:
            raise APIError(
                422,
                "invalid_history_or_values",
                "History must strictly precede the batch with disjoint IDs; amounts must support finite derived features.",
            ) from exc
        originals = {r["record_id"]: r for r in current.to_dicts()}
        warnings = list(dict.fromkeys(coverage + [w for row in rows for w in row["warnings"]]))
        operations = []
        for row in rows[:top_k]:
            source = dict(originals[row["record_id"]])
            source["timestamp"] = source["timestamp"].isoformat(timespec="seconds")
            operations.append(
                {
                    **source,
                    "rank": row["rank"],
                    "score": row["risk_score"],
                    **{
                        key: row[key]
                        for key in (
                            "score_kind",
                            "reasons",
                            "explanation_kind",
                            "review_required",
                            "model_version",
                            "validation_status",
                        )
                    },
                    "warnings": list(dict.fromkeys(coverage + row["warnings"])),
                }
            )
        return dict(
            analyzed_count=current.height,
            history_count=history_count,
            top_k=top_k,
            queue_count=len(operations),
            operations=operations,
            warnings=warnings,
            model_id=self.model_id,
            model_version=self.entry["model_version"],
        )
