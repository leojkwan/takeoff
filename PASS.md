# Review this repository before release

Work in the repository for the current session. Find defects in its checks,
run the relevant checks, and leave a concise report. A request to review is
not permission to publish, deploy, spend money, or alter account access.

## Read the project

Run `takeoff root` to locate this tool. Read its `METHOD.md`, then the target
repository's `AGENTS.md` or `CLAUDE.md`, test configuration, and release
instructions. Read a matching file in `profiles/` if one exists. Treat its
commands as examples to verify against current source, not mandatory commands.

Use a clean worktree pinned to fresh `origin/main`. If this session is in the
primary checkout, use `takeoff prepare-worktree <canonical-repo> <generated-worktree>`
to prepare an isolated sibling. Preserve all unrelated changes. Untracked
entries under `evidence/takeoff-pass/` are this review's output and do not make
the worktree dirty. Respect any host build queue or existing work owner.
The helper refuses rather than delete unknown dirty changes.

Check for a recent unfinished report before starting. It is a warning of
possible concurrent work, not a lock or proof that another process is alive.
Resolve overlap through the repository's existing coordination mechanism.

## State what you will test

Open a report under `evidence/takeoff-pass/<UTC>-receipt.md`. Record the exact
commit, time budget, checks selected, excluded checks, and why. For each check,
record its command, expected completion output, and minimum executed count.
Derive those expectations from source or actual tool output.

Choose a small set of deliberate defects to challenge the checks. Name the
expected failure for each. Repeat suites only when flake history or a specific
uncertainty justifies the extra runs.

## Run and challenge the checks

Run each selected command. Record its exit status, completion output, and test
count. Investigate missing tests and unexpected output instead of calling the
run successful from its exit status alone. If a required dependency, queue, or
permission is unavailable, name the exact next action and leave that check open.

On a temporary local branch, introduce each declared defect and confirm it
reached the code or artifact the check reads. Commit changes first when the
check reads Git HEAD. Run the check and quote the failure it catches. A check
that accepts the defect needs investigation.

Stage only the experiment's exact paths. Preserve its history on a named
branch, return to the judged commit, and verify the source diff is empty.
Keep the report outside those commits so restoring source cannot remove it.

You may repair a test or guard when a demonstrated failure calls for it. Follow
the repository's normal review and merge rules. Report product defects; change
product behavior only when the user's task authorizes it. Re-run affected
checks after any accepted repair.

## Release only when authorized

Follow the target repository's release process and existing permissions.
Verify the rollback command before a release. A push that triggers deployment
is a release action, including a push containing only test changes. Inspect
the destination after deployment; a successful command alone does not show
that the expected version is live. Record pending external decisions separately.

## Save a readable report

Write the report under `evidence/takeoff-pass/<UTC>-receipt.md`. Lead with the
finding that most affects the release decision. Include:

- the commit reviewed and the purpose of the change;
- defects found, with file locations and how to reproduce them;
- checks run, their commands, results, and executed counts;
- deliberate defects used to challenge the checks and what caught them;
- test repairs and their verification;
- `not exercised:` followed by anything the review did not cover;
- release status, if an authorized release was attempted;
- the next action for each unresolved issue.

If there are no findings, say which checks support that conclusion and what
remains untested. Do not turn uncertainty into a passing verdict.

Before removing your generated worktree, preserve the report under
`${TAKEOFF_EVIDENCE_ROOT:-$HOME/Development/takeoff-evidence}/<repo>/`.
Never remove unrelated or uncertain work.

Archiving with `takeoff stamp` is optional. If requested, follow
`<takeoff-root>/docs/archiving.md`; it describes the existing ledger format and
the local commit the helper creates. Do not archive or commit a report merely
because a review ran.

Takeoff ships no scheduler or background service. Its documented pass path
begins with an explicit command. `takeoff stamp` validates receipt shape,
source checkout identity, and ledger serialization; it does not authenticate
the invoker, receipt authorship, channel acceptance, or the truth of semantic
claims.
