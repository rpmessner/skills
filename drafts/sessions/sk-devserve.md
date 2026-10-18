# sk-devserve — sk-9ro.1

## Coordinator correction: flaky integration suite

**Fixed and reverified: 20 consecutive full-suite green runs, 22 tests per run (440 checks), no skips.** This section supersedes the original single-run verification below.

### Reproduction and cause

Ran the exact requested command unchanged until failure:

```sh
DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts
```

Runs 01–84 passed; run 85 failed in `test_copied_preview_lifecycle_and_secret_boundary`, at its `PGPASSWORD` argv assertion. Every run is saved in `drafts/sessions/devserve-flake-before/run-*.log`. Run 85 is redacted: the old assertion dumped the entire machine's process arguments, including unrelated credentials, so retaining that raw dump would itself be unsafe.

Confirmed cause: `ps -eo args` inspected every process on the machine. An unrelated coordinator shell running a foreman database query happened to have a password assignment in its command text. The preview worker/app argv did not contain the match. Thus unrelated concurrent work decided this test's result. The earlier report had noticed this symptom but treated a separated rerun as sufficient; that left the faulty observation boundary in place.

### Deterministic regression and fix

Added an unrelated live Python process carrying the secret canary in argv to the existing copied-preview test. Before the fix it deterministically failed in 2.820s; the sanitized failure is `devserve-flake-before/deterministic-red.log`.

Changed only `skills/devserve/scripts/test_integration.py`:

- Resolve each preview's systemd `ControlGroup`; collect PIDs from its `cgroup.procs` and descendant cgroups; inspect their `/proc/<pid>/cmdline`. This includes workers and app descendants, not unrelated sessions.
- Require the live worker's MainPID in the inspected set, preventing an empty inspection from passing vacuously.
- Check both preview units, retain full unit-show and JSON secret checks, and use assertion messages that never dump secret-bearing command lines.
- Keep the unrelated-canary regression active in every full run.
- Add `test_argv_inspection_detects_secret_in_preview_child`: deliberately place the canary in the real stub app's argv and require the scoped detector to fail. This proves the corrected boundary still catches a real application leak rather than merely skipping checks.

The deterministic copied-preview regression then passed (`devserve-flake-before/deterministic-green.log`), and the planted in-preview leak was detected. No production changes, retries, timeout increases, or extra sleeps were used.

Lesson/prevention: the original completion claim relied on a clean rerun of an environment-dependent assertion. The code-level prevention is ownership-scoped inspection plus paired unrelated-process/real-child canaries. No lesson bead was written because this session remains prohibited from bead writes.

### Twenty consecutive green runs

Each output is saved under `drafts/sessions/devserve-flake-after/`. The loop stopped on any failure; no failed run was discarded or counter reset. All 20 outputs were subsequently parsed to require `Ran 22 tests`, `OK`, no `FAILED`, and no skips.

```text
run-01.log: Ran 22 tests in 30.969s — OK
run-02.log: Ran 22 tests in 30.450s — OK
run-03.log: Ran 22 tests in 29.867s — OK
run-04.log: Ran 22 tests in 29.989s — OK
run-05.log: Ran 22 tests in 31.414s — OK
run-06.log: Ran 22 tests in 30.451s — OK
run-07.log: Ran 22 tests in 29.667s — OK
run-08.log: Ran 22 tests in 29.097s — OK
run-09.log: Ran 22 tests in 29.367s — OK
run-10.log: Ran 22 tests in 29.733s — OK
run-11.log: Ran 22 tests in 29.879s — OK
run-12.log: Ran 22 tests in 29.021s — OK
run-13.log: Ran 22 tests in 30.731s — OK
run-14.log: Ran 22 tests in 28.745s — OK
run-15.log: Ran 22 tests in 29.258s — OK
run-16.log: Ran 22 tests in 28.797s — OK
run-17.log: Ran 22 tests in 29.632s — OK
run-18.log: Ran 22 tests in 28.820s — OK
run-19.log: Ran 22 tests in 29.175s — OK
run-20.log: Ran 22 tests in 29.806s — OK

python3 scripts/check.py
45 skills, always-on ~1254/2500 tokens, 0 errors

python3 -m unittest discover -s skills/dispatch/scripts
Ran 18 tests in 9.393s — OK

git diff --check
(no output; exit 0)

systemctl --user list-units --all 'devserve-*' --no-pager
0 loaded units listed.
```

