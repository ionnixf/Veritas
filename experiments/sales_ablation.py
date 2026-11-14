"""One validation-only ablation: remove both sales features from the fixed blend."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd

from experiments.evaluate import (
    FEATURES, Q, TEST_START, fit_reserves, paired_loss_interval,
    partition_origins, reserve_metrics,
)


CANCELLATION_FEATURES = ["cancel_7d", "cancel_28d_weekly"]
BOUNDARY_DAY = pd.Timestamp("2011-04-04")
REPRODUCE = """python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.evaluate
.venv/bin/python -m experiments.sales_ablation
.venv/bin/python -m unittest experiments.test_sales_ablation -v"""


def boundary_check(daily, day=BOUNDARY_DAY):
    """Inject synthetic invoice lines via daily sums; never touch the source file.

    For each day from D through June 30, add a cancellation invoice with quantity
    -1 and price GBP 1,000 and an ordinary sale with quantity 1 and price GBP 2,000.
    These increments match the importer's invoice-line rules. This checks the
    feature/forecast boundary on supplied aggregates, not workbook parsing.
    """
    daily = daily.loc[daily.index < TEST_START].copy()
    train, before = partition_origins(daily, "validation")
    if day not in before.index:
        raise ValueError("Boundary probe must be an eligible validation origin")
    changed = daily.copy()
    changed.loc[day:, "cancel_gbp"] += 1000.0
    changed.loc[day:, "sales_gbp"] += 2000.0
    changed.loc[day:, "lines"] += 2
    changed_train, after = partition_origins(changed, "validation")
    pd.testing.assert_frame_equal(train, changed_train, check_exact=True)
    pd.testing.assert_index_equal(before.index, after.index)
    feature_columns = FEATURES + ["historical_q80"]
    pd.testing.assert_frame_equal(before.loc[:day, feature_columns],
                                  after.loc[:day, feature_columns], check_exact=True)
    predictions = {}
    for name, features in [("full_blend", FEATURES),
                           ("without_sales_blend", CANCELLATION_FEATURES)]:
        _, original = fit_reserves(train, before, features)
        _, perturbed = fit_reserves(changed_train, after, features)
        pd.testing.assert_frame_equal(original.loc[:day], perturbed.loc[:day], check_exact=True)
        predictions[name] = {"before_gbp": float(original.loc[day, "model_q80"]),
                             "after_gbp": float(perturbed.loc[day, "model_q80"])}
    predictions["training_q80"] = {
        "before_gbp": float(original.loc[day, "training_q80"]),
        "after_gbp": float(perturbed.loc[day, "training_q80"]),
    }
    target_delta = float(after.loc[day, "actual_gbp"] - before.loc[day, "actual_gbp"])
    np.testing.assert_allclose(target_delta, 7000.0, rtol=0, atol=1e-8)
    # A positive control: tomorrow's features must see the added transactions in D.
    next_day = day + pd.Timedelta(days=1)
    np.testing.assert_allclose(
        after.loc[next_day, FEATURES] - before.loc[next_day, FEATURES],
        [1000.0, 250.0, 2000.0, 500.0], rtol=0, atol=1e-8,
    )
    return {
        "passed": True,
        "as_of": str(day.date()),
        "perturbation": "Add GBP 1,000 cancellation and GBP 2,000 sale (two invoice lines) "
                        "per day from D through 2011-06-30, in memory at daily-aggregate level.",
        "train_and_origins_unchanged": True,
        "all_features_through_D_exactly_unchanged": True,
        "features_at_D_before": {key: float(before.loc[day, key]) for key in feature_columns},
        "features_at_D_after": {key: float(after.loc[day, key]) for key in feature_columns},
        "reserves_at_D": predictions,
        "actual_week_before_gbp": float(before.loc[day, "actual_gbp"]),
        "actual_week_after_gbp": float(after.loc[day, "actual_gbp"]),
        "actual_week_delta_gbp": target_delta,
        "next_day_features_respond": True,
        "scope": "Feature and model boundary on daily aggregates; raw workbook parsing not tested.",
    }


def fit_details(method, features):
    scaler, regression = method.steps[0][1], method.steps[1][1]
    slopes = regression.coef_ / scaler.scale_
    return {
        "features": features,
        "scaler_mean_train": scaler.mean_.tolist(),
        "scaler_scale_train": scaler.scale_.tolist(),
        "linear_intercept_gbp": float(regression.intercept_ - slopes @ scaler.mean_),
        "linear_slopes": dict(zip(features, slopes.tolist(), strict=True)),
    }


def write_summary(report, output):
    rows = []
    for name, label in [("training_q80", "Constant train-Q80"),
                        ("full_blend", "Full 50:50 blend"),
                        ("without_sales_blend", "50:50 blend without sales")]:
        metric = report["metrics"][name]
        rows.append(f"| {label} | {metric['pinball_gbp']:,.2f} | {metric['coverage']:.2%} | "
                    f"{metric['mean_shortfall_gbp']:,.2f} | {metric['mean_unused_gbp']:,.2f} |")
    comparison = report["full_minus_without_sales"]
    low, high = comparison["interval_95_gbp"]
    boundary = report["temporal_boundary_check"]
    summary = f"""# ReserveWeek: sales-feature ablation (validation only)

