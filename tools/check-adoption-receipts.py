#!/usr/bin/env python3
"""Heal safe receipt pointers, then grade ADOPTION repo/ref reconstruction."""
from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

from adoption_lock import exclusive_adoption_lock


ROOT = Path(__file__).resolve().parents[1]
ADOPTION = ROOT / "ADOPTION.md"
EVIDENCE_ROOT = Path.home() / "Development" / "takeoff-evidence"
SAFE_REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SAFE_REF = re.compile(r"[0-9a-f]{7,40}")


class PointerRepair(NamedTuple):
    line_index: int
    pointer: str
    missing: Path
    durable: Path
    repo: str
    ref: str
    digest: str


class TrackedAdoption(NamedTuple):
    root: Path
    relative: str


class PointerWake(Exception):
    """One deterministic operator wake for an ambiguous receipt pointer."""


def configured_evidence_root() -> Path:
    configured = os.environ.get("TAKEOFF_EVIDENCE_ROOT")
    try:
        root = (
            Path(configured).expanduser()
            if configured
            else Path.home() / "Development" / "takeoff-evidence"
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise PointerWake(
            f"cannot resolve TAKEOFF_EVIDENCE_ROOT: {error}; "
            "set it to an absolute path"
        )
    if not root.is_absolute():
        raise PointerWake("TAKEOFF_EVIDENCE_ROOT must be an absolute path")
    return root


def pointer_wake(repo: str, ref: str, receipt_name: str) -> str:
    return (
        "WAKE receipt pointer: missing receipt; leave exactly one byte-compatible "
        f"{receipt_name} for {repo}@{ref} under {EVIDENCE_ROOT / repo}, "
        "then rerun adoption grading"
    )


def receipt_names_identity(content: str, repo: str, ref: str) -> bool:
    pass_title = re.search(
        r"^# takeoff pass — (\S+) — (?:BLESSED|REFUSED|DEFERRED|PROOF-ONLY)\s*$",
        content,
        re.M,
    )
    train_title = re.search(r"^# takeoff train receipt — (\S+)\s*$", content, re.M)
    if pass_title:
        named_repo = pass_title.group(1)
        ref_match = re.search(
            r"^- ref judged[^:]*:\s*"
            r"(?:`?[A-Za-z0-9][A-Za-z0-9._/-]*`?\s+)?"
            r"`?([0-9a-f]{7,40})",
            content,
            re.M,
        )
    elif train_title:
        named_repo = train_title.group(1)
        ref_match = re.search(r"^- ref:\s*`?([0-9a-f]{7,40})", content, re.M)
    else:
        return False
    return (
        named_repo == repo
        and ref_match is not None
        and ref_match.group(1).startswith(ref)
    )


def regular_file_bytes(candidate: Path) -> Optional[bytes]:
    try:
        before = candidate.lstat()
        if not stat.S_ISREG(before.st_mode):
            return None
        descriptor = os.open(
            str(candidate), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            opened = os.fstat(descriptor)
            after = candidate.lstat()
            if (
                not stat.S_ISREG(opened.st_mode)
                or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
                or (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino)
            ):
                return None
            chunks = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_read = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after = candidate.lstat()
        if (
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (
                after_read.st_dev,
                after_read.st_ino,
                after_read.st_size,
                after_read.st_mtime_ns,
            )
            or (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            != (
                after_read.st_dev,
                after_read.st_ino,
                after_read.st_size,
                after_read.st_mtime_ns,
            )
        ):
            return None
        return b"".join(chunks)
    except (OSError, ValueError):
        return None


def regular_candidate_bytes(candidate: Path) -> Optional[bytes]:
    """Read one in-root regular file without following a symlink replacement."""
    try:
        evidence_root = EVIDENCE_ROOT.resolve()
        resolved = candidate.resolve()
        resolved.relative_to(evidence_root)
    except (OSError, ValueError):
        return None
    return regular_file_bytes(candidate)


def durable_candidate(missing: Path, repo: str, ref: str) -> Tuple[Path, str]:
    """Resolve one durable byte identity without guessing between histories."""
    wake = pointer_wake(repo, ref, missing.name)
    if (
        not SAFE_REPO.fullmatch(repo)
        or not SAFE_REF.fullmatch(ref)
        or not missing.name
    ):
        raise PointerWake(wake)

    logical_root = EVIDENCE_ROOT.absolute()
    evidence_root = EVIDENCE_ROOT.resolve()
    repo_root = logical_root / repo
    if not repo_root.is_dir():
        raise PointerWake(wake)

    candidates = []
    try:
        def walk_error(error: OSError) -> None:
            raise error

        for directory, _, filenames in os.walk(repo_root, onerror=walk_error):
            if missing.name not in filenames:
                continue
            candidate = Path(directory) / missing.name
            resolved = candidate.resolve()
            try:
                resolved.relative_to(evidence_root)
            except ValueError:
                continue
            try:
                candidate_stat = candidate.lstat()
            except OSError:
                continue
            if stat.S_ISREG(candidate_stat.st_mode):
                candidates.append(candidate.absolute())
    except OSError:
        raise PointerWake(wake)

    candidates = sorted(set(candidates), key=lambda path: path.as_posix())
    if not candidates:
        raise PointerWake(wake)

    by_digest = {}
    candidate_bytes = {}
    for candidate in candidates:
        content_bytes = regular_candidate_bytes(candidate)
        if content_bytes is None:
            raise PointerWake(wake)
        digest = hashlib.sha256(content_bytes).hexdigest()
        candidate_bytes[candidate] = content_bytes
        by_digest.setdefault(digest, []).append(candidate)
    if len(by_digest) != 1:
        raise PointerWake(wake)

    chosen = candidates[0]
    content = candidate_bytes[chosen].decode("utf-8", errors="replace")
    if not receipt_names_identity(content, repo, ref):
        raise PointerWake(wake)
    return chosen, next(iter(by_digest))


def replace_receipt_cell(line: str, pointer: str, durable: Path) -> str:
    """Replace only the final Markdown cell while preserving every other byte."""
    parts = line.rsplit("|", 2)
    if len(parts) != 3 or parts[1].strip() != pointer:
        raise PointerWake("receipt pointer row changed while recovery was preparing")
    cell = parts[1]
    leading = cell[: len(cell) - len(cell.lstrip())]
    trailing = cell[len(cell.rstrip()) :]
    parts[1] = f"{leading}{durable}{trailing}"
    return "|".join(parts)


def recovery_plan(adoption_text: str) -> List[PointerRepair]:
    repairs = []
    for line_index, line in enumerate(adoption_text.splitlines(keepends=True)):
        if not line.startswith("| 20"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) not in {7, 9}:
            continue
        repo = cells[1]
        ref = cells[2]
        pointer = cells[-1]
        receipt = Path(pointer).expanduser()
        if not receipt.is_absolute():
            receipt = ROOT / receipt
        if not receipt.is_file():
            durable, digest = durable_candidate(receipt, repo, ref)
            repairs.append(
                PointerRepair(
                    line_index,
                    pointer,
                    receipt,
                    durable,
                    repo,
                    ref,
                    digest,
                )
            )
    return repairs


def regular_adoption_stat(adoption: Path) -> os.stat_result:
    adoption_stat = adoption.lstat()
    if not stat.S_ISREG(adoption_stat.st_mode):
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md must be a regular file, not a "
            "symlink or special file"
        )
    return adoption_stat


def tracked_adoption(adoption: Path) -> Optional[TrackedAdoption]:
    """Return the owning Git target, or None for an intentionally standalone fixture."""
    repository = subprocess.run(
        ["git", "-C", str(adoption.parent), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
    )
    if repository.returncode != 0:
        return None

    root = Path(repository.stdout.strip()).resolve()
    try:
        relative = adoption.resolve().relative_to(root).as_posix()
    except ValueError:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md escaped its Git checkout; "
            "restore the checkout path, then rerun adoption grading"
        )
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative],
        text=True,
        capture_output=True,
    )
    if tracked.returncode != 0:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md is inside Git but untracked; "
            "restore the tracked ledger, then rerun adoption grading"
        )
    branch = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--quiet", "--short", "HEAD"],
        text=True,
        capture_output=True,
    )
    if branch.returncode != 0:
        raise PointerWake(
            "WAKE receipt pointer: tracked ADOPTION.md is on detached HEAD; "
            "attach its owning branch, then rerun adoption grading"
        )
    return TrackedAdoption(root, relative)


