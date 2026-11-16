#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ ! -x .venv-app/bin/uvicorn || ! -d frontend/node_modules ]]; then
  ./scripts/setup_local.sh
fi

# Ignore development API URL overrides: the demo serves UI and API on one origin.
# The exported value takes precedence over every Vite .env file.
env VITE_API_BASE_URL=/api/v1 npm --prefix frontend run build -- --mode unified
port="${AUDITLENS_PORT:-8088}"
echo "AuditLens AI: http://127.0.0.1:${port} (Ctrl+C to stop)"
exec .venv-app/bin/uvicorn auditlens.backend.app:app \
  --host 127.0.0.1 --port "$port" --workers 1 --no-access-log
