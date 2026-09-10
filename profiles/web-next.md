# Reviewing a Next.js application

Find the commands in the target application's package scripts and CI. This
profile is a starting point, not a command list to copy into every project.

## Check the change

Run the relevant type checks and unit tests. Include the production build when
the change affects routing, imports, bundling, or environment configuration:
passing TypeScript and unit tests does not show that Next.js can build the app.

For database behavior, run the affected operation against the project's test
database. For a user flow, drive the built application in a browser and inspect
the result. A mocked request does not establish that either integration works.

Challenge one relevant failure case, such as an invalid route, denied request,
or incorrect calculation. Verify the test rejects it, then restore the source.

## If deployment is authorized

Follow the project's branch, review, and deployment rules. Some projects deploy
automatically from the default branch, so pushing a test-only change can still
publish a release. Check the resulting deployment's commit and status, then
exercise the changed behavior at that deployment URL.

Identify the project's rollback method before publishing. Record production
monitoring or user feedback that still needs a later check.
