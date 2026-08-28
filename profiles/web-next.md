# Profile: web-next

Reference implementation: **resplit-web** (pilot 1 — first marker-gated
pre-push and first scheduled train). Worked example: **strongyes-web**,
mapped from a real P0 change (Stripe checkout rate-limit fix).

Applies to Next.js apps deployed on Vercel. The repo's own release path is
untouched: takeoff grades and stamps it, it does not replace it.

## Rung map (worked example: strongyes-web)

| Rung | Command | Notes |
|---|---|---|
| L0 static | typecheck + lint (repo's own scripts) | |
| L1 logic | focused jest falsifier for the lane | the falsifier tier |
| L2 real-dep | `db:test` (real local Supabase) | P0 path must touch it once |
| L3 journey | `e2e:release:public` subset | train-only today |
| L4a channel-accept | Vercel deployment READY + `e2e:prod-auth` smoke | highest rung a gate may require |
| L4b field readback | Sentry/PostHog delta, one exact wake | obligation, never a gate |

Landing mode (unchanged): local green + Graphite ack = V1 trunk land; deploy
via `deploy:vercel` wrapper (clean tree, exact ack, fresh origin/main).

## Rung map (reference: resplit-web)

| Rung | Command | Notes |
|---|---|---|
| L0 static | typecheck + lint | |
| L1 logic | `test:parity` (settlement parity vs iOS fixtures) | marker-gated pre-push: `executed-count=N`, floors on Test Files AND Tests |
| L2 real-dep | `none` | gap backlog |
| L3 journey | smoke suite | train lane |
| L4a channel-accept | Vercel Production READY (deploys off main only — no previews) | |
| L4b field readback | Sentry/PostHog delta, one exact wake | never a gate |

## Conduct (per-repo; the pass reads this as its prior — METHOD T1 v2)

- resplit-web — cadence prior: nightly-equivalent, 45-min budget incl.
  `npm ci` preflight; lanes unit/parity/smoke. **Direct-push collapse law:
  a test-surgery push IS the release event** — `next build` (the only
  route-export gate) + full affected lanes green BEFORE the push. Release
  path: direct push to main → Vercel Production build (no previews on this
  repo); L4a = deployment READY readback. Rollback: `git revert` of the
  landed commit pushed through the same hooks (Vercel redeploys), verified
  callable before any push. Watchers: none.
- strongyes-web — cadence prior: weekly, 45-min budget (fleet-HOLD caps
  StrongYes at ~1hr/week; the pass IS that hour); lanes `smoke:local` +
  `db:test` (dedicated port — host :3000 is routinely held) + browser
  journeys (Playwright browsers must be provisioned in preflight; the
  version-keyed cache goes stale on any bump). Release path: vidux/* branch
  → PR → cursor review → squash merge → `deploy:vercel` wrapper; L4a =
  Vercel deployment READY. Rollback: revert PR through the same flow.

## Backfill backlog (the `none` cells + audits)

- strongyes-web: marker-audit `smoke:local` / `db:test` (rc-only today? the
  audit decides).
- resplit-web: L2 is `none`.

Known trap: `next build` is the only route-export gate — jest+tsc green does
not prove deployable.
