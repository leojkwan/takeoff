from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
CHECKER = Path(
    os.environ.get(
        "TAKEOFF_RECEIPT_CHECKER",
        ROOT / "tools" / "check-adoption-receipts.py",
    )
)
REPO = "sample-repo"
REF = "abc123def456"
RECEIPT_NAME = "2026-08-22T034500Z-receipt.md"


def receipt(extra: str = "") -> str:
    return (
        f"# takeoff pass — {REPO} — PROOF-ONLY\n"
        f"- ref judged: {REF}7890abcdef; host: test-host\n"
        '- lane unit rc=0 marker="1 passed" count=1\n'
        f"{extra}"
    )


class ReceiptPointerRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evidence = self.root / "takeoff-evidence"
        self.adoption = self.root / "ADOPTION.md"
        self.missing = (
            self.root
            / "removed-worktree"
            / "evidence"
            / "takeoff-pass"
            / RECEIPT_NAME
        )

    def adoption_text(self, receipt_path: Optional[Path] = None) -> str:
        pointer = receipt_path or self.missing
        return (
            "# takeoff — ADOPTION\n\n"
            "| date | repo | ref | verdict | host | lanes | executed | elapsed | receipt |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            f"| 2026-08-22T034500Z | {REPO} | {REF} | PROOF-ONLY | test-host "
            f"| unit | executed=1 | 1s/2s | {pointer} |\n"
            "\n# history after the row must remain byte-identical\n"
        )

    def candidate(self, relative_parent: str, content: Optional[str] = None) -> Path:
        path = self.evidence / REPO / relative_parent / RECEIPT_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if content is not None else receipt())
        return path

    def make_tracked_adoption(self, content: str) -> Path:
        repository = self.root / "takeoff-repository"
        repository.mkdir()
        self.adoption = repository / "ADOPTION.md"
        self.adoption.write_text(content)
        for command in (
            ("init",),
            ("config", "user.name", "Takeoff Pointer Test"),
            ("config", "user.email", "pointer-test@example.invalid"),
            ("add", "ADOPTION.md"),
            ("commit", "-m", "initial adoption ledger"),
        ):
            subprocess.run(
                ["git", *command],
                cwd=repository,
                text=True,
                capture_output=True,
                check=True,
            )
        return repository

    def run_checker(
        self, evidence_root: Optional[Path] = None, *, cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["TAKEOFF_EVIDENCE_ROOT"] = str(evidence_root or self.evidence)
        return subprocess.run(
            ["/usr/bin/python3", str(CHECKER), str(self.adoption)],
            cwd=cwd or ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def load_checker_module(self):
        module_name = f"takeoff_receipt_checker_{id(self)}"
        spec = importlib.util.spec_from_file_location(module_name, CHECKER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        old_root = os.environ.get("TAKEOFF_EVIDENCE_ROOT")
        os.environ["TAKEOFF_EVIDENCE_ROOT"] = str(self.evidence)
        sys.path.insert(0, str(CHECKER.parent))
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        finally:
            sys.path.pop(0)
            if old_root is None:
                os.environ.pop("TAKEOFF_EVIDENCE_ROOT", None)
            else:
                os.environ["TAKEOFF_EVIDENCE_ROOT"] = old_root

    def wake(self, receipt_name: str = RECEIPT_NAME) -> str:
        return (
            "WAKE receipt pointer: missing receipt; leave exactly one byte-compatible "
            f"{receipt_name} for {REPO}@{REF} under {self.evidence / REPO}, "
            "then rerun adoption grading"
        )

    def test_missing_source_pointer_is_repaired_before_real_grading(self) -> None:
        """The real adoption grader must consume the repair, not an unused helper."""
        before = self.adoption_text()
        self.adoption.write_text(before)
        durable = self.candidate("takeoff-pass")

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HEALED receipt pointer", result.stdout)
        self.assertIn("adoption receipts: PASS rows=1", result.stdout)
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(self.missing), str(durable), 1),
        )

    def test_no_candidate_refuses_with_one_exact_wake_and_no_rewrite(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake())
        self.assertEqual(result.stderr.count("WAKE receipt pointer:"), 1)
        self.assertEqual(self.adoption.read_text(), before)
        self.assertFalse(self.evidence.exists())

    def test_nonidentical_candidates_refuse_with_one_exact_wake_and_no_rewrite(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        self.candidate("copy-a", receipt("# candidate a\n"))
        self.candidate("copy-b", receipt("# candidate b\n"))

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake())
        self.assertEqual(result.stderr.count("WAKE receipt pointer:"), 1)
        self.assertEqual(self.adoption.read_text(), before)

    def test_byte_identical_candidates_collapse_to_one_deterministic_choice(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        chosen = self.candidate("a-copy")
        self.candidate("z-copy")

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(self.missing), str(chosen), 1),
        )

    def test_candidate_must_name_the_row_repo_and_judged_ref(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        self.candidate(
            "takeoff-pass",
            "# takeoff pass — different-repo — PROOF-ONLY\n"
            "- ref judged: deadbeefdeadbeef\n",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake())
        self.assertEqual(self.adoption.read_text(), before)

    def test_arbitrary_repo_and_ref_tokens_are_not_receipt_identity(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        self.candidate(
            "takeoff-pass",
            f"not a takeoff receipt; arbitrary {REPO} prose; arbitrary {REF} token\n",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake())
        self.assertEqual(self.adoption.read_text(), before)

    def test_repair_preserves_crlf_and_every_non_pointer_byte(self) -> None:
        before = self.adoption_text().replace("\n", "\r\n")
        self.adoption.write_bytes(before.encode("utf-8"))
        durable = self.candidate("takeoff-pass")

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.adoption.read_bytes(),
            before.replace(str(self.missing), str(durable), 1).encode("utf-8"),
        )

    def test_receipt_basename_is_literal_not_a_glob(self) -> None:
        self.missing = self.missing.with_name("*.md")
        before = self.adoption_text()
        self.adoption.write_text(before)
        different = self.evidence / REPO / "takeoff-pass" / "different-name.md"
        different.parent.mkdir(parents=True)
        different.write_text(receipt())

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake("*.md"))
        self.assertEqual(self.adoption.read_text(), before)

    def test_relative_missing_pointer_repairs_only_its_raw_cell(self) -> None:
        relative = Path("removed-worktree") / "takeoff-pass" / RECEIPT_NAME
        before = self.adoption_text(relative)
        self.adoption.write_text(before)
        durable = self.candidate("takeoff-pass")

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(relative), str(durable), 1),
        )

    def test_legacy_train_receipt_has_a_canonical_identity(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        durable = self.candidate(
            "takeoff-train",
            f"# takeoff train receipt — {REPO}\n"
            f"- ref: {REF}7890abcdef (pinned to origin/main)\n",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(self.missing), str(durable), 1),
        )

    def test_qualified_judged_ref_has_a_canonical_identity(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        durable = self.candidate(
            "takeoff-pass",
            f"# takeoff pass — {REPO} — PROOF-ONLY\n"
            f"- ref judged: origin/main {REF}7890abcdef; host: test-host\n",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(self.missing), str(durable), 1),
        )

    def test_symlink_candidate_is_not_durable_evidence(self) -> None:
        before = self.adoption_text()
        self.adoption.write_text(before)
        target = self.evidence / REPO / "real" / "actual-receipt.md"
        target.parent.mkdir(parents=True)
        target.write_text(receipt())
        link = self.evidence / REPO / "linked" / RECEIPT_NAME
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), self.wake())
        self.assertEqual(self.adoption.read_text(), before)
        self.assertTrue(link.is_symlink())

    def test_symlink_adoption_ledger_refuses_without_replacing_link(self) -> None:
        before = self.adoption_text()
        target = self.root / "real-adoption.md"
        target.write_text(before)
        self.adoption.symlink_to(target)
        self.candidate("takeoff-pass")

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "WAKE receipt pointer: ADOPTION.md must be a regular file, not a "
            "symlink or special file",
        )
        self.assertTrue(self.adoption.is_symlink())
        self.assertEqual(target.read_text(), before)

    def test_tracked_adoption_repair_is_committed_and_clean(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        durable = self.candidate("takeoff-pass")

        result = self.run_checker()

        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        subject = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(status.stdout, "")
        self.assertEqual(subject.stdout.strip(), "adoption: heal 1 receipt pointer")
        self.assertEqual(
            self.adoption.read_text(),
            before.replace(str(self.missing), str(durable), 1),
        )

    def test_relative_evidence_root_refuses_before_tracked_ledger_mutation(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        cwd = self.root / "candidate-cwd"
        evidence = cwd / "relative-evidence"
        candidate = evidence / REPO / "takeoff-pass" / RECEIPT_NAME
        candidate.parent.mkdir(parents=True)
        candidate.write_text(receipt())
        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        ).stdout

        result = self.run_checker(Path("relative-evidence"), cwd=cwd)

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "TAKEOFF_EVIDENCE_ROOT must be an absolute path",
        )
        self.assertEqual(self.adoption.read_bytes(), before.encode("utf-8"))
        self.assertEqual(head_after, head_before)
        self.assertEqual(status.stdout, "")

    def test_dirty_tracked_adoption_refuses_before_any_rewrite(self) -> None:
        before = self.adoption_text()
        self.make_tracked_adoption(before)
        dirty = before + "# unrelated owner edit\n"
        self.adoption.write_text(dirty)
        self.candidate("takeoff-pass")

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "WAKE receipt pointer: tracked ADOPTION.md must be clean at HEAD "
            "before repair; restore or commit it, then rerun adoption grading",
        )
        self.assertEqual(self.adoption.read_text(), dirty)

    def test_failed_git_commit_rolls_back_without_a_dirty_ledger(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        signer = repository / "refuse-signing"
        signer.write_text("#!/bin/sh\nexit 1\n")
        signer.chmod(0o755)
        subprocess.run(
            ["git", "config", "commit.gpgSign", "true"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "gpg.program", str(signer)],
            cwd=repository,
            check=True,
        )
        self.candidate("takeoff-pass")

        result = self.run_checker()

        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "WAKE receipt pointer: Git could not commit healed ADOPTION.md; "
            "restore commit identity or hooks, then rerun adoption grading",
        )
        self.assertEqual(self.adoption.read_text(), before)
        self.assertEqual(status.stdout, "")

    def test_rerun_commits_a_crash_after_atomic_pointer_replacement(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        durable = self.candidate("takeoff-pass")
        healed = before.replace(str(self.missing), str(durable), 1)
        self.adoption.write_text(healed)

        result = self.run_checker()

        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        subject = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HEALED receipt pointer", result.stdout)
        self.assertEqual(status.stdout, "")
        self.assertEqual(subject.stdout.strip(), "adoption: heal 1 receipt pointer")
        self.assertEqual(self.adoption.read_text(), healed)

    def test_rerun_refuses_healed_pointer_mixed_with_unrelated_edit(self) -> None:
        before = self.adoption_text()
        self.make_tracked_adoption(before)
        durable = self.candidate("takeoff-pass")
        dirty = before.replace(str(self.missing), str(durable), 1) + "# unrelated\n"
        self.adoption.write_text(dirty)

        result = self.run_checker()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "WAKE receipt pointer: tracked ADOPTION.md must be clean at HEAD "
            "before repair; restore or commit it, then rerun adoption grading",
        )
        self.assertEqual(self.adoption.read_text(), dirty)

    def test_rerun_preserves_a_staged_ledger_edit(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        durable = self.candidate("takeoff-pass")
        staged = before + "# staged owner edit\n"
        self.adoption.write_text(staged)
        subprocess.run(
            ["git", "add", "ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        healed = before.replace(str(self.missing), str(durable), 1)
        self.adoption.write_text(healed)

        result = self.run_checker()

        staged_after = subprocess.run(
            ["git", "show", ":ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "WAKE receipt pointer: tracked ADOPTION.md index must match HEAD "
            "before recovery; preserve or commit staged edits, then rerun "
            "adoption grading",
        )
        self.assertEqual(staged_after.stdout, staged)
        self.assertEqual(self.adoption.read_text(), healed)

    def test_commit_hook_cannot_stage_wrong_ledger_bytes(self) -> None:
        before = self.adoption_text()
        repository = self.make_tracked_adoption(before)
        durable = self.candidate("takeoff-pass")
        hook = repository / ".git" / "hooks" / "pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            "printf '# WRONG HOOK BYTE\\n' > ADOPTION.md\n"
            "git add ADOPTION.md\n"
        )
        hook.chmod(0o755)

        result = self.run_checker()

        healed = before.replace(str(self.missing), str(durable), 1)
        committed = subprocess.run(
            ["git", "show", "HEAD:ADOPTION.md"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(committed.stdout, healed)
        self.assertEqual(self.adoption.read_text(), healed)

    def test_atomic_replace_refuses_bytes_changed_at_publish_boundary(self) -> None:
        checker = self.load_checker_module()
        before = self.adoption_text().encode("utf-8")
        self.adoption.write_bytes(before)
        expected_stat = self.adoption.lstat()
        concurrent = before + b"# concurrent owner edit\n"
        self.adoption.write_bytes(concurrent)

        with self.assertRaisesRegex(
            checker.PointerWake,
            "ADOPTION.md changed while recovery was preparing",
        ):
            checker.atomic_replace_bytes(
                self.adoption,
                b"healed",
                0o644,
                expected_original=before,
                expected_stat=expected_stat,
            )

        self.assertEqual(self.adoption.read_bytes(), concurrent)

    def test_candidate_revalidation_refuses_late_outside_symlink(self) -> None:
        checker = self.load_checker_module()
        durable = self.candidate("takeoff-pass")
        digest = checker.hashlib.sha256(durable.read_bytes()).hexdigest()
        repair = checker.PointerRepair(
            0,
            str(self.missing),
            self.missing,
            durable,
            REPO,
            REF,
            digest,
        )
        outside = self.root / "outside-receipt.md"
        outside.write_text(receipt())
        durable.unlink()
        durable.symlink_to(outside)

        with self.assertRaisesRegex(checker.PointerWake, "WAKE receipt pointer"):
            checker.validate_repair_candidates([repair])

        self.assertTrue(durable.is_symlink())


if __name__ == "__main__":
    unittest.main()