def tracked_adoption_status(target: TrackedAdoption) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-C",
            str(target.root),
            "status",
            "--porcelain",
            "--untracked-files=no",
            "--",
            target.relative,
        ],
        text=True,
        capture_output=True,
    )


def require_index_at_head(target: TrackedAdoption) -> None:
    index = subprocess.run(
        [
            "git",
            "-C",
            str(target.root),
            "diff",
            "--cached",
            "--quiet",
            "--exit-code",
            "HEAD",
            "--",
            target.relative,
        ],
        text=True,
        capture_output=True,
    )
    if index.returncode == 1:
        raise PointerWake(
            "WAKE receipt pointer: tracked ADOPTION.md index must match HEAD "
            "before recovery; preserve or commit staged edits, then rerun "
            "adoption grading"
        )
    if index.returncode != 0:
        raise PointerWake(
            "WAKE receipt pointer: could not inspect the ADOPTION.md index; "
            "restore its Git checkout, then rerun adoption grading"
        )


def dirty_tracked_adoption(adoption: Path) -> Optional[TrackedAdoption]:
    """Return a dirty tracked ledger without constraining healthy detached checkouts."""
    repository = subprocess.run(
        ["git", "-C", str(adoption.parent), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
    )
    if repository.returncode != 0:
        return None
    root = Path(repository.stdout.strip()).resolve()
    try:
        relative = adoption.resolve().relative_to(root).as_posix()
    except ValueError:
        return None
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative],
        text=True,
        capture_output=True,
    )
    if tracked.returncode != 0:
        return None
    status = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "status",
            "--porcelain",
            "--untracked-files=no",
            "--",
            relative,
        ],
        text=True,
        capture_output=True,
    )
    if status.returncode != 0:
        raise PointerWake(
            "WAKE receipt pointer: could not inspect tracked ADOPTION.md; "
            "restore its Git checkout, then rerun adoption grading"
        )
    if not status.stdout:
        return None
    return tracked_adoption(adoption)


