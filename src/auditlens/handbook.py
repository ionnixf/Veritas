"""Interpretable transaction input and strictly past-only, target-free history.

No persistent shared state: callers supply history explicitly for each batch.
Every rolling window is [t-window, t), excluding ALL simultaneous observations.
"""
from pathlib import Path

import joblib
import numpy as np
import polars as pl
from threadpoolctl import threadpool_limits

from .io import read_table, validate_record_ids

RAW_COLUMNS = ["record_id", "timestamp", "customer_id", "terminal_id", "amount"]
FEATURE_VERSION = "handbook-past-only-v1"
FEATURES = ["amount", "log_amount", "hour_sin", "hour_cos", "weekday", "weekend"]
for _entity, _windows in [("customer", (1, 7, 30)), ("terminal", (1, 7))]:
    for _days in _windows:
        FEATURES += [f"{_entity}_{s}_{_days}d" for s in ("count", "sum", "mean", "std")]
FEATURES += ["customer_amount_ratio", "customer_amount_z", "customer_cold", "terminal_cold",
             "pair_count_30d", "pair_new"]


def validate_transactions(frame):
    if not isinstance(frame, pl.DataFrame):
        raise ValueError("Input must be a Polars DataFrame")
    if not frame.height or frame.height > 2_000_000:
        raise ValueError("Need 1..2,000,000 rows including history")
    if set(frame.columns) != set(RAW_COLUMNS):
        raise ValueError(f"Exact required columns: {RAW_COLUMNS}; target and extra fields forbidden")
    validate_record_ids(frame)
    for col in ("customer_id", "terminal_id"):
        if frame[col].dtype != pl.String or frame[col].null_count() or frame[col].str.strip_chars().eq("").any():
            raise ValueError(f"{col} must contain nonempty text IDs")
    if frame["amount"].dtype == pl.Boolean:
        raise ValueError("amount must be numeric, not boolean")
    try:
        amount = frame["amount"].cast(pl.Float64, strict=True)
    except Exception as error:
        raise ValueError("amount must be numeric") from error
    if not np.isfinite(amount.to_numpy()).all() or (amount < 0).any():
        raise ValueError("amount must be finite, complete and nonnegative")
    # Explicit UTC convention: ISO wall times with no suffix are interpreted as UTC.
    # Uniform format prevents silently mixing offsets/local times in exported files.
    timestamp = frame["timestamp"]
    if timestamp.dtype == pl.String:
        try:
            timestamp = timestamp.str.to_datetime(format="%Y-%m-%dT%H:%M:%S", strict=True)
        except Exception as error:
            raise ValueError("timestamp requires YYYY-MM-DDTHH:MM:SS in UTC (without suffix)") from error
    elif not isinstance(timestamp.dtype, pl.Datetime) or timestamp.dtype.time_zone is not None:
        raise ValueError("timestamp must be UTC wall-time text or timezone-naive datetime")
    if timestamp.null_count():
        raise ValueError("timestamp must be complete")
    return frame.select(RAW_COLUMNS).with_columns(amount, timestamp.cast(pl.Datetime("us")))


def source_transactions(frame):
    """Explicit publisher-to-public-schema mapping, labels excluded by construction."""
    return frame.select(
        pl.col("TRANSACTION_ID").cast(pl.String).alias("record_id"),
        pl.col("TX_DATETIME").cast(pl.Datetime("us")).alias("timestamp"),
        pl.col("CUSTOMER_ID").cast(pl.String).alias("customer_id"),
        pl.col("TERMINAL_ID").cast(pl.String).alias("terminal_id"),
        pl.col("TX_AMOUNT").cast(pl.Float64).alias("amount"),
    )


