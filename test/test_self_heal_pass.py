#!/usr/bin/env python3
"""One deliberately dirtied pass through Takeoff's four accepted healers."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from typing import Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "self-heal-pass-check.sh"
TAKEOFF = ROOT / "bin" / "takeoff"
XBQ_GRADER = ROOT / "tools" / "grade-xbq-result.py"
RECEIPT_CHECKER = ROOT / "tools" / "check-adoption-receipts.py"
FIXTURES = ROOT / "test" / "fixtures" / "self-heal-pass"
REPO = "sample-repo"
RECEIPT_NAME = "2026-08-22T050000Z-receipt.md"
CORE_IOS_KEYS = ("DEVELOPER_DIR", "IOS_DESTINATION", "XCB_LOCK_WAIT", "DERIVED_DATA")


class FixtureFailure(RuntimeError):
    """The composed proof did not exercise the expected real helper behavior."""


def command(
    argv: List[str],
    *,
    cwd: Path,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureFailure(message)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class DirtiedPassFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.home = root / "home"
        self.development = self.home / "Development"
        self.remote = root / "remotes" / f"{REPO}.git"
        self.canonical = self.development / REPO
        self.generated = (
            self.development
            / f"{REPO}-worktrees"
            / "takeoff-pass-20260822T050000Z"
        )
        self.source_pointer = (
            self.generated / "evidence" / "takeoff-pass" / RECEIPT_NAME
        )
        self.evidence_root = self.development / "takeoff-evidence"
        self.durable_receipt = (
            self.evidence_root
            / REPO
            / "recovered"
            / self.generated.name
            / RECEIPT_NAME
        )
        self.ledger_repo = root / "takeoff-ledger"
        self.adoption = self.ledger_repo / "ADOPTION.md"
        self.tmpdir = root / "tmp"
        self.healed: List[str] = []

    def run_git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = command(["git", "-C", str(repo), *args], cwd=ROOT)
        if result.returncode != 0:
            raise FixtureFailure(
                f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
            )
        return result

    def setup(self) -> None:
        self.development.mkdir(parents=True)
        self.remote.parent.mkdir(parents=True)
        self.tmpdir.mkdir()

        initialized = command(
            ["git", "init", "--bare", "--initial-branch=main", str(self.remote)],
            cwd=ROOT,
        )
        require(initialized.returncode == 0, initialized.stderr)
        self.canonical.mkdir()
        self.run_git(self.canonical, "init", "-b", "main")
        self.run_git(self.canonical, "config", "user.name", "Takeoff Self-Heal Test")
        self.run_git(
            self.canonical,
            "config",
            "user.email",
            "self-heal@example.invalid",
        )
        self.run_git(self.canonical, "remote", "add", "origin", str(self.remote))

        tracked = self.canonical / "tracked.txt"
        tracked.write_bytes(b"stale source\n")
        self.run_git(self.canonical, "add", "tracked.txt")
        self.run_git(self.canonical, "commit", "-m", "stale source")
        self.run_git(self.canonical, "push", "-u", "origin", "main")
        self.old_ref = self.run_git(self.canonical, "rev-parse", "HEAD").stdout.strip()

        self.generated.parent.mkdir()
        self.run_git(
            self.canonical,
            "worktree",
            "add",
            "--detach",
            str(self.generated),
            self.old_ref,
        )
        self.source_pointer.parent.mkdir(parents=True)
        self.source_pointer.write_text(self.receipt(self.old_ref), encoding="utf-8")

        tracked.write_bytes(b"current source\n")
        self.run_git(self.canonical, "add", "tracked.txt")
        self.run_git(self.canonical, "commit", "-m", "current source")
        self.run_git(self.canonical, "push", "origin", "main")
        self.new_ref = self.run_git(self.canonical, "rev-parse", "HEAD").stdout.strip()

        self.ledger_repo.mkdir()
        self.run_git(self.ledger_repo, "init", "-b", "main")
        self.run_git(self.ledger_repo, "config", "user.name", "Takeoff Ledger Test")
        self.run_git(
            self.ledger_repo,
            "config",
            "user.email",
            "ledger@example.invalid",
        )
        self.adoption_before = self.adoption_text(self.source_pointer).encode("utf-8")
        self.adoption.write_bytes(self.adoption_before)
        self.run_git(self.ledger_repo, "add", "ADOPTION.md")
        self.run_git(self.ledger_repo, "commit", "-m", "stale receipt pointer")

        self.developer = root_developer = self.root / "Xcode.app" / "Contents" / "Developer"
        xcodebuild = root_developer / "usr" / "bin" / "xcodebuild"
        xcodebuild.parent.mkdir(parents=True)
        xcodebuild.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        xcodebuild.chmod(0o755)

        self.canonical_before = self.tracked_snapshot(self.canonical)
        self.generated_before = self.tracked_snapshot(self.generated)

    def receipt(self, ref: str, extra: str = "") -> str:
        return (
            f"# takeoff pass — {REPO} — PROOF-ONLY\n"
            f"- ref judged: {ref}; host: fixture-host\n"
            '- lane unit rc=0 marker="1 passed" count=1\n'
            f"{extra}"
        )

    def adoption_text(self, pointer: Path) -> str:
        return (
            "# takeoff — ADOPTION\n\n"
            "| date | repo | ref | verdict | host | lanes | executed | elapsed | receipt |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            f"| 2026-08-22T050000Z | {REPO} | {self.old_ref[:12]} | PROOF-ONLY "
            f"| fixture-host | unit | executed=1 | 1s/2s | {pointer} |\n"
            "\n# ledger history must remain byte-identical\n"
        )

    def tracked_snapshot(self, repo: Path) -> Dict[str, bytes]:
        names = self.run_git(repo, "ls-files", "-z").stdout.split("\0")
        return {
            name: (repo / name).read_bytes()
            for name in names
            if name
        }

    def snapshot_digest(self, snapshot: Dict[str, bytes]) -> str:
        digest = hashlib.sha256()
        for name, content in sorted(snapshot.items()):
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(content)
            digest.update(b"\0")
        return digest.hexdigest()

    def helper_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["TMPDIR"] = str(self.tmpdir)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def heal_worktree(self) -> None:
        result = command(
            [
                str(TAKEOFF),
                "prepare-worktree",
                str(self.canonical),
                str(self.generated),
            ],
            cwd=ROOT,
            env=self.helper_env(),
        )
        require(result.returncode == 0, result.stderr)
        lines = result.stdout.splitlines()
        require(len(lines) == 1 and lines[0].startswith("HEALED worktree "), result.stdout)
        self.healed.append(lines[0])

        self.generated_after_heal = self.tracked_snapshot(self.generated)
        require(
            self.canonical_before == self.tracked_snapshot(self.canonical),
            "worktree recovery changed canonical source bytes",
        )
        require(
            self.generated_after_heal == self.canonical_before,
            "worktree recovery did not install exact origin/main source bytes",
        )
        require(self.durable_receipt.is_file(), "stale receipt was not preserved durably")

    def heal_ios_environment(self) -> None:
        env = self.helper_env()
        for key in CORE_IOS_KEYS:
            env.pop(key, None)
        env["TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR"] = str(self.developer)
        probe = (
            "import json,os; "
            f"print(json.dumps({{k: os.environ[k] for k in {CORE_IOS_KEYS!r}}}, sort_keys=True))"
        )
        result = command(
            [
                str(TAKEOFF),
                "ios-env",
                "--pass-root",
                str(self.generated),
                "--",
                sys.executable,
                "-c",
                probe,
            ],
            cwd=ROOT,
            env=env,
        )
        require(result.returncode == 0, result.stderr)
        lines = result.stdout.splitlines()
        expected = "HEALED ios-env DEVELOPER_DIR,IOS_DESTINATION,XCB_LOCK_WAIT,DERIVED_DATA"
        require(len(lines) == 2 and lines[0] == expected, result.stdout)
        payload = json.loads(lines[1])
        require(payload["DEVELOPER_DIR"] == str(self.developer), "wrong iOS developer repair")
        require(Path(payload["DERIVED_DATA"]).is_dir(), "DerivedData repair is absent")
        self.healed.append(lines[0])

    def refuse_xbq_false_green(self) -> None:
        result = command(
            [
                sys.executable,
                str(XBQ_GRADER),
                "--expect-marker",
                "Test Succeeded",
                "--floor",
                "1",
                str(FIXTURES / "xbq-rc0-failed.json"),
            ],
            cwd=ROOT,
            env=self.helper_env(),
        )
        lines = result.stderr.splitlines()
        expected = "HEALED false-green refusal: result is 'FAILED', not 'PASSED'"
        require(result.returncode == 1, "xbq rc=0 false-green was accepted")
        require(not result.stdout and lines == [expected], result.stdout + result.stderr)
        self.healed.append(lines[0])

    def heal_receipt_pointer(self, ambiguous: bool) -> Optional[str]:
        if ambiguous:
            conflict = self.evidence_root / REPO / "ambiguous" / RECEIPT_NAME
            conflict.parent.mkdir(parents=True)
            conflict.write_text(
                self.receipt(self.old_ref, "# conflicting durable bytes\n"),
                encoding="utf-8",
            )

        env = self.helper_env()
        env["TAKEOFF_EVIDENCE_ROOT"] = str(self.evidence_root)
        result = command(
            [sys.executable, str(RECEIPT_CHECKER), str(self.adoption)],
            cwd=ROOT,
            env=env,
        )
        if ambiguous:
            wake = (
                "WAKE receipt pointer: missing receipt; leave exactly one byte-compatible "
                f"{RECEIPT_NAME} for {REPO}@{self.old_ref[:12]} under "
                f"{self.evidence_root / REPO}, then rerun adoption grading"
            )
            require(result.returncode == 1, "ambiguous receipts were accepted")
            require(not result.stdout and result.stderr.splitlines() == [wake], result.stderr)
            require(self.adoption.read_bytes() == self.adoption_before, "ambiguous ledger changed")
            require(
                not self.run_git(
                    self.ledger_repo,
                    "status",
                    "--porcelain",
                    "--",
                    "ADOPTION.md",
                ).stdout,
                "ambiguous ledger became dirty",
            )
            return wake

        lines = result.stdout.splitlines()
        require(result.returncode == 0, result.stderr)
        require(
            len(lines) == 2
            and lines[0].startswith("HEALED receipt pointer: ")
            and lines[1] == "adoption receipts: PASS rows=1",
            result.stdout,
        )
        self.healed.append(lines[0])
        return None

    def grade_real_lane(self) -> str:
        result = command(
            [
                sys.executable,
                str(XBQ_GRADER),
                "--expect-marker",
                "Test Succeeded",
                "--floor",
                "1",
                str(FIXTURES / "xbq-passed.json"),
            ],
            cwd=ROOT,
            env=self.helper_env(),
        )
        require(result.returncode == 0 and not result.stderr, result.stderr)
        require(
            result.stdout.strip()
            == "xbq marker: PASS result=PASSED executed=13 marker='Test Succeeded'",
            result.stdout,
        )
        return '- lane xbq rc=0 marker="Test Succeeded" count=13'

    def audit_lines(self) -> List[str]:
        canonical_after = self.tracked_snapshot(self.canonical)
        generated_after = self.tracked_snapshot(self.generated)
        require(canonical_after == self.canonical_before, "canonical source bytes drifted")
        require(generated_after == self.generated_after_heal, "healed pass source bytes drifted")

        expected_adoption = self.adoption_before.replace(
            str(self.source_pointer).encode("utf-8"),
            str(self.durable_receipt).encode("utf-8"),
            1,
        )
        adoption_after = self.adoption.read_bytes()
        require(adoption_after == expected_adoption, "ledger changed beyond the receipt cell")
        require(
            not self.run_git(
                self.ledger_repo,
                "status",
                "--porcelain",
                "--",
                "ADOPTION.md",
            ).stdout,
            "healed ledger is not committed cleanly",
        )
        committed = self.run_git(
            self.ledger_repo,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        ).stdout.splitlines()
        require(committed == ["ADOPTION.md"], "pointer heal committed another path")

        return [
            "BYTE-AUDIT source canonical unchanged "
            f"sha256={self.snapshot_digest(canonical_after)}",
            "BYTE-AUDIT source pass tracked.txt "
            f"sha256={sha256(self.generated_before['tracked.txt'])}->{sha256(generated_after['tracked.txt'])} "
            "expected-origin/main",
            "BYTE-AUDIT ledger ADOPTION.md "
            f"sha256={sha256(self.adoption_before)}->{sha256(adoption_after)} "
            "receipt-cell-only clean-commit",
        ]

    def run(self, ambiguous: bool) -> int:
        self.setup()
        self.heal_worktree()
        self.heal_ios_environment()
        self.refuse_xbq_false_green()
        wake = self.heal_receipt_pointer(ambiguous)

        if wake is not None:
            require(
                self.canonical_before == self.tracked_snapshot(self.canonical),
                "ambiguous pass changed canonical source",
            )
            require(
                self.generated_after_heal == self.tracked_snapshot(self.generated),
                "ambiguous pass changed healed source",
            )
            print(wake, file=sys.stderr)
            return 1

        lane = self.grade_real_lane()
        require(len(self.healed) == 4, "not every accepted helper emitted one HEALED line")
        receipt = ["# takeoff self-heal pass fixture", *self.healed, *self.audit_lines(), lane]
        lane_index = receipt.index(lane)
        require(
            all(receipt.index(line) < lane_index for line in self.healed),
            "a HEALED action appeared after lane output",
        )
        print("\n".join(receipt))
        return 0


class SelfHealPassCheckTests(unittest.TestCase):
    def run_check(self, *, ambiguous: bool = False) -> subprocess.CompletedProcess[str]:
        self.assertTrue(CHECK.is_file(), f"missing exact proof harness: {CHECK}")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        argument = "--fixture-ambiguity" if ambiguous else "--fixture"
        return command(["bash", str(CHECK), argument], cwd=ROOT, env=env)

    def test_exact_proof_command_composes_four_healers_before_lane_output(self) -> None:
        result = self.run_check()

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], "# takeoff self-heal pass fixture")
        heals = [line for line in lines if line.startswith("HEALED ")]
        self.assertEqual(len(heals), 4, result.stdout)
        self.assertTrue(heals[0].startswith("HEALED worktree "))
        self.assertEqual(
            heals[1],
            "HEALED ios-env DEVELOPER_DIR,IOS_DESTINATION,XCB_LOCK_WAIT,DERIVED_DATA",
        )
        self.assertEqual(
            heals[2],
            "HEALED false-green refusal: result is 'FAILED', not 'PASSED'",
        )
        self.assertTrue(heals[3].startswith("HEALED receipt pointer: "))
        lane = '- lane xbq rc=0 marker="Test Succeeded" count=13'
        lane_index = lines.index(lane)
        self.assertTrue(all(lines.index(healed) < lane_index for healed in heals))
        audits = [line for line in lines if line.startswith("BYTE-AUDIT ")]
        self.assertEqual(len(audits), 3, result.stdout)
        self.assertTrue(all(lines.index(audit) < lane_index for audit in audits))
        print(result.stdout, end="")

    def test_unrecognized_receipt_ambiguity_refuses_with_one_exact_wake(self) -> None:
        result = self.run_check(ambiguous=True)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        lines = result.stderr.splitlines()
        self.assertEqual(len(lines), 1, result.stderr)
        self.assertTrue(
            lines[0].startswith(
                "WAKE receipt pointer: missing receipt; leave exactly one byte-compatible "
            ),
            result.stderr,
        )
        self.assertTrue(lines[0].endswith("then rerun adoption grading"), result.stderr)
        self.assertEqual(result.stderr.count("WAKE receipt pointer:"), 1)


def fixture_main(ambiguous: bool) -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="takeoff-self-heal-") as temporary:
            return DirtiedPassFixture(Path(temporary)).run(ambiguous)
    except (FixtureFailure, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"self-heal pass fixture: RED — {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if sys.argv[1:] in (["--fixture"], ["--fixture-ambiguity"]):
        raise SystemExit(fixture_main(sys.argv[1] == "--fixture-ambiguity"))
    unittest.main()