Correction review: Standards — stdlib process-boundary helpers, no production lifecycle changes. Spec — secret checks retain worker/app coverage and now check both previews. Risk — paired real-process regressions prove unrelated processes are excluded and a leaking preview child is detected; assertion failures no longer expose raw argv. No outstanding Critical/Important findings in this correction.


Verified complete for sk-9ro.1. No commits, pushes, bead writes, installation, dotfile changes, real-app changes, or real-app database changes.

## Changed

- `catalog.toml`: registers the own `devserve` skill, job `worktree-previews`.
- `skills/devserve/scripts/devserve`: executable Python stdlib CLI; config validation, git common-dir matching, bounded collision-resistant identities, port selection, transient systemd registry, copy/fresh PostgreSQL preparation, migrations, EnvironmentFile secret transport, journald, lifecycle/cleanup.
- `skills/devserve/scripts/test_devserve.py`: pure boundary tests.
- `skills/devserve/scripts/test_integration.py`: real user-systemd/PostgreSQL tests with an HTTP stub and throwaway `devserve_test*` databases.
- `skills/devserve/scripts/render_lifecycle.py` and `skills/devserve/lifecycle.md`: generated diagram and full state/event golden matrix.
- `skills/devserve/SKILL.md` and `skills/devserve/configuration.md`: usage, install note, schema, JSON interface, app contract and operational limits.

No real app needs changing to run these tests. Main services are read-only in the CLI; the test for main-unit behavior creates its own transient stand-in.

## Lifecycle table

The house state-machine-skeleton principle shaped the implementation: pure `step` returns effects, adapters perform IO, and terminal state is published even if an effect fails. Invalid state/event pairs raise ValueError and appear in the generated golden matrix.

| From | Event | To | Effects |
|---|---|---|---|
| absent | up | starting | prepare, launch |
| stopped | up | starting | prepare, launch |
| failed | up | starting | prepare, launch |
| running | up | running | none |
| starting | ready | running | none |
| starting | error | failed | rollback |
| running | error | failed | terminate |
| running | down | stopped | terminate |
| starting | down | stopped | terminate, rollback |
| stopped | down | stopped | none |
| failed | down | stopped | terminate |
| stopped | drop | absent | drop |
| failed | drop | absent | drop |

Stopped previews retain an active/exited systemd unit; no registry file is introduced. That retains the exact database/connection metadata for later `down --drop-db` and gc. Runtime flock serializes CLI mutations. PostgreSQL ownership comments gate reuse/deletion.

## Test-first evidence

- Initial pure seam run: validation did not reject invalid config, naming returned an empty unit, port choice returned None, and absent/up returned no effects. Implemented each seam and reached green.
- First real CLI run: `up` printed no URL; the stub lifecycle assertion failed. Implemented the real systemd/Postgres path, then passed copied-data HTTP, two-worktree isolation, logs and cleanup.
- Further red/green regressions: restart skipped migrations; failed starts left a child process/new database until cleanup completed; Ctrl-C left a new database; failed/down still displayed failed; stopped-unit claims were ignored; rollback refusal still displayed starting. All now have passing regression checks.
- Mutation checks in disposable copies: inclusive-overlap comparison, first-free ordering, identity suffix length, and missing rollback effect each failed assertions. No source mutation was retained.
- The skill is a new CLI reference, not behavioral-policy guidance; retrieval is through its trigger description and linked schema/help. No agent trials or subagents were launched.

## Standards review (first axis)

Scope: requested base `0b4cf3911e66a963d5f25479a783a66a918b12a5` plus this session's uncommitted additions. HEAD equals that base; there are no intervening commits. Reviewed catalog diff and all new devserve files directly (untracked additions do not appear in ordinary git diff). The pre-existing `drafts/briefs/sk-devserve.md` is not session work.

Inputs: root/local AGENTS.md, house standards baseline, state-machine-skeleton principle, dispatch process-boundary script/test style.

