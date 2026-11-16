#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

for executable in uv node npm; do
  command -v "$executable" >/dev/null || { echo "Missing prerequisite: $executable (see README.md)" >&2; exit 1; }
done
node -e 'const [major,minor]=process.versions.node.split(".").map(Number); if (major<22 || (major===22 && minor<12)) { console.error("Node 22.12+ is required"); process.exit(1); }'

# Create the CPU runtime environment.
uv venv --python 3.12 --allow-existing .venv-app
uv pip sync --python .venv-app/bin/python requirements.txt
uv pip install --python .venv-app/bin/python --no-deps -e .
(
  cd frontend
  NODE_OPTIONS="${NODE_OPTIONS:-} --dns-result-order=ipv4first" npm ci
)
echo "CPU environment and frontend dependencies installed. Run ./scripts/run_local.sh"