def apply_repairs(original: str, repairs: List[PointerRepair]) -> bytes:
    lines = original.splitlines(keepends=True)
    for repair in repairs:
        lines[repair.line_index] = replace_receipt_cell(
            lines[repair.line_index], repair.pointer, repair.durable
        )
    return "".join(lines).encode("utf-8")


def validate_repair_candidates(repairs: List[PointerRepair]) -> None:
    for repair in repairs:
        content = regular_candidate_bytes(repair.durable)
        if (
            content is None
            or hashlib.sha256(content).hexdigest() != repair.digest
            or not receipt_names_identity(
                content.decode("utf-8", errors="replace"), repair.repo, repair.ref
            )
        ):
            raise PointerWake(pointer_wake(repair.repo, repair.ref, repair.missing.name))


def atomic_replace_bytes(
    adoption: Path,
    content: bytes,
    mode: int,
    *,
    expected_original: Optional[bytes] = None,
    expected_stat: Optional[os.stat_result] = None,
    repairs: Optional[List[PointerRepair]] = None,
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=adoption.parent,
        prefix=f".{adoption.name}.receipt-pointer-",
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if expected_original is not None:
            current_stat = regular_adoption_stat(adoption)
            if (
                expected_stat is not None
                and (expected_stat.st_dev, expected_stat.st_ino)
                != (current_stat.st_dev, current_stat.st_ino)
            ) or adoption.read_bytes() != expected_original:
                raise PointerWake(
                    "WAKE receipt pointer: ADOPTION.md changed while recovery was preparing"
                )
        if repairs is not None:
            validate_repair_candidates(repairs)
        os.replace(temporary, adoption)
        directory_fd = os.open(str(adoption.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def commit_tracked_repair(
    target: TrackedAdoption,
    adoption: Path,
    original: bytes,
    repaired: bytes,
    mode: int,
    repair_count: int,
) -> None:
    require_index_at_head(target)
    expected_stat = regular_adoption_stat(adoption)
    if adoption.read_bytes() != repaired:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md changed while Git was committing; "
            "preserved the concurrent edit, inspect it before retrying"
        )
    suffix = "pointer" if repair_count == 1 else "pointers"
    committed = subprocess.run(
        [
            "git",
            "-C",
            str(target.root),
            "commit",
            "--only",
            "--no-verify",
            "-m",
            f"adoption: heal {repair_count} receipt {suffix}",
            "--",
            target.relative,
        ],
        text=True,
        capture_output=True,
    )
    if committed.returncode != 0:
        current_stat = regular_adoption_stat(adoption)
        unchanged = (
            (expected_stat.st_dev, expected_stat.st_ino)
            == (current_stat.st_dev, current_stat.st_ino)
            and adoption.read_bytes() == repaired
        )
        if not unchanged:
            raise PointerWake(
                "WAKE receipt pointer: ADOPTION.md changed while Git was committing; "
                "preserved the concurrent edit, inspect it before retrying"
            )
        require_index_at_head(target)
        atomic_replace_bytes(
            adoption,
            original,
            mode,
            expected_original=repaired,
            expected_stat=expected_stat,
        )
        raise PointerWake(
            "WAKE receipt pointer: Git could not commit healed ADOPTION.md; "
            "restore commit identity or hooks, then rerun adoption grading"
        )

    committed_payload = subprocess.run(
        ["git", "-C", str(target.root), "show", f"HEAD:{target.relative}"],
        capture_output=True,
        check=False,
    )
    if committed_payload.returncode != 0 or committed_payload.stdout != repaired:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md changed while Git was committing; "
            "preserved the concurrent edit, inspect it before retrying"
        )
    status = tracked_adoption_status(target)
    if status.returncode != 0 or status.stdout:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md changed while Git was committing; "
            "preserved the concurrent edit, inspect it before retrying"
        )


