from __future__ import annotations

import fcntl
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
STAMP = ROOT / "bin" / "stamp"
CHECKER = ROOT / "tools" / "check-adoption-receipts.py"


def receipt(
    ref: str,
    repo: str = "sample-repo",
    count: str = "1",
    verdict: str = "PROOF-ONLY",
    rc: str = "0",
) -> str:
    released = "- RELEASED: fixture release completed\n" if verdict == "BLESSED" else ""
    return f"""# takeoff pass — {repo} — {verdict}
- repo purpose: deterministic stamp integration fixture
- last BLESSED: 2026-08-21 {ref}
- live surfaces: fixture source repository and local adoption ledger
- open contradictions: none
- why: deterministic test fixture
- ref judged: {ref}; host: test-host
- lane unit rc={rc} marker="1 passed" count={count}
{released}
"""


class StampDurabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.takeoff_root = self.home / "relocated takeoff"
        (self.takeoff_root / "bin").mkdir(parents=True)
        (self.takeoff_root / "tools").mkdir()
        self.stamp = self.takeoff_root / "bin" / "stamp"
        shutil.copy2(STAMP, self.stamp)
        shutil.copy2(
            ROOT / "tools" / "adoption_lock.py",
            self.takeoff_root / "tools" / "adoption_lock.py",
        )
        self.adoption = self.takeoff_root / "ADOPTION.md"
        self.adoption.write_text(
            "# takeoff — ADOPTION\n\n## v2 — chief pass history\n\n"
            "| date | repo | ref | verdict | host | lanes | executed | elapsed | receipt |\n"
        )
        self.git("init")
        self.git("config", "user.name", "Takeoff Test")
        self.git("config", "user.email", "takeoff-test@example.invalid")
        self.git("add", "ADOPTION.md")
        self.git("commit", "-m", "initial adoption ledger")
        self.source_repo = self.home / "work" / "sample-repo"
        self.source_repo.mkdir(parents=True)
        self.source_git("init")
        self.source_git("config", "user.name", "Takeoff Source Test")
        self.source_git("config", "user.email", "takeoff-source@example.invalid")
        self.source_git("remote", "add", "origin", "git@example.invalid:firstbite/sample-repo.git")
        (self.source_repo / "tracked.txt").write_text("source authority\n")
        self.source_git("add", "tracked.txt")
        self.source_git("commit", "-m", "source fixture")
        self.source_ref = self.source_git("rev-parse", "HEAD").stdout.strip()
        self.source = (
            self.source_repo
            / "evidence"
            / "takeoff-pass"
            / "2026-08-22T030000Z-receipt.md"
        )
        self.source.parent.mkdir(parents=True)
        self.source.write_text(receipt(self.source_ref))

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.adoption.parent,
            text=True,
            capture_output=True,
            check=True,
        )

    def source_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.source_repo,
            text=True,
            capture_output=True,
            check=True,
        )

    def run_stamp(
        self,
        source: Optional[Path] = None,
        extra_env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [str(self.stamp), str(source or self.source)],
            cwd=self.takeoff_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def durable_path(self, evidence_root: Optional[Path] = None) -> Path:
        return (
            (
                evidence_root
                or self.home / "Development" / "takeoff-evidence"
            )
            / "sample-repo"
            / "takeoff-pass"
            / self.source.name
        )

    def adoption_lock_path(self) -> Path:
        common = self.git("rev-parse", "--git-common-dir").stdout.strip()
        return (self.adoption.parent / common).resolve() / "takeoff-adoption.lock"

    def test_copies_receipt_before_recording_durable_path(self) -> None:
        """Removing the pass worktree must not break the stamped receipt pointer."""
        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        durable = self.durable_path()
        self.assertEqual(durable.read_text(), self.source.read_text())
        adoption = self.adoption.read_text()
        self.assertIn(str(durable), adoption)
        self.assertNotIn(str(self.source), adoption)

    def test_evidence_root_override_controls_durable_copy(self) -> None:
        """The durable store may move without moving the Takeoff checkout."""
        evidence_root = self.home / "custom evidence"

        result = self.run_stamp(
            extra_env={"TAKEOFF_EVIDENCE_ROOT": str(evidence_root)}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        durable = self.durable_path(evidence_root)
        self.assertEqual(durable.read_bytes(), self.source.read_bytes())
        self.assertIn(str(durable), self.adoption.read_text())

    def test_relative_evidence_root_refuses_without_ledger_change(self) -> None:
        """Durable evidence must not follow whichever repo invoked Takeoff."""
        before = self.adoption.read_bytes()

        result = self.run_stamp(
            extra_env={"TAKEOFF_EVIDENCE_ROOT": "relative evidence"}
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stderr.splitlines()), 1)
        self.assertIn(
            "TAKEOFF_EVIDENCE_ROOT must be an absolute path",
            result.stderr,
        )
        self.assertEqual(self.adoption.read_bytes(), before)
        self.assertFalse((self.takeoff_root / "relative evidence").exists())

    def test_receipt_path_cannot_break_the_markdown_ledger_row(self) -> None:
        for unsafe in ("|", "\n"):
            with self.subTest(unsafe=repr(unsafe)):
                before = self.adoption.read_bytes()
                source = self.source.with_name(
                    f"2026-08-22T030000Z{unsafe}receipt.md"
                )
                source.write_text(receipt(self.source_ref))

                result = self.run_stamp(source)

                self.assertEqual(result.returncode, 1)
                self.assertIn("receipt path cannot contain", result.stderr)
                self.assertEqual(self.adoption.read_bytes(), before)

    def test_evidence_root_cannot_break_the_markdown_ledger_row(self) -> None:
        for unsafe in ("|", "\n"):
            with self.subTest(unsafe=repr(unsafe)):
                before = self.adoption.read_bytes()
                evidence_root = self.home / f"evidence{unsafe}root"

                result = self.run_stamp(
                    extra_env={"TAKEOFF_EVIDENCE_ROOT": str(evidence_root)}
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn("evidence root cannot contain", result.stderr)
                self.assertEqual(self.adoption.read_bytes(), before)
                self.assertFalse(evidence_root.exists())

    def test_receipt_without_leading_cold_reader_reconstruction_is_refused(self) -> None:
        """A stamp must not admit a receipt that cannot re-orient a cold reader."""
        before = self.adoption.read_text()
        self.source.write_text(
            f"# takeoff pass — sample-repo — PROOF-ONLY\n"
            f"- why: legacy receipt with no cold-reader lead\n"
            f"- ref judged: {self.source_ref}; host: test-host\n"
            '- lane unit rc=0 marker="1 passed" count=1\n'
        )

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cold-reader reconstruction", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_receipt_title_must_be_the_first_nonblank_line(self) -> None:
        before = self.adoption.read_bytes()
        self.source.write_text("operator preface\n\n" + receipt(self.source_ref))

        result = self.run_stamp()

        self.assertEqual(result.returncode, 1)
        self.assertIn("first nonblank line", result.stderr)
        self.assertEqual(self.adoption.read_bytes(), before)
        self.assertFalse(self.durable_path().exists())

    def test_blank_lines_may_precede_the_receipt_title(self) -> None:
        self.source.write_text("\n \n" + receipt(self.source_ref))

        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.durable_path().read_bytes(), self.source.read_bytes())

    def test_cold_reader_reconstruction_must_precede_why_and_lane_output(self) -> None:
        """Moving purpose below why must fail even when every field is present."""
        before = self.adoption.read_text()
        content = self.source.read_text()
        purpose = "- repo purpose: deterministic stamp integration fixture\n"
        content = content.replace(purpose, "", 1).replace(
            "- why: deterministic test fixture\n",
            "- why: deterministic test fixture\n" + purpose,
            1,
        )
        self.source.write_text(content)

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("before why or lane output", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_cold_reader_reconstruction_is_the_first_receipt_screen(self) -> None:
        """Ref metadata cannot push the reconstruction below the title."""
        before = self.adoption.read_text()
        content = self.source.read_text()
        ref_line = f"- ref judged: {self.source_ref}; host: test-host\n"
        content = content.replace(ref_line, "", 1).replace(
            "- repo purpose: deterministic stamp integration fixture\n",
            ref_line + "- repo purpose: deterministic stamp integration fixture\n",
            1,
        )
        self.source.write_text(content)

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cold-reader reconstruction", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_success_commits_the_adoption_row(self) -> None:
        """A successful stamp must not leave its only ledger row uncommitted."""
        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("status", "--porcelain", "--", "ADOPTION.md").stdout, "")
        self.assertIn(
            "adoption: sample-repo PROOF-ONLY train stamp",
            self.git("log", "-1", "--pretty=%s").stdout,
        )

    def test_pointer_heal_does_not_make_the_next_stamp_refuse(self) -> None:
        """A live pointer heal must be durable before the next chief stamps."""
        old_name = "2026-08-22T020000Z-receipt.md"
        missing = self.home / "removed-worktree" / "evidence" / "takeoff-pass" / old_name
        durable = self.durable_path().with_name(old_name)
        durable.parent.mkdir(parents=True, exist_ok=True)
        durable.write_text(receipt(self.source_ref))
        with self.adoption.open("a") as adoption:
            adoption.write(
                f"| 2026-08-22T020000Z | sample-repo | {self.source_ref[:12]} "
                f"| PROOF-ONLY | test-host | unit | executed=1 | 1s/2s | {missing} |\n"
            )
        self.git("add", "ADOPTION.md")
        self.git("commit", "-m", "fixture: stale receipt pointer")

        env = os.environ.copy()
        env["TAKEOFF_EVIDENCE_ROOT"] = str(durable.parent.parent.parent)
        healed = subprocess.run(
            ["/usr/bin/python3", str(CHECKER), str(self.adoption)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        stamped = self.run_stamp()

        self.assertEqual(healed.returncode, 0, healed.stderr)
        self.assertIn("HEALED receipt pointer", healed.stdout)
        self.assertEqual(stamped.returncode, 0, stamped.stderr)
        self.assertNotIn("pre-existing uncommitted changes", stamped.stderr)
        self.assertEqual(self.git("status", "--porcelain", "--", "ADOPTION.md").stdout, "")

    def test_copy_failure_leaves_adoption_unchanged(self) -> None:
        """A failed durable copy must never mint an unverifiable adoption row."""
        before = self.adoption.read_text()
        durable = self.durable_path()
        durable.mkdir(parents=True)

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.adoption.read_text(), before)

    def test_conflicting_durable_receipt_refuses_without_overwrite(self) -> None:
        """The same durable name with different evidence must fail closed."""
        before = self.adoption.read_text()
        durable = self.durable_path()
        durable.parent.mkdir(parents=True)
        durable.write_text("different evidence\n")

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(durable.read_text(), "different evidence\n")
        self.assertEqual(self.adoption.read_text(), before)

    def test_symlinked_durable_receipt_refuses_without_ledger_change(self) -> None:
        before = self.adoption.read_bytes()
        durable = self.durable_path()
        durable.parent.mkdir(parents=True)
        target = self.home / "replaceable-receipt.md"
        target.write_bytes(self.source.read_bytes())
        durable.symlink_to(target)

        result = self.run_stamp()

        self.assertEqual(result.returncode, 1)
        self.assertIn("durable receipt collision", result.stderr)
        self.assertTrue(durable.is_symlink())
        self.assertEqual(self.adoption.read_bytes(), before)

    def test_unsafe_repo_name_cannot_escape_evidence_root(self) -> None:
        """Receipt-controlled repo names must not become path traversal."""
        before = self.adoption.read_text()
        self.source.write_text(receipt(self.source_ref, "../../escaped"))

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.adoption.read_text(), before)
        self.assertFalse((self.home / "Development" / "escaped").exists())

    def test_repeat_stamp_is_idempotently_refused(self) -> None:
        """A source worktree path must not bypass durable-row duplicate detection."""
        first = self.run_stamp()
        after_first = self.adoption.read_text()

        second = self.run_stamp()

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(self.adoption.read_text(), after_first)

    def test_symlinked_source_receipt_refuses_without_ledger_change(self) -> None:
        before = self.adoption.read_bytes()
        actual = self.source.with_name("actual-receipt.md")
        self.source.rename(actual)
        self.source.symlink_to(actual)

        result = self.run_stamp()

        self.assertEqual(result.returncode, 1)
        self.assertIn("receipt must be a regular file", result.stderr)
        self.assertTrue(self.source.is_symlink())
        self.assertEqual(self.adoption.read_bytes(), before)
        self.assertFalse(self.durable_path().exists())

    def test_legacy_source_path_row_is_healed_without_duplicate(self) -> None:
        """A prior source-path row is committed on retry, never appended twice."""
        before = self.adoption.read_text() + f"| legacy | {self.source} |\n"
        self.adoption.write_text(before)

        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.adoption.read_text(), before)
        self.assertEqual(self.git("status", "--porcelain", "--", "ADOPTION.md").stdout, "")

    def test_concurrent_stamps_append_and_commit_exactly_once(self) -> None:
        """Two chiefs racing the same receipt must produce one row and one commit."""
        large_receipt = receipt(self.source_ref) + ("# evidence padding\n" * 100_000)
        self.source.write_text(large_receipt)
        sources = [self.source] * 6

        env = os.environ.copy()
        env["HOME"] = str(self.home)
        processes = [
            subprocess.Popen(
                [str(self.stamp), str(source)],
                cwd=self.takeoff_root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for source in sources
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]

        self.assertEqual(sum(returncode == 0 for _, _, returncode in results), 1, results)
        self.assertEqual(self.adoption.read_text().count(str(self.durable_path())), 1)
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "2")
        self.assertEqual(self.git("status", "--porcelain", "--", "ADOPTION.md").stdout, "")

    def test_stamp_waits_for_the_stable_receipt_pointer_lock(self) -> None:
        """The ledger lock cannot move when the durable evidence root moves."""
        lock_path = self.adoption_lock_path()
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        before = self.adoption.read_bytes()
        evidence_root = self.home / "different durable root"
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["TAKEOFF_EVIDENCE_ROOT"] = str(evidence_root)

        with lock_path.open("a+") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            process = subprocess.Popen(
                [str(self.stamp), str(self.source)],
                cwd=self.takeoff_root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            def stop_process() -> None:
                if process.poll() is None:
                    process.kill()
                process.communicate()

            self.addCleanup(stop_process)
            try:
                early_output = process.communicate(timeout=1.0)
            except subprocess.TimeoutExpired:
                early_output = None

            self.assertIsNone(early_output, early_output)
            self.assertEqual(self.adoption.read_bytes(), before)

        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, stderr)
        self.assertIn("stamp: OK", stdout)
        self.assertIn(str(self.durable_path(evidence_root)), self.adoption.read_text())

    def test_non_repository_source_refuses_without_ledger_change(self) -> None:
        """A hand-written receipt outside a real source repository is not execution."""
        before = self.adoption.read_text()
        source = (
            self.home
            / "not-a-repository"
            / "evidence"
            / "takeoff-pass"
            / self.source.name
        )
        source.parent.mkdir(parents=True)
        source.write_text(receipt(self.source_ref))

        result = self.run_stamp(source)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a git repository", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_unresolvable_judged_ref_refuses_without_ledger_change(self) -> None:
        """The judged SHA must resolve to a commit in the receipt's source repo."""
        before = self.adoption.read_text()
        self.source.write_text(receipt("deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"))

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("judged ref does not resolve", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_receipt_worktree_head_must_equal_the_judged_ref(self) -> None:
        before = self.adoption.read_bytes()
        (self.source_repo / "tracked.txt").write_text("later checkout state\n")
        self.source_git("add", "tracked.txt")
        self.source_git("commit", "-m", "later source state")

        result = self.run_stamp()

        self.assertEqual(result.returncode, 1)
        self.assertIn("worktree HEAD does not match judged ref", result.stderr)
        self.assertEqual(self.adoption.read_bytes(), before)
        self.assertFalse(self.durable_path().exists())

    def test_repo_title_must_match_source_origin(self) -> None:
        """A real worktree cannot lend its execution to another named repo."""
        before = self.adoption.read_text()
        self.source.write_text(receipt(self.source_ref, repo="other-repo"))

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match source origin", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_one_malformed_lane_cannot_hide_behind_a_valid_lane(self) -> None:
        """Every claimed lane must expose a parseable execution count."""
        before = self.adoption.read_text()
        self.source.write_text(
            receipt(self.source_ref)
            + '- lane hidden rc=0 marker="looked fine" count=unknown\n'
        )

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed lane row", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_zero_executed_count_refuses_without_ledger_change(self) -> None:
        """A correctly shaped lane with zero executions cannot enter adoption."""
        before = self.adoption.read_text()
        self.source.write_text(receipt(self.source_ref, count="0"))

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("zero executed", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)

    def test_non_refused_verdict_rejects_nonzero_lane_rc(self) -> None:
        """A failed lane cannot be transcribed as a successful or deferred pass."""
        for receipt_index, (verdict, rc) in enumerate(
            (("BLESSED", "1"), ("PROOF-ONLY", "7"), ("DEFERRED", "255")),
            start=1,
        ):
            with self.subTest(verdict=verdict):
                before = self.adoption.read_text()
                source = self.source.with_name(
                    f"2026-08-22T03000{receipt_index}Z-receipt.md"
                )
                source.write_text(
                    receipt(self.source_ref, verdict=verdict, rc=rc)
                )

                result = self.run_stamp(source)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    f"lane unit: rc={rc} requires REFUSED verdict", result.stderr
                )
                self.assertEqual(self.adoption.read_text(), before)

    def test_duplicate_rc_fields_refuse_without_ledger_change(self) -> None:
        """A lane cannot hide a later failure behind an earlier zero return code."""
        for separator in (" ", "|"):
            with self.subTest(separator=separator):
                before = self.adoption.read_text()
                self.source.write_text(
                    receipt(self.source_ref).replace(
                        "rc=0 marker=", f"rc=0{separator}rc=7 marker=", 1
                    )
                )

                result = self.run_stamp()

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("malformed lane row", result.stderr)
                self.assertEqual(self.adoption.read_text(), before)
                self.assertFalse(self.durable_path().exists())

    def test_later_nonzero_lane_rc_refuses_without_ledger_change(self) -> None:
        """Every lane must be checked, not only the first parsed lane."""
        before = self.adoption.read_text()
        self.source.write_text(
            receipt(self.source_ref)
            + '- lane integration rc=7 marker="failed" count=1\n'
        )

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lane integration: rc=7 requires REFUSED verdict", result.stderr)
        self.assertEqual(self.adoption.read_text(), before)
        self.assertFalse(self.durable_path().exists())

    def test_refused_verdict_preserves_nonzero_lane_rc(self) -> None:
        """A refused pass may retain the failed lane that justified refusal."""
        self.source.write_text(receipt(self.source_ref, verdict="REFUSED", rc="7"))

        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| REFUSED |", self.adoption.read_text())
        self.assertEqual(self.durable_path().read_bytes(), self.source.read_bytes())
        self.assertIn("rc=7", self.durable_path().read_text())

    def test_durable_copy_uses_the_bytes_that_were_judged(self) -> None:
        original = self.source.read_bytes()
        shim_dir = self.home / "git-shim"
        shim_dir.mkdir()
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        shim = shim_dir / "git"
        shim.write_text(
            "#!/usr/bin/env python3\n"
            "import os, subprocess, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "result = subprocess.run(\n"
            "    [os.environ['TAKEOFF_REAL_GIT'], *args], capture_output=True\n"
            ")\n"
            "if 'rev-parse' in args and '--verify' in args:\n"
            "    receipt = Path(os.environ['TAKEOFF_MUTATE_RECEIPT'])\n"
            "    receipt.write_bytes(receipt.read_bytes() + b'# late replacement\\n')\n"
            "sys.stdout.buffer.write(result.stdout)\n"
            "sys.stderr.buffer.write(result.stderr)\n"
            "raise SystemExit(result.returncode)\n"
        )
        shim.chmod(0o755)

        result = self.run_stamp(
            extra_env={
                "PATH": f"{shim_dir}{os.pathsep}{os.environ['PATH']}",
                "TAKEOFF_MUTATE_RECEIPT": str(self.source),
                "TAKEOFF_REAL_GIT": str(real_git),
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.source.read_bytes(), original)
        self.assertEqual(self.durable_path().read_bytes(), original)

    def test_commit_hook_cannot_replace_the_ledger_payload(self) -> None:
        hook = self.takeoff_root / ".git" / "hooks" / "pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            "printf '# WRONG HOOK BYTE\\n' > ADOPTION.md\n"
            "git add ADOPTION.md\n"
        )
        hook.chmod(0o755)

        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        committed = self.git("show", "HEAD:ADOPTION.md").stdout
        self.assertNotIn("WRONG HOOK BYTE", committed)
        self.assertIn(str(self.durable_path()), committed)
        self.assertEqual(self.adoption.read_text(), committed)

    def test_retry_commits_an_existing_uncommitted_row_for_same_receipt(self) -> None:
        """A crash after append must heal on retry instead of stranding the row."""
        durable = self.durable_path()
        durable.parent.mkdir(parents=True)
        durable.write_text(self.source.read_text())
        self.adoption.write_text(
            self.adoption.read_text()
            + f"| interrupted | sample-repo | {durable} |\n"
        )

        result = self.run_stamp()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.adoption.read_text().count(str(durable)), 1)
        self.assertEqual(self.git("status", "--porcelain", "--", "ADOPTION.md").stdout, "")

    def test_retry_refuses_to_commit_unrelated_adoption_edits(self) -> None:
        """Crash recovery must not absorb another person's ledger changes."""
        durable = self.durable_path()
        durable.parent.mkdir(parents=True)
        durable.write_text(self.source.read_text())
        dirty = (
            self.adoption.read_text()
            + f"| interrupted | sample-repo | {durable} |\n"
            + "# unrelated human edit\n"
        )
        self.adoption.write_text(dirty)

        result = self.run_stamp()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.adoption.read_text(), dirty)
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")


class RealLedgerContractTests(unittest.TestCase):
    def test_shipped_adoption_md_matches_the_stamp_section_contract(self) -> None:
        """The real ledger must stay stamp-writable: 269c13e renamed the v2
        section header without updating the stamp check, so every stamp on the
        real repo refused. Pin the ledger and the tool to one name."""
        stamp_source = STAMP.read_text(encoding="utf-8")
        match = re.search(r'if "(## v2 — [^"]+)" not in adoption:', stamp_source)
        self.assertIsNotNone(match, "stamp must name its required v2 section")
        ledger = (ROOT / "ADOPTION.md").read_text(encoding="utf-8")
        self.assertIn(match.group(1), ledger)


if __name__ == "__main__":
    unittest.main()
