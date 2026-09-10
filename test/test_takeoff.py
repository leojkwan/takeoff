from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
TAKEOFF = ROOT / "bin" / "takeoff"
INVOCATION_BOUNDARY_CONTRACT = (
    "Takeoff ships no scheduler or background service. Its documented pass path "
    "begins with an explicit command. `takeoff stamp` validates receipt shape, "
    "source checkout identity, and ledger serialization; it does not authenticate "
    "the invoker, receipt authorship, channel acceptance, or the truth of semantic "
    "claims."
)
STALE_CADENCE_CLAIMS = (
    "Takeoff has zero standing automation",
    "only that deliberate pass can stamp",
    "closing the decommission cadence gap",
    "single definition of the scheduled surface",
    "gap it closes",
    "until a host-owned automation exists",
    "Wake (owned by",
)
PUBLIC_COMMAND_CONTRACTS = {
    ROOT / "README.md": (
        "Set up Takeoff and review this repository for release.",
        "takeoff root",
        "takeoff prompt",
    ),
    ROOT / "AUTOMATION.md": (
        "./bin/takeoff install",
        "takeoff prompt",
    ),
    ROOT / "PASS.md": (
        "takeoff root",
        "takeoff prepare-worktree",
        "takeoff stamp",
        "${TAKEOFF_EVIDENCE_ROOT:-$HOME/Development/takeoff-evidence}",
    ),
    ROOT / "METHOD.md": ("takeoff stamp",),
    ROOT / "ADOPTION.md": ("takeoff stamp",),
    ROOT / "DECOMMISSION-2026-08-15.md": ("takeoff prompt",),
    ROOT / "profiles" / "ios.md": ("takeoff ios-env",),
}


class TakeoffLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sandbox = Path(self.tmp.name)

    def run_launcher(
        self,
        *arguments: str,
        launcher: Path = TAKEOFF,
        env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        command_env = os.environ.copy()
        if env:
            command_env.update(env)
        return subprocess.run(
            [str(launcher), *arguments],
            cwd=self.sandbox,
            env=command_env,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_relocated_checkout(self) -> tuple[Path, Path]:
        checkout = self.sandbox / "relocated checkout"
        bin_dir = checkout / "bin"
        bin_dir.mkdir(parents=True)
        launcher = bin_dir / "takeoff"
        shutil.copy2(TAKEOFF, launcher)
        for document in ("PASS.md", "METHOD.md", "ADOPTION.md"):
            (checkout / document).write_text(f"{document} from relocated checkout\n")
        for helper_name in ("prepare-worktree", "ios-env", "stamp"):
            helper = bin_dir / helper_name
            helper.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "from pathlib import Path\n"
                "print(json.dumps({'helper': Path(__file__).name, 'args': sys.argv[1:]}))\n"
            )
            helper.chmod(0o755)
        launcher.chmod(0o755)
        return checkout, launcher

    def test_root_resolves_the_current_checkout(self) -> None:
        result = self.run_launcher("root")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()), ROOT.resolve())

    def test_prompt_emits_the_canonical_pass_bytes(self) -> None:
        result = subprocess.run(
            [str(TAKEOFF), "prompt"],
            cwd=self.sandbox,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout, (ROOT / "PASS.md").read_bytes())

    def test_prompt_does_not_require_unused_ledger_or_helpers(self) -> None:
        checkout, launcher = self.make_relocated_checkout()
        (checkout / "ADOPTION.md").unlink()
        for name in ("prepare-worktree", "ios-env", "stamp"):
            (checkout / "bin" / name).unlink()

        result = self.run_launcher("prompt", launcher=launcher)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (checkout / "PASS.md").read_text())

    def test_relocated_checkout_routes_every_helper(self) -> None:
        checkout, launcher = self.make_relocated_checkout()

        root = self.run_launcher("root", launcher=launcher)
        prompt = self.run_launcher("prompt", launcher=launcher)

        self.assertEqual(root.returncode, 0, root.stderr)
        self.assertEqual(Path(root.stdout.strip()), checkout.resolve())
        self.assertEqual(
            prompt.stdout,
            (checkout / "PASS.md").read_text(),
        )
        for helper in ("prepare-worktree", "ios-env", "stamp"):
            with self.subTest(helper=helper):
                result = self.run_launcher(
                    helper,
                    "first",
                    "second argument",
                    launcher=launcher,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    json.loads(result.stdout),
                    {
                        "helper": helper,
                        "args": ["first", "second argument"],
                    },
                )

    def test_helper_exit_status_is_preserved(self) -> None:
        checkout, launcher = self.make_relocated_checkout()
        helper = checkout / "bin" / "stamp"
        helper.write_text("#!/bin/sh\nexit 17\n")
        helper.chmod(0o755)

        result = self.run_launcher("stamp", launcher=launcher)

        self.assertEqual(result.returncode, 17, result.stderr)

    def test_install_creates_an_idempotent_stable_symlink(self) -> None:
        checkout, launcher = self.make_relocated_checkout()
        home = self.sandbox / "home"
        env = {"HOME": str(home)}

        first = self.run_launcher("install", launcher=launcher, env=env)
        target = home / ".local" / "bin" / "takeoff"
        second = self.run_launcher("install", launcher=launcher, env=env)
        rooted = self.run_launcher("root", launcher=target, env=env)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(target.is_symlink())
        self.assertEqual(target.resolve(strict=True), launcher.resolve(strict=True))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed", second.stdout)
        self.assertEqual(rooted.returncode, 0, rooted.stderr)
        self.assertEqual(Path(rooted.stdout.strip()), checkout.resolve())

    def test_install_refuses_to_replace_an_existing_command(self) -> None:
        bin_dir = self.sandbox / "commands"
        bin_dir.mkdir()
        target = bin_dir / "takeoff"
        target.write_text("owned by another installation\n")

        result = self.run_launcher(
            "install",
            "--bin-dir",
            str(bin_dir),
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), "owned by another installation\n")
        self.assertEqual(len(result.stderr.splitlines()), 1)
        self.assertIn("refusing to replace", result.stderr)
        self.assertIn("remove it or use takeoff install --bin-dir", result.stderr)

    def test_incomplete_installation_refuses_with_one_action(self) -> None:
        checkout = self.sandbox / "incomplete checkout"
        launcher = checkout / "bin" / "takeoff"
        launcher.parent.mkdir(parents=True)
        shutil.copy2(TAKEOFF, launcher)

        result = self.run_launcher("root", launcher=launcher)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(result.stderr.splitlines()), 1)
        self.assertIn("invalid installation", result.stderr)
        self.assertIn(
            "repair or reclone <takeoff-checkout>, then run "
            "<takeoff-checkout>/bin/takeoff install",
            result.stderr,
        )

    def test_non_executable_helper_refuses_with_one_action(self) -> None:
        checkout, launcher = self.make_relocated_checkout()
        helper = checkout / "bin" / "ios-env"
        helper.chmod(0o644)

        result = self.run_launcher("ios-env", launcher=launcher)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(result.stderr.splitlines()), 1)
        self.assertIn("bin/ios-env is not executable", result.stderr)
        self.assertIn(
            "repair or reclone <takeoff-checkout>, then run "
            "<takeoff-checkout>/bin/takeoff install",
            result.stderr,
        )

    def test_symlinked_helper_cannot_escape_the_checkout(self) -> None:
        checkout, launcher = self.make_relocated_checkout()
        external = self.sandbox / "external-helper"
        external.write_text("#!/bin/sh\nprintf 'EXTERNAL_HELPER\\n'\n")
        external.chmod(0o755)
        helper = checkout / "bin" / "stamp"
        helper.unlink()
        helper.symlink_to(external)

        result = self.run_launcher("stamp", launcher=launcher)

        self.assertEqual(result.returncode, 2)
        self.assertNotIn("EXTERNAL_HELPER", result.stdout)
        self.assertIn("bin/stamp is a symlink", result.stderr)

    def test_public_docs_use_the_stable_command_boundary(self) -> None:
        forbidden = (
            "~/Development/takeoff/PASS.md",
            "~/Development/takeoff/bin/",
            "/Development/takeoff/PASS.md",
            "/Development/takeoff/bin/",
            "${TAKEOFF_EVIDENCE_ROOT:-~/",
            "~/" ".shadow/",
        )

        for path, required in PUBLIC_COMMAND_CONTRACTS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text()
                for snippet in required:
                    self.assertIn(snippet, content)
                for snippet in forbidden:
                    self.assertNotIn(snippet, content)

    def test_landing_docs_distinguish_local_receipts_from_optional_adoption(self) -> None:
        for path in (ROOT / "README.md", ROOT / "docs" / "index.html"):
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text()
                self.assertIn("local receipt", content)
                self.assertIn("ADOPTION", content)
                self.assertIn("independent verification", content)

    def test_detailed_docs_explain_the_invocation_boundary(self) -> None:
        for relative in (
            "AUTOMATION.md",
            "PASS.md",
            "DECOMMISSION-2026-08-15.md",
        ):
            with self.subTest(path=relative):
                content = " ".join((ROOT / relative).read_text().split())
                self.assertIn(INVOCATION_BOUNDARY_CONTRACT, content)
                for stale_claim in STALE_CADENCE_CLAIMS:
                    self.assertNotIn(stale_claim, content)


if __name__ == "__main__":
    unittest.main()
