# ReserveWeek: sales-feature ablation (validation only)

Reproduce from the repository root (pinned packages in `requirements.txt`):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.evaluate
.venv/bin/python -m experiments.sales_ablation
.venv/bin/python -m unittest experiments.test_sales_ablation -v
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
| Constant train-Q80 | 5,381.14 | 84.00% | 4,412.19 | 9,256.94 |
| Full 50:50 blend | 5,357.68 | 80.57% | 4,553.50 | 8,574.42 |
| 50:50 blend without sales | 5,454.88 | 84.00% | 4,283.40 | 10,140.78 |

Loss(full blend) minus loss(blend without sales): GBP -97.20.
Paired 95% moving-block bootstrap interval: [GBP -697.76, GBP 140.05];
14-day blocks, 2,000 draws, seed 2026, using the existing bootstrap implementation
on unrounded per-origin losses. Negative favors sales. The interval includes zero:
these validation data do not establish that sales improve the reserve decision.
The full blend also differs from the constant by only GBP -23.46 in mean loss;
the existing 14-day interval is [GBP -717.90, GBP 290.19]. These are exploratory
validation comparisons; seven-day targets overlap and the blend was previously
tried on validation. This is one retailer and recorded cancellation values, not
refund settlement cash flows.

## Temporal boundary probe

D = 2011-04-04. In memory, add two synthetic invoice lines per day from
D through 2011-06-30: GBP 1,000 cancellation and GBP 2,000 sale. Their contributions
are added to the supplied daily aggregates according to the importer rules.
All features (including historical Q80), training data, origins and all three
reserve predictions through the morning of D remain exactly unchanged.
The actual D..D+6 total changes from GBP 12,885.66
to GBP 19,885.66, a GBP 7,000 increase. Tomorrow's
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
