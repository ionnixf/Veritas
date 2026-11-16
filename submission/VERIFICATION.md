# Verification record

Verified on 2026-11-16 using the source from
`a0cba914925d84fa8fca0134c217f6a0c80f0009` plus submission documentation and CI.
No model training or benchmark recomputation was performed.

| Check | Result |
| --- | --- |
| Python application tests (`pytest -q`) | 81 passed |
| Python lint (`ruff check src tests`) | Passed |
| Frontend unit tests (`npm --prefix frontend test`) | 20 passed |
| TypeScript and production UI build (`npm --prefix frontend run build -- --mode unified`) | Passed |
| Chromium end-to-end tests against the unified local app | 15 passed |
| Docker multi-stage build | Passed with the environment's trusted proxy CA supplied at build time |
| Container readiness (`/api/v1/health`) | HTTP 200, ready, model available, CPU |
| Container real demo inference (`POST /api/v1/demo/analyze`) | Five operations in the review queue |
| Container user | UID/GID 10001, unprivileged |
| `docker compose down` | Container and network removed successfully |

Browser coverage includes CSV/XLSX upload, validation and size limits, real model
inference, history context, review budgets, pagination/filter/export, backend
outage recovery, keyboard access, accessibility checks and mobile/tablet overflow.

## Environment notes
The cloud environment intercepts outbound TLS. An unmodified Docker build hit a
certificate error downloading Python packages. Verification used a temporary
Dockerfile that supplied the environment CA through a BuildKit secret to `pip`
and `npm`; the committed Dockerfile and application were unchanged, and TLS
verification remained enabled. The resulting image was started using
`AUDITLENS_PORT=8089 docker compose up -d --no-build --wait` because the local
script was already serving on 8088. This verifies the image and Compose runtime;
a clean-machine build with the unmodified Dockerfile was not independently run.
An initial browser run exhausted disk space after Docker builds; after removal
of build cache, the full browser suite passed.

Python tests emit an upstream Starlette/httpx deprecation warning and XGBoost
GPU-to-CPU fallback warnings when loading the bundled artifact. CPU inference
succeeds. These checks verify application behavior, not real-world model quality.
The frozen benchmark's limitations are disclosed in the write-up.
