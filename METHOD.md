# Review principles

Takeoff asks an agent to establish what a repository's checks actually tell
you. The executable instructions are in [PASS.md](PASS.md).

## Start from the project

Read the current source, test commands, release instructions, and any previous
report. Stack profiles are examples, not a substitute for that inspection.
Before running commands, record the commit, time budget, checks selected,
expected completion output, and any checks that will be left out.

Use an isolated worktree. Respect the project's hooks, build queues, concurrent
owners, and release permissions. Takeoff does not grant permission to deploy.

## Check that the tests ran

A successful exit code is insufficient when a test filter can select zero
tests. Inspect the actual completion output and executed test count. Derive
expected markers from that command's source or observed output; do not guess
one from a different tool.

Choose checks for the behavior at risk: unit tests for local logic, a real
dependency for integration, and the built application for a user journey.
These answer different questions. Running one does not establish the others.

## Try to expose a false pass

Introduce a specific defect on a temporary local branch and run the check that
should catch it. Verify the defect reached the input being tested. A tool that
reads committed files needs a committed test change; editing the working tree
alone will not exercise it.

Restore the original source afterward and keep the experiment recoverable.
Repeat checks when flake history or nondeterminism warrants it, and report any
intermittent failure.

## Report the boundary of the result

Record commands, observed output, test counts, failures, and a `not exercised:`
line. Keep source checks, merged code, deployment, and behavior in use distinct.
If a release is authorized, inspect the destination's actual state after it.
If an external decision is pending, name it and when to check again.

Check vendor boundaries against the implementation. If a dependency cannot be
replaced without changing callers, say so and explain why it is accepted.

The report belongs with the project reviewed. `takeoff stamp` is an optional
archive helper for the existing Takeoff ledger. Its checks validate report
format and local writes; they cannot establish that its conclusions are true.
See [archiving](docs/archiving.md) when that additional record is wanted.
