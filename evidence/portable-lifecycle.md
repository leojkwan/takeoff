# Portable lifecycle proof

## Verdict

PASS at pushed Takeoff ref `3341fcaf51b8e8c2aedbe3e002fa98264c42d647`
on `2026-08-27T09:54:54Z`.

The isolated run cloned Takeoff into a path containing spaces, installed the
stable command, emitted the exact prompt bytes, prepared a detached
`origin/main` worktree, admitted an iOS command, stamped a durable receipt and
committed ledger row, removed the generated worktree without losing the
receipt, killed two launcher path mutants, restored the launcher, and finished
with every participating checkout clean.

The sandbox was
`/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox`. It was
deleted only after all final-state assertions passed.

## Exact lifecycle commands

The successful run used these resolved paths:

```bash
SANDBOX='/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox'
RELOCATED="$SANDBOX/relocated takeoff"
COMMANDS="$SANDBOX/commands"
TAKEOFF="$COMMANDS/takeoff"
ORIGIN="$SANDBOX/sample-repo.git"
CANONICAL="$SANDBOX/canonical sample-repo"
WORKTREE="$SANDBOX/sample-repo-worktrees/takeoff-pass-20260827T095454Z"
FAKE_DEV="$SANDBOX/Fake Xcode.app/Contents/Developer"
TMP_ROOT="$SANDBOX/tmp"
EVIDENCE_ROOT="$SANDBOX/durable evidence"
```

### Relocated command

```bash
git clone --quiet --branch hardening/release-oracle --single-branch \
  "$(git remote get-url origin)" "$RELOCATED"
git -C "$RELOCATED" config user.name 'Leo Kwan'
git -C "$RELOCATED" config user.email 'leojkwan@gmail.com'
"$RELOCATED/bin/takeoff" install --bin-dir "$COMMANDS"
"$TAKEOFF" root
"$TAKEOFF" prompt > "$SANDBOX/prompt.out"
cmp "$RELOCATED/PASS.md" "$SANDBOX/prompt.out"
```

Receipts:

```text
relocated_head=3341fcaf51b8e8c2aedbe3e002fa98264c42d647
root=/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox/relocated takeoff
prompt=byte-exact
```

### Worktree admission

The fixture created a local bare origin, committed `tracked.txt` on `main`,
pushed it, then invoked the installed Takeoff command:

```bash
git init --quiet --bare "$ORIGIN"
git --git-dir="$ORIGIN" symbolic-ref HEAD refs/heads/main
git clone --quiet "$ORIGIN" "$CANONICAL"
git -C "$CANONICAL" config user.name 'Leo Kwan'
git -C "$CANONICAL" config user.email 'leojkwan@gmail.com'
printf '%s\n' 'portable fixture' > "$CANONICAL/tracked.txt"
git -C "$CANONICAL" add tracked.txt
git -C "$CANONICAL" commit --quiet -m 'Add portable lifecycle fixture'
git -C "$CANONICAL" push --quiet -u origin main
"$TAKEOFF" prepare-worktree "$CANONICAL" "$WORKTREE"
```

Receipts:

```text
sample_ref=012abdc11f0a00717fb7cf908a8744eee552b8bd
HEALED worktree <absent> -> 012abdc11f0a00717fb7cf908a8744eee552b8bd
worktree=detached-origin-main@012abdc11f0a00717fb7cf908a8744eee552b8bd
```

The run separately asserted that the generated worktree's `HEAD` equaled
`refs/remotes/origin/main`, `git symbolic-ref --quiet HEAD` returned no branch,
and the canonical checkout was clean.

### iOS environment admission

The fake developer directory contained one executable `usr/bin/xcodebuild`
probe that printed the four admitted environment values. The installed command
invoked that executable directly:

```bash
env \
  -u DEVELOPER_DIR \
  -u IOS_DESTINATION \
  -u XCB_LOCK_WAIT \
  -u DERIVED_DATA \
  TAKEOFF_IOS_DEFAULT_DEVELOPER_DIR="$FAKE_DEV" \
  TMPDIR="$TMP_ROOT" \
  "$TAKEOFF" ios-env --pass-root "$WORKTREE" -- \
  "$FAKE_DEV/usr/bin/xcodebuild"
```

Receipts:

```text
HEALED ios-env DEVELOPER_DIR,IOS_DESTINATION,XCB_LOCK_WAIT,DERIVED_DATA
{"DERIVED_DATA": "/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox/tmp/takeoff-ios-derived-data/9841cc554b1dd089", "DEVELOPER_DIR": "/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox/Fake Xcode.app/Contents/Developer", "IOS_DESTINATION": "platform=iOS Simulator,name=iPhone 17 Pro", "XCB_LOCK_WAIT": "900"}
ios-env=validated
```