Reproduce from the repository root (pinned packages in `requirements.txt`):

```bash
{REPRODUCE}
```

This command writes `validation_sales_ablation.json`,
`validation_sales_ablation_replay.csv` and this report to `artifacts/`.
The ablation command never writes the interface's `validation_replay.csv` or
`validation_metrics.json`; the standard evaluate command reproduces them unchanged.

## Fixed comparison

333 training origins; training targets finish 2010-12-31. All three methods use
the same 175 validation origins, 2011-01-01 through 2011-06-24 (last target day
2011-06-30). The target is cancellations on D through D+6, with observations only
through D-1. The two retained features are `cancel_7d` and `cancel_28d_weekly`;
only `sales_7d` and `sales_28d_weekly` are removed. Both regressions use the
same train-only StandardScaler and QuantileRegressor(q=0.8, alpha=0, solver=highs),
nonnegative linear forecasts, the same constant train-Q80 and 50:50 blend.
No weight, date, target, hyperparameter or feature search was performed.

Control reproduction passed: train-Q80 GBP 5,381.14 and full blend GBP 5,357.68.
Amounts below are GBP; means include every origin, including zeros.
Coverage is the fraction of seven-day outcomes fully covered, not daily coverage.

| Method | Pinball loss | Coverage | Mean shortfall | Mean unused reserve |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Loss(full blend) minus loss(blend without sales): GBP {comparison['delta_gbp']:,.2f}.
Paired 95% moving-block bootstrap interval: [GBP {low:,.2f}, GBP {high:,.2f}];
14-day blocks, 2,000 draws, seed 2026, using the existing bootstrap implementation
on unrounded per-origin losses. Negative favors sales. The interval includes zero:
these validation data do not establish that sales improve the reserve decision.
The full blend also differs from the constant by only GBP -23.46 in mean loss;
the existing 14-day interval is [GBP -717.90, GBP 290.19]. These are exploratory
validation comparisons; seven-day targets overlap and the blend was previously
tried on validation. This is one retailer and recorded cancellation values, not
refund settlement cash flows.

## Temporal boundary probe

D = {boundary['as_of']}. In memory, add two synthetic invoice lines per day from
D through 2011-06-30: GBP 1,000 cancellation and GBP 2,000 sale. Their contributions
are added to the supplied daily aggregates according to the importer rules.
All features (including historical Q80), training data, origins and all three
reserve predictions through the morning of D remain exactly unchanged.
The actual D..D+6 total changes from GBP {boundary['actual_week_before_gbp']:,.2f}
to GBP {boundary['actual_week_after_gbp']:,.2f}, a GBP 7,000 increase. Tomorrow's
features do change, confirming the perturbation reached the inputs. Assertions
enforce these checks. This tests feature/model timing on daily aggregates;
raw workbook parsing is outside this probe.

The input is truncated before 2011-07-01 before feature construction, fitting,
mutation or scoring. The final period remains closed; no test evaluation ran.

## Jury wording

