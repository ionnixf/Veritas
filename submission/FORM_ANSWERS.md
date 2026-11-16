# Submission form answers

Copy the technical answers below into the organizer's form. Personal registration
fields are intentionally omitted from this public repository: fill in individual/team,
team name, each member's name/email/school and prior AI experience privately.

## Project title
AuditLens AI — Transaction Review for Small Online Merchants

## Track
AI + Finance

## Starting point
4.2.2 Card fraud detection — adapted to small online merchants using the synthetic Fraud Detection Handbook dataset.

## One-sentence pitch
AuditLens AI helps small online merchants review potentially suspicious purchases by turning transaction files and optional customer history into a ranked review queue with spending context.

## Code link
https://github.com/ionnixf/Veritas

## Write-up link
https://github.com/ionnixf/Veritas/blob/main/submission/WRITEUP.md

## What we added
We adapted card fraud detection into a transaction review workflow for small online merchants. Users upload CSV/XLSX transactions and optional prior history, run a frozen XGBoost model locally, inspect a ranked review queue with customer spending context, and export results. We engineered 32 past-only features, compared the model against amount ranking, added file validation and history-coverage warnings, and packaged the app for one-command Docker startup. The tool supports human review and does not automatically block payments.

## Datasets, models and AI tools used
Synthetic Fraud Detection Handbook dataset by Yann-Aël Le Borgne, Wissam Siblini, Bertrand Lebichot and Gianluca Bontempi (2022): https://github.com/Fraud-Detection-Handbook/simulated-data-raw, pinned to commit 6e67dbd0a3bfe0d7ec33abc4bce5f37cd4ff0d6a. XGBoost with 32 past-only features; Python, FastAPI, Polars, scikit-learn, React, TypeScript and Vite. Self-authored fictional demo transactions. OpenAI Codex assisted with coding, tests and documentation. Add any other tools actually used by your team before submitting.

## Demo video
Optional but recommended under the Project Briefs. No hosted video is included in
this release. Record using [the script](DEMO_SCRIPT.md), upload with view access
and paste its URL in the form; otherwise leave the optional field empty.

## Final private checks
Open the code and write-up links while logged out. Enter accurate team details.
Do not submit old ReserveWeek links or metrics: the submission is AuditLens AI.
The repository does not submit the organizer's form automatically.