The probe asserted the exact developer directory, destination, and lock wait,
and asserted that the derived-data directory existed below
`$TMP_ROOT/takeoff-ios-derived-data`.

### Receipt and ledger stamping

The source receipt lived under the generated worktree at
`evidence/takeoff-pass/2026-08-27T095454Z-portable-lifecycle.md`. Its judged
ref was the fixture commit above and its one lane was:

```text
- lane portable-lifecycle rc=0 marker="relocated command lifecycle passed" count=1
```

The installed command stamped it with an absolute custom evidence root:

```bash
TAKEOFF_EVIDENCE_ROOT="$EVIDENCE_ROOT" \
  "$TAKEOFF" stamp \
  "$WORKTREE/evidence/takeoff-pass/2026-08-27T095454Z-portable-lifecycle.md"
```

Receipts:

```text
stamp: OK — sample-repo PROOF-ONLY executed=1 -> ADOPTION.md
ledger_commit=a3eeed575f3ec1f3d60669c629e822a38c45f513
ledger_subject=adoption: sample-repo PROOF-ONLY train stamp (executed=1)
durable_receipt=/private/tmp/takeoff-portable-lifecycle.RP6QDo/lifecycle sandbox/durable evidence/sample-repo/takeoff-pass/2026-08-27T095454Z-portable-lifecycle.md
```

Before cleanup, `cmp` proved that the durable copy was byte-identical to the
source receipt, the ledger contained the durable path, the ledger subject was
exact, and the relocated Takeoff checkout was clean.

The generated worktree was then removed and the durable copy was checked
again:

```bash
git -C "$CANONICAL" worktree remove --force "$WORKTREE"
test ! -e "$WORKTREE"
cmp "$SANDBOX/expected-receipt.md" \
  "$EVIDENCE_ROOT/sample-repo/takeoff-pass/2026-08-27T095454Z-portable-lifecycle.md"
test -z "$(git -C "$CANONICAL" status --porcelain=v1)"
```

Receipt:

```text
worktree-cleanup=source-removed,durable-bytes-preserved,canonical-clean
```

## RED controls

Both mutations were planted only in the disposable relocated clone. Each
mutation was restored with:

```bash
git -C "$RELOCATED" restore --source=HEAD -- bin/takeoff
```

### Fixed-home root

Mutation:

```diff
-    root = launcher.parent.parent
+    root = Path.home() / 'Development' / 'takeoff'
```

Test:

```bash
cd "$RELOCATED"
HOME="$SANDBOX/home without takeoff" \
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_takeoff.py' -v
```

Result:

```text
test_root_resolves_the_current_checkout ... FAIL
Ran 10 tests in 0.867s
FAILED (failures=6, errors=1)
rc=1
```

This kills a launcher that silently returns to one fixed home-directory
checkout.

### Caller-working-directory helper dispatch

Mutation:

```diff
-    helper = root / "bin" / HELPERS[command]
+    helper = Path.cwd() / "bin" / HELPERS[command]
```

Test:

```bash
cd "$RELOCATED"
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_takeoff.py' -v
```

Result:

```text
test_relocated_checkout_routes_every_helper (helper='prepare-worktree') ... FAIL
test_relocated_checkout_routes_every_helper (helper='ios-env') ... FAIL
test_relocated_checkout_routes_every_helper (helper='stamp') ... FAIL
Ran 10 tests in 1.180s
FAILED (failures=4)
rc=1
```

This kills helper dispatch that follows the caller's current directory instead
of the installed launcher's checkout.

## Restored GREEN

After both restorations, the same relocated suite passed:

```bash
cd "$RELOCATED"
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s test -p 'test_takeoff.py' -v
```

```text
Ran 10 tests in 1.771s
OK
```

Final assertions:

```bash
test -z "$(git -C "$RELOCATED" status --porcelain=v1)"
test -z "$(git -C "$CANONICAL" status --porcelain=v1)"
test "$(git -C "$SOURCE_ROOT" status --porcelain=v1)" = "$SOURCE_BEFORE"
```

```text
final_state=relocated-clean,canonical-clean,source-unchanged
portable_lifecycle=PASS
```

## Proof ceiling

This proves one isolated local lifecycle from the pushed branch head and proves
the launcher suite rejects the two named path regressions. The ledger commit
`a3eeed575f3ec1f3d60669c629e822a38c45f513` existed only in the disposable
relocated clone. This is not pull-request, merge, release, publication, or
production-runtime proof.
