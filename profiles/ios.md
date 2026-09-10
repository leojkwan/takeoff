# Reviewing an iOS application

Read the project's build instructions and use its existing build queue. Find
the relevant schemes, destinations, tests, and release commands in current
source. Do not copy another project's simulator or release authorization.

## Check the change

Run the affected unit tests and a simulator build. For an interaction change,
exercise the built app with its UI tests or a recorded manual check. Inspect
the executed test count: selective testing can choose zero tests on an
unchanged commit, and a wrapper can return zero even when the build failed.

Where the host uses `xbq`, route the command through the queue:
`takeoff ios-env --pass-root "$PWD" -- xbq <lane command>`.
Every `xbq` lane must write a structured result and use
`tools/grade-xbq-result.py` with its actual `--expect-marker` and a positive
`--floor`; raw `xbq` rc or prose is never acceptance.

## Configure the helper

Set `DEVELOPER_DIR` to an installed Xcode developer directory and
`IOS_DESTINATION` to a simulator this project supports. The helper preserves
valid values and validates paths before invoking the command.

For a host with known defaults, you may set
`TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR` and `TAKEOFF_IOS_DEFAULT_DESTINATION`.
Those values are used only when the corresponding command value is absent or
invalid. Without a valid explicit value or configured default, the helper
refuses and names the setting needed. It never assumes an Xcode version or
simulator model.

`XCB_LOCK_WAIT=900` is the default queue wait. `DERIVED_DATA` defaults to a
separate temporary directory for the review worktree. The helper validates
destination syntax but does not query installed simulators; verify the chosen
destination with the project's build tooling.

## If release is authorized

Follow the project's signing, upload, and distribution steps. Confirm the
expected build in App Store Connect or the selected distribution channel.
Uploading a build, submitting for review, and App Review approval are separate
events. None grants permission for the next.

Record how the project recovers from a bad build before uploading it, and name
any later device check or external decision still needed.
