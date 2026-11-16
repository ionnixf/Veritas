# AuditLens AI

**Track:** AI + Finance · **Starting point:** 4.2.2 Card fraud detection

This project is a prototype and is not financial advice.

## The problem
Small online merchants have limited time to review suspicious purchases. Sorting
only by transaction amount can overlook unusual customer behavior, while an
unexplained fraud label gives reviewers little context for deciding what to inspect.

## What we built
AuditLens AI takes a CSV/XLSX transaction batch and optional prior history and
returns a ranked review queue, customer spending context and a CSV export. A
merchant chooses a review budget, inspects the highest-priority purchases and
makes the final decision. A bundled live demo runs real model inference without
an account, GPU or external AI API. Start the UI and API with `docker compose up`.

## What we added
We adapted the card-fraud starting point to a merchant review workflow using a
different, synthetic dataset with customer and terminal histories. Our additions
include 32 past-only features, comparison against amount ranking, a local upload
and review interface, history-coverage warnings, strict file validation and
one-command Docker packaging. The application prioritizes human review; it does
not automatically block payments.

## How it works
We used the synthetic Fraud Detection Handbook dataset, pinned to commit
`6e67dbd0a3bfe0d7ec33abc4bce5f37cd4ff0d6a`. April 2018 supplies history,
May–July training, August validation and September testing. The September test
contains 287,873 transactions, including 2,547 fraud labels. Features describe
amount, time and preceding customer/terminal activity; future records and target
labels are excluded from feature history. XGBoost combines these tabular signals
and runs on CPU in the application. The frozen model, schema and benchmark are
bundled; training data and the historical training pipeline are not included in
this release. File checks reject invalid schemas, identifiers and timestamps;
missing history produces coverage warnings.

## Results and limitations
On the historical synthetic September test, average precision was **0.3428** for
XGBoost versus **0.2444** for amount ranking. Precision among the top 1,000 ranked
transactions was **0.794** versus **0.569**. Metrics come from the bundled
[benchmark](../models/handbook-xgboost-v1/benchmark.json), not the five-row demo.

A history-alignment bug invalidated the initial results. The corrected benchmark
uses a test set that had already been opened, so it is **not an untouched
independent holdout**. Terminal-compromise recall at the selected threshold was
only **0.0006**. Scores are uncalibrated priorities, and displayed history is
context rather than a causal explanation. Synthetic performance does not establish
real-bank effectiveness; no merchant pilot has been completed. Data and derived
weight redistribution permission remains unconfirmed (see README credits).

## What we'd do next
Evaluate a fixed model on a new, untouched chronological period, with stronger
terminal-compromise features and per-scenario error analysis. Then test the review
workflow with consenting merchants using appropriately licensed data.

## Sources and assistance
- [Fraud Detection Handbook synthetic data](https://github.com/Fraud-Detection-Handbook/simulated-data-raw), Yann-Aël Le Borgne, Wissam Siblini, Bertrand Lebichot and Gianluca Bontempi (2022), pinned commit above.
- [XGBoost](https://xgboost.readthedocs.io/), [scikit-learn](https://scikit-learn.org/), [Polars](https://pola.rs/), [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/) and [Vite](https://vite.dev/); versions are locked in the repository.
- [OpenAI Codex](https://openai.com/codex/) assisted with coding, tests and documentation. Demo CSVs are self-authored fictional records.
