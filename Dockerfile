FROM node:22-bookworm-slim AS frontend

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build -- --mode unified

FROM scratch AS application
COPY src/ /src/
COPY models/ /models/
COPY --from=frontend /app/frontend/dist/ /frontend/dist/

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    POLARS_MAX_THREADS=2 \
    OMP_NUM_THREADS=2 \
    OPENBLAS_NUM_THREADS=2

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 auditlens \
    && useradd --uid 10001 --gid auditlens --no-create-home auditlens

WORKDIR /app
COPY --chown=auditlens:auditlens requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=application --chown=auditlens:auditlens / /app/

USER auditlens
EXPOSE 8088
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/api/v1/health', timeout=4).close()"]
CMD ["uvicorn", "auditlens.backend.app:app", "--host", "0.0.0.0", "--port", "8088", "--workers", "1", "--no-access-log"]
