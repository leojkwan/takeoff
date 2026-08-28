# takeoff — ADOPTION

This ledger preserves historical local execution claims. `takeoff stamp` is
the supported writer: it checks receipt shape, source repo/ref identity,
nonzero lane syntax, exact durable bytes, and serialized ledger commits.
It does not authenticate the invoker, receipt authorship, marker provenance,
channel acceptance, or semantic truth. Under METHOD.md T6, v2 BLESSED and
PROOF-ONLY rows count as adoption; v2 REFUSED and DEFERRED rows are execution
evidence.

The v1 rows below are self-reported local script-train history. Their absolute
receipt paths are non-portable and may not resolve away from the machine that
wrote them. The rows remain byte-for-byte historical records, not independent
verification of current public state.

| date (UTC) | repo | ref | lanes | executed | elapsed/budget | receipt |
|---|---|---|---|---|---|---|
| 2026-08-12T163744Z | resplit-web | 5b65b4f76cc5 | unit,parity,smoke | unit=4523 parity=58 smoke=14 | 53s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-train/2026-08-12T163744Z-receipt.md |
| 2026-08-12T163931Z | resplit-web | 5b65b4f76cc5 | unit,parity,smoke | unit=4523 parity=58 smoke=14 | 52s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-train/2026-08-12T163931Z-receipt.md |
| 2026-08-13T073005Z | resplit-web | 9ff80496c9b2 | unit,parity,smoke | unit=4523 parity=58 smoke=14 | 50s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-train/2026-08-13T073005Z-receipt.md |
| 2026-08-14T045330Z | resplit-ios | 788dd4fca6a0 | integration,ui,chaos_network,chaos_boot | executed=37 | 1119s/5400s | /Users/leokwan/Development/resplit-ios-train-evidence/train/2026-08-14T045330Z-receipt.md |
| 2026-08-14T051806Z | trysnowcubes-web | e61e338710d7 | preflight,allergen,facts | jest=1870 allergen_products=7 facts=CLEAN | 70s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-train/2026-08-14T051806Z-receipt.md |
| 2026-08-14T073004Z | resplit-web | 9ff80496c9b2 | unit,parity,smoke | unit=4523 parity=58 smoke=14 | 57s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-train/2026-08-14T073004Z-receipt.md |
| 2026-08-14T175732Z | trysnowcubes-web | c7fdccd08fca | preflight,allergen,facts,site-proof | jest=1878 allergen_products=7 facts=CLEAN site_proof=22/22p,44f | 139s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-train/2026-08-14T175732Z-receipt.md |
| 2026-08-15T073005Z | resplit-web | 9ff80496c9b2 | unit,parity,smoke | unit=4523 parity=58 smoke=14 | 51s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-train/2026-08-15T073005Z-receipt.md |
| 2026-08-15T080004Z | resplit-ios | e8816f062f22 | integration,ui,chaos_network,chaos_boot | executed=37 | 1141s/5400s | /Users/leokwan/Development/resplit-ios-train-evidence/train/2026-08-15T080004Z-receipt.md |

## v2 — chief pass history

The v2 rows are self-reported local pass history written through the
then-current `takeoff stamp` path. Each row carries verdict and host, but no row
alone proves human provenance, current public-main state, or external release.

Receipt paths dated on/before 2026-08-16 referred to per-repo pass worktrees
later removed according to the local 2026-08-16 record. Their durable copies
were recorded under a machine-local evidence root.

