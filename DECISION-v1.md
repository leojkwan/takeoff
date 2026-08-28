# TAKEOFF — Decision Record v1 (2026-08-12)

Vendor-independent, determinism-first development method for Leo's projects.
Decided by a five-lens adversarial panel against three read-only repo surveys
(Resplit cluster, four web repos, method machinery), the memory-lesson corpus,
and Leo's /leo decision filters. This record contains the challenges and the
decision, per the goal's proof line. No code, deployment, provider, or
credential changes were made in producing it.

## 1. The decision

**Adopt Position B, amended: one page of NEW law + countable adoption, built
around one keystone — a scheduled full-ladder proof run ("the train") per
product repo, using that repo's own scripts.** Codify-only (A) and shared
tooling (C) are rejected. Build-nothing (0) is rejected on three defects found
live during the panel round (§4). The method is named **takeoff**.

The thesis it encodes (Leo's, verbatim intent): everything that CAN be
deterministic and scripted MUST be — build, test, deploy, release, evidence.
Open-ended LLM reasoning is reserved for what needs judgment: feature intent,
design, hypothesis generation, quality passes. Hosted services execute; the
repo is the authority.

## 2. The core method (new law only — everything else cites its owner)

Existing skills already encode most of the discipline; takeoff does not
restate them (that was challenged and killed — §4 trap-lens). By reference:
test-harness law = `groundtruth` (10 laws); lifecycle truth table (commit ≠
push ≠ merge ≠ deploy ≠ runtime) = `pr-factory`; iOS host/receipt separation =
`bigapple`; severity scaling = memory `severity-scaled-testing-not-blanket-
gates`; proof grammar and claims = Shadow. The NEW law is six lines:

- **T1 — The train.** Every product repo runs a scheduled full-ladder proof
  run using its OWN scripts (launchd or repo CI — the executor is
  interchangeable; the scripts are the authority). Shadow's standing goal
  already mandates this train; today it exists only for the shadow repo.
  A train run declares a wall-clock lock budget and a lane subset, is
  admitted through the host queue (`xbq` on iOS), and stamps ADOPTION.md.
- **T2 — Positive markers.** Every gate asserts the marker only a completed
  run emits (`Executed ≥1 tests`, `BUILD SUCCEEDED`, receipt file exists,
  N ≥ expected). Exit codes and filter-based selection alone never gate.
  One-time audit row per repo; the train re-asserts it forever.
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
- **T6 — Adoption is countable.** A repo has adopted takeoff when its row in
  ADOPTION.md is stamped by its own train run emitting positive markers with
  nonzero executed counts. A file existing counts for nothing — the previous
  method plan died exactly that way (m1, `~w5d9`).

## 3. The harness ladder (vocabulary, not a renaming exercise)

Five rungs, descriptive. Repos keep their command names; a profile maps rungs
to existing commands, and every cell is a real command or the literal `none`
(the `none` cells ARE the gap backlog).

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
affected L0–L2; release = full ladder for touched P0/P1 surfaces; the train =
full declared subset on schedule. Landing mode (direct-push vs PR) stays a
per-repo profile choice; the RUNG is the law.

Optional stack profiles (adopt as needed; each names its reference
implementation, one line, no adoption row for the vocabulary itself):
**web-next** = resplit-web · **shopify-theme** = trysnowcubes-web's 4-step
release · **ios** = resplit-ios local-ci lanes + fastlane · **android** =
inherits ios profile (subdir, beneficiary not pilot) · **api-worker** =
resplit-currency-api · **static-site** = floor only (L0 + config-pin test +
one read screenshot). Release evidence = the receipt set for a shipped
change: lane falsifier receipt, train receipt, L4a channel-accept receipt,
L4b field-readback receipt (or its exact wake), each with ref, command,
positive markers, and a `not exercised:` line — lifecycle states never
collapse (pr-factory law).

## 4. The challenge round (auditable; five lenses, one round)

**Trap lens (argue build-nothing):** sustained 9 of 10 counts against the
draft — 8 of 10 proposed laws restated groundtruth/pr-factory/bigapple/Shadow
(each overlap named); ladder-as-renaming fixes unmeasured pain; VENDORS.md ×7
is YAGNI; naming section over-engineered. Conceded exactly one corpse beats
Position 0: no product repo has a scheduled run, and a dead suite executed 0
tests for 5 months, found by accident. Insisted: adoption counts only on an
executed run with nonzero count. → ADOPTED: laws collapsed to cite-don't-
restate (§2), T6 as written, no renames.

**10x lens (Leo's hours):** the bottleneck is unattended false greens, not
vocabulary; the train is not new machinery but an already-mandated Shadow law
silently skipped by every product repo — reframed as compliance, defusing the
more-systems trap. Ranked components; killed per-repo VENDORS.md and
profiles-as-adoption-rows; kept train, marker audit, "not exercised:", and
landing law into repo AGENTS.md (as the successor goal's work). Exposed a
draft error: Android is a resplit-ios subdir, not greenfield — beneficiary,
not pilot. → ADOPTED: T1/T2/T5 promoted; pilot order changed (§6).

**Platform lens (determinism realism; verified in-repo):** (a) nightly
full-ladder on iOS is arithmetically impossible — 18 lanes ≈ 9.17h summed
timeout behind one host-global flock with 40-min waiter eviction → trains
declare lock budget + lane subset, admitted through xbq (folded into T1);
(b) L4 for iOS waits on App Review — days, and a human opinion → T3 split,
"no gate on approval" (memory: unsatisfiable gates breed rule-breaking under
pressure); (c) **found live: resplit-web's money-law pre-push gate is
exit-code-only today** — `test:parity` gates on `$?` with zero executed-count
assertion, saved only by an unpinned vitest default. Kills Position 0
empirically; the fix is pilot 1. (d) Shopify live theme is a write source the
repo reconciles against → vendor-as-authority clause in T4.

**Adoption lens (rot; measured live):** the skill roots are serving retired
`impeccable` from an unrelated repo while successor `taste` is mounted
nowhere — this is what an uncodified method does over a quarter; a method doc
in the skill roots would fail identically → method lives in ONE git repo, one
file, with 3-line pointers in each repo's AGENTS.md; ADOPTION.md rows stamped
by trains (T6); exit-test cells executable-or-GAP; keep 5 rungs but every
cell command-or-`none`; half-day adoption cap applies to MAPPING only —
brownfield retrofit (resplit-ios: 1994-line Fastfile, ~74 worktrees, four
evidence sinks) is separate opt-in rows with no deadline.

**Vendor lens (YAGNI vs exit insurance; verified in-repo):** two draft table
rows were false on day one — Sentry "isolated" (87 direct imports in
strongyes business paths) and PostHog "adapter" (36 files bypass it) — proving
prose seams rot at authoring time → T4 replaces the registry. The only proven
SEAM is Redis/Upstash (three transports + real-redis suite — and that swap was
FORCED by the vendor, not foreseen). **Found live: expenses-web's backup cron
writes backups into the same Vercel Blob token it insures against** — a P0
data-durability bug, the one vendor row that pays for itself. Secret scanning
exists locally only in snowcubes → L0 floor includes a secrets scan. A solo
founder never voluntarily migrates off Vercel/ASC/Shopify: name the lock.

**Panel tally:** Position 0 rejected 4–1 (trap dissent recorded above, its
salvage adopted). Position A rejected 5–0. Position B accepted 4–1 as
amended. Position C killed 5–0; its one saved piece is T1. Name: takeoff 4–1
(trap voted "no name"; overruled — the pointer needs a stable public name).

## 5. Vendor comparison (goal-required; T4 states applied)

| Vendor | Role | State | Reason / seam | Interchangeable alternative |
|---|---|---|---|---|
| GitHub | VCS + optional executor | LOCK | push protection + bot review are real features hooks don't replace; gates are already local | any git remote executes; scripts unchanged |
| Vercel | web hosting/cron | LOCK | behavioral lock (GET crons, NEXT_PUBLIC/Ignored Build Step, analytics); real seam kept: `next build` is the artifact, git-gate pinned by test | CF Pages/self-host possible, never exercised |
| Cloudflare | workers/pages/KV | LOCK | wrangler-shaped; GH Pages fallback exists for currency snapshots | Deno Deploy/Fastly, unexercised |
| Supabase | Postgres/auth/fns | LOCK | GoTrue+RLS+PostgREST don't port; 21 files import outside lib/supabase; docker stack's value is L2, not portability | Neon/RDS would need auth rewrite |
| PostHog | product analytics | LOCK→SEAM candidate | adapter exists, bypassed by 36 files; ~20-min banned-import lint would flip it | self-host PostHog, Plausible+contract |
| Sentry | errors | LOCK | 87 direct imports; dSYM/source-map pipeline is the tie | GlitchTip exit test deleted as theater |
| Upstash Redis | KV/ratelimit | **SEAM (proven)** | three transports incl. memory + real-redis docker suite; swap was vendor-forced once already | any Redis |
| Shopify | commerce | LOCK + vendor-as-authority | business lock; live theme is a write source — reconciliation receipts (safe-theme-sync exists but is interactive + bare `git add -A`, never a rung) | none (named honestly) |
| ASC/TestFlight | iOS distribution | LOCK + vendor-as-authority | platform monopoly; App Review is an L4b obligation, never a gate | none (named honestly) |
| Vercel Blob | expenses data | **OPEN P0 BUG** | backup cron is circular (same token); no restore drill | fix is `backup:local` to disk, ~1h — not a migration |

## 6. Successor work (none of it performed in this goal)

Agent-side, in value order:
1. **resplit-web**: add executed-count assertion to the pre-push parity gate
   (~20 min); stand up the first train from existing smoke/e2e/parity scripts
   with a declared budget. The empirical answer to Position 0.
2. **expenses-web**: `backup:local` off-token backup + restore drill (P0 bug).
3. **firstbitelabs-web**: floor pass — AGENTS.md (repo has none), L0 +
   secrets scan + keep the config-pin test.
4. Marker audit rows (T2) per remaining repo; PostHog banned-import lint to
   flip LOCK→SEAM if wanted.
5. Mint the `takeoff` method repo (METHOD.md vN + ADOPTION.md) — [LEO-GATED:
   creating a GitHub repo is an external account action].
6. AGENTS.md 3-line pointers per repo — with active lanes, land via each
   repo's own landing mode.
Android beta: beneficiary — inherits the ios profile; NOT a pilot.

## 7. Naming

**takeoff.** Deterministic checklist on the ground, judgment in the air; V1
(trunk land) is the commit point past which you fly it; "preflight" keeps
exactly its existing snowcubes meaning (the lane gate before push) — no repo
command is renamed; "readback" is already live vocabulary in Leo's plans.
Runner-up liftoff (same metaphor, weaker sub-terms); yolo-test/test-party
rejected as jokes-in-six-months; one-test rejected as describing only the
ladder. Trap-lens "no name" dissent recorded.
