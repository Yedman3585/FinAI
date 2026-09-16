#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_DIR="/Users/yedige.mussabayev/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
PNPM_BIN="/Users/yedige.mussabayev/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm"

cd "$ROOT"

if [ -x "$NODE_DIR/node" ]; then
  export PATH="$NODE_DIR:$PATH"
fi

exec "$PNPM_BIN" --dir "$ROOT/apps/web" dev

