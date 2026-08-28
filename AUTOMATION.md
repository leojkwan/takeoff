# Pass invocation — manual cadence contract

Takeoff ships no scheduler or background service. Its documented pass path
begins with an explicit command. `takeoff stamp` validates receipt shape,
source checkout identity, and ledger serialization; it does not authenticate
the invoker, receipt authorship, channel acceptance, or the truth of semantic
claims.

This file defines the invocation command and cadence priors, not a schedule.
DECOMMISSION-2026-08-15.md records the scheduled surfaces removed on
August 15, 2026.

## Deliberate invocation

```bash
cd <clean worktree of the target repo> && \
  codex exec --cd "$PWD" "$(takeoff prompt)"
```

Example hosts using the same prompt bytes (cwd = repo identity, zero arguments):

```bash
claude -p "$(takeoff prompt)"                       # from the worktree
cursor-agent -p --output-format text \
  "$(takeoff prompt)"                               # from the worktree
```

Install that command once from any clone with `./bin/takeoff install`.
The documented manual path is one of the commands above, or the output of
`takeoff prompt` pasted into a session opened in the target worktree.

## Cadence (profile priors)

| repo | prior | worktree |
|---|---|---|
| resplit-web | nightly-equivalent | `../resplit-web-worktrees/takeoff-pass-<UTC>` |
| resplit-ios | nightly-equivalent | `../resplit-ios-worktrees/takeoff-pass-<UTC>` |
| strongyes-web | weekly (fleet-HOLD hour) | `../strongyes-web-worktrees/takeoff-pass-<UTC>` |
| trysnowcubes-web | weekly | `../trysnowcubes-web-worktrees/takeoff-pass-<UTC>` |

## Automation shipped by Takeoff: none

Takeoff itself installs no cron job, launchd job, or background loop. The
cadence table above is a prior for whoever invokes a pass, not a schedule.
External automation can still invoke the command; Takeoff neither discovers
nor authenticates that provenance. Without a new pass receipt, there is no new
Takeoff release proof.

PASS.md's prior-receipt probe provides an observational occupancy signal:
an unfinished receipt younger than its declared budget reads OCCUPIED. It is
not an atomic lock; simultaneous starts can both observe free, so concurrent
invocation still needs external coordination.
