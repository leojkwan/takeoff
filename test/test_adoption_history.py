from __future__ import annotations

import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADOPTION = Path(os.environ.get("TAKEOFF_ADOPTION_FILE", ROOT / "ADOPTION.md"))

EXPECTED_PASSES = {
    ("2026-08-20T024048Z", "trysnowcubes-web", "0dd70d1e78ef", "DEFERRED", "executed=6551"),
    ("2026-08-20T030416Z", "resplit-web", "ac9c87a72223", "PROOF-ONLY", "executed=4611"),
    ("2026-08-20T031526Z", "resplit-ios", "499f5912ff83", "PROOF-ONLY", "executed=21"),
    ("2026-08-22T022226Z", "trysnowcubes-web", "5ebcd8e23439", "REFUSED", "executed=8473"),
}


class AdoptionHistoryTests(unittest.TestCase):
    def test_preserves_the_four_recovered_pass_identities(self) -> None:
        observed = set()
        for line in ADOPTION.read_text().splitlines():
            if not line.startswith("| 20"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            observed.add((cells[0], cells[1], cells[2], cells[3], cells[-3]))

        self.assertEqual(EXPECTED_PASSES - observed, set())


if __name__ == "__main__":
    unittest.main()
