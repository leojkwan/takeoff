from __future__ import annotations

import os
import importlib.machinery
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "bin" / "prepare-worktree"
PASS_DOC = Path(os.environ.get("TAKEOFF_PASS_DOC", ROOT / "PASS.md"))


class PrepareWorktreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.remote = self.root / "sample-repo.git"
        self.publisher = self.root / "publisher"
        self.canonical = self.root / "sample-repo"
        self.pass_root = self.root / "sample-repo-worktrees"
        self.worktree = self.pass_root / "takeoff-pass-20260822T040000Z"

        self.run_cmd("git", "init", "--bare", str(self.remote))
        self.run_cmd("git", "init", "-b", "main", str(self.publisher))
        self.git(self.publisher, "config", "user.name", "Takeoff Test")
        self.git(self.publisher, "config", "user.email", "takeoff@example.invalid")
        self.git(self.publisher, "remote", "add", "origin", str(self.remote))
        (self.publisher / "tracked.txt").write_text("one\n")
        (self.publisher / ".gitignore").write_text("evidence/\nscratch/\n")
        self.git(self.publisher, "add", "tracked.txt", ".gitignore")
        self.git(self.publisher, "commit", "-m", "one")
        self.git(self.publisher, "push", "-u", "origin", "main")
        self.first_ref = self.git(self.publisher, "rev-parse", "HEAD").stdout.strip()

        self.run_cmd("git", "clone", "--branch", "main", str(self.remote), str(self.canonical))
        self.canonical_head = self.git(self.canonical, "rev-parse", "HEAD").stdout.strip()
        self.canonical_status = self.git(self.canonical, "status", "--porcelain=v1").stdout

        (self.publisher / "tracked.txt").write_text("two\n")
        self.git(self.publisher, "add", "tracked.txt")
        self.git(self.publisher, "commit", "-m", "two")
        self.git(self.publisher, "push", "origin", "main")
        self.second_ref = self.git(self.publisher, "rev-parse", "HEAD").stdout.strip()

        self.pass_root.mkdir()
        self.git(
            self.canonical,
            "worktree",
            "add",
            "--detach",
            str(self.worktree),
            self.first_ref,
        )

    def run_cmd(
        self, *args: str, cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return self.run_cmd("git", "-C", str(repo), *args)

    def prepare(
        self,
        path: Optional[Path] = None,
        extra_env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(PREPARE), str(self.canonical), str(path or self.worktree)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )

    def assert_canonical_untouched(self) -> None:
        self.assertEqual(
            self.git(self.canonical, "rev-parse", "HEAD").stdout.strip(),
            self.canonical_head,
        )
        self.assertEqual(
            self.git(self.canonical, "status", "--porcelain=v1").stdout,
            self.canonical_status,
        )

    def durable_recovery(self, evidence_root: Optional[Path] = None) -> Path:
        return (
            (
                evidence_root
                or self.home / "Development" / "takeoff-evidence"
            )
            / "sample-repo"
            / "recovered"
            / self.worktree.name
        )

    def test_heals_stale_generated_worktree_and_preserves_receipt(self) -> None:
        receipt = self.worktree / "evidence" / "takeoff-pass" / "receipt.md"
        receipt.parent.mkdir(parents=True)
        receipt.write_text("durable evidence\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"HEALED worktree {self.first_ref} -> {self.second_ref}",
            result.stdout,
        )
        self.assertEqual(
            self.git(self.worktree, "rev-parse", "HEAD").stdout.strip(),
            self.second_ref,
        )
        self.assertEqual(
            subprocess.run(
                ["git", "-C", str(self.worktree), "symbolic-ref", "-q", "HEAD"],
                text=True,
                capture_output=True,
                check=False,
            ).returncode,
            1,
        )
        durable = self.durable_recovery() / receipt.name
        self.assertEqual(durable.read_text(), "durable evidence\n")
        self.assert_canonical_untouched()

    def test_evidence_root_override_controls_recovered_receipts(self) -> None:
        receipt = self.worktree / "evidence" / "takeoff-pass" / "receipt.md"
        receipt.parent.mkdir(parents=True)
        receipt.write_text("custom durable evidence\n")
        evidence_root = self.root / "custom evidence"

        result = self.prepare(
            extra_env={"TAKEOFF_EVIDENCE_ROOT": str(evidence_root)}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.durable_recovery(evidence_root) / receipt.name).read_text(),
            "custom durable evidence\n",
        )
        self.assertFalse(
            (
                self.home
                / "Development"
                / "takeoff-evidence"
                / "sample-repo"
            ).exists()
        )
        self.assert_canonical_untouched()

    def test_symlinked_evidence_destination_refuses_without_moving_receipts(self) -> None:
        receipt = self.worktree / "evidence" / "takeoff-pass" / "receipt.md"
        receipt.parent.mkdir(parents=True)
        receipt.write_text("stay in the worktree\n")
        for symlink_level in ("root", "repo", "recovered"):
            with self.subTest(symlink_level=symlink_level):
                external = self.root / f"external durable store {symlink_level}"
                external.mkdir()
                evidence_root = self.root / f"custom evidence {symlink_level}"
                repo_root = evidence_root / "sample-repo"
                recovered_root = repo_root / "recovered"
                if symlink_level == "root":
                    evidence_root.symlink_to(external, target_is_directory=True)
                elif symlink_level == "repo":
                    evidence_root.mkdir()
                    repo_root.symlink_to(external, target_is_directory=True)
                else:
                    repo_root.mkdir(parents=True)
                    recovered_root.symlink_to(external, target_is_directory=True)

                result = self.prepare(
                    extra_env={"TAKEOFF_EVIDENCE_ROOT": str(evidence_root)}
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn("durable", result.stderr)
                self.assertIn("must be a real directory", result.stderr)
                self.assertEqual(receipt.read_text(), "stay in the worktree\n")
                self.assertEqual(list(external.iterdir()), [])
                self.assert_canonical_untouched()

    def test_pass_routes_generated_worktrees_through_the_admission_helper(self) -> None:
        """A safe helper that the release chief never calls is still absent."""
        contract = " ".join(PASS_DOC.read_text().split())
        self.assertIn(
            "takeoff prepare-worktree <canonical-repo> <generated-worktree>",
            contract,
        )
        self.assertIn("refuses rather than delete unknown dirty changes", contract)

    def test_refuses_unknown_dirty_changes_with_one_exact_wake(self) -> None:
        (self.worktree / "tracked.txt").write_text("human edit\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "prepare-worktree: REFUSED — wake: inspect and preserve "
            f"non-evidence changes in {self.worktree.resolve()}",
        )
        self.assertEqual((self.worktree / "tracked.txt").read_text(), "human edit\n")
        self.assert_canonical_untouched()

    def test_refuses_a_path_that_is_not_a_generated_takeoff_worktree(self) -> None:
        unsafe = self.root / "arbitrary" / "takeoff-pass-20260822T040000Z"

        result = self.prepare(unsafe)

        self.assertEqual(result.returncode, 1)
        self.assertIn("not the canonical generated worktree location", result.stderr)
        self.assertFalse(unsafe.exists())
        self.assert_canonical_untouched()

    def test_refuses_ignored_non_evidence_before_removal(self) -> None:
        ignored = self.worktree / "scratch" / "user-cache.txt"
        ignored.parent.mkdir()
        ignored.write_text("not Takeoff evidence\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("inspect and preserve non-evidence changes", result.stderr)
        self.assertEqual(ignored.read_text(), "not Takeoff evidence\n")
        self.assert_canonical_untouched()

    def test_refuses_ignored_data_created_after_the_final_scan(self) -> None:
        shim_dir = self.root / "git-shim"
        shim_dir.mkdir()
        counter = self.root / "status-count"
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
            "if (\n"
            "    len(args) >= 3\n"
            "    and args[0] == '-C'\n"
            "    and Path(args[1]) == Path(os.environ['TAKEOFF_RACE_WORKTREE'])\n"
            "    and args[2] == 'status'\n"
            "):\n"
            "    counter = Path(os.environ['TAKEOFF_RACE_COUNTER'])\n"
            "    count = int(counter.read_text()) + 1 if counter.exists() else 1\n"
            "    counter.write_text(str(count))\n"
            "    if count == 2:\n"
            "        late = Path(os.environ['TAKEOFF_RACE_WORKTREE']) / 'scratch' / 'late-race.txt'\n"
            "        late.parent.mkdir(parents=True, exist_ok=True)\n"
            "        late.write_text('created after final scan\\n')\n"
            "sys.stdout.buffer.write(result.stdout)\n"
            "sys.stderr.buffer.write(result.stderr)\n"
            "raise SystemExit(result.returncode)\n"
        )
        shim.chmod(0o755)
        late = self.worktree / "scratch" / "late-race.txt"

        result = self.prepare(
            extra_env={
                "PATH": f"{shim_dir}{os.pathsep}{os.environ['PATH']}",
                "TAKEOFF_REAL_GIT": str(real_git),
                "TAKEOFF_RACE_COUNTER": str(counter),
                "TAKEOFF_RACE_WORKTREE": str(self.worktree.resolve()),
            }
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("changed during cleanup", result.stderr)
        self.assertEqual(late.read_text(), "created after final scan\n")
        self.assertEqual(
            self.git(self.worktree, "rev-parse", "HEAD").stdout.strip(),
            self.first_ref,
        )
        self.assert_canonical_untouched()

    def test_refuses_assume_unchanged_edits_before_removal(self) -> None:
        self.git(self.worktree, "update-index", "--assume-unchanged", "tracked.txt")
        (self.worktree / "tracked.txt").write_text("hidden human edit\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("hidden index flags", result.stderr)
        self.assertEqual((self.worktree / "tracked.txt").read_text(), "hidden human edit\n")
        self.assert_canonical_untouched()

    def test_refuses_skip_worktree_edits_before_removal(self) -> None:
        self.git(self.worktree, "update-index", "--skip-worktree", "tracked.txt")
        (self.worktree / "tracked.txt").write_text("hidden sparse edit\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("hidden index flags", result.stderr)
        self.assertEqual((self.worktree / "tracked.txt").read_text(), "hidden sparse edit\n")
        self.assert_canonical_untouched()

    def test_refuses_symlinked_evidence_root(self) -> None:
        external = self.root / "external-evidence"
        external.mkdir()
        (external / "secret.md").write_text("outside worktree\n")
        (self.worktree / "evidence").symlink_to(external, target_is_directory=True)

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("symlinked evidence root", result.stderr)
        self.assertEqual((external / "secret.md").read_text(), "outside worktree\n")
        self.assert_canonical_untouched()

    def test_refuses_fifo_evidence_without_blocking(self) -> None:
        fifo = self.worktree / "evidence" / "takeoff-pass" / "receipt.pipe"
        fifo.parent.mkdir(parents=True)
        os.mkfifo(fifo)

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("non-regular evidence", result.stderr)
        self.assertTrue(fifo.exists())
        self.assert_canonical_untouched()

    def test_refuses_local_only_history_before_removal(self) -> None:
        self.git(self.worktree, "switch", "-c", "human-local-pass")
        (self.worktree / "tracked.txt").write_text("local commit\n")
        self.git(self.worktree, "add", "tracked.txt")
        self.git(self.worktree, "commit", "-m", "preserve me")
        local_ref = self.git(self.worktree, "rev-parse", "HEAD").stdout.strip()

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("local-only history", result.stderr)
        self.assertEqual(
            self.git(self.worktree, "rev-parse", "HEAD").stdout.strip(),
            local_ref,
        )
        self.assert_canonical_untouched()

    def test_preserves_nested_receipts_without_flattening(self) -> None:
        first = self.worktree / "evidence" / "takeoff-pass" / "a" / "receipt.md"
        second = self.worktree / "evidence" / "takeoff-pass" / "b" / "receipt.md"
        first.parent.mkdir(parents=True)
        second.parent.mkdir(parents=True)
        first.write_text("first\n")
        second.write_text("second\n")

        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.durable_recovery() / "a" / "receipt.md").read_text(), "first\n")
        self.assertEqual((self.durable_recovery() / "b" / "receipt.md").read_text(), "second\n")
        self.assert_canonical_untouched()

    def test_locked_cleanup_refuses_before_moving_evidence(self) -> None:
        receipt = self.worktree / "evidence" / "takeoff-pass" / "receipt.md"
        receipt.parent.mkdir(parents=True)
        receipt.write_text("stay put\n")
        self.git(self.canonical, "worktree", "lock", str(self.worktree))

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("locked worktree", result.stderr)
        self.assertEqual(receipt.read_text(), "stay put\n")
        self.assertFalse(self.durable_recovery().exists())
        self.assert_canonical_untouched()

    def test_keeps_a_clean_current_detached_worktree(self) -> None:
        self.git(self.canonical, "fetch", "origin", "main")
        self.git(self.canonical, "worktree", "remove", str(self.worktree))
        self.git(
            self.canonical,
            "worktree",
            "add",
            "--detach",
            str(self.worktree),
            self.second_ref,
        )

        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"READY worktree {self.second_ref}")
        self.assert_canonical_untouched()

    def test_recreates_a_registered_worktree_missing_from_disk(self) -> None:
        shutil.rmtree(self.worktree)

        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"HEALED worktree <absent> -> {self.second_ref}",
        )
        self.assertEqual(
            self.git(self.worktree, "rev-parse", "HEAD").stdout.strip(),
            self.second_ref,
        )
        self.assert_canonical_untouched()

    def test_missing_target_recovery_does_not_prune_other_metadata(self) -> None:
        other = self.pass_root / "takeoff-pass-20260822T050000Z"
        self.git(self.canonical, "worktree", "add", "--detach", str(other), self.first_ref)
        shutil.rmtree(other)
        shutil.rmtree(self.worktree)

        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stderr)
        listed = self.git(self.canonical, "worktree", "list", "--porcelain").stdout
        self.assertIn(f"worktree {other.resolve()}", listed)
        self.assert_canonical_untouched()

    def test_missing_worktree_refuses_local_only_history(self) -> None:
        (self.worktree / "tracked.txt").write_text("missing local commit\n")
        self.git(self.worktree, "add", "tracked.txt")
        self.git(self.worktree, "commit", "-m", "missing but valuable")
        local_ref = self.git(self.worktree, "rev-parse", "HEAD").stdout.strip()
        shutil.rmtree(self.worktree)

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("local-only history", result.stderr)
        listed = self.git(self.canonical, "worktree", "list", "--porcelain").stdout
        self.assertIn(f"HEAD {local_ref}", listed)
        self.assert_canonical_untouched()

    def test_missing_worktree_refuses_staged_index_data(self) -> None:
        (self.worktree / "tracked.txt").write_text("staged before disappearance\n")
        self.git(self.worktree, "add", "tracked.txt")
        shutil.rmtree(self.worktree)

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("staged index data", result.stderr)
        listed = self.git(self.canonical, "worktree", "list", "--porcelain").stdout
        self.assertIn(f"worktree {self.worktree.resolve()}", listed)
        self.assert_canonical_untouched()

    def test_missing_worktree_refuses_reflog_only_history(self) -> None:
        (self.worktree / "tracked.txt").write_text("reflog-only commit\n")
        self.git(self.worktree, "add", "tracked.txt")
        self.git(self.worktree, "commit", "-m", "reflog only")
        local_ref = self.git(self.worktree, "rev-parse", "HEAD").stdout.strip()
        self.git(self.worktree, "reset", "--hard", self.first_ref)
        shutil.rmtree(self.worktree)

        result = self.prepare()

        self.assertEqual(result.returncode, 1)
        self.assertIn("reflog-only history", result.stderr)
        self.assertEqual(
            self.git(self.canonical, "cat-file", "-t", local_ref).stdout.strip(),
            "commit",
        )
        self.assert_canonical_untouched()

    def test_restore_refuses_replaced_symlink_parent(self) -> None:
        loader = importlib.machinery.SourceFileLoader(
            "takeoff_prepare_worktree", str(PREPARE)
        )
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        recovered = self.root / "recovered"
        recovered.mkdir()
        (recovered / "receipt.md").write_text("stay recovered\n")
        shutil.rmtree(self.worktree / "evidence", ignore_errors=True)
        external = self.root / "external-restore"
        external.mkdir()
        (self.worktree / "evidence").symlink_to(external, target_is_directory=True)

        self.assertFalse(module.restore_receipts(self.worktree, recovered))
        self.assertEqual((recovered / "receipt.md").read_text(), "stay recovered\n")
        self.assertFalse((external / "takeoff-pass").exists())


if __name__ == "__main__":
    unittest.main()
