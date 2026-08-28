# Takeoff model-named remote branch hygiene audit

Audit date: 2026-08-27.

Comparison refs:

- `origin/main` at `87249ea7fae3c556a63937d70dcea15811a74dfa`
- `origin/hardening/release-oracle` at
  `269c13e872eff8c1b3946f5345237b76b8c09575`

The literal `claude/` and `codex/` prefixes below are historical remote branch
identifiers, not claims about authorship. `git ls-remote --heads origin` found
11 remote heads: the two comparison branches above and the nine model-named
branches audited here.

## Method

The audit fetched every remote head, then classified each model-named ref with:

1. `git merge-base --is-ancestor <branch> <comparison>` for exact ancestry.
2. `git rev-list --left-right --count <comparison>...<branch>` for branch-only
   commit count.
3. `git cherry -v <comparison> <branch>` and `git patch-id --stable` for
   content-patch equivalence.
4. `git diff --name-status <merge-base>..<branch>` for the branch-side file
   payload.

An exact ancestor preserves the original commit and its full history. A stable
patch-id match preserves the file change but not the original commit metadata
or topology. No branch is deleted by this audit.

## Classification

| Remote branch | Tip | Ancestry | Patch equivalence | Branch-side files | Unique file diff | Preservation verdict |
|---|---|---|---|---|---|---|
| `origin/claude/shake-head-gates-20260816` | `e35c8ffe7359cccabce70559b10aa190d7a26522` | Not an ancestor; exactly one branch-only commit versus both comparison refs. | Stable patch-id `cb2dcb3ab1ce00b8105a786804ea53e3a0e92d4a` matches `3edcdb4cdb1c2d05554924ac192b7eac8113b4fc`, which is an ancestor of both comparison refs. The commit message differs only by the merged-review suffix `(#1)`. | `PASS.md` | None after patch equivalence. | File work is preserved. Safe to delete only after explicit approval; the original commit metadata/topology is the remaining loss. |
| `origin/codex/takeoff-adoption-catchup-20260822` | `d5786fd8be84c3af94f7af12605373d47bac9174` | Not an ancestor; exactly one branch-only commit versus both comparison refs. | Stable patch-id `fbfff3e390fd53c4d47d171f96c143c6568eba3b` matches `c45fa5de9c93f9ebcb2794dc739d1768fa7d035c`, which is an ancestor of both comparison refs. The commit message differs only by the merged-review suffix `(#3)`. | `ADOPTION.md` | None after patch equivalence. | File work is preserved. Safe to delete only after explicit approval; the original commit metadata/topology is the remaining loss. |
| `origin/codex/takeoff-adoption-history-proof-20260822` | `c885afb2550bb40e81b4822983e0bfa28f22ece8` | Exact ancestor of both comparison refs; zero branch-only commits. | Not needed; the exact tip is reachable. | None beyond the reachable tip. | None. | Exact commit and file work are preserved. Safe to delete only after explicit approval. |
| `origin/codex/takeoff-durable-receipts-20260822` | `9db498e42f2e1629019798aa2689190bc80c428f` | Not an ancestor; exactly one branch-only commit versus both comparison refs. | Stable patch-id `d8df674a31ee90b6d9a9f494111adbac87ef70e6` matches `ab17a48e8a57fb13d99abaa0e6b840407ce382da`, which is an ancestor of both comparison refs. The commit message differs only by the merged-review suffix `(#2)`. | `bin/stamp`, `test/test_stamp.py`, `tools/receipt-durability-check.sh` | None after patch equivalence. | File work is preserved. Safe to delete only after explicit approval; the original commit metadata/topology is the remaining loss. |
| `origin/codex/takeoff-receipt-crash-recovery-20260822` | `c9105d7fe67ace1d73834927b59c9b23f4803321` | Exact ancestor of both comparison refs; zero branch-only commits. | Not needed; the exact tip is reachable. | None beyond the reachable tip. | None. | Exact commit and file work are preserved. Safe to delete only after explicit approval. |
| `origin/codex/takeoff-receipt-pointer-20260822` | `70a9f5855b5ad5636885137d04984a003dc6035e` | Not an ancestor; exactly one branch-only commit versus both comparison refs. | Stable patch-id `8efefb57b56894ca54deb7fe390abe88feaf12dc` matches `9562c8dc2d33711afc485bdd44a5b320648ed5da`, which is an ancestor of both comparison refs. `git range-diff` reports an exact commit-patch match. | `test/test_receipt_pointer.py`, `tools/check-adoption-receipts.py` | None after patch equivalence. | File work is preserved. Safe to delete only after explicit approval; the original branch topology is the remaining loss. |
| `origin/codex/takeoff-self-heal-pass-20260822` | `7142ea6fb0c3301ac458a5233ba2ff1247181576` | Exact ancestor of both comparison refs; zero branch-only commits. | Not needed; the exact tip is reachable. | None beyond the reachable tip. | None. | Exact commit and file work are preserved. Safe to delete only after explicit approval. |
| `origin/codex/takeoff-stamp-atomicity-20260822` | `28fe92c49db13aaa6e9e40fdc307d4c120b8a7b9` | Not an ancestor; exactly one branch-only commit versus both comparison refs. | Stable patch-id `c6c4cabe7a69eb1c62cfcfa4b9a6c535d9c29f9b` matches `b3035dfec6d3ff93e90d6229fbf1ea21c2777ce8`, which is an ancestor of both comparison refs. The commit message differs only by the merged-review suffix `(#4)`. | `bin/stamp`, `test/test_stamp.py`, `tools/stamp-durability-check.sh` | None after patch equivalence. | File work is preserved. Safe to delete only after explicit approval; the original commit metadata/topology is the remaining loss. |
| `origin/codex/takeoff-xbq-marker-20260822` | `c152624992f3d6ae9953eb413aed772f1f4bb8f4` | Exact ancestor of both comparison refs; zero branch-only commits. | Not needed; the exact tip is reachable. | None beyond the reachable tip. | None. | Exact commit and file work are preserved. Safe to delete only after explicit approval. |

## Exact deletion commands

These commands are recorded only as the bounded approval wake. They were not
run:

```bash
git push origin --delete claude/shake-head-gates-20260816
git push origin --delete codex/takeoff-adoption-catchup-20260822
git push origin --delete codex/takeoff-adoption-history-proof-20260822
git push origin --delete codex/takeoff-durable-receipts-20260822
git push origin --delete codex/takeoff-receipt-crash-recovery-20260822
git push origin --delete codex/takeoff-receipt-pointer-20260822
git push origin --delete codex/takeoff-self-heal-pass-20260822
git push origin --delete codex/takeoff-stamp-atomicity-20260822
git push origin --delete codex/takeoff-xbq-marker-20260822
```

## Verdict

All nine model-named remote branches have zero unique file payload relative to
the current public history:

- Four tips are exact ancestors of both `origin/main` and
  `origin/hardening/release-oracle`.
- Five tips each contain one branch-only commit whose stable patch-id is
  already present in both comparison histories.
- No branch needs a preservation branch, tag, cherry-pick, or file export.
- Remote deletion remains destructive and therefore waits for explicit
  approval of the exact commands above.
