#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

cd "$repo_root"
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s test -p 'test_stamp.py' -v
/usr/bin/python3 -c 'compile(open("bin/stamp").read(), "bin/stamp", "exec")'
echo "stamp durability: PASS"