def past_features(frame):
    """Return float features in original input order, invariant to future suffixes."""
    frame = validate_transactions(frame).with_row_index("_order").sort(["timestamp", "_order"])
    seconds = frame["timestamp"].dt.hour() * 3600.0 + frame["timestamp"].dt.minute() * 60.0
    seconds = seconds + frame["timestamp"].dt.second()
    result = frame.with_columns(
        pl.col("amount").log1p().alias("log_amount"),
        pl.Series("hour_sin", np.sin(2 * np.pi * seconds.to_numpy() / 86400)),
        pl.Series("hour_cos", np.cos(2 * np.pi * seconds.to_numpy() / 86400)),
        (pl.col("timestamp").dt.weekday() - 1).cast(pl.Float64).alias("weekday"),
        (pl.col("timestamp").dt.weekday() >= 6).cast(pl.Float64).alias("weekend"),
    )
    for entity, windows in [("customer", (1, 7, 30)), ("terminal", (1, 7))]:
        key = f"{entity}_id"
        grouped = frame.sort([key, "timestamp", "_order"])
        for days in windows:
            stats = grouped.rolling("timestamp", period=f"{days}d", group_by=key, closed="left").agg(
                pl.len().alias(f"{entity}_count_{days}d"),
                pl.col("amount").sum().alias(f"{entity}_sum_{days}d"),
                pl.col("amount").mean().alias(f"{entity}_mean_{days}d"),
                pl.col("amount").std(ddof=0).alias(f"{entity}_std_{days}d"),
            )
            # Group output order is NOT an alignment contract. Join on semantic
            # keys; simultaneous records have identical left-closed history.
            stats = stats.unique(subset=[key, "timestamp"], maintain_order=True)
            result = result.join(stats, on=[key, "timestamp"], validate="m:1", maintain_order="left")
    grouped = frame.sort(["customer_id", "terminal_id", "timestamp", "_order"])
    pair = grouped.rolling("timestamp", period="30d", group_by=["customer_id", "terminal_id"],
                           closed="left").agg(pl.len().alias("pair_count_30d"))
    pair_keys = ["customer_id", "terminal_id", "timestamp"]
    result = result.join(pair.unique(subset=pair_keys, maintain_order=True),
                         on=pair_keys, validate="m:1", maintain_order="left").fill_null(0)
    result = result.with_columns(
        (pl.col("amount") / (pl.col("customer_mean_30d") + 1)).alias("customer_amount_ratio"),
        ((pl.col("amount") - pl.col("customer_mean_30d")) / (pl.col("customer_std_30d") + 1))
        .alias("customer_amount_z"),
        (pl.col("customer_count_30d") == 0).cast(pl.Float64).alias("customer_cold"),
        (pl.col("terminal_count_7d") == 0).cast(pl.Float64).alias("terminal_cold"),
        (pl.col("pair_count_30d") == 0).cast(pl.Float64).alias("pair_new"),
    )
    features = result.sort("_order").select(FEATURES).cast(pl.Float32)
    if not np.isfinite(features.to_numpy()).all():
        raise ValueError("Input amounts produce nonfinite float32 features; numeric range unsupported")
    return features


class HandbookModel:
    """CPU batch scoring. History is supplied, never secretly recovered from training."""
    def __init__(self, directory, threads=2):
        import json
        if threads not in (1, 2):
            raise ValueError("Serving supports 1 or 2 threads")
        self.directory = Path(directory)
        self.metadata = json.loads((self.directory / "metadata.json").read_text())
        if self.metadata["feature_version"] != FEATURE_VERSION or self.metadata["features"] != FEATURES:
            raise ValueError("Artifact feature contract mismatch")
        self.pipeline = joblib.load(self.directory / "pipeline.joblib")
        self.threads = threads
        if self.metadata["kind"] == "xgboost":
            self.pipeline.set_params(device="cpu", n_jobs=threads)
        elif self.metadata["kind"] == "lightgbm":
            self.pipeline.set_params(n_jobs=threads)

    def prepare(self, frame, history=None):
        current = validate_transactions(frame)
        if history is None:
            return past_features(current)
        history = validate_transactions(history)
        if history["timestamp"].max() >= current["timestamp"].min():
            raise ValueError("All explicit history must strictly precede the earliest batch timestamp")
        if set(history["record_id"].to_list()) & set(current["record_id"].to_list()):
            raise ValueError("History and batch record_id must be disjoint")
        combined = pl.concat([history, current])
        return past_features(combined).tail(current.height)

    def analyze(self, frame, *, history=None, top_k=None, explain=True):
        from .inference import DISCLAIMER, top_results
        if top_k is not None and (type(top_k) is not int or top_k < 1):
            raise ValueError("top_k must be a positive integer")
        features = self.prepare(frame, history)
        with threadpool_limits(limits=self.threads):
            scores = self.pipeline.predict_proba(features.to_numpy())[:, 1]
        rows = []
        for i, values in enumerate(features.iter_rows(named=True)):
            warnings = ["Synthetic benchmark only; uncalibrated score; no real-bank validation",
                        "Requires stable IDs, one currency/unit and at least 30 days of supplied history for full windows",
                        "No fraud-label history; terminal compromise can be unobservable"]
            if values["customer_cold"]:
                warnings.append("Customer cold start: no earlier customer transaction in 30 days")
            if values["terminal_cold"]:
                warnings.append("Terminal cold start: no earlier terminal transaction in 7 days")
            reasons = [f"amount={values['amount']:.2f}; customer prior-30d mean={values['customer_mean_30d']:.2f}",
                       f"customer prior-1d count={values['customer_count_1d']:.0f}; prior-7d count={values['customer_count_7d']:.0f}",
                       f"customer-terminal prior-30d count={values['pair_count_30d']:.0f}"] if explain else []
            rows.append(dict(record_id=frame["record_id"][i], module="handbook", risk_score=float(scores[i]),
                             score_kind="uncalibrated_classifier_score",
                             review_required=bool(scores[i] >= self.metadata["threshold"]),
                             reasons=reasons, explanation_kind="observed_past_history_not_model_attribution",
                             missing_features=[], model_version=self.directory.name,
                             supported_domain="Handbook synthetic transaction schema; single currency/unit",
                             validation_status="RESEARCH DEMO", warnings=warnings, disclaimer=DISCLAIMER))
        return top_results(rows, top_k)

    def analyze_file(self, path, *, history_path=None, **kwargs):
        history = read_table(history_path) if history_path else None
        return self.analyze(read_table(path), history=history, **kwargs)