| date (UTC) | repo | ref | verdict | host | lanes | executed | elapsed/budget | receipt |
|---|---|---|---|---|---|---|---|---|
| 2026-08-15T144050Z | resplit-web | 9d5c36b4081b | PROOF-ONLY | Leos-Mac-Studio-10442.local | unit,parity,smoke | executed=4595 | 511s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-pass/2026-08-15T143024Z-receipt.md |
| 2026-08-15T150126Z | trysnowcubes-web | 90dcd36fe4a8 | PROOF-ONLY | Leos-Mac-Studio-10442.local | preflight,allergen,facts | executed=1966 | 800s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-15T144705Z-receipt.md |
| 2026-08-15T161718Z | resplit-ios | 50fb4b2be692 | REFUSED | Leos-Mac-Studio-10442.local | resplit_ios_integration,resplit_ios_ui,resplit_ios_chaos_network,resplit_ios_chaos_boot | executed=37 | 2334s/5400s | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/2026-08-15T153724Z-receipt.md |
| 2026-08-15T172356Z | resplit-ios | 50fb4b2be692 | REFUSED | Leos-Mac-Studio-10442.local | `resplit_ios_integration`,`resplit_ios_ui`,`resplit_ios_chaos_network`,`resplit_ios_chaos_boot` | executed=37 | 3124s/5400s | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/2026-08-15T163005Z-receipt.md |
| 2026-08-15T200343Z | resplit-ios | 113524bc6328 | PROOF-ONLY | Leos-Mac-Studio-10442.local | resplit_ios_integration,resplit_ios_ui,resplit_ios_chaos_network,resplit_ios_chaos_boot | executed=37 | 2940s/5400s | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/2026-08-15T191110Z-receipt.md |
| 2026-08-15T205508Z | strongyes-web | 8b25480c3ace | REFUSED | Leos-Mac-Studio-10442.local | smoke,db,e2e-public | executed=238 | 2598s/2700s | /Users/leokwan/Development/takeoff-evidence/strongyes-web/takeoff-pass/2026-08-15T201036Z-receipt.md |
| 2026-08-16T022509Z | resplit-web | 9d5c36b4081b | BLESSED | Leos-Mac-Studio-10442.local | unit,parity,smoke | executed=4595 | 1261s/2700s | /Users/leokwan/Development/takeoff-evidence/resplit-web/takeoff-pass/2026-08-16T020243Z-receipt.md |
| 2026-08-16T030306Z | trysnowcubes-web | a69abf9747a4 | PROOF-ONLY | Leos-Mac-Studio-10442.local | preflight,allergen,facts | executed=1987 | 263s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/2026-08-16T025756Z-receipt.md |
| 2026-08-16T031129Z | trysnowcubes-web | cf24e3f8c4fe | REFUSED | Leos-Mac-Studio-10442.local | preflight,analytics-jest,analytics-health-unit,allergen,facts,live-health | executed=2018 | 263s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/2026-08-16T030510Z-receipt.md |
| 2026-08-16T045059Z | shadow | ce7481bb8 | BLESSED | claude-shadow | L1-full-suite,L2-public-ready,L3-release-identity | executed=1451 | 3300s/2700s | /Users/leokwan/Development/takeoff-evidence/shadow/20260816T041810Z-receipt.md |
| 2026-08-16T085211Z | trysnowcubes-web | 4c051c0715af | REFUSED | Leos-Mac-Studio-10442.local | preflight,allergen,facts | executed=1988 | 363s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/2026-08-16T084500Z-receipt.md |
| 2026-08-16T171635Z | trysnowcubes-web | 2912d22c7a46 | DEFERRED | Leos-Mac-Studio-10442.local | preflight,node-contracts,visual-contracts,render-integrity,asset-integrity,fact-assert,gift-shake-one,gift-shake-two,shopify-preview,calm-hierarchy,mutation-edit-card,mutation-asset-reference | executed=3046 | 3015s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T162500Z-receipt.md |
| 2026-08-16T180144Z | trysnowcubes-web | e52e1923080d | BLESSED | Leos-Mac-Studio-10442.local | preflight,facts,gift-focused-first,gift-focused-repeat,live-journey,public-L4a | executed=2126 | 498s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T175214Z-receipt.md |
| 2026-08-16T185254Z | trysnowcubes-web | 248c6c6e89a0 | BLESSED | Leos-Mac-Studio-10442.local | full-jest,node-preflight,visual-preflight,facts,gift-focused-first,gift-focused-repeat,live-composer,live-cart,public-L4a | executed=3065 | 1904s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T182019Z-receipt.md |
| 2026-08-16T193229Z | resplit-ios | 0c61e8e7269f | BLESSED | Leos-Mac-Studio-10442.local | resplit_ios_lint,resplit_ios_integration,resplit_ios_ui,resplit_ios_chaos_network,resplit_ios_chaos_boot | executed=45 | 4357s/7200s | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/2026-08-16T181836Z-receipt.md |
| 2026-08-16T213527Z | trysnowcubes-web | 54340df89c02 | BLESSED | Leos-Mac-Studio-10442.local | preflight,full-jest,facts,gift-focused-a,gift-focused-b,post-push,all-five-live | executed=5137 | 480s/900s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T212632Z-receipt.md |
| 2026-08-16T215254Z | trysnowcubes-web | a9acff9e3848 | DEFERRED | Leos-Mac-Studio-10442.local | preflight,full-jest,facts,gift-page-focused-a,gift-page-focused-b,post-push,public-accessibility | executed=2345 | 420s/900s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T214559Z-receipt.md |
| 2026-08-16T223916Z | trysnowcubes-web | 4c9f3e582454 | PROOF-ONLY | Leos-Mac-Studio-10442.local | preflight,full-jest,fulfillment-focused-a,fulfillment-focused-b,post-restore-fulfillment | executed=2566 | ?/? | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/2026-08-16T223557Z-receipt.md |
| 2026-08-16T232330Z | trysnowcubes-web | 56cd75abd7a3 | PROOF-ONLY | Leos-Mac-Studio-10442.local | secrets,gift-customizer,fulfillment-focused-a,fulfillment-focused-b,fact-assert,post-restore-fulfillment | executed=291 | ?/? | /Users/leokwan/Development/snowcubes-plugin-canonical-v043-worktrees/takeoff-pass-20260816T232040Z/evidence/takeoff-pass/2026-08-16T232200Z-receipt.md |
| 2026-08-17T020333Z | trysnowcubes-web | f3c57d7cda20 | BLESSED | Leos-Mac-Studio-10442.local | preflight,jest,theme-check,fact-assert,allergen-verify,freshness-check,theme-push,page-cache-rotate,recipes-go,live-verify | executed=2574 | 5400s/900s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/evidence/takeoff-pass/2026-08-17T0042Z-receipt.md |
| 2026-08-17T150003Z | trysnowcubes-web | 5a8078f6f4d5 | PROOF-ONLY | Leos-Mac-Studio-10442. | test:storefront,test:storefront:node,test:storefront:node-hooks,render:preflight,allergen:verify,push:facts,freshness-check | executed=2538 | ?/? | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/20260817T145820Z-receipt.md |
| 2026-08-18T193019Z | trysnowcubes-web | c3990efe051b | PROOF-ONLY | Leos-Mac-Studio-10442 | secrets:check,test:storefront,test:storefront:node,render:preflight:test,render:preflight,test:asset-refs,theme:check,allergen:verify,push:facts | executed=2972 | 1500s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/20260818T192207Z-receipt.md |
| 2026-08-18T201523Z | trysnowcubes-web | 89d48d9a8528 | PROOF-ONLY | Leos-Mac-Studio-10442 | secrets:check,test:storefront,test:storefront:node,render:preflight:test,render:preflight,test:asset-refs,theme:check,wysiwyg:check,assets:orphans:check,parity:selftest,allergen:verify,push:facts | executed=2611 | 1700s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/20260818T200929Z-receipt.md |
| 2026-08-18T213256Z | shadow | 0e32fcc4 | BLESSED | claude-shadow | L1-full-suite,L2-public-ready,L3-release-identity | executed=1303 | ?/? | /Users/leokwan/Development/takeoff-evidence/shadow/20260818T193335Z-receipt.md |
| 2026-08-19T003143Z | trysnowcubes-web | f0397474ec4e | DEFERRED | Leos-Mac-Studio | secrets:check,test:storefront,test:storefront:node,render:preflight,test:asset-refs,wysiwyg:check,assets:orphans:check,theme:check,allergen:verify,push:facts | executed=2603 | 900s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/20260819T002827Z-receipt.md |
| 2026-08-19T204905Z | strongyes-web | 4d58bc4dbf41 | PROOF-ONLY | Leos-Mac-Studio-10442.local | smoke,db,e2e-public | executed=241 | 1260s/3600s | /Users/leokwan/Development/takeoff-evidence/strongyes-web/takeoff-pass/20260819T202549Z-receipt.md |
| 2026-08-20T024048Z | trysnowcubes-web | 0dd70d1e78ef | DEFERRED | Leos-Mac-Studio-10442 | secrets-check,test-storefront,test-storefront-node,test-visual-scan,render-preflight-test,render-preflight,test-asset-refs,wysiwyg-check,assets-orphans-check,theme-check,test-node,allergen-verify,push-facts,full-jest | executed=6551 | ?/? | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/20260820T022149Z-receipt.md |
| 2026-08-20T030416Z | resplit-web | ac9c87a72223 | PROOF-ONLY | Leos-Mac-Studio-10442 | lint,lint-js,parity-gate,test-run,guard-styles,check-dead-code | executed=4611 | ?/? | /Users/leokwan/Development/takeoff-evidence/resplit-web/20260820T025712Z-receipt.md |
| 2026-08-20T031526Z | resplit-ios | 499f5912ff83 | PROOF-ONLY | Leos-Mac-Studio-10442 | resplit-ios-lint,resplit-ios-integration | executed=21 | ?/? | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/20260820T030539Z-receipt.md |
| 2026-08-22T022226Z | trysnowcubes-web | 5ebcd8e23439 | REFUSED | Leos-Mac-Studio-10442.local | preflight,full-jest,test-node-run-1,test-node-run-2,test-node-run-3,cart-contract-run-1,cart-contract-run-2,cart-contract-run-3,allergen,facts,freshness,cart-contract-mutation,post-push-role-mutation | executed=8473 | 885s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/20260822T020647Z-receipt.md |
| 2026-08-22T054050Z | trysnowcubes-web | c5041019090b | DEFERRED | Leos-Mac-Studio-10442.local | preflight,full-jest,test-node-run-1,test-node-run-2,test-node-run-3,flavor-focused-run-1,flavor-focused-run-2,preview-journey-run-1,preview-journey-run-2,allergen-preview,fact-assert,exact-file-freshness,product-suppression-mutation,product-post-restore,installer-contract-green,installer-inverse-mutation,post-land-storefront-node | executed=9538 | 900s/1800s | /Users/leokwan/Development/takeoff-evidence/trysnowcubes-web/takeoff-pass/20260822T052244Z-receipt.md |
| 2026-08-22T155324Z | resplit-ios | c8a927ed71c7 | DEFERRED | Leos-Mac-Studio-10442.local | resplit_ios_lint,resplit_ios_integration,resplit_ios_chaos_network | executed=43 | 3120s/5400s | /Users/leokwan/Development/takeoff-evidence/resplit-ios/takeoff-pass/20260822T150023Z-receipt.md |
| 2026-08-22T230115Z | ai-leo | 473f6c83051b | PROOF-ONLY | Codex-Studio | L0,L1,L2 | executed=110 | 287s/1800s | /Users/leokwan/Development/takeoff-evidence/ai-leo/takeoff-pass/20260822T225541Z-receipt.md |
| 2026-08-23T192629Z | ai-leo | 6d671890957c | DEFERRED | Leos-Macbook-M4-Pro | L0,L1,L2 | executed=111 | 473s/1800s | /Users/leokwan/Development/takeoff-evidence/ai-leo/takeoff-pass/20260823T191751Z-receipt.md |
| 2026-08-28T120823Z | strongyes-web | e89b472fb2db | PROOF-ONLY | K240MPKGQW | L0-static,L1-smoke,L2-db,L3-journey | executed=1931 | ?/? | /Users/lkwan/Development/takeoff-evidence/strongyes-web/takeoff-pass/20260828T114130Z-receipt.md |