def recover_interrupted_commit(adoption: Path) -> List[PointerRepair]:
    """Commit only the exact pointer-only payload a prior process already healed."""
    target = dirty_tracked_adoption(adoption)
    if target is None:
        return []
    head = subprocess.run(
        ["git", "-C", str(target.root), "show", f"HEAD:{target.relative}"],
        capture_output=True,
        check=False,
    )
    if head.returncode != 0:
        raise PointerWake(
            "WAKE receipt pointer: could not read ADOPTION.md at HEAD; "
            "restore its Git checkout, then rerun adoption grading"
        )
    try:
        head_text = head.stdout.decode("utf-8")
    except UnicodeError:
        raise PointerWake(
            "WAKE receipt pointer: ADOPTION.md at HEAD is not valid UTF-8; "
            "restore the tracked ledger, then rerun adoption grading"
        )
    repairs = recovery_plan(head_text)
    current = adoption.read_bytes()
    if not repairs or apply_repairs(head_text, repairs) != current:
        raise PointerWake(
            "WAKE receipt pointer: tracked ADOPTION.md must be clean at HEAD "
            "before repair; restore or commit it, then rerun adoption grading"
        )
    mode = stat.S_IMODE(regular_adoption_stat(adoption).st_mode)
    commit_tracked_repair(target, adoption, head.stdout, current, mode, len(repairs))
    return repairs


