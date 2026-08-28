from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[1]
GRADER = Path(os.environ.get("TAKEOFF_XBQ_GRADER", ROOT / "tools" / "grade-xbq-result.py"))
IOS_PROFILE = Path(
    os.environ.get("TAKEOFF_IOS_PROFILE", ROOT / "profiles" / "ios.md")
)
REFUSAL = "HEALED false-green refusal"


def passing_record(**overrides: Any) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "rc": 0,
        "result": "PASSED",
        "marker": "Test Succeeded",
        "executed": 13,
    }
    record.update(overrides)
    return record


class XbqMarkerTests(unittest.TestCase):
    def run_grader(
        self,
        record: Dict[str, Any],
        *,
        marker: str = "Test Succeeded",
        floor: int = 1,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(record, handle)
            handle.flush()
            return subprocess.run(
                [
                    "/usr/bin/python3",
                    str(GRADER),
                    "--expect-marker",
                    marker,
                    "--floor",
                    str(floor),
                    handle.name,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_refused(
        self, result: subprocess.CompletedProcess[str], detail: Optional[str] = None
    ) -> None:
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.startswith(REFUSAL), result.stderr)
        if detail:
            self.assertIn(detail, result.stderr)

    def test_rc_zero_with_failed_result_is_refused(self) -> None:
        """The exact xbq false green must lose even when its process rc is zero."""
        self.assert_refused(
            self.run_grader(passing_record(result="FAILED")), "not 'PASSED'"
        )

    def test_absent_result_marker_is_refused(self) -> None:
        record = passing_record()
        del record["marker"]
        self.assert_refused(self.run_grader(record), "marker is absent")

    def test_historical_success_prose_is_not_the_expected_marker(self) -> None:
        self.assert_refused(
            self.run_grader(passing_record(marker="** TEST SUCCEEDED **")),
            "does not match",
        )

    def test_zero_executed_count_is_refused(self) -> None:
        self.assert_refused(self.run_grader(passing_record(executed=0)), "below floor")

    def test_execution_count_below_lane_floor_is_refused(self) -> None:
        self.assert_refused(
            self.run_grader(passing_record(executed=3), floor=4), "below floor 4"
        )

    def test_nonzero_process_rc_is_refused(self) -> None:
        self.assert_refused(self.run_grader(passing_record(rc=65)), "exited 65")

    def test_matching_positive_marker_above_floor_is_accepted(self) -> None:
        result = self.run_grader(passing_record(executed=13), floor=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("xbq marker: PASS", result.stdout)
        self.assertIn("executed=13", result.stdout)

    def test_ios_profile_requires_grader_at_call_site(self) -> None:
        """A fail-soft helper that the release lane never calls is still absent."""
        profile = IOS_PROFILE.read_text()
        normalized = " ".join(profile.split())
        self.assertIn("tools/grade-xbq-result.py", profile)
        self.assertIn("Every `xbq` lane must", profile)
        self.assertIn("raw `xbq` rc or prose is never acceptance", normalized)


if __name__ == "__main__":
    unittest.main()
