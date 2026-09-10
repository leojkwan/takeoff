#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s test -p 'test_*.py' -v
/usr/bin/python3 -c 'compile(open("bin/stamp").read(), "bin/stamp", "exec")'
/usr/bin/python3 -c 'compile(open("tools/adoption_lock.py").read(), "tools/adoption_lock.py", "exec")'
/usr/bin/python3 -c 'compile(open("tools/check-adoption-receipts.py").read(), "tools/check-adoption-receipts.py", "exec")'
echo "operational adoption audit: NOT RUN by source receipt durability"
echo "run separately: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 tools/check-adoption-receipts.py"
echo "source receipt durability: PASS"
