#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest -v test.test_xbq_marker
/usr/bin/python3 -c 'compile(open("tools/grade-xbq-result.py").read(), "tools/grade-xbq-result.py", "exec")'
echo "xbq marker grader: PASS"
