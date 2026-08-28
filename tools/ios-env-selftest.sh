#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 test/test_ios_env.py -v
