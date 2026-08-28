# Takeoff public hygiene audit

Audit date: 2026-08-27.

Audit baseline: `60b14c0` on `hardening/release-oracle`. The `METHOD.md`
private-plan-path removal and this audit are part of the same successor change.
Live GitHub metadata was re-read at `2026-08-27T11:31:08Z`.

## Verdict

The candidate source tree has no unresolved private-company identifier,
generated-author footer, unsupported automation promise, current-branch model
authorship claim, or nonhistorical private home path. The 43 historical
execution rows remain byte-preserved and explicitly bounded.

The existing repository cannot satisfy a literal zero-model-authorship-metadata
bar in place:

- Nine model-prefixed remote branches remain live.
- Fourteen merged pull requests retain model-prefixed historical head names.
- Five of those pull-request head refs are already deleted, while GitHub still
  displays their original names. Deleting the remaining nine refs therefore
  cannot erase the pull-request metadata.
- Thirteen commit messages reachable from `origin/main` contain historical
  model vocabulary: twelve branch or merge-topology records and one dated
  method description.

The GitHub repository is private as of 2026-08-27, so this is a publication
readiness blocker rather than a current public disclosure.

## Current surfaces

| Surface | Current observation | Disposition |
|---|---|---|
| GitHub repository | `firstbitelabsllc/takeoff` is private; default branch is `main`; description and homepage are empty. | No current public exposure. Publication remains a separate protected action. |
| Pull requests | Fourteen merged pull requests, zero open pull requests. Every merged pull request records a `claude/` or `codex/` historical head name; five of those refs no longer exist. | The live repository itself proves branch deletion does not remove pull-request head metadata. |
| Reachable commit metadata | Thirteen `origin/main` commit messages contain model vocabulary: twelve branch or merge records and one historical method description. | A neutral branch name does not sanitize inherited commit metadata. |
| Releases and tags | No GitHub releases and no remote tags. | No release metadata to sanitize. |
| Current work branch | `hardening/release-oracle`. | Neutral branch name; no authorship claim. |
| Live model-prefixed branches | Nine refs under `claude/` or `codex/`. | Every ref has zero unique file payload by `evidence/branch-hygiene-audit.md`; deletion still requires explicit approval. |

## Exact source scans

| Check | Result | Meaning |
|---|---|---|
| Private employer names, corporate email suffixes, internal host suffixes, and workspace archive links across the candidate tree. | Zero matches. | The tree carries no private employer identity. |
| Generated-author footer shapes in candidate files and all reachable commit messages. | Zero matches. | No attribution footer or generated-author commit trailer is present. |
| Unsupported cadence or deliberate-invoker claims pinned by `test/test_takeoff.py` across `README.md`, `AUTOMATION.md`, `PASS.md`, and `DECOMMISSION-2026-08-15.md`. | Zero matches. | Public documents stay within the checked explicit-command boundary. |
| Concrete macOS user-home absolute paths. | Forty-three matches, all in the 43 historical `ADOPTION.md` data rows. | Intentional historical exception; the rows remain byte-for-byte unchanged and are disclosed as non-portable self-reported local records. |
| Home-relative private Shadow plan pointers. | Zero matches after the `METHOD.md` change. | The public method now points only to `DECISION-v1.md`; `test/test_takeoff.py` pins the removal. |
| Model vocabulary in candidate files. | Supported invocation examples, one generic reasoning description, historical profile/decommission facts, immutable adoption host fields, and the two hygiene audits that identify the metadata being remediated. | These are commands or bounded historical identifiers, not claims that a model authored the current branch. |

The exact scan commands used were:

