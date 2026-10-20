# devserve cross-platform build

## Changed

- `skills/devserve/scripts/devserve` retains the systemd launch/stop path and adds platform selection: Linux defaults to systemd, macOS to tmux. `DEVSERVE_BACKEND` overrides creation; existing previews keep their backend.
- `devserve_tmux.py` adds owned tmux windows, atomic private state, persistent logs, literal dotenv loading, and process cleanup through the existing worker/table.
- `devserve_data.py` adds template refresh/clone and conservative orphan cleanup. These apply to both backends, as does `gc --stopped`.
- Linux `ls`, `logs`, `down`, and `gc` see both registries. Existing systemd JSON stays unchanged; tmux rows add `backend`.
- Updated `SKILL.md`, `configuration.md`, and generated `lifecycle.md`. Existing Linux unit/integration files are unchanged.

## Verified

- `python3 -m unittest discover -s skills/devserve/scripts`: 41 discovered, 8 passed, 33 integration tests skipped as intended.
- `DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts`: all 41 passed in 75.846s. Includes the unchanged 15 systemd integration tests plus 18 new integration checks using scratch tmux, mixed registries, and systemd templates.
- `python3 scripts/check.py`: 58 skills, approximately 2385/2500 always-on tokens, 0 errors.
- `foreman check`: tickets valid. `git diff --check`: clean.
- `git diff --exit-code aee2388 -- skills/devserve/scripts/test_devserve.py skills/devserve/scripts/test_integration.py`: no changes.
- Final PostgreSQL query found no `devserve_test*` databases; systemd listed no test preview units. Fixtures shut down their scratch tmux servers. Installed devserve was not changed; no commits or pushes.

Failing-first evidence: platform default returned systemd for Darwin; the override initially launched a systemd preview; orphan GC retained a missing-worktree database; restart emitted an extra line; wrong-socket down succeeded; configured-source and live-window orphan checks both observed an unintended drop. Each now has a passing regression test. Mixed cleanup and template CLI cases first failed because their requested commands/options were absent. The original lifecycle golden/reachability suite passes without changing the table.

## Not verified / open

No native macOS host was available. Backend execution was verified under the requested Linux override. Python 3.11+ remains required; the reference's Python 3.9 parser and unrelated configuration extensions were not ported. Installed main-systemd service logs remain Linux-only.

One failed test run initially left a throwaway source database. Cleanup approval was recorded in request `3f92e554-c3d8-41ea-a754-9997e5eb0d24`; the safety tool still blocked it. Request `173748f9-edbc-48a9-9c7a-67b38f6bbba3` was answered `Removed manually; continue`. A subsequent database query confirmed removal. Test cleanup now uses finally blocks.

No new tickets requested. sk-99j remains in progress for coordinator close-out. Pre-existing `docs/briefs/` is untouched.

## Review: Standards

Reviewed the working diff and new files against `aee2388871a6691b539407f9b089ac937ae28bac`.
HEAD equals that base; there are no commits in this build. The requested review therefore includes uncommitted files.

- Important, `skills/devserve/scripts/devserve:26`: the adapter API copied all globals into a namespace. Replace it with an explicit set of shared operations so backend dependencies remain visible.
- Minor, `skills/devserve/scripts/devserve_tmux.py:118`: window ownership compared a list containing its own dead-state field. Compare only the named identity fields instead.
- Minor, `skills/devserve/scripts/test_tmux_integration.py:24`: test cleanup could skip database/unit cleanup after an assertion failure. Put fixture cleanup in a finally block.
- The existing lifecycle table remains the single source of transitions; both workers execute it. No new parallel lifecycle machine was introduced.

Declined to judge: unrelated pre-existing brief files; no changes requested there.
Initial verdict: Ready with fixes. All three findings fixed before the Spec axis.

## Review: Spec

Checked sk-99j against the CLI, reference backend, docs and test coverage.

- Important, `skills/devserve/scripts/devserve_tmux.py:179`: restarting a tmux preview printed a stop message before the URL, violating the shared `up` output contract. A real CLI regression test reproduced it; silence the internal stop.
- Important, `skills/devserve/scripts/test_tmux_integration.py:54`: the shared template implementation had only tmux evidence. Added the same real refresh/clone check through systemd; it passed.
- Minor, `skills/devserve/scripts/devserve`, logs branch: app-level systemd logs on macOS attempted journalctl. Return an explicit Linux-only error instead.
- Ported the reference's tmux windows, private registry, persistent logs, orphan cleanup, stopped cleanup and template refresh. Kept Python 3.11/tomllib and existing Linux semantics rather than importing the reference's custom TOML parser, extra ports, or timeout configuration.

Declined to judge: native macOS execution, unavailable on this Linux host. The requested acceptance gate explicitly uses the tmux override on Linux.
Initial verdict: Ready with fixes. Both fixes applied before Risk.

## Review: Risk

The safety requirement is that cleanup proves ownership and checks both registries before deleting anything.
Real scratch-service tests exercise this at proof level 5, through the CLI and PostgreSQL.

- Critical, `skills/devserve/scripts/devserve:586` and `devserve_data.py:71`: orphan GC could drop a formerly owned preview now configured as a source database. Reproduced with a real database; GC now excludes every configured source/base and base staging name.
- Critical, `skills/devserve/scripts/devserve:597`: losing a state entry could make a live tmux preview look like an orphan when its application held no database connection. Reproduced with a live HTTP preview; GC now also protects database identities named by existing devserve-session windows.
- Important, `skills/devserve/scripts/devserve_tmux.py:79`: wrong-socket access could treat a live preview as absent. Reproduced and fixed earlier with an exact registry/socket guard.
- Cleared: changed window tokens fail closed; unrelated windows survive GC; mixed-systemd/tmux down routes to the owning backend; failed setup rolls back only owned new data. The original Linux test files are unchanged.
- Preserved the original fresh-mode validation behavior rather than tightening an unrelated Linux config rule.

Declined to judge: malicious same-user modification of private state, external SIGKILL of workers, and native macOS execution. Those are not claims made by the Linux acceptance suite.
Final verdict: Ready. Every Critical and Important finding above is fixed and covered by the final 41-test run. Cheapest repeat gate is the full `DEVSERVE_INTEGRATION=1` command listed above.

Review totals: Standards 1 Important and 2 Minor fixed; Spec 2 Important and 1 Minor fixed; Risk 2 Critical and 1 Important fixed. No unresolved findings within the requested Linux acceptance scope.


