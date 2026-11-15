# Handbook dataset

- `raw/handbook/`: the 183 original daily files and acquisition manifest.
- `processed/handbook/raw.parquet`: combined original transactions.
- `processed/handbook/features-v1.parquet`: prepared past-only features.
- `examples/transactions.csv` + `examples/history.csv`: small, fictional app demo.
- `examples/handbook_template.csv/.xlsx`: minimal input templates.
- `examples/stage4_handbook.csv/.xlsx` + `stage4_handbook_history.csv`: larger
  publisher-derived input batch and its preceding history for local checks.
- `provenance/`: preserved upstream README and book code-license text.

Source: https://github.com/Fraud-Detection-Handbook/simulated-data-raw,
pinned commit `6e67dbd0a3bfe0d7ec33abc4bce5f37cd4ff0d6a`.
Authors: Yann-Aël Le Borgne, Wissam Siblini, Bertrand Lebichot and Gianluca Bontempi,
*Reproducible Machine Learning for Credit Card Fraud Detection — Practical Handbook* (2022).
All records are synthetic. April is history warmup; May–July training, August
validation, September testing. Application inference does not read these datasets;
it uses the selected frozen model and supplied input files.

The stored book license does not establish a separate raw-data redistribution
grant. Publisher data and derived files remain local and ignored by Git.
