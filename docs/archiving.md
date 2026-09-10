# Optional report archiving

The normal review leaves a report in the target project. If you also want to
record it in this Takeoff checkout's historical `ADOPTION.md` ledger, use
`takeoff stamp <receipt-path>` with the format below.

This command writes a durable copy and commits a ledger row in the Takeoff
checkout. It is local bookkeeping, not a release approval or an independent
verification of the findings. Keep private reports and paths out of public
commits. Existing verdict names are retained for saved-report compatibility.

## Accepted format

Choose the applicable saved-report verdict:

- `BLESSED`: checks passed and an authorized release was confirmed at its destination.
- `REFUSED`: a check failed or accepted a deliberate defect.
- `DEFERRED`: a required resource, permission, or prior task prevents completion.
- `PROOF-ONLY`: checks ran, with no release performed.

Keep these fields in this order for `takeoff stamp`:

```text
# takeoff pass — <repo> — <VERDICT>
- repo purpose: <what the repository does and what this review covers>
- last BLESSED: <date and ref> | none found
- live surfaces: <relevant observed deployments> | none found
- open contradictions: <conflicting instructions or results> | none found
- why: <one-line conclusion>
- ref judged: <commit>; ref conducted: <commit or none>; host: <hostname>; elapsed/budget: <seconds>/<seconds>
- RELEASED: <observed destination and version> | not released: <reason>
- pre-declaration: <budget, checks, exclusions, expected output, experiments>
- derivation table: <check, command, completion output, minimum count>
- lane <name> rc=<exit code> marker="<observed completion line>" count=<executed count>
- repeated runs: <checks repeated and their results>
- deliberate defects: <changes, observed failures, source restoration>
- test repairs: <changes, validation, and merge status>
- findings: <product defects and next actions>
- not exercised: <omitted checks or behavior>
- rollback: <command and how it was checked, or not applicable>
```

Use `none found` only after inspecting the relevant source. Do not fabricate
completion markers or test counts. Reports with zero executed checks remain
local notes; otherwise save one with `takeoff stamp <receipt-path>`.

Before removing your generated worktree, preserve its reports under
`${TAKEOFF_EVIDENCE_ROOT:-$HOME/Development/takeoff-evidence}/<repo>/`.
Never remove unrelated or uncertain work.
