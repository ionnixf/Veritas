# ReserveWeek frozen final evaluation protocol

Frozen on 2026-11-14, before this owner opens the test outcomes. This file is
committed separately before the single final `--split test` invocation.

## Provenance and ownership

- Owner: participant 2, branch `codex/ml-final`; no other final run is requested.
- Implementation commit: `76fc2f76af2494aadb7bca6bcfd57a7d849108e9`
  (`origin/codex/team-start` at branch creation; includes ML commit `61c0399`).
- `experiments/evaluate.py` Git blob: `4fb04abc988b6f98b2755a6e2afdad8053952e97`.
- Evaluator SHA-256: `e5e44ba7d5c09d4e98632068973b320329367cc9a5b66ed3fd9df5db80e24242`.
- `data/processed/daily.csv` SHA-256:
  `78e3b7691b41995ec380221cac416a71f5e12e7102ed6435128b27833ebba30c`.
- `requirements.txt` SHA-256:
  `b18d4db4962da9e8fd1db12ec32e792e0a80eda9d5aa69109e40b7a8c00a9cfd`.
- Audit before disclosure: fetched all origin branches; no tracked
  `experiments/final_protocol.md`, `artifacts/final_results.md`,
  `artifacts/test_metrics.json` or `artifacts/test_replay.csv` in the fetched
  history. Existing team reports describe validation only and explicitly leave
  test closed. No prior recorded final run was found.
- Read `README.md`, `experiments/evaluate.py` and
  `artifacts/validation_sales_ablation.md`. All three
  `experiments.test_sales_ablation` tests passed in the isolated environment;
  `pip check` passed. Only validation outcomes were examined before this commit.

## Locked model, data and chronology

Use the evaluator and aggregate data above unchanged. The target at opening on D
is the sum of recorded cancellation values on D through D+6, in GBP. Features
use observations through D-1: `cancel_7d`, `cancel_28d_weekly`, `sales_7d`,
`sales_28d_weekly`. Keep all four; sales ablation remains validation evidence.

Keep q=0.8, train-only StandardScaler and QuantileRegressor(quantile=0.8,
alpha=0, solver="highs"), clipping the linear forecast at zero. The primary
model is the fixed 50:50 blend of that linear forecast and constant train-Q80.
Keep the original training window: targets finish by 2010-12-31 (333 origins,
last origin 2010-12-25), with no refit on validation. Validation origins are
2011-01-01 through 2011-06-24, targets ending by 2011-06-30. Test origins start
2011-07-01 and end at the last date admitting a complete seven-day target under
the existing code. Do not adjust any dates, features, weights or hyperparameters
after disclosure.

## Locked comparisons and interpretation

Primary comparator: constant 80th percentile of training targets (`training_q80`).
Primary statistic: mean pinball loss(full blend) minus mean pinball
loss(constant train-Q80). At each origin, pinball loss is
`0.8 * max(actual - reserve, 0) + 0.2 * max(reserve - actual, 0)`.
Negative differences favor the blend; positive differences favor the constant.

Use the existing paired moving-block bootstrap on unrounded per-origin loss
differences: consecutive overlapping 14-day blocks, sampled with replacement
from valid block starts, concatenate and truncate to the number of origins;
2,000 draws, NumPy default_rng seed 2026, percentile 2.5%/97.5% bounds.
Report 7-day and 28-day blocks as sensitivity, without selecting a block by its
result. Seven-day targets overlap; origins are not independent weekly trials.

If the primary interval includes zero, state that an advantage is not established.
If the constant has lower observed loss, say so even if the interval includes
zero; distinguish observed ranking from an established advantage. Report all
existing methods, including last week's amount, without choosing a new model.
Also report coverage of the entire seven-day target, mean shortfall and mean
unused reserve over all origins (including zeros), all monetary means in GBP.
The hypothetical 4:1 shortfall/unused cost motivates q=0.8; it is not measured
cash cost or a claim of realized savings.

## Execution and delivery

Isolated runtime: CPython 3.15.0, `.venv-ml-final`, installed from the unchanged
`requirements.txt`. Direct pins: NumPy 2.5.4, pandas 3.1.1, python-calamine 0.9.1,
scikit-learn 1.9.1, SciPy 1.18.1. Preserve installed versions in final provenance.

```bash
python3 -m venv .venv-ml-final
.venv-ml-final/bin/python -m pip install -r requirements.txt
.venv-ml-final/bin/python -m unittest experiments.test_sales_ablation -v
# Commit this protocol before proceeding.
.venv-ml-final/bin/python -m experiments.evaluate --split test
```

The single final run writes `artifacts/test_metrics.json` and
`artifacts/test_replay.csv`, preserving the existing CSV schema. Audit the
number and continuity of dates, target boundaries, units, metrics and difference
sign. Publish `artifacts/final_results.md` with one compact English results table,
the primary and sensitivity intervals, exact period and count, and one checked
English sentence for the write-up/video. Identify the large 2011-01-18 error as
validation, not a test example. State the limits: one retailer, cancellation
values from the invoice log, and unknown actual payout dates.

After disclosure, only audit/report the frozen run; do not tune or replace the
model. Push `codex/ml-final`, open a PR into `codex/team-start`, and hand off its
URL, this protocol commit SHA and the checked sentence.
