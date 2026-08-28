# Profile: ios

Reference implementation: **resplit-ios** (local-ci lanes + fastlane).
Worked example: a P0 settlement rounding fix. The android app is a resplit-ios
subdir and inherits this profile (beneficiary, not pilot).

The repo's own release path is untouched: fastlane beta → TestFlight with
SHA-256 digest gates, exactly as-is.

## Rung map

| Rung | Command | Notes |
|---|---|---|
| L0 static | pre-commit SwiftFormat/SwiftLint/guards | needs DEVELOPER_DIR set |
| L1 logic | SettlementCrossSurfaceEmit + Corpus lanes via `xbq` | run with `--no-selective-testing` and assert `Executed ≥1 tests` — the known tuist false-green traps are law here |
| L2 real-dep | simulator build lane | |
| L3 journey | XCUITest journey lanes | most of the 18 lanes; `none` for the train subset |
| L4a channel-accept | TestFlight build state via ASC API | scriptable |
| L4b field readback | App Review approval + Sentry/PostHog delta, one exact wake each | **never a gate** — the release row closes on L4a (T3) |

Landing mode (unchanged): pre-commit hooks + affected lanes; V1 = trunk land.

## iOS environment admission

Every Xcode lane starts at the profile-owned call site:
`takeoff ios-env --pass-root "$PWD" -- xbq <lane command>`.
The helper preserves an explicit valid override and repairs only these four keys
when missing or invalid:

- `DEVELOPER_DIR` defaults to the installed
  `/Applications/Xcode-26.6.0.app/Contents/Developer`; a valid override must be
  an absolute developer directory with an executable `usr/bin/xcodebuild`.
- `IOS_DESTINATION` defaults to
  `platform=iOS Simulator,name=iPhone 17 Pro`; a valid override must match iOS
  Simulator destination syntax by name or id. Admission does not query whether
  that simulator is installed.
- `XCB_LOCK_WAIT=900`; a valid override is an integer from 1 through 7200
  seconds.
- `DERIVED_DATA` defaults to
  `${TMPDIR:-/tmp}/takeoff-ios-derived-data/<pass-root-sha256-prefix>`; a valid
  override is an absolute, non-root directory without parent traversal.

Admission emits exactly one path-safe line before the lane starts:
`HEALED ios-env <repaired-key-list>`. The line names keys only, in the order
above, and says `none` when every explicit value was already valid. A missing
installed Xcode or an uncreatable DerivedData directory refuses admission.

## Conduct (per-repo; the pass reads this as its prior — METHOD T1 v2)

Cadence prior: nightly-equivalent, ~90-min budget, ~4-6 lane subset, every
lane through `xbq` with an explicit `XCB_LOCK_WAIT` so a starved lane
reports deferred, not failed. The full 18-lane ladder sums to ~9h — never
in one pass. Selective-test lanes are structurally zero-test at unchanged
trunk (runner refuses the missing xcresult) — full `test`-mode lanes only.
Release path: `~/bin/resplit-deploy --once` (wraps fastlane beta →
TestFlight). NEVER from the canonical checkout (quarantined, ~1000 commits
stale — its release-staleness.py is missing and its tree is dirty; the
2026-08-15T163005Z pass hit exactly this AND caught the wrapper returning
rc=0 on refusal — parse its refusal lines, never trust its rc). Conduct
invocation: `DEPLOY_WATCHER_REPO=<this clean worktree> resplit-deploy
--once` — the wrapper's disposable-clone path; `.env` resolves via its
fallback chain to the canonical checkout's copy. **Leo's ruling 2026-08-15 ("you can totally submit... take it
on fully"): App Store Review submission is chief-conductable — the ceiling
is lifted. TestFlight L4a stays the build gate; submission is a further
conduct step with its own ASC readback, and App REVIEW's verdict remains
L4b field truth (a third-party decision is never a gate — T3).** Rollback: TestFlight builds
are additive (prior build stays installable); a bad build is superseded,
never recalled. Watchers: NONE. `com.leokwan.deploy-watcher` was documented as shipping every 3h but is not installed on this host (no plist, no loaded job, no log, verified 2026-08-16) — resplit-ios CLAUDE.md now says so too. The chief is the only release conductor; there is no build owner to race.

Known traps (all law): `xbq` exits 0 on FAILED builds — parse the build
result, not rc; selective testing runs 0 tests at rc=0 — assert executed
counts; never pipe a release through `tail`. Every `xbq` lane must write a
structured result record and invoke `tools/grade-xbq-result.py` with its exact
`--expect-marker` and positive `--floor`; raw `xbq` rc or prose is never
acceptance.

## Backfill backlog

- Executed-count audit across all 18 lane definitions (T2 one-time audit).
- The two settlement surfaces (ios + web) share parity fixtures — one bug
  exercises both trains.
