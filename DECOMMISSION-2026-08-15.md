# Floor-train decommission receipt — 2026-08-15 (METHOD v1 → v2)

Per Leo's ruling (2026-08-15, recorded in the takeoff plan): the deterministic
train scripts are deleted entirely; the pass is the train (METHOD v2 T1).

## What was removed

| surface | action | evidence |
|---|---|---|
| launchd com.leokwan.resplit-takeoff-train (03:30 nightly) | bootout + plist deleted | `launchctl list` carries zero takeoff-train jobs |
| launchd com.leokwan.resplit-ios-takeoff-train (04:00 nightly) | bootout + plist deleted | same |
| launchd com.leokwan.snowcubes-takeoff-train (Tue 06:30) | bootout + plist deleted | same |
| launchd com.leokwan.strongyes-takeoff-train (Mon 04:30, never bootstrapped) | plist deleted | same |
| resplit-web scripts/takeoff-train.sh | deleted, direct push through marker-gated pre-push | 9d5c36b4 (AGENTS.md pointer → v2 in same commit) |
| resplit-ios scripts/takeoff-train-ios.sh | deleted via PR #2410 (cursor approved, squash) | 59c70d1e8 |
| strongyes-web scripts/takeoff-train.sh | deleted via PR #1489 | 66b3e2092 |
| trysnowcubes-web scripts/takeoff-train.sh | deleted via PR #2401 | 4a6d4bae8 |

Preserved: the 9 v1 ADOPTION rows (boundary header added in 020e417); every
v1 train receipt in each repo's evidence/ dir; the env fixes the trains
earned (strongyes #1485 dedicated port + #1486 playwright provisioning;
resplit-ios xcb-lock py3.9 fix on ai-leo main b4bba514) — the pass inherits
all of it through the profiles' Conduct sections. The trysnowcubes nightly
drift sweep is untouched (drift-detection only, never stamped).

## The cadence gap this opened

The decommission removed all scheduled proof pressure — no nightly
false-green hunting on any repo. The v1 trains caught real lies on a schedule
(tuist 0-test pass, node reporter drift, EADDRINUSE); that pressure is now
manual-only.

## Current contract — August 27, 2026

Takeoff ships no scheduler or background service. Its documented pass path
begins with an explicit command. `takeoff stamp` validates receipt shape,
source checkout identity, and ledger serialization; it does not authenticate
the invoker, receipt authorship, channel acceptance, or the truth of semantic
claims.

The cadence gap remains open by choice. Adding a scheduler is a separate future
decision, not unfinished setup. The canonical deliberate invocation remains
`codex exec --cd <repo-worktree> "$(takeoff prompt)"`; Takeoff ships nothing
that schedules it. Until that contract changes, no new receipt means no new
Takeoff release proof.
