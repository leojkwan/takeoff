# takeoff — METHOD v2

Provenance: decided 2026-08-12 by a five-lens adversarial panel against three
read-only repository surveys. `DECISION-v1.md` preserves the public decision
record.

## 2. The core method

Earlier local skills influenced this vocabulary: `groundtruth` for test
discipline, `pr-factory` for lifecycle separation, `bigapple` for iOS
host/receipt separation, and Shadow for proof grammar. They are optional
historical references, not unpublished required law. The public contract is
the checked-in documentation, profiles, and tools in this repository:

- **T1 — The pass is the train.** Every product repo is evaluated by the
  takeoff pass: a release chief (a person or coding host) executing `PASS.md`
  from a clean worktree of that repo. The chief
  re-derives the repo's lane table from source each pass (profiles are
  priors, source is authority), pre-declares budget, lane subset, per-lane
  positive marker + count floor, repeat counts, and mutation targets in the
  receipt BEFORE running. The receipt is the pass's local record, not
  authenticated semantic truth. Deterministic
  train scripts are retired (v1→v2, 2026-08-15); host admission law
  (`xbq` on iOS) still binds every lane the pass drives.
- **T2 — Positive markers.** Every gate asserts the marker only a completed
  run emits (`Executed ≥1 tests`, `BUILD SUCCEEDED`, receipt file exists,
  N ≥ expected). Exit codes and filter-based selection alone never gate.
  One-time audit row per repo; each later pass re-asserts it.
- **T3 — L4 split; no gate on approval.** L4a = artifact accepted by the
  channel (TestFlight build state, Vercel READY, live theme id = pushed
  digest) — scriptable, the highest rung a gate may require. L4b = field
  readback (telemetry delta, dogfood) — an obligation with one exact wake,
  never a gate. **No gate may depend on a third-party approval decision.**
- **T4 — Enforced seam or named lock.** A vendor is SEAM only if a guard in
  the repo FAILS when the seam is bypassed (banned-import lint, driver-flip
  test, real-dep run on the generic substrate). Otherwise the row reads
  [LOCK] + the one-line business reason. Two machine-checkable states; no
  prose exit notes. Where the vendor owns state (Shopify live theme, ASC
  metadata, Vercel project config), the method owns a **reconciliation
  receipt**, not a build receipt.
- **T5 — "not exercised:".** Every receipt names what was NOT exercised.
  Existing receipt formats are blessed as-is; this is the one new field.
- **T6 — Adoption is countable, stamping is uniform.** The method expects every
  pass that executed at least one lane to record exactly one ADOPTION row
  through `takeoff stamp`, the supported ledger writer, carrying verdict
  (BLESSED / REFUSED / DEFERRED / PROOF-ONLY) and host columns. The tool checks
  canonical receipt shape, source repo/ref identity, lane syntax, exact durable
  bytes, and serialized ledger commit. It does not authenticate the invoker,
  receipt authorship, marker provenance, channel acceptance, or semantic truth.
  Adoption is counted on
  BLESSED and PROOF-ONLY rows with nonzero executed counts; REFUSED and
  DEFERRED rows are countable execution evidence, never adoption. BLESSED
  additionally requires a syntactically present L4a channel-accept pointer;
  validating that external acceptance remains a review obligation. A zero-lane
  refusal (dirty tree, occupied claim) writes the memo only, no row.

## 3. The harness ladder (vocabulary, not a renaming exercise)

Five rungs, descriptive. Repos keep their command names; a profile maps rungs
to executable commands, named evidence obligations, descriptive priors, or the
literal `none`. A `none` cell is an explicit gap.

- **L0 static** — typecheck, lint, format, deterministic guards (secrets scan,
  config pins, banned imports/symbols)
- **L1 logic** — unit + law oracles (settlement parity/corpus, fact-assert,
  contract suites). The falsifier tier for most lanes.
- **L2 real-dep** — the real dependency at least once on P0/P1 paths (local
  Supabase docker, real Redis, sim build, Shopify preview)
- **L3 journey** — E2E on the built artifact + pixel proof actually read
- **L4a channel-accept / L4b field readback** — per T3

Gate placement (severity-scaled, already lived practice): lane push = the
focused falsifier (cheapest rung that can refuse the change); trunk land =
affected L0–L2; release = full ladder for touched P0/P1 surfaces; a deliberate
pass = its full declared subset within the stated budget. Landing mode
(direct-push vs PR) stays a per-repo profile choice; the RUNG is the law.

Optional stack profiles (adopt as needed; each names its reference
implementation, one line, no adoption row for the vocabulary itself):
**ai-leo** = assistant-digest source + disposable install seam · **web-next**
= resplit-web · **shopify-theme** = trysnowcubes-web's 4-step release ·
**ios** = resplit-ios local-ci lanes + fastlane. Release evidence = the receipt
set for a shipped change: lane falsifier receipt, pass receipt, L4a
channel-accept receipt,
L4b field-readback receipt (or its exact wake), each with ref, command,
positive markers, and a `not exercised:` line — lifecycle states never
collapse.
