#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3)}
PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" "$ROOT/test/test_prepare_worktree.py" -v
echo "worktree self-heal: PASS"
