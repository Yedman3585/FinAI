#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_DIR="/Users/yedige.mussabayev/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
BUNDLED_PNPM="/Users/yedige.mussabayev/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"

cd "$ROOT"

if [ -x "$NODE_DIR/node" ]; then
  export PATH="$NODE_DIR:$PATH"
fi

if command -v pnpm >/dev/null 2>&1; then
  PNPM_BIN="$(command -v pnpm)"
elif [ -x "$BUNDLED_PNPM" ]; then
  PNPM_BIN="$BUNDLED_PNPM"
else
  echo "pnpm was not found. Install pnpm or set it on PATH." >&2
  exit 1
fi

exec "$PNPM_BIN" --dir "$ROOT/apps/web" dev
