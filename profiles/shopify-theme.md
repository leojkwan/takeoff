# Profile: shopify-theme

Reference implementation: **trysnowcubes-web** — THE SNOWCUBES METHOD's 4-step
release (freshness-check → fact-assert vs human-owned facts JSON → guarded
`theme push` → post-push-proof writing a dated receipt or exit 3). This is
already the most takeoff-shaped release in the fleet; the 4-step path is
untouched. Worked example: correcting an allergen line on a PDP (P0
customer fact).

## Rung map

| Rung | Command | Notes |
|---|---|---|
| L0 static | secrets check (`check-secrets.mjs`) | exists |
| L1 logic | `fact-assert` + storefront jest falsifier (`test:storefront:node`) | allergen canon lives in `custom.ingredients` |
| L2 real-dep | `shopify:preview:e2e` | real Shopify preview, not localhost |
| L3 journey | playwright preview journey | train lane |
| L4a channel-accept | post-push-proof receipt (live theme id = pushed digest) | already mandatory |
| L4b field readback | PostHog checkout-pixel delta, one exact wake | never a gate |

Vendor-as-authority (T4): the live theme is a write source — Nicole edits
live settings directly. The freshness-check **reconciliation receipt** is the
law here, not a build receipt.

## Conduct (per-repo; the pass reads this as its prior — METHOD T1 v2)

Cadence prior: weekly ~30-min; lanes preflight (secrets + storefront jest +
node --test hooks — node emits the spec reporter's `ℹ pass N`, accept both
TAP and spec forms) + `allergen:verify` (live canon) + `push:facts`
(fact-assert vs live Admin). Release path: THE SNOWCUBES METHOD 4-step —
freshness-check reconciliation → fact-assert → guarded `theme push` →
post-push-proof receipt (exit 3 respected); L4a = post-push-proof receipt +
live theme digest. **Nicole-owned facts are an inherited pause: the pass
never authors an allergen or ingredient value.** Rollback: re-push the
prior theme ref through the same 4-step. **Structural releases (deletions):**
the `--only` path cannot remove a file; Leo ruled 2026-08-19 that publishing a
parity-proven candidate theme IS the release mechanism for those — revert is
republishing the prior theme id (first conducted flip: 147256672374 → 147327352950). Watchers: the nightly drift sweep
stays drift-detection only and never stamps; section cache can pin stale
CSS — probe the exact `?v=` the HTML links.

## Backfill backlog

- Marker-audit the three hook scripts (exit codes are typed — 2/3 — but
  confirm positive markers, T2).
- Smallest backfill in the fleet: this repo is closer to being the reference
  than a target.
