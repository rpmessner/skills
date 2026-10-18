You are a build session in the house skills repo (~/dev/utils/sk-devserve, a git worktree on branch `sk-devserve`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
devserve, end to end: one command runs a worktree's app as a preview (a transient systemd user service on a port from the app's range, its own database copied from the app's main data, logs in journald), with ls, logs, down and gc, verified against a tiny stub app so no real app needs changing yet.

## Read first
- AGENTS.md (this repo: catalog.toml, check.py, provenance comments, one skill per job); docs/specs/devserve.md (approved spec; this ticket is Decisions 1-9 except the per-app contract work, acceptance checks 2-5); `bd show sk-9ro.1` is fine to read but do not write beads.
- skills/dispatch/scripts/ (house script style: small, stdlib, tested at the process boundary) and its tests.

## Tickets
sk-9ro.1 (claimed by the coordinator; do not run bd writes).

## Skills
- `tdd` at these seams: apps.toml validation (fields, absolute paths, overlapping ranges refused); port choice; unit naming; the preview lifecycle table's pure step; the CLI against real systemd-run --user with a stub HTTP app that reads PORT and DATABASE_URL and a throwaway Postgres database (create, copy via pg_dump/pg_restore, drop), all cleaned up by the tests.
- `verify-before-claiming` before writing the report.
- `code-review` on your own diff against 0b4cf3911e66a963d5f25479a783a66a918b12a5 before printing the marker: Standards (this repo's rules; the house state-machine rule for the lifecycle), Spec (sk-9ro.1 acceptance), Risk (secrets never in unit names, descriptions, show output or argv; never dropping a database devserve did not create; cleanup on failed starts). Run the axes one after another; spawn no subagents. Fix every Critical and Important finding.

## Decisions already made
- Everything in the spec's Decisions 1-9, including: config at ~/.config/devserve/apps.toml (tests use a temp config dir via an env override); transient unit devserve-<app>-<worktree>; systemd as the registry (no state file); PORT, DATABASE_URL and PREVIEW=1 for every preview; secrets only via EnvironmentFile; copy data by dump/restore then migrate; down keeps the db, --drop-db and gc drop it.
- Postgres for tests: the local dev server, postgres/postgres on localhost (as the Elixir apps' test configs use); create only databases with a devserve test prefix and drop them.

## Rules
- No commits, no pushes, no bd writes. Stay inside this worktree. Spawn no subagents.
- Do not create ~/.config/devserve or edit dotfiles; do not install anything into ~/.local/bin; do not touch real apps' databases (foreman, *_dev) or the installed foreman services. Tests clean up every unit and database they create. Use /usr/bin/rm, not rm.

## Done when
- Every sk-9ro.1 acceptance item holds with test evidence; scripts/check.py green; a transcript in the report of up / ls / logs / down --drop-db / gc against the stub app with a copied database.
Work until every item above holds. Hand off early only near your context limit (above about 85%), at a clean, green point, with a precise list of what remains.

## Report back
Write drafts/sessions/sk-devserve.md: what changed, the lifecycle table, the transcript, review findings per axis, final gate output. Then print SK-DEVSERVE DONE alone on the last line.
