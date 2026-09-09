# Reviewing a local automation

This profile began with a private assistant workflow. Use the target project's
current source and permissions; no account, schedule, or authorization carries
over from that workflow.

## Check the change

Run syntax checks and unit tests for the changed behavior. Test installers in
disposable home directories, including missing files, corrupted backups, and
changes made after installation. Verify rollback preserves those later changes.

Mock external transports while checking message construction. Exercise errors
and ambiguous responses so a retry cannot silently send a duplicate message.
Keep actual sends, account access, and installed schedules behind the user's
existing authorization.

Inspect rendered output when the automation produces HTML or other visual
content. String assertions cannot establish that people can read the result.

## If installation is authorized

Compare the installed files with the reviewed source. Inspect the actual
registered service and schedule. Keep the previous version recoverable.

A manual run does not show that a scheduled run occurred. Observe the next
scheduled execution when that behavior matters, and record the expected time
as the follow-up. Do not change the schedule or trigger an external action just
to produce a successful report.
