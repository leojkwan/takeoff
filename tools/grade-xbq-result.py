#!/usr/bin/env python3
"""Fail closed on the structured result emitted by an xbq lane wrapper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, NoReturn


REFUSAL = "HEALED false-green refusal"


def refuse(reason: str) -> NoReturn:
    print(f"{REFUSAL}: {reason}", file=sys.stderr)
    raise SystemExit(1)


def read_record(path: str) -> Dict[str, Any]:
    try:
        raw = sys.stdin.read() if path == "-" else Path(path).read_text()
        record = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        refuse(f"invalid record: {error}")

    if not isinstance(record, dict):
        refuse("record must be a JSON object")
    return record


def grade(record: Dict[str, Any], expected_marker: str, floor: int) -> None:
    rc = record.get("rc")
    result = record.get("result")
    marker = record.get("marker")
    executed = record.get("executed")

    if isinstance(rc, bool) or not isinstance(rc, int):
        refuse("rc must be an integer")
    if rc != 0:
        refuse(f"xbq exited {rc}")
    if result != "PASSED":
        refuse(f"result is {result!r}, not 'PASSED'")
    if not isinstance(marker, str) or not marker:
        refuse("result marker is absent")
    if marker != expected_marker:
        refuse(f"result marker {marker!r} does not match {expected_marker!r}")
    if isinstance(executed, bool) or not isinstance(executed, int):
        refuse("executed must be an integer")
    if executed < floor:
        refuse(f"executed {executed} is below floor {floor}")

    print(
        f"xbq marker: PASS result={result} executed={executed} "
        f"marker={marker!r}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reject xbq false greens using its structured result marker."
    )
    parser.add_argument("record", help="JSON record path, or - for stdin")
    parser.add_argument("--expect-marker", required=True)
    parser.add_argument("--floor", required=True, type=int)
    args = parser.parse_args()

    if not args.expect_marker:
        refuse("expected marker must not be empty")
    if args.floor < 1:
        refuse("execution floor must be at least 1")

    grade(read_record(args.record), args.expect_marker, args.floor)


if __name__ == "__main__":
    main()
