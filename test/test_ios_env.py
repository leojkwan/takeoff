#!/usr/bin/env python3
"""Behavior tests for Takeoff's repo-agnostic iOS environment admission."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "bin" / "ios-env"
PROFILE = ROOT / "profiles" / "ios.md"
CORE_KEYS = ("DEVELOPER_DIR", "IOS_DESTINATION", "XCB_LOCK_WAIT", "DERIVED_DATA")


class IosEnvironmentAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.sandbox = Path(self.tempdir.name)
        self.pass_root = self.sandbox / "pass-worktree"
        self.pass_root.mkdir()
        self.default_developer = self._fake_developer("Xcode-default")
        self.tmpdir = self.sandbox / "tmp"
        self.tmpdir.mkdir()

    def _fake_developer(self, name: str) -> Path:
        developer = self.sandbox / name / "Contents" / "Developer"
        xcodebuild = developer / "usr" / "bin" / "xcodebuild"
        xcodebuild.parent.mkdir(parents=True)
        xcodebuild.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        xcodebuild.chmod(0o755)
        return developer

    def _base_env(self) -> dict[str, str]:
        env = os.environ.copy()
        for key in CORE_KEYS:
            env.pop(key, None)
        env["TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR"] = str(self.default_developer)
        env["TAKEOFF_IOS_DEFAULT_DESTINATION"] = "platform=iOS Simulator,name=Example Phone"
        env["TMPDIR"] = str(self.tmpdir)
        return env

    def _run_helper(self, overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = self._base_env()
        env.update(overrides or {})
        probe = (
            "import json, os; "
            f"print(json.dumps({{key: os.environ[key] for key in {CORE_KEYS!r}}}, sort_keys=True))"
        )
        return subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--pass-root",
                str(self.pass_root),
                "--",
                sys.executable,
                "-c",
                probe,
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def _payload(self, result: subprocess.CompletedProcess[str]) -> tuple[str, dict[str, str]]:
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2, result.stdout)
        return lines[0], json.loads(lines[1])

    def test_missing_values_are_repaired_for_the_invoked_command(self) -> None:
        healed, payload = self._payload(self._run_helper())

        self.assertEqual(
            healed,
            "HEALED ios-env DEVELOPER_DIR,IOS_DESTINATION,XCB_LOCK_WAIT,DERIVED_DATA",
        )
        self.assertEqual(payload["DEVELOPER_DIR"], str(self.default_developer))
        self.assertEqual(
            payload["IOS_DESTINATION"],
            "platform=iOS Simulator,name=Example Phone",
        )
        self.assertEqual(payload["XCB_LOCK_WAIT"], "900")
        derived_data = Path(payload["DERIVED_DATA"])
        self.assertTrue(derived_data.is_absolute())
        self.assertTrue(derived_data.is_dir())
        self.assertEqual(derived_data.parent, self.tmpdir / "takeoff-ios-derived-data")

    def test_explicit_valid_overrides_are_preserved(self) -> None:
        custom_developer = self._fake_developer("Xcode-custom")
        custom_derived_data = self.sandbox / "custom DerivedData"
        overrides = {
            "DEVELOPER_DIR": str(custom_developer),
            "IOS_DESTINATION": "platform=iOS Simulator,id=A1B2-C3D4,OS=latest",
            "XCB_LOCK_WAIT": "120",
            "DERIVED_DATA": str(custom_derived_data),
        }

        healed, payload = self._payload(self._run_helper(overrides))

        self.assertEqual(healed, "HEALED ios-env none")
        self.assertEqual(payload, overrides)
        self.assertTrue(custom_derived_data.is_dir())

    def test_unconfigured_simulator_is_not_guessed(self) -> None:
        result = self._run_helper({"TAKEOFF_IOS_DEFAULT_DESTINATION": ""})
        self.assertEqual(result.returncode, 2)
        self.assertIn("set IOS_DESTINATION", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_unconfigured_xcode_names_the_required_setting(self) -> None:
        result = self._run_helper({"TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR": ""})
        self.assertEqual(result.returncode, 2)
        self.assertIn("set DEVELOPER_DIR", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_invalid_values_are_repaired(self) -> None:
        overrides = {
            "DEVELOPER_DIR": "/definitely/missing/Xcode.app/Contents/Developer",
            "IOS_DESTINATION": "platform=macOS,name=This is not an iOS simulator",
            "XCB_LOCK_WAIT": "0",
            "DERIVED_DATA": "../relative-derived-data",
        }

        healed, payload = self._payload(self._run_helper(overrides))

        self.assertEqual(
            healed,
            "HEALED ios-env DEVELOPER_DIR,IOS_DESTINATION,XCB_LOCK_WAIT,DERIVED_DATA",
        )
        self.assertEqual(payload["DEVELOPER_DIR"], str(self.default_developer))
        self.assertEqual(payload["XCB_LOCK_WAIT"], "900")
        self.assertNotEqual(payload["IOS_DESTINATION"], overrides["IOS_DESTINATION"])
        self.assertTrue(Path(payload["DERIVED_DATA"]).is_absolute())

    def test_healed_line_names_only_repaired_keys_and_never_values(self) -> None:
        custom_derived_data = self.sandbox / "do-not-log-this-path"
        overrides = {
            "DEVELOPER_DIR": str(self.default_developer),
            "IOS_DESTINATION": "platform=iOS Simulator,name=Private Device Label",
            "XCB_LOCK_WAIT": "not-a-number",
            "DERIVED_DATA": str(custom_derived_data),
        }

        healed, payload = self._payload(self._run_helper(overrides))

        self.assertEqual(healed, "HEALED ios-env XCB_LOCK_WAIT")
        self.assertEqual(payload["XCB_LOCK_WAIT"], "900")
        self.assertNotIn(str(self.default_developer), healed)
        self.assertNotIn("Private Device Label", healed)
        self.assertNotIn(str(custom_derived_data), healed)

    def test_profile_names_defaults_and_routes_the_xcode_call_site(self) -> None:
        profile = PROFILE.read_text(encoding="utf-8")

        self.assertTrue(os.access(HELPER, os.X_OK))
        self.assertIn("TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR", profile)
        self.assertIn("TAKEOFF_IOS_DEFAULT_DESTINATION", profile)
        self.assertIn("`XCB_LOCK_WAIT=900`", profile)
        self.assertIn("`takeoff ios-env --pass-root", profile)
        self.assertIn("-- xbq", profile)


if __name__ == "__main__":
    unittest.main()