- **Important, fixed:** the initial CLI special-cased running `up`, and `down` on an already-failed worker printed stopped without recording that transition. `TRANSITIONS` now includes idempotent running/up, restart workers enter from their previous state, and failed/down uses the table and a retained stopped unit. The real regression test first failed (`failed != stopped`) and then passed.
- Diagram and complete state/event matrix are generated from the table; a golden check, reachability check and deterministic random-event check cover drift. Effects stay outside pure `step`.
- Own skill provenance, unique manifest job, stdlib-only implementation, process-boundary tests. No unrelated cleanup.

Declined to judge: real app config and dispatch brief adoption belong to sk-9ro.2/.3. No subagents, commits, pushes, bead writes, user config writes, or installation.

Verdict: Ready; no outstanding Critical or Important Standards findings.

## Spec review (second axis)

Compared sk-9ro.1's acceptance checklist and spec Decisions 1–9 (excluding real-app and dispatch adoption) against the script, config reference and real integration suite.

- **Important, fixed:** port selection initially ignored stopped units' port claims, contrary to “no unit claims it.” The exhausted-range regression first succeeded when failure was required; selection now excludes every other registered unit, including stopped ones. Same-preview restart can reclaim its own port.
- **Minor, fixed:** numeric `source_database` produced a TypeError rather than a validation error; added an explicit string guard and regression case.
- Added real main-unit list/tail/read-only verification, full required-field validation, and a secret canary assertion inside the HTTP stub (proves the EnvironmentFile actually reached the application).
- Verified all commands, JSON fields, common-dir matching, distinct ports/databases, range exhaustion without borrowing another app's ports, overlap rejection, copy/fresh ordering, migrate on reuse, owner identity, PREVIEW, journald follow, kept/dropped data, missing-worktree gc, and ownership refusal.

Evidence: `DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts` — 19 tests, 25.662s, OK.

Declined to judge: acceptance checks 1, 6, 7 require real foreman/dispatch adoption, explicitly outside this ticket. No real app or installed main service was changed.

Verdict: Ready; no outstanding Critical or Important Spec findings.

## Risk review (third axis)

Safety fact: a database name alone never authorizes reuse or deletion. Both generated identity and the exact ownership COMMENT must match. Credentials reach preparation, the app, and cleanup only through systemd EnvironmentFile; DATABASE_URL is assembled in worker memory. Unit metadata contains public config only. Proof level 5: exercised against real systemd and PostgreSQL, including an unowned database containing a precious table and a database whose ownership marker changes before rollback.

- **Important, fixed:** a rollback refusal raised before publishing failed StatusText, leaving an exited worker displayed as starting. The planted ownership-change regression first failed (`starting != failed`); transition notification now runs in `finally`, preserving failed state and metadata while refusing the drop. The CLI returns failure rather than waiting for a phantom startup.
- Earlier regression-driven fixes also covered migration reruns, child process-group cleanup, and Ctrl-C during migration (the original interrupted run left one new database; it now leaves zero).
- Cleared: source data untouched; same-basename worktrees cannot collide; unowned collisions retain their table; removed/mismatched ownership blocks deletion; failures after creation roll back new data; live app credentials/canary do not appear in full unit show, ls JSON or `ps -eo args`; main units are only listed/tailed.

Fresh focused proofs (same interpreter and actual services):

```text
DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts -p test_integration.py -k rollback_refusal
Ran 1 test in 1.818s — OK
... -k unowned
Ran 1 test in 1.215s — OK
... -k interrupt
Ran 1 test in 1.738s — OK
```

Residual boundaries: this is not a sandbox for arbitrary application code; commands must honor PREVIEW and avoid printing secrets/putting them in argv. SIGKILL/power loss between PostgreSQL CREATE and ownership COMMENT can leave an unmarked database, intentionally not auto-dropped. Reboot loses the transient registry, not kept databases; gc cannot discover those pre-reboot orphans. These limits are documented, not hidden behind a completion claim.

Declined to judge: malicious same-user tampering and real apps' external-write guards; this ticket provides the process contract, not a security boundary against its owner. Cheapest pre-merge check: the full opt-in integration suite plus check.py.

Verdict: Ready; no outstanding Critical or Important Risk findings.

## Stub transcript (final run)

