"""Audit the existing frozen test artifacts without fitting or selecting a model."""

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd


PROTOCOL_SHA = "06407270d4d7c972832c86ed0b74c7ab07f54aad"
IMPLEMENTATION_SHA = "76fc2f76af2494aadb7bca6bcfd57a7d849108e9"
FROZEN_HASHES = {
    "data/processed/daily.csv": "78e3b7691b41995ec380221cac416a71f5e12e7102ed6435128b27833ebba30c",
    "experiments/evaluate.py": "e5e44ba7d5c09d4e98632068973b320329367cc9a5b66ed3fd9df5db80e24242",
    "requirements.txt": "b18d4db4962da9e8fd1db12ec32e792e0a80eda9d5aa69109e40b7a8c00a9cfd",
}
METHODS = ("last_week", "training_q80", "historical_q80", "linear_q80", "model_q80")
FEATURES = ("cancel_7d", "cancel_28d_weekly", "sales_7d", "sales_28d_weekly")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, atol=0.0002):
    # The replay CSV stores four decimals, while JSON scores use full precision.
    np.testing.assert_allclose(actual, expected, atol=atol, rtol=0)


def audit():
    for path, expected in FROZEN_HASHES.items():
        require(sha256(path) == expected, f"Frozen input changed: {path}")
    report = json.loads(Path("artifacts/test_metrics.json").read_text())
    daily = pd.read_csv("data/processed/daily.csv", index_col="date", parse_dates=["date"])
    replay = pd.read_csv("artifacts/test_replay.csv", index_col="as_of", parse_dates=["as_of"])
    schema = [*FEATURES, "historical_q80", "actual_gbp", "linear_q80",
              "last_week", "training_q80", "model_q80"]
    require(list(replay.columns) == schema, "Replay CSV schema changed")
    require(report["split"] == "test" and report["quantile"] == 0.8, "Wrong split/quantile")
    require(report["weight_on_linear"] == 0.5, "Blend weight changed")
    require(daily.index.equals(pd.date_range(daily.index.min(), daily.index.max())),
            "Daily input is not continuous")
    expected_dates = pd.date_range("2011-07-01", daily.index.max() - pd.Timedelta(days=6))
    require(replay.index.equals(expected_dates), "Missing/extra/out-of-order test dates")
    require(len(replay) == report["origins"], "Origin count mismatch")
    require(str(replay.index[0].date()) == report["first_origin"], "First origin mismatch")
    require(str(replay.index[-1].date()) == report["last_origin"], "Last origin mismatch")
    require(np.isfinite(replay.to_numpy()).all() and replay.ge(0).all().all(),
            "Nonfinite or negative replay values")

    # Independently reconstruct history and labels; no model fitting occurs here.
    features = pd.DataFrame(index=daily.index)
    for column, prefix in (("cancel_gbp", "cancel"), ("sales_gbp", "sales")):
        history = daily[column].shift(1)
        features[f"{prefix}_7d"] = history.rolling(7).sum()
        features[f"{prefix}_28d_weekly"] = history.rolling(28).sum() / 4
    weeks = pd.concat([features.cancel_7d.shift(7 * i) for i in range(8)], axis=1)
    features["historical_q80"] = weeks.quantile(0.8, axis=1).where(weeks.notna().all(axis=1))
    features["actual_gbp"] = sum(daily.cancel_gbp.shift(-i) for i in range(7))
    eligible = features.dropna()
    train = eligible.loc[eligible.index + pd.Timedelta(days=6) < pd.Timestamp("2011-01-01")]
    require(len(train) == report["train_origins"] == 333, "Training window changed")
    require(str((train.index[-1] + pd.Timedelta(days=6)).date()) ==
            report["train_last_target_day"] == "2010-12-31", "Training boundary changed")
    for column in features.columns:
        close(replay[column], features.loc[replay.index, column])
    close(replay.training_q80, train.actual_gbp.quantile(0.8))
    close(replay.last_week, replay.cancel_7d)
    linear = report["linear_intercept_gbp"] + sum(
        features.loc[replay.index, name] * report["linear_slopes"][name] for name in FEATURES)
    close(replay.linear_q80, np.maximum(0, linear))
    close(replay.model_q80, 0.5 * (replay.linear_q80 + replay.training_q80))
    validation = json.loads(Path("artifacts/validation_metrics.json").read_text())
    close(report["linear_intercept_gbp"], validation["linear_intercept_gbp"], atol=1e-8)
    for name in FEATURES:
        close(report["linear_slopes"][name], validation["linear_slopes"][name], atol=1e-10)

    losses = {}
    for name in METHODS:
        shortfall = (replay.actual_gbp - replay[name]).clip(lower=0)
        unused = (replay[name] - replay.actual_gbp).clip(lower=0)
        losses[name] = (0.8 * shortfall + 0.2 * unused).to_numpy()
        metrics = report["metrics"][name]
        close(losses[name].mean(), metrics["pinball_gbp"], atol=0.0051)
        close(shortfall.mean(), metrics["mean_shortfall_gbp"], atol=0.0051)
        close(unused.mean(), metrics["mean_unused_gbp"], atol=0.0051)
        close((shortfall == 0).mean(), metrics["coverage"], atol=0.000051)
        require(int((shortfall > 0).sum()) == metrics["shortfall_days"], "Shortfall count mismatch")

    delta = losses["model_q80"] - losses["training_q80"]
    for block in (7, 14, 28):
        # Independent resampling from the saved, rounded predictions. Tolerance
        # allows their four-decimal serialization and two-decimal reported CIs.
        rng = np.random.default_rng(2026)
        draws = []
        for _ in range(2000):
            starts = rng.integers(0, len(delta) - block + 1,
                                  size=(len(delta) + block - 1) // block)
            sample = np.concatenate([delta[start:start + block] for start in starts])[:len(delta)]
            draws.append(sample.mean())
        comparison = report["comparison_vs_training_q80"][f"block_{block}d"]
        close(delta.mean(), comparison["delta_gbp"], atol=0.0051)
        close(np.quantile(draws, [0.025, 0.975]), comparison["interval_95_gbp"], atol=0.0051)

    audit_report = {
        "protocol_commit": PROTOCOL_SHA,
        "implementation_commit": IMPLEMENTATION_SHA,
        "command": ".venv-ml-final/bin/python -m experiments.evaluate --split test",
        "final_evaluator_invocations_by_this_owner": 1,
        "audit_command": ".venv-ml-final/bin/python -m experiments.audit_final",
        "audit_refits_model": False,
        "python": platform.python_version(),
        "packages": {name: version(name) for name in (
            "numpy", "pandas", "python-calamine", "scikit-learn", "scipy", "joblib",
            "threadpoolctl", "narwhals", "cloudpickle", "python-dateutil", "tzdata")},
        "sha256": {path: sha256(path) for path in (
            *FROZEN_HASHES, "experiments/final_protocol.md", "experiments/audit_final.py",
            "artifacts/test_metrics.json", "artifacts/test_replay.csv")},
        "origins": len(replay),
        "first_origin": str(replay.index[0].date()),
        "last_origin": str(replay.index[-1].date()),
        "last_target_day": str((replay.index[-1] + pd.Timedelta(days=6)).date()),
        "currency": "GBP",
        "delta_definition": "mean pinball(full blend) minus mean pinball(constant train-Q80)",
        "checks_passed": ["frozen hashes", "CSV schema", "consecutive complete target dates",
                          "train boundary and count", "history through D-1", "D through D+6 targets",
                          "constant and last-week baselines", "linear formula and 50:50 blend",
                          "unchanged validation fit", "all method metrics", "all paired bootstrap intervals"],
    }
    Path("artifacts/final_run.json").write_text(json.dumps(audit_report, indent=2) + "\n")
    print(json.dumps(audit_report, indent=2))


if __name__ == "__main__":
    audit()