def atomic_repair_pointers(adoption: Path) -> List[PointerRepair]:
    """Resolve every missing pointer first, then publish one all-or-nothing edit."""
    regular_adoption_stat(adoption)
    preflight_repairs = recovery_plan(adoption.read_bytes().decode("utf-8"))
    if not preflight_repairs:
        with exclusive_adoption_lock(adoption):
            regular_adoption_stat(adoption)
            return recover_interrupted_commit(adoption)

    with exclusive_adoption_lock(adoption):
        locked_stat = regular_adoption_stat(adoption)
        original_bytes = adoption.read_bytes()
        original = original_bytes.decode("utf-8")
        repairs = recovery_plan(original)
        if not repairs:
            return []

        target = tracked_adoption(adoption)
        if target is not None:
            status = tracked_adoption_status(target)
            if status.returncode != 0:
                raise PointerWake(
                    "WAKE receipt pointer: could not inspect tracked ADOPTION.md; "
                    "restore its Git checkout, then rerun adoption grading"
                )
            if status.stdout:
                raise PointerWake(
                    "WAKE receipt pointer: tracked ADOPTION.md must be clean at HEAD "
                    "before repair; restore or commit it, then rerun adoption grading"
                )

        repaired_bytes = apply_repairs(original, repairs)

        current_stat = regular_adoption_stat(adoption)
        if (locked_stat.st_dev, locked_stat.st_ino) != (
            current_stat.st_dev,
            current_stat.st_ino,
        ):
            raise PointerWake(
                "WAKE receipt pointer: ADOPTION.md changed while recovery was preparing"
            )
        mode = stat.S_IMODE(current_stat.st_mode)
        atomic_replace_bytes(
            adoption,
            repaired_bytes,
            mode,
            expected_original=original_bytes,
            expected_stat=current_stat,
            repairs=repairs,
        )
        if target is not None:
            commit_tracked_repair(
                target,
                adoption,
                original_bytes,
                repaired_bytes,
                mode,
                len(repairs),
            )
        return repairs


def main() -> int:
    global EVIDENCE_ROOT
    adoption = Path(sys.argv[1]).expanduser() if len(sys.argv) == 2 else ADOPTION
    if len(sys.argv) > 2:
        print("usage: check-adoption-receipts.py [ADOPTION.md]", file=sys.stderr)
        return 2
    try:
        EVIDENCE_ROOT = configured_evidence_root()
        repairs = atomic_repair_pointers(adoption)
    except PointerWake as wake:
        print(str(wake), file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(f"adoption receipts: RED — pointer recovery failed: {error}", file=sys.stderr)
        return 1
    for repair in repairs:
        print(f"HEALED receipt pointer: {repair.pointer} -> {repair.durable}")

    failures = []
    checked = 0
    recognized = 0
    for line_number, line in enumerate(adoption.read_text().splitlines(), 1):
        if line.lstrip().startswith("| 20") and not line.startswith("| 20"):
            failures.append(
                f"line {line_number}: adoption row must start in column 1"
            )
            continue
        if not line.startswith("| 20"):
            continue
        recognized += 1
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) not in {7, 9}:
            failures.append(f"line {line_number}: malformed adoption row")
            continue

        repo = cells[1]
        ref = cells[2]
        receipt = Path(cells[-1]).expanduser()
        if not receipt.is_absolute():
            receipt = ROOT / receipt
        checked += 1

        content_bytes = regular_file_bytes(receipt)
        if content_bytes is None:
            failures.append(f"line {line_number}: missing receipt: {receipt}")
            continue

        content = content_bytes.decode("utf-8", errors="replace")
        if not receipt_names_identity(content, repo, ref):
            failures.append(
                f"line {line_number}: receipt lacks canonical repo/ref identity "
                f"for {repo}@{ref}"
            )

    if recognized == 0:
        failures.append("no adoption rows recognized")

    if failures:
        for failure in failures:
            print(f"adoption receipts: RED — {failure}", file=sys.stderr)
        return 1

    print(f"adoption receipts: PASS rows={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
