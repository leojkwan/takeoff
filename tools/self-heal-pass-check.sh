#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--fixture" || "${1:-}" == "--fixture-ambiguity" ]]; then
  [[ "$#" == "1" ]] || { echo "usage: self-heal-pass-check.sh" >&2; exit 2; }
  exec /usr/bin/python3 "$repo_root/test/test_self_heal_pass.py" "$1"
fi
[[ "$#" == "0" ]] || { echo "usage: self-heal-pass-check.sh" >&2; exit 2; }

cd "$repo_root"
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover \
  -s test -p 'test_self_heal_pass.py' -v
echo "self-heal pass: PASS"
