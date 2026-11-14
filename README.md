# ReserveWeek

**Track: AI + Finance.** Our own idea: help an online shopkeeper choose a seven-day reserve for recorded invoice cancellations before buying stock. The offline demo takes a historical decision date, shows a model reserve beside a simple fixed rule, then reveals the next week's cancellations and the shortfall or unused reserve.

This project is a prototype and is not financial advice.

## Run the demo

Python 3 alone is sufficient; no installation, internet or API keys are needed.

```bash
python3 -m demo.app
```

Open http://127.0.0.1:8000. [Recording instructions](demo/README.md). A terminal replay is also available:

```bash
python3 -m demo.replay 2011-01-18 --reveal
```

## Method and results

We use *Online Retail II*, the transaction history of one UK retailer. Each daily row aggregates recorded sales and cancellations across customers. Features use observations through D−1; the target is cancellations on D through D+6. Training targets end in December 2010, validation targets in June 2011, and the final test starts in July 2011. Targets crossing a split boundary are excluded.

The model averages a linear quantile regression and the training-period 80th percentile. The target quantile represents a **hypothetical 4:1 cost** of insufficient versus unused reserve. Baselines are the previous week's cancellations, the 80th percentile of eight past weeks and the fixed training-period percentile. Pinball loss measures this trade-off in GBP; lower is better.

On **155 held-out daily decision dates** (1 July–2 December 2011), the blend's pinball loss was **£2,455.68**, compared with **£4,950.14** for the previous week and **£2,483.98** for the fixed rule. The paired 95% interval for blend minus fixed rule was **[−£484.27, +£707.08]**. It includes zero: **an advantage over the stronger rule is not established**. Seven-day targets overlap. [Final results and provenance](artifacts/final_results.md) · [One-page write-up](submission/SUMMARY.md).

One failure, from **validation**: on 18 January 2011 the model reserved £24,050.42 against £81,851.42 in recorded cancellations, leaving a £57,801.00 shortfall. Recent history did not anticipate this spike; its cause is not established. [Validation sales-feature experiment](artifacts/validation_sales_ablation.md).

The data cover one retailer and record invoice cancellations, **not refund settlement dates, cash balances or stock purchases**. Manual credits may contribute to cancellations. A next step is to test the decision against a retailer's actual refund-payment ledger before making claims about cash savings.

## Reproduce validation

Run from the repository root. The included daily aggregates avoid downloading the original workbook for model evaluation.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.evaluate
.venv/bin/python -m experiments.sales_ablation
.venv/bin/python -m unittest experiments.test_sales_ablation -v
```

On Windows use `.venv\Scripts\python` instead of `.venv/bin/python`.

To rebuild daily aggregates, download the [UCI archive](https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip) to `data/raw/retail.zip`, then run `.venv/bin/python -m data_pipeline.prepare data/raw/retail.zip`. The importer verifies the checksum, assigns overlapping worksheet dates to one sheet, excludes partial boundary days and fills unrecorded calendar days with zero. Sales sum positive ordinary-invoice lines; cancellations sum the absolute value of negative-quantity, positive-price lines on invoices prefixed with C. [Data manifest](data/processed/manifest.json).

The final test is already disclosed. Use `python -m experiments.audit_final` in the installed environment to verify the saved result without refitting; do not tune the method on test outcomes. [Team instructions](docs/TEAM_START.md) · [Requirements and remaining work](docs/FINANCE_PLAN.md).

## Sources

- Daqing Chen, [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), UCI Machine Learning Repository, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [SciPy](https://scipy.org/) and [python-calamine](https://github.com/dimastbk/python-calamine).
- [Codex](https://openai.com/codex/) assisted with design, implementation, evaluation and editing. [GLM via ZCode](https://zcode.z.ai/en/docs/welcome) supplied text/script drafts adapted for the write-up and recording. Credit any additional tools actually used before submission.
