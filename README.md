# AuditLens AI

A local transaction review application for small online merchants. Upload a
CSV/XLSX batch and optional prior history, rank purchases with a frozen XGBoost
model on CPU, inspect spending history and export a review queue.

## Hackathon submission

**Track: AI + Finance.** AuditLens AI helps small online merchants turn transaction
files into a prioritized review queue with customer spending context.

- [One-page project write-up](submission/WRITEUP.md)
- [Submission form answers](submission/FORM_ANSWERS.md)
- [Two-minute demo script](submission/DEMO_SCRIPT.md)
- [Verification record](submission/VERIFICATION.md)

## Run

With Docker and Docker Compose installed, run from the project root:

```bash
docker compose up
```

The first run builds the image and installs dependencies. Open
**http://127.0.0.1:8088** and select **Run live demo**. Readiness is available at
`http://127.0.0.1:8088/api/v1/health`. Stop and remove the container with
`docker compose down`. To use another local port:
`AUDITLENS_PORT=8089 docker compose up`. After changing the source, rebuild with
`docker compose up --build`.

### Local development

The local scripts use **Bash on Linux or WSL**. On macOS, use Docker for the
bundled CPU dependencies.

Requires **uv, Python 3.12, Node.js 22.12+ and npm**. The first setup downloads
dependencies. The selected model and fictional demo inputs are included.

```bash
./scripts/run_local.sh
```

Open **http://127.0.0.1:8088** and select **Run live demo**. Stop with Ctrl+C.
Use another port with `AUDITLENS_PORT=8089 ./scripts/run_local.sh`.
To reinstall locked dependencies, run `./scripts/setup_local.sh`.

The same local server serves the UI and API. No external AI API, GPU, account or
training dataset is needed. API documentation: `http://127.0.0.1:8088/docs`.

## Structure

```text
frontend/                      React + TypeScript interface and browser tests
src/auditlens/backend/         FastAPI server, upload validation and demo CSVs
src/auditlens/handbook.py       Past-only features and CPU model inference
src/auditlens/inference.py      Frozen model loader
src/auditlens/io.py             CSV/XLSX readers
models/handbook-xgboost-v1/     Selected weights, schemas and benchmark metadata
models/registry.json           Single supported model route
data/                         Provenance notes and optional local research data
scripts/                       Dependency setup and local server startup
tests/                         Backend and static-serving tests
requirements.txt               Locked CPU Python dependencies and test tools
```

## Input

CSV (UTF-8) or the active XLSX sheet must contain exactly these columns:

| Column | Value |
|---|---|
| `record_id` | Unique, nonempty text ID |
| `timestamp` | UTC wall time `YYYY-MM-DDTHH:MM:SS`, without a suffix |
| `customer_id` | Stable, nonempty text customer ID |
| `terminal_id` | Stable, nonempty text terminal ID |
| `amount` | Finite, nonnegative number in one consistent currency/unit |

Download example CSVs in the application. XLSX identifiers must be text cells;
formulas, links and extra columns are rejected. History uses the same columns,
must strictly precede the batch and must have disjoint record IDs. Supply the
preceding 30 complete calendar days for full customer/pair windows. Missing
history is accepted with coverage warnings.

Default limits: 8 MiB per file, 17 MiB per request, 10,000 batch rows,
100,000 history rows and one concurrent analysis. Uploads stay in RAM.

## Checks

After setup:

```bash
.venv-app/bin/pytest -q
.venv-app/bin/ruff check src tests
npm --prefix frontend test
npm --prefix frontend run build -- --mode unified
```

Browser tests require Playwright Chromium (`cd frontend && npx playwright install chromium`).
With the application running:

```bash
cd frontend
E2E_BASE_URL=http://127.0.0.1:8088 npm run test:e2e
```

## Model and credits

The 32-feature model was trained on the synthetic
[Fraud Detection Handbook dataset](https://github.com/Fraud-Detection-Handbook/simulated-data-raw)
by Yann-Aël Le Borgne, Wissam Siblini, Bertrand Lebichot and Gianluca Bontempi
(2022), pinned to commit `6e67dbd0a3bfe0d7ec33abc4bce5f37cd4ff0d6a`.
April 2018 supplies history; May–July training, August validation and September
testing. Historical test AP is 0.3428 versus 0.2444 for amount ranking;
precision@1000 is 0.794 versus 0.569. Frozen metrics used by the UI are stored in
`models/handbook-xgboost-v1/benchmark.json`.

Evidence is synthetic only. A history-alignment bug invalidated the initial
results; the corrected test had already been opened and is not an untouched
independent holdout. Terminal-compromise recall is only 0.0006. No real-bank
effectiveness or merchant pilot is established. Scores are uncalibrated review
priorities; explanations show observed history, not causal attribution.

Training datasets are not included in a fresh clone or downloaded during setup.
Optional research files under `data/` are ignored by Git; see `data/README.md`
for provenance and the local directory layout. The fictional demo CSVs are
included in `src/auditlens/backend/assets/`.
The selected weights are included at the owner's
request; upstream redistribution permission remains unconfirmed. No AuditLens
source-code license has been selected. Load only the trusted bundled model.
The application uses FastAPI, Polars, XGBoost, scikit-learn, React and Vite;
versions are locked in the dependency manifests. OpenAI Codex assisted with
coding, tests and documentation. Demo CSVs are self-authored fictional records.

Built for the Veritas AI International High School Hackathon 2026, AI + Finance.
This project is a prototype and is not financial advice.
