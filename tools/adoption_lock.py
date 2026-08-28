#!/usr/bin/env python3
"""One stable lock for every process that can replace or append ADOPTION.md."""
from __future__ import annotations

import fcntl
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


LOCK_NAME = "takeoff-adoption.lock"


def adoption_lock_path(adoption: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(adoption.parent), "rev-parse", "--git-common-dir"],
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        common = Path(result.stdout.strip())
        if not common.is_absolute():
            common = adoption.parent / common
        return common.resolve() / LOCK_NAME
    return adoption.parent / f".{LOCK_NAME}"


@contextmanager
def exclusive_adoption_lock(adoption: Path) -> Iterator[None]:
    lock_path = adoption_lock_path(adoption)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        str(lock_path),
        os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    with os.fdopen(descriptor, "a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
