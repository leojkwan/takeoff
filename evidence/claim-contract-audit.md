# Takeoff public claim contract audit

Audit baseline: `89e4743` on `hardening/release-oracle`. The corrections and
new falsifiers described here are part of the same successor change. A
"current check" is executable inside this repository; a "remaining gap" is
not promoted as proof.

## Conclusion

Takeoff's local fixtures strongly prove checkout-relative dispatch, generated
worktree path safety, exact receipt-byte preservation, strict row syntax, and
serialization among cooperating ledger writers. They do not prove human
provenance, deliberate invocation, semantic receipt truth, external channel
acceptance, current public-main state, external release, or machine-global
absence of automation.

No public claim should exceed the ceiling in its row:

| Claim family | Source | Canonical owner | Current check | Strongest executable falsifier | Truthful ceiling | Remaining gap |
|---|---|---|---|---|---|---|
| Launcher, install, and prompt dispatch | `bin/takeoff`, `README.md` | `bin/takeoff` | `test/test_takeoff.py` checks checkout-relative root resolution, exact `PASS.md` bytes, idempotent symlink install, local helper dispatch, exit propagation, and malformed-install refusal. | Relocate the checkout, replace a helper with a symlink, remove or de-execute a helper, or compare `takeoff prompt` byte-for-byte with `PASS.md`. | A valid installation resolves its own checkout, emits the checked-in prompt bytes, and dispatches only executable non-symlink helpers from that checkout. | It does not prove that any coding host executed, understood, or obeyed the prompt. |
| Manual invocation and host neutrality | `README.md`, `AUTOMATION.md`, `PASS.md` | The caller for invocation; `bin/takeoff` for prompt bytes | `test_public_docs_share_the_invocation_boundary_contract` keeps the four public documents aligned; launcher tests contain no host-specific branch. | Invoke `takeoff prompt` from a relocated checkout, then pass those bytes to a chosen host; any host-specific failure is outside the launcher. | Takeoff ships no scheduler or background service, and its documented entrypoint is host-neutral prompt text. | It cannot discover an external scheduler, authenticate the invoker, or prove that an invocation was deliberate. |
| Generated worktree admission and teardown | `bin/prepare-worktree`, `PASS.md` | `bin/prepare-worktree` | `test/test_prepare_worktree.py` covers stale and missing generated worktrees, fresh `origin/main`, unknown dirt, ignored data, hidden index flags, local-only history, late writes, evidence preservation, and destination symlinks. | Plant unknown tracked, ignored, reflog-only, index-hidden, FIFO, symlinked, or late-created data in a generated `takeoff-pass-<UTC>` worktree and require refusal or exact preservation. | The helper admits only its generated worktree shape, preserves `evidence/takeoff-pass/`, and refuses cleanup when unknown data could be lost. | It does not prove target-repository test correctness, remote availability beyond the performed fetch, or behavior of non-cooperating processes. |
| Observational occupancy | `PASS.md`, `AUTOMATION.md` | The pass operator or an external coordinator | The documents define one prior-receipt age/verdict observation; Takeoff has no occupancy-lock implementation. | Start two passes simultaneously after both read the same apparently free prior-receipt state. | An unfinished receipt younger than its declared budget is an OCCUPIED observation. | The observation is non-atomic; simultaneous starts can both see free and require coordination outside Takeoff. |
| iOS environment and XBQ grading | `bin/ios-env`, `tools/grade-xbq-result.py`, `profiles/ios.md` | The two helpers for local admission; the selected profile and target repo for lane truth | `test/test_ios_env.py` checks Xcode executable/path rules, destination syntax, lock bounds, DerivedData safety, and value-safe output. `test/test_xbq_marker.py` checks rc, result, exact marker, and count floor. | Supply a missing `xcodebuild`, malformed destination, unsafe DerivedData, rc-zero FAILED record, missing or historical marker, or zero/below-floor execution count. | The helpers validate local environment/path syntax and the structured XBQ result record they receive. | Destination syntax does not prove an installed simulator; the record does not prove the underlying lane, TestFlight, ASC, or field outcome without external readback. |
| Receipt parsing and verdict syntax | `bin/stamp`, `PASS.md` | `bin/stamp` | `test/test_stamp.py` covers first-nonblank title, cold-reader order, repo/origin and HEAD/ref identity, exactly one rc/marker/count per lane, nonzero counts, verdict/rc compatibility, BLESSED release-field presence, and row-safe paths. | Move the title below prose, duplicate or corrupt lane fields, use zero counts, stamp a non-REFUSED failure, omit BLESSED `RELEASED`, mismatch repo/ref, or inject a Markdown table delimiter or newline into a ledger path. | `stamp` can reject locally malformed or internally inconsistent receipts tied to the current source checkout. | It cannot authenticate who wrote the receipt, whether markers came from the named commands, whether a release pointer is genuine, or whether narrative claims are true. |
| Durable copy and ledger serialization | `bin/stamp`, `tools/adoption_lock.py` | `bin/stamp` and the Git-common-directory lock | `test/test_stamp.py` covers exact judged bytes, source and durable symlinks, collisions, concurrent writers, root-independent locking, hook rewrites, commit-byte verification, and interrupted-row recovery. | Mutate the receipt after parsing, race two stamps under different evidence roots, pre-place a symlink or conflicting durable file, or install a hook that rewrites `ADOPTION.md`. | Cooperating `stamp` processes serialize on one repository lock, preserve the judged bytes, and verify the committed ledger payload. | There is no cryptographic signer or proof against privileged out-of-band edits to the Git history or durable store. |
| Adoption provenance and pointer recovery | `ADOPTION.md`, `tools/check-adoption-receipts.py` | The checker for local pointer integrity; the historical row author for provenance | `test/test_receipt_pointer.py`, `test/test_adoption_receipts.py`, and `test/test_adoption_history.py` cover canonical title/ref identity, byte-compatible deterministic repair, CRLF/non-pointer preservation, symlink and ambiguity refusal, dirty/staged ledger refusal, empty-ledger refusal, indented-row refusal, and selected historical identities. | Remove a receipt, provide zero or multiple nonidentical candidates, use arbitrary prose instead of canonical identity, indent every row, or present an empty ledger. | The checker can show that a recognized local row points to a canonical receipt identity and can repair one unambiguous byte-compatible pointer without changing other row bytes. | Historical rows remain self-reported and paths are non-portable; the checker does not prove authorship, human invocation, public-main state, or external release. |
| Profiles and external release facts | `profiles/*.md`, `METHOD.md`, `PASS.md` | Current target-repository source and the named external platform; profiles are priors | The pass must re-derive commands and Conduct facts from current source. Local tests only pin a few helper call sites and profile text contracts. | Compare every profile command, watcher, pause, release route, and readback against the target repo and live platform before a pass; any mismatch invalidates the prior. | Profiles provide vocabulary, example commands, evidence obligations, descriptive priors, and explicit `none` gaps. A selected profile owns its platform-specific pauses. | Profiles are not automatically synchronized and cannot prove current external service, watcher, app-review, deployment, or ownership state. |
| Historical evidence ceilings | `ADOPTION.md`, `evidence/*.md` | Each dated artifact and its recorded ref | Historical rows are byte-preserved; the adoption checker grades reachable receipt identity; `evidence/takeoff-adversary.md` now distinguishes baseline `38affc0`, recorded passing implementation `89e4743`, and later heads. | Re-run the recorded revision's exact command, compare historical row bytes, or run the same falsifier against a later head and require fresh evidence. | A historical artifact can report what one local run recorded for its named revision. | It does not prove a later head, current public branch, merge, release, deployment, runtime behavior, or independent verification. |

## Acceptance commands

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_stamp.py' -v

PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_adoption_receipts.py' -v

PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_*.py' -v

git diff --check
```
