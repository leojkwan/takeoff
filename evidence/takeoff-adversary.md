# Takeoff adversary proof

## Verdict

Historical PASS on `hardening/release-oracle`. The attacked baseline was
`38affc000cd1a1a766fe01ef65df99065996f8c5`; the recorded passing
implementation was `89e4743`. This artifact does not prove a later head.

The adversary found eleven ways a shallow implementation could lose evidence,
delete late worktree data, accept the wrong receipt, commit the wrong ledger
bytes, bypass the shared ledger lock, or dispatch code outside the Takeoff
checkout. Every confirmed blocker is fixed at its owning boundary. The final
recorded suite passed 105 tests, all nine planted guard mutations were killed,
and that checkout passed `git diff --check`.

## Attack matrix

| Surface | Attack | Pre-fix false green | Canonical fix | Disposition |
|---|---|---|---|---|
| recovered evidence root | Set `TAKEOFF_EVIDENCE_ROOT` to a non-default absolute path | cleanup still wrote below the default home path | resolve the configured root once and pass it into receipt preservation | fixed |
| recovered evidence destination | Make the configured root, repo directory, or `recovered` directory a symlink | cleanup moved receipts through the link and outside the named durable boundary | require each owned destination node to be a real directory via `lstat`; treat a destination symlink as an existing collision | fixed |
| worktree cleanup | Create ignored data after the last scan but before removal | `git worktree remove` deleted the late file | atomically move the worktree to a retirement path, rescan there, and restore or preserve it on any late dirt | fixed |
| source receipt | Replace the receipt path with a symlink | `is_file` and `read_text` followed the link | open one regular file with `O_NOFOLLOW` and verify descriptor and path identity | fixed |
| durable receipt | Pre-place a symlink with byte-compatible target content | the destination looked like an acceptable existing file | use `lexists`, `lstat`, and the stable regular-file reader before accepting a collision as idempotent | fixed |
| judged receipt bytes | Change the receipt after parsing and source validation | the durable copy reread and preserved different bytes | read one receipt snapshot and pass those exact bytes through validation and durable copy | fixed |
| judged source ref | Put a valid old commit in the receipt while the worktree is at a later commit | the old SHA resolved, so the later checkout lent it execution | require source worktree `HEAD` to equal the resolved judged commit | fixed |
| existing receipt identity | Put repo and ref tokens in arbitrary prose or linked JSON | substring search accepted the file as evidence | require a canonical Takeoff pass or train title plus its canonical ref field | fixed |
| ledger commit | Install a pre-commit hook that rewrites and stages `ADOPTION.md` | the commit could contain bytes the stamper did not append | commit with `--no-verify`, compare `HEAD:ADOPTION.md` byte-for-byte, and require final ledger cleanliness | fixed |
| ledger serialization | Change `TAKEOFF_EVIDENCE_ROOT` between cooperating processes | each root selected a different lock inode | anchor `takeoff-adoption.lock` in Git's common directory | fixed |
| launcher dispatch | Replace a checkout helper with an executable symlink | the stable launcher executed the external target | reject helper symlinks before command dispatch | fixed |

## RED receipts

Ten focused regressions were first run against the pre-fix implementation.
They reproduced the expected false greens:

```text
custom evidence root ignored
late ignored worktree data deleted
arbitrary receipt identity accepted
pre-commit hook changed committed ledger bytes
external helper symlink executed
source receipt symlink followed
durable receipt symlink accepted
post-judgment receipt bytes recopied
receipt worktree HEAD allowed to differ from judged ref
evidence-root-specific locks failed to serialize one ledger
```

The final destination traversal regression was then added separately. Before
its fix, a symlink at any of the three owned destination levels let
`prepare-worktree` exit `0` and move the source receipt through the link.

The compatibility control stayed green: a legacy
`# takeoff train receipt — <repo>` with its canonical `- ref:` field remains
valid even when it links auxiliary JSON. Linked JSON may add context, but it no
longer supplies receipt identity.

## GREEN receipts

Focused recovered-evidence and cleanup proof:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_prepare_worktree.py' -v
```

```text
Ran 22 tests in 12.693s
OK
```

Complete repository proof:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_*.py' -v
```

```text
Ran 105 tests in 38.857s
OK
```

Whitespace proof:

```bash
git diff --check
```

```text
rc=0
```

The two stable receipt readers were also probed with a final path snapshot that
kept the same device and inode but changed size and modification time:

```text
stamp_final_path_metadata=refused rc=1
checker_final_path_metadata=refused
```

## Mutation proof

Each mutation was applied alone, its focused test was run, and the original
working file was restored byte-for-byte before the next mutation.

| Planted shallow implementation | Focused test | Result |
|---|---|---|
| ignore configured evidence root | `test_evidence_root_override_controls_recovered_receipts` | killed, `rc=1` |
| accept symlinked destination directories | `test_symlinked_evidence_destination_refuses_without_moving_receipts` | killed, three failing subtests |
| skip retirement-path rescan | `test_refuses_ignored_data_created_after_the_final_scan` | killed, helper incorrectly returned `0` |
| accept arbitrary repo/ref substrings | `test_arbitrary_repo_and_ref_tokens_are_not_existing_receipt_identity` | killed, checker incorrectly returned `0` |
| allow commit hooks | `test_commit_hook_cannot_replace_the_ledger_payload` | killed, committed payload differed |
| accept helper symlinks | `test_symlinked_helper_cannot_escape_the_checkout` | killed, external helper returned `0` |
| reread receipt during durable copy | `test_durable_copy_uses_the_bytes_that_were_judged` | killed, durable bytes changed |
| skip worktree `HEAD` equality | `test_receipt_worktree_head_must_equal_the_judged_ref` | killed, stamp incorrectly returned `0` |
| place the lock beside `ADOPTION.md` instead of Git common state | `test_stamp_waits_for_the_stable_receipt_pointer_lock` | killed, competing stamp bypassed the held lock |

```text
ALL_MUTANTS_KILLED 9/9
```

## Remaining gap

The owned destination directories are checked by path immediately before the
receipt move; they are not held as an `openat` descriptor chain. A concurrent
process that already has permission to rewrite the durable store's parent
namespace could still swap a checked directory between that check and the
rename. Closing that race would require descriptor-relative directory creation
and rename operations rather than more path checks.

Stable receipt reads reject symlinks and changes to inode, size, or modification
time, then preserve the exact bytes already judged. They cannot prove against a
writer that changes bytes during the read and restores both content metadata
and path identity before the final snapshots. Filesystem immutability or an
independently trusted content digest would be needed for that stronger claim.

No pull request, release, publication, deployment, branch deletion, or
human-facing message was performed.
