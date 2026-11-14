# ReserveWeek final held-out results

The frozen final evaluation covers **155 consecutive decision dates,
2011-07-01 through 2011-12-02**. Each decision forecasts the seven-day recorded
cancellation total on D through D+6; the final target ends **2011-12-08**.
The original **333 training origins** are unchanged, with training targets ending
2010-12-31. Validation was not added to training. All amounts and losses below
are **GBP per decision origin**; lower q=0.8 pinball loss is better.

| Method | Pinball loss (£) | Coverage | Mean shortfall (£) | Mean unused reserve (£) |
| --- | ---: | ---: | ---: | ---: |
| Previous week's cancellations | 4,950.14 | 53.55% | 5,105.87 | 4,327.24 |
| Constant train-Q80 (primary comparator) | 2,483.98 | 76.13% | 1,340.02 | 7,059.82 |
| Q80 of eight completed weeks | 2,741.83 | 70.32% | 1,726.93 | 6,801.44 |
| Linear Q80, all four features | 2,967.01 | 93.55% | 124.17 | 14,338.35 |
| Frozen full 50:50 blend (primary model) | 2,455.68 | 87.74% | 462.28 | 10,429.27 |

Coverage is the fraction of origins whose entire seven-day cancellation target
fits inside the reserve. Shortfall and unused reserve are averaged over every
origin, including zeros. Pinball loss equals 0.8 × shortfall + 0.2 × unused
reserve; the 4:1 cost ratio is hypothetical, not an observed monetary saving.

The primary paired difference is **loss(full blend) − loss(constant train-Q80)
= −£28.30**; negative favors the blend. Its **95% moving-block bootstrap
interval is [−£484.27, £707.08]**, using 14-day blocks, 2,000 draws and seed 2026.
Sensitivity intervals are [−£467.37, £632.49] for 7-day blocks and
[−£565.26, £476.74] for 28-day blocks, with the same draws and seed settings.
All intervals include zero: **the test does not establish an advantage over the
constant reserve**. Overlapping weekly targets are not independent trials.

The blend has the lowest observed loss, but its improvement over the constant
is small and uncertain. Relative to the constant, it reduces mean shortfall
by £877.74 while increasing mean unused reserve by £3,369.45. Relative to the
previous-week rule, its observed loss is £2,494.46 lower. These secondary
descriptions do not replace the predeclared primary comparison. No model,
feature, weight or training-window change followed test disclosure.

## Checked sentence for the write-up and video

“On 155 held-out decision dates, our fixed blend had £28.30 lower mean pinball
loss than the constant reserve, but the paired 95% interval includes zero, so
an advantage is not established.”

## Failure example and limits

**2011-01-18 is a validation example**, not part of the final test. The proposed
reserve was **£24,050.42**, recorded cancellations over the following seven days
were **£81,851.42**, and shortfall was **£57,801.00**. The sales-feature ablation
also remains a validation-only result; no sales ablation was run on test.

This is **one retailer**, using **cancellation values from the invoice log**.
**Actual payout dates are unknown**; the target does not measure settlement
cash flows, cash balances or stock purchasing decisions. The results do not
establish transfer to other shops. This project is a prototype and is not
financial advice.

## Provenance and reproduction

- Pre-disclosure protocol commit:
  [`06407270d4d7c972832c86ed0b74c7ab07f54aad`](https://github.com/ionnixf/Veritas/commit/06407270d4d7c972832c86ed0b74c7ab07f54aad),
  [frozen protocol](../experiments/final_protocol.md).
- Unchanged implementation commit:
  `76fc2f76af2494aadb7bca6bcfd57a7d849108e9` (includes ML experiment `61c0399`).
- Input `data/processed/daily.csv` SHA-256:
  `78e3b7691b41995ec380221cac416a71f5e12e7102ed6435128b27833ebba30c`.
- This owner executed the final evaluator once, after committing the protocol.
  [Test metrics](test_metrics.json) use full-precision predictions; the
  [replay CSV](test_replay.csv) preserves the interface schema and four-decimal
  amounts. [Run provenance](final_run.json) records runtime versions, file hashes,
  boundaries and passed audit checks.
- All three `experiments.test_sales_ablation` tests and `pip check` passed before
  disclosure. The post-run audit independently reconstructed targets/features,
  checked all scores and three bootstrap intervals against saved outputs,
  verified coefficients against the original validation fit, and confirmed
  unchanged evaluator/data hashes. It performs no fitting or model selection.

The final artifacts are already committed. From the repository root, the audit
verifies existing files and prints PASS without rerunning the evaluator or
writing files. It preserves the historical `final_run.json` from the original
CPython 3.15.0 run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.audit_final
```

Independent reproduction uses the unchanged evaluator and settings in the
[frozen protocol](../experiments/final_protocol.md). Routine verification only
needs the read-only audit above. Original runtime versions and file hashes are
retained in the historical `final_run.json`; the audit does not replace them
with the current environment.