```bash
candidate_files() {
  git ls-files --cached --others --exclude-standard -z
}

company_pattern="$(
  printf '%s' '\bS' 'nap(chat)?\b|@s' 'nap(chat)?\.com|sc-' \
    'corp|github\.sc-' 'corp\.net|jira\.sc-' \
    'corp\.net|https://[^[:space:]]*slack\.com/archives'
)"
! candidate_files |
  xargs -0 rg -n -i "$company_pattern" --

footer_pattern='^[[:space:]]*(Co-Authored-By:|Generated (by|with) (ChatGPT|Claude|Codex|Gemini|Copilot|Grok|OpenAI|Anthropic))'
! candidate_files |
  xargs -0 rg -n -i "$footer_pattern" --
! git log --all --format='%B' |
  rg -n -i "$footer_pattern"

! rg -n -F \
  -e 'Takeoff has zero standing automation' \
  -e 'only that deliberate pass can stamp' \
  -e 'closing the decommission cadence gap' \
  -e 'single definition of the scheduled surface' \
  -e 'gap it closes' \
  -e 'until a host-owned automation exists' \
  -e 'Wake (owned by' \
  README.md AUTOMATION.md PASS.md DECOMMISSION-2026-08-15.md

home_prefix="$(printf '\057Users\057')"
test "$(
  candidate_files |
    xargs -0 rg -n -F "$home_prefix" -- |
    wc -l |
    tr -d ' '
)" = 43

private_plan_prefix="$(printf '\176\057.shadow\057')"
! candidate_files |
  xargs -0 rg -n -F "$private_plan_prefix" --
```

The 43 `ADOPTION.md` data rows were compared with the pinned `origin/main`
baseline `87249ea7fae3c556a63937d70dcea15811a74dfa`. Both row sets contain 43
lines, are byte-identical, and hash to
`2a8df326de62bf0dd240b0057f9e8a994e71f9477839e53808115d5fa5bf0576`.

## Intentional historical exceptions

### Adoption rows

All 43 `ADOPTION.md` data rows preserve their original receipt paths and host
fields. Replacing those cells would rewrite the recorded evidence and break
the byte-preservation proof. The ledger now says plainly that these are
self-reported, machine-local records rather than portable or independent
verification.

### Audit identifiers

`evidence/branch-hygiene-audit.md` names each model-prefixed ref because the
exact identifier is required to prove preservation and state the deletion
command. This audit names the same branch, pull-request, and commit metadata to
explain why zero-residue publication is not yet true.

### Invocation and profile vocabulary

`README.md` and `AUTOMATION.md` show supported host commands. `PASS.md` names
common repository instruction files. Profiles and decommission history retain
dated process facts. None of these statements attribute authorship of the
current source or upgrade a host receipt into acceptance proof.

## Publication boundary

The stated zero-residue bar cannot be met by deleting branches alone because
merged pull-request objects retain their historical head names and the
reachable Git history retains model-associated topology text.

The minimum path that satisfies the literal bar is:

1. Keep this repository private as the full historical source.
2. Produce a neutral, clean-history publication candidate from the accepted
   tree, with no pull-request or model-prefixed branch history.
3. Re-run the source scans and clone-anywhere proof against that candidate.
4. Publish only after explicit approval of the destination and exact content.

If preserving the existing GitHub history matters more than literal
zero-residue publication, the alternative is to accept the merged pull-request
head names and reachable commit-message vocabulary as disclosed historical
exceptions, then separately approve the nine branch deletions already listed
in `evidence/branch-hygiene-audit.md`.

Recommendation: keep the current repository private and use a clean-history
publication candidate. That is the only path that satisfies the written
zero-model-authorship-metadata requirement without pretending GitHub can
rewrite merged pull-request history.

## Exact wake

Leo chooses one publication policy:

- **Literal zero residue:** approve preparation of a clean-history publication
  candidate; repository creation and publication remain separately gated.
- **Preserve GitHub history:** approve the nine exact branch-deletion commands
  and accept the merged pull-request and commit-message metadata as intentional
  historical exceptions, which requires narrowing the `~d402` acceptance
  sentence.

Until one policy is chosen and executed, `~d402` remains blocked.
