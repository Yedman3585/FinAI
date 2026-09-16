#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/apps/api"

ARGS=(
  app.main:app
  --app-dir "$ROOT/apps/api"
  --host "${HOST:-127.0.0.1}"
  --port "${PORT:-8000}"
)

if [[ "${FINAI_API_RELOAD:-0}" == "1" ]]; then
  ARGS+=(--reload)
fi

exec "$ROOT/apps/api/.venv/bin/uvicorn" "${ARGS[@]}"
