# takeoff

A release can look green while proving little: an exit code can hide zero
tests, a marker can be guessed, and a deploy can finish without an external
readback.

Takeoff is a clone-anywhere, host-neutral release method in which a person or
coding host acts as release chief, re-derives the repository's real gates,
attacks them, follows its own release path, and leaves a bounded receipt.

## Quick start

Install the command from any clone:

```bash
git clone https://github.com/firstbitelabsllc/takeoff.git
cd takeoff
./bin/takeoff install
export PATH="$HOME/.local/bin:$PATH"  # if ~/.local/bin is not already on PATH
takeoff root
```

The installed command is a symlink back to that checkout. Every subcommand
therefore resolves the same `PASS.md`, ledger, profiles, and helper tools
regardless of the clone's location. If the checkout moves, reinstall from its
new location; use `./bin/takeoff install --bin-dir <directory>` when
`$HOME/.local/bin` is not the right command directory.

Run one pass from a clean worktree of the repository being judged:

```bash
cd <clean-target-worktree>
codex exec --cd "$PWD" "$(takeoff prompt)"
```

Codex is one invocation example, not a dependency. Any person or coding host
can consume the same prompt bytes; `AUTOMATION.md` shows equivalent command
forms. The pass reads the current Takeoff method, the selected stack profile,
and the target repository's own instructions before deriving or running a
lane.

## Proof ladder

Takeoff gives existing repository checks a shared vocabulary; it does not
rename them or replace their commands.

| Rung | Question answered | Typical evidence |
|---|---|---|
| **L0 static** | Does the source satisfy deterministic structural rules? | Typecheck, lint, format, secrets, config pins, banned imports. |
| **L1 logic** | Does the behavior obey its local laws? | Unit, contract, parity, and corpus tests with positive counts. |
| **L2 real dependency** | Does a critical path work against the real dependency? | Simulator build, real Redis or database, Shopify preview. |
| **L3 journey** | Does the built artifact complete the user journey? | End-to-end execution plus inspected visual or artifact evidence. |
| **L4a channel acceptance** | Did the release channel accept the artifact? | TestFlight state, Vercel READY, or another quoted external readback. |
| **L4b field readback** | Did the released behavior work in the field? | Telemetry or dogfood readback; this remains an obligation, not a gate on third-party approval. |

A profile maps these rungs to commands, evidence obligations, descriptive
priors, or the literal `none`. The target repository's current source remains
authority, so every pass re-derives the lane table before execution.

The repository boundary stays small:

```text
Takeoff checkout                         Target repository worktree
PASS prompt ---------------------------> release chief
METHOD + selected profile --------read->      |
                                              +-- derives and attacks repo gates
                                              +-- follows the repo release path
                                              +-- writes one bounded receipt
                                                           |
                                                     takeoff stamp
                                                           v
                                              durable copy + ADOPTION row
```

`METHOD.md` owns the six method rules and ladder semantics. `PASS.md` owns the
release-chief runbook and receipt shape. `profiles/` supplies stack-specific
priors. Keeping those owners separate lets this README stay an entrypoint
instead of a second method.

## Where proof lands

- The target worktree receives
  `evidence/takeoff-pass/<UTC>-receipt.md` for every verdict.
- Teardown preserves the exact receipt bytes under
  `${TAKEOFF_EVIDENCE_ROOT:-$HOME/Development/takeoff-evidence}/<repo>/`.
- `takeoff stamp <receipt-path>` records an eligible execution in
  `ADOPTION.md`, the historical local ledger.
- `evidence/` in this repository holds Takeoff's own portability, adversarial,
  public-claim, and branch-preservation audits.

An adoption row is evidence to inspect, not independent attestation of who ran
the pass or whether every sentence in its receipt is true.

## Invocation boundary

Takeoff ships no scheduler or background service. Its documented pass path
begins with an explicit command. `takeoff stamp` validates receipt shape,
source checkout identity, and ledger serialization; it does not authenticate
the invoker, receipt authorship, channel acceptance, or the truth of semantic
claims.

Cadence entries in `AUTOMATION.md` are priors for an operator, not scheduled
jobs. External automation can invoke the command, and Takeoff cannot discover
or authenticate that provenance. Its prior-receipt occupancy check is also
observational rather than an atomic lock, so concurrent starts need
coordination outside Takeoff.

## Adopt it in a repository

Add a short pointer to the target repository's `AGENTS.md` naming:

1. this Takeoff checkout or public repository;
2. the selected profile in `profiles/`; and
3. the target source files that own its real rung commands and release path.

That pointer stays small because the next pass re-reads both repositories
instead of trusting copied instructions.

## Limits and human judgment

- Takeoff can reject malformed local evidence; it cannot prove receipt
  authorship, marker provenance, semantic truth, or external acceptance
  without reviewing the named source.
- Profiles are checked-in priors, not live mirrors of another repository or
  platform. Drift discovered during recon invalidates the prior.
- Takeoff ships no automation itself, but it cannot prove machine-global
  absence of cron jobs, agents, or external schedulers.
- Product intent, lane selection, evidence meaning, release authorization, and
  L4b field interpretation remain human judgments.
- Source, commit, push, merge, channel acceptance, deployment, and field
  behavior are separate facts; no earlier receipt proves a later one.

For the complete law, read `METHOD.md`. To conduct a pass or audit its receipt,
read `PASS.md`.
