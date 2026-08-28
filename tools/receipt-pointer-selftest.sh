#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover \
  -s test -p 'test_receipt_pointer.py' -v
PYTHONPATH="$repo_root/test" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest -v \
  test_stamp.StampDurabilityTests.test_stamp_waits_for_the_stable_receipt_pointer_lock \
  test_stamp.StampDurabilityTests.test_pointer_heal_does_not_make_the_next_stamp_refuse
/usr/bin/python3 -c 'compile(open("tools/adoption_lock.py").read(), "tools/adoption_lock.py", "exec")'
/usr/bin/python3 -c 'compile(open("tools/check-adoption-receipts.py").read(), "tools/check-adoption-receipts.py", "exec")'
/usr/bin/python3 -c 'compile(open("bin/stamp").read(), "bin/stamp", "exec")'
echo "receipt pointer recovery: PASS"
