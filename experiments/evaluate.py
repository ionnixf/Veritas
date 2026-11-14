"""Fit a fixed 80th-percentile forecast, then replay validation or frozen test dates."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import QuantileRegressor
from sklearn.metrics import mean_pinball_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


Q = 0.80
VAL_START = pd.Timestamp("2011-01-01")
TEST_START = pd.Timestamp("2011-07-01")
FEATURES = ["cancel_7d", "cancel_28d_weekly", "sales_7d", "sales_28d_weekly"]


def paired_loss_interval(actual, baseline, model, block_size):
    """Moving-block bootstrap of the paired mean loss difference; negative favors model."""
    def losses(reserve):
        error = actual.to_numpy() - reserve.to_numpy()
        return np.maximum(Q * error, (Q - 1) * error)

    diff = losses(model) - losses(baseline)
    rng = np.random.default_rng(2026)
    count = (len(diff) + block_size - 1) // block_size
    starts = rng.integers(0, len(diff) - block_size + 1, size=(2000, count))
    indices = (starts[:, :, None] + np.arange(block_size)).reshape(2000, -1)[:, :len(diff)]
    bounds = np.quantile(diff[indices].mean(axis=1), [0.025, 0.975])
    return {"delta_gbp": round(float(diff.mean()), 2), "interval_95_gbp": bounds.round(2).tolist()}


def forecast_origins(daily):
    if not daily.index.equals(pd.date_range(daily.index.min(), daily.index.max(), freq="D")):
        raise ValueError("daily.csv must have one row per consecutive calendar day in date order")
    values = daily[["cancel_gbp", "sales_gbp"]]
    if not np.isfinite(values.to_numpy()).all() or values.lt(0).any().any():
        raise ValueError("The daily totals must be finite and nonnegative")
    past = values.shift(1)  # Forecast at opening, before today's transactions.
    frame = pd.DataFrame(index=daily.index)
    for column, prefix in [("cancel_gbp", "cancel"), ("sales_gbp", "sales")]:
        frame[f"{prefix}_7d"] = past[column].rolling(7).sum()
        frame[f"{prefix}_28d_weekly"] = past[column].rolling(28).sum() / 4
    weeks = pd.concat([frame.cancel_7d.shift(7 * i) for i in range(8)], axis=1)
    frame["historical_q80"] = weeks.quantile(Q, axis=1).where(weeks.notna().all(axis=1))
    frame["actual_gbp"] = daily.cancel_gbp.rolling(7).sum().shift(-6)
    return frame.dropna()


def evaluate(daily, split, output):
    if split == "validation":
        daily = daily.loc[daily.index < TEST_START]
    frame = forecast_origins(daily)
    # The seven-day target must finish before the next partition begins.
    train = frame.loc[frame.index + pd.Timedelta(days=6) < VAL_START]
    if split == "validation":
        replay = frame.loc[frame.index >= VAL_START].copy()
    else:
        replay = frame.loc[frame.index >= TEST_START].copy()
    if train.empty or replay.empty:
        raise ValueError("Daily series does not cover the required training and replay periods")
    method = make_pipeline(StandardScaler(), QuantileRegressor(quantile=Q, alpha=0, solver="highs"))
    method.fit(train[FEATURES], train.actual_gbp)
    replay["linear_q80"] = np.maximum(0, method.predict(replay[FEATURES]))
    replay["last_week"] = replay.cancel_7d
    replay["training_q80"] = train.actual_gbp.quantile(Q)
    replay["model_q80"] = 0.5 * replay.linear_q80 + 0.5 * replay.training_q80
    metrics = {}
    for name in ["last_week", "training_q80", "historical_q80", "linear_q80", "model_q80"]:
        actual, reserve = replay.actual_gbp, replay[name]
        metrics[name] = {
            "pinball_gbp": round(float(mean_pinball_loss(actual, reserve, alpha=Q)), 2),
            "coverage": round(float((actual <= reserve).mean()), 4),
            "shortfall_days": int((actual > reserve).sum()),
            "mean_shortfall_gbp": round(float((actual - reserve).clip(lower=0).mean()), 2),
            "mean_unused_gbp": round(float((reserve - actual).clip(lower=0).mean()), 2),
        }
    # Convert the standardized fit back to GBP-scale slopes for exact local explanations.
    scaler, regression = method.steps[0][1], method.steps[1][1]
    slopes = regression.coef_ / scaler.scale_
    formula = {key: float(value) for key, value in zip(FEATURES, slopes, strict=True)}
    report = {"split": split, "quantile": Q, "train_origins": len(train),
              "linear_intercept_gbp": float(regression.intercept_ - slopes @ scaler.mean_),
              "linear_slopes": formula, "weight_on_linear": 0.5,
              "comparison_vs_training_q80": {f"block_{block}d": paired_loss_interval(
                  replay.actual_gbp, replay.training_q80, replay.model_q80, block)
                  for block in (7, 14, 28)},
              "train_last_target_day": str((train.index[-1] + pd.Timedelta(days=6)).date()),
              "first_origin": str(replay.index.min().date()), "last_origin": str(replay.index.max().date()),
              "origins": len(replay), "metrics": metrics}
    output.mkdir(parents=True, exist_ok=True)
    replay.rename_axis("as_of").to_csv(output / f"{split}_replay.csv", float_format="%.4f")
    (output / f"{split}_metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily", type=Path, default=Path("data/processed/daily.csv"))
    parser.add_argument("--split", choices=["validation", "test"], default="validation")
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    evaluate(pd.read_csv(args.daily, index_col="date", parse_dates=["date"]), args.split, args.output)
