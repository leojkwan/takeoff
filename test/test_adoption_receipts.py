from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check-adoption-receipts.py"


class AdoptionReceiptTests(unittest.TestCase):
    def test_legacy_receipt_identity_can_link_additional_json_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            report = temp / "merged-report.json"
            report.write_text('{"repo":"resplit-ios","source_head":"abc123def456"}')
            receipt = temp / "receipt.md"
            receipt.write_text(
                "# takeoff train receipt — resplit-ios\n"
                "- ref: abc123def456\n"
                f"- merged report: {report}\n"
            )
            adoption = temp / "ADOPTION.md"
            adoption.write_text(
                "| 2026-08-14T045330Z | resplit-ios | abc123def456 | integration "
                f"| executed=1 | 1s/2s | {receipt} |\n"
            )

            result = subprocess.run(
                ["/usr/bin/python3", str(CHECKER), str(adoption)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_arbitrary_repo_and_ref_tokens_are_not_existing_receipt_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            receipt = temp / "receipt.md"
            receipt.write_text(
                "not a takeoff receipt; arbitrary resplit-ios prose; "
                "arbitrary abc123def456 token\n"
            )
            adoption = temp / "ADOPTION.md"
            adoption.write_text(
                "| 2026-08-14T045330Z | resplit-ios | abc123def456 | integration "
                f"| executed=1 | 1s/2s | {receipt} |\n"
            )

            result = subprocess.run(
                ["/usr/bin/python3", str(CHECKER), str(adoption)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("canonical repo/ref identity", result.stderr)

    def test_removed_worktree_pointer_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            missing = temp / "removed-worktree" / "receipt.md"
            adoption = temp / "ADOPTION.md"
            adoption.write_text(
                "| 2026-08-14T045330Z | resplit-ios | abc123def456 | integration "
                f"| executed=1 | 1s/2s | {missing} |\n"
            )

            result = subprocess.run(
                ["/usr/bin/python3", str(CHECKER), str(adoption)],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing receipt", result.stderr)

    def test_empty_ledger_refuses_instead_of_passing_zero_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adoption = Path(temp_dir) / "ADOPTION.md"
            adoption.write_text(
                "# takeoff — ADOPTION\n\n"
                "| date | repo | ref | verdict | host | lanes | executed | elapsed | receipt |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
            )

            result = subprocess.run(
                ["/usr/bin/python3", str(CHECKER), str(adoption)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("no adoption rows recognized", result.stderr)
            self.assertNotIn("PASS rows=0", result.stdout)

    def test_indented_row_shape_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            receipt = temp / "receipt.md"
            receipt.write_text(
                "# takeoff pass — resplit-ios — PROOF-ONLY\n"
                "- ref judged: abc123def456\n"
            )
            adoption = temp / "ADOPTION.md"
            adoption.write_text(
                "  | 2026-08-14T045330Z | resplit-ios | abc123def456 | integration "
                f"| executed=1 | 1s/2s | {receipt} |\n"
            )

            result = subprocess.run(
                ["/usr/bin/python3", str(CHECKER), str(adoption)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("adoption row must start in column 1", result.stderr)
            self.assertNotIn("PASS rows=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