Excerpt of the real integration suite's emitted transcript, not simulated output. Config was in a temporary directory via DEVSERVE_CONFIG_DIR; the HTTP request asserted `value = copied-data`, `preview = 1`, and the isolated database name. The source contained one evidence row and was not modified. Separate tests cover live `logs -f`, fresh migration/seed, main-unit logs, failures and ownership refusal.

```text
$ devserve up /tmp/devserve test-s8a8p3up/one
http://127.0.0.1:47787

$ devserve up /tmp/devserve test-s8a8p3up/two
http://127.0.0.1:47788

$ devserve ls
devserve-devserve_test1634944-one-1abc7b73a809.service app=devserve_test1634944 branch=one port=47787 http://127.0.0.1:47787 owner=stub-session state=running
devserve-devserve_test1634944-two-70e0d4f2b006.service app=devserve_test1634944 branch=two port=47788 http://127.0.0.1:47788 owner=stub-session state=running
devserve-devserve_test1634944-main.service app=devserve_test1634944 main state=inactive

$ devserve logs devserve-devserve_test1634944-one-1abc7b73a809.service
Oct 18 17:06:33 ORGANIC-PC systemd[737]: Starting devserve-devserve_test1634944-one-1abc7b73a809.service...
Oct 18 17:06:33 ORGANIC-PC systemd[737]: Started devserve-devserve_test1634944-one-1abc7b73a809.service.
Oct 18 17:06:33 ORGANIC-PC python3[1635106]: stub-ready
Oct 18 17:06:33 ORGANIC-PC python3[1635106]: 127.0.0.1 - - [18/Oct/2026 17:06:33] "GET / HTTP/1.1" 200 -

$ devserve down devserve-devserve_test1634944-one-1abc7b73a809.service
devserve-devserve_test1634944-one-1abc7b73a809.service stopped (database kept)

$ devserve down devserve-devserve_test1634944-one-1abc7b73a809.service --drop-db
devserve-devserve_test1634944-one-1abc7b73a809.service removed

$ devserve gc
devserve-devserve_test1634944-two-70e0d4f2b006.service removed

$ devserve ls --json
{"main_units": [{"app": "devserve_test1634944", "state": "inactive", "unit": "devserve-devserve_test1634944-main.service"}], "previews": []}
```

Before gc the test deleted worktree `two` and asserted its JSON `missing` flag. Before dropping `one`, it asserted the stopped state and that its database still existed. Distinct copied databases in this run:

```text
devserve_test1634944_preview_one_1abc7b73a809
devserve_test1634944_preview_two_70e0d4f2b006
```

## Final gates

```text
$ DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts
.....................
Ran 21 tests in 27.297s
OK

$ python3 -m unittest discover -s skills/dispatch/scripts
..................
Ran 18 tests in 9.181s
OK

$ python3 scripts/check.py
45 skills, always-on ~1254/2500 tokens, 0 errors

$ git diff --check
(no output; exit 0)

$ systemctl --user list-units --all 'devserve-*' --no-pager
  UNIT LOAD ACTIVE SUB DESCRIPTION
0 loaded units listed.

$ SELECT count(*) FROM pg_database WHERE starts_with(datname, 'devserve_test') OR starts_with(datname, 'dstest');
0
```

The SQL cleanup probe ran separately using the authorized local test login. One earlier combined final-gate shell failed the global `ps` assertion because its own later cleanup command contained the test PGPASSWORD assignment in the enclosing shell's argv. It was not a devserve unit leak; the separate reruns above passed without weakening the assertion. The first disposable mutation harness also stopped on a mismatched quote in its search string before mutating anything; the corrected four mutations all failed assertions as intended.

**Verified:** every sk-9ro.1 acceptance item, spec checks 2–5, 21 core/integration tests, 18 existing dispatch tests, manifest gate, no remaining preview units or test databases. Review axes: Standards 1 Important fixed; Spec 1 Important and 1 Minor fixed; Risk 1 Important fixed. No outstanding Critical/Important findings.

**Not verified / deliberately deferred:** real foreman data/UI/live-reload adoption, a real dispatched browser-check session, and application-level external-write refusal (spec checks 1, 6, 7; sk-9ro.2/.3). No install performed. Coordinator retains ownership of bead updates and any commit decision.
