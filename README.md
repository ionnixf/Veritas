# Veritas

**Команде:** [начать параллельную работу на двух устройствах](docs/TEAM_START.md).

## ReserveWeek starter

At opening time a shopkeeper chooses a buffer for seven days of recorded invoice cancellations. This offline replay tests that decision on one UK retailer. The data do not record refund settlement dates, cash balances or stock purchasing decisions.

This project is a prototype and is not financial advice.

### Run a historical decision

From the repository root, Python alone is sufficient to replay the included validation predictions.

```bash
python3 -m demo.replay 2011-01-18
python3 -m demo.replay 2011-01-18 --reveal
```

### Reproduce the starter

Tested with CPython 3.14. Run the following commands from the repository root. The small daily aggregates are included, so the first model run does not need the original workbook.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.evaluate
```

To rebuild the aggregates from the original archive, run the commands below. The importer verifies the archive checksum, assigns the overlapping worksheet dates to one sheet, removes the two boundary dates and fills dates without recorded transactions with zero recorded value. The manifest documents those choices. Each output row represents one calendar day across all customers. Sales sum positive lines on ordinary invoices. Cancellations sum the absolute value of negative-quantity lines with positive unit price on invoices prefixed with C. Within an individual sheet each source line is counted once. Manual credits can be included.

```bash
mkdir -p data/raw
curl -fL 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip' -o data/raw/retail.zip
.venv/bin/python -m data_pipeline.prepare data/raw/retail.zip
.venv/bin/python -m experiments.evaluate
```

Day D is the first day of a seven-day forecast. Features include observations through D−1. The target sums cancellations from D to D+6. Training targets end by 2010-12-31, validation targets by 2011-06-30, and test origins start on 2011-07-01. The default command truncates the series before constructing validation targets. After model and evaluation choices are frozen, run `.venv/bin/python -m experiments.evaluate --split test` and use `--file artifacts/test_replay.csv` with the replay tool. This starter uses the same training period for both evaluations.

The 80th-percentile target represents a hypothetical 4:1 cost of insufficient versus unused buffer. We compare the previous week's amount, the 80th percentile of all training targets and the 80th percentile of the past eight disjoint weeks with a linear quantile model and a 50:50 blend of the linear and training-quantile estimates. The blend was tried during validation. Mean pinball loss is in GBP and lower is better. Coverage counts origins at which the entire week's recorded cancellations fit inside the reserve. Nearby seven-day outcomes overlap. The paired moving-block bootstrap uses 2,000 draws, with 14 days as the main block and 7/28 for sensitivity. Its validation intervals are exploratory.

### Sources and ownership

- Daily aggregates and workbook input are derived from Daqing Chen, *Online Retail II*, UCI Machine Learning Repository, under CC BY 4.0. Aggregation and date handling are described above. [Dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) · [Licence](https://creativecommons.org/licenses/by/4.0/)
- Model and data tooling use [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [SciPy](https://scipy.org/) and [python-calamine](https://github.com/dimastbk/python-calamine). [Codex](https://openai.com/codex/) helped design, implement and run this starter.
- The team work plan, validation figures, ownership and submission schedule are in [the finance plan](docs/FINANCE_PLAN.md).
