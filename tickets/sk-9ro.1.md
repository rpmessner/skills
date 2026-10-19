---
id: sk-9ro.1
title: "devserve core, proven with a stub app"
type: feature
status: closed
priority: 2
parent: sk-9ro
blocked_by: []
related: []
discovered_from: null
labels: ["initiative"]
created: 2026-10-18
closed: 2026-10-18
close_reason: "Merged d5680fc: devserve core; 22-test opt-in integration suite green 20x; check.py green."
---

## What to build
The devserve tool itself, end to end, verified against a tiny stub app so it does not depend on any real app's changes. Spec Decisions 1-9 except the per-app contract work, acceptance checks 2-5.

## Interfaces
Produces: the apps.toml schema, the `devserve` CLI and its JSON for `ls`, the PORT / DATABASE_URL / PREVIEW=1 preview contract apps must honour, unit naming `devserve-<app>-<worktree>`. Consumed by tickets 2 and 3 and by foreman's preview button (foreman fm-c2w.14).


## Acceptance
- [ ] devserve skill (own) and script (Python 3 stdlib): up [worktree], ls, logs <preview|app> [-f], down <preview> [--drop-db], gc; --json on ls
- [ ] ~/.config/devserve/apps.toml validated on load: required fields, absolute paths, non-overlapping inclusive port ranges (overlap refused with both app names)
- [ ] up matches the worktree to an app by git common dir, takes the first free port in the app's range (no devserve unit claims it, nothing listens), starts transient unit devserve-<app>-<worktree> via systemd-run --user, prints the URL
- [ ] Data: copy (pg_dump/pg_restore source_database into <app>_preview_<worktree>, then migrate) and fresh (create, migrate, seed)
- [ ] PORT, DATABASE_URL and PREVIEW=1 set for every preview; secrets only via EnvironmentFile from env_file; no secret in unit name, description, show output or ps arguments (check 5)
- [ ] systemd is the registry: ls reads app, worktree, branch, port, URL, database, owner and state back from units, plus the app's main_units; owner = user or the session name from the caller's environment
- [ ] down keeps the database; down --drop-db drops it; gc removes previews whose worktree is gone; afterwards no devserve unit or preview database remains (check 4)
- [ ] Preview lifecycle (absent, starting, running, failed, stopped) as a declared table with a pure step, tested
- [ ] Unit tests (config, ports, naming, step) and integration tests with real systemd-run --user, a stub HTTP app reading PORT/DATABASE_URL and a throwaway Postgres database, all cleaned up; check.py green