“On 175 validation dates, adding sales history slightly lowered the fixed blend's
pinball loss, but the paired 95% interval includes zero, so we cannot yet claim
that sales improve cancellation reserves.”

The JSON records input SHA-256, runtime versions, coefficients, scaling,
exact boundary values and bootstrap settings; the separate CSV retains paired
forecasts for audit. Existing CSV field names and meanings are preserved.
"""
    (output / "validation_sales_ablation.md").write_text(summary)


def run(daily_path, output):
    daily = pd.read_csv(daily_path, index_col="date", parse_dates=["date"])
    daily = daily.loc[daily.index < TEST_START].copy()
    train, replay = partition_origins(daily, "validation")
    full_method, full = fit_reserves(train, replay)
    reduced_method, reduced = fit_reserves(train, replay, CANCELLATION_FEATURES)
    pd.testing.assert_series_equal(full.training_q80, reduced.training_q80, check_exact=True)
    metrics = {
        "training_q80": reserve_metrics(replay.actual_gbp, full.training_q80),
        "full_blend": reserve_metrics(replay.actual_gbp, full.model_q80),
        "without_sales_blend": reserve_metrics(replay.actual_gbp, reduced.model_q80),
    }
    # Fail rather than silently report results from changed dates/data or fit conditions.
    if len(train) != 333 or len(replay) != 175:
        raise ValueError("Validation origins differ from the fixed experiment")
    if (metrics["training_q80"]["pinball_gbp"] != 5381.14
            or metrics["full_blend"]["pinball_gbp"] != 5357.68):
        raise ValueError("Validation control scores differ from the fixed experiment")
    report = {
        "split": "validation",
        "reproduce_commands": REPRODUCE.splitlines(),
        "daily_path": str(daily_path),
        "daily_sha256": hashlib.sha256(daily_path.read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), **{
            package: version(package) for package in
            ["numpy", "pandas", "scikit-learn", "scipy", "python-calamine"]}},
        "quantile": Q, "weight_on_linear": 0.5,
        "train_origins": len(train),
        "train_first_origin": str(train.index[0].date()),
        "train_last_origin": str(train.index[-1].date()),
        "train_last_target_day": str((train.index[-1] + pd.Timedelta(days=6)).date()),
        "first_origin": str(replay.index[0].date()),
        "last_origin": str(replay.index[-1].date()),
        "validation_last_target_day": str((replay.index[-1] + pd.Timedelta(days=6)).date()),
        "origins": len(replay),
        "control_reproduction_passed": True,
        "metrics": metrics,
        "fits": {"full": fit_details(full_method, FEATURES),
                 "without_sales": fit_details(reduced_method, CANCELLATION_FEATURES)},
        "bootstrap": {"method": "existing paired moving-block bootstrap",
                      "block_days": 14, "draws": 2000, "seed": 2026,
                      "difference": "loss(full blend) - loss(blend without sales)",
                      "negative_favors": "full blend (sales features)"},
        "full_minus_without_sales": paired_loss_interval(
            replay.actual_gbp, reduced.model_q80, full.model_q80, 14),
        "temporal_boundary_check": boundary_check(daily),
        "final_test_evaluated": False,
    }
    output.mkdir(parents=True, exist_ok=True)
    paired = pd.DataFrame({
        "actual_gbp": replay.actual_gbp,
        "training_q80": full.training_q80,
        "linear_q80": full.linear_q80,
        "model_q80": full.model_q80,
        "linear_without_sales_q80": reduced.linear_q80,
        "model_without_sales_q80": reduced.model_q80,
    })
    paired.rename_axis("as_of").to_csv(output / "validation_sales_ablation_replay.csv",
                                      float_format="%.4f")
    (output / "validation_sales_ablation.json").write_text(json.dumps(report, indent=2) + "\n")
    write_summary(report, output)
    print(json.dumps({key: report[key] for key in
                      ["origins", "metrics", "full_minus_without_sales", "final_test_evaluated"]},
                     indent=2))
    print(f"Boundary probe at {BOUNDARY_DAY.date()}: PASS; actual week changes by GBP 7,000.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily", type=Path, default=Path("data/processed/daily.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    run(args.daily, args.output)
