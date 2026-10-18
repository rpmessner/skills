You are a build session in the house skills repo (~/dev/utils/sk-tickets, a git worktree on branch `sk-tickets`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
The house workflow moves from `bd` to foreman's ticket files: `to-tickets`, `dispatch` (including dispatch from ready across repos), `wayfinder` and the `foreman` skill use the `foreman` ticket commands for repos that have switched to ticket files, and keep working with `bd` for repos still on beads until they are migrated. foreman itself switched today; skills, form-engine, dotfiles and the WoW repos switch later with `foreman adopt`.

## Read first
- AGENTS.md (this repo's rules); ticket fm-axu.4 in ~/dev/utils/foreman/tickets/fm-axu.4.md (and the spec ~/dev/utils/foreman/docs/specs/ticket-files.md, Decisions 5, 9, 10).
- The foreman CLI ticket commands: `foreman --help`, ~/dev/utils/foreman/docs/sessions/bb-files.md and fm-adopt.md; a converted repo to look at: ~/dev/utils/foreman/tickets/.
- skills/to-tickets (SKILL.md, references/beads.md), skills/dispatch, skills/wayfinder, skills/foreman, skills/flow; ~/dev/AGENTS.md's beads section (the house rules file; propose its replacement text in your report, do not edit it).

## Tickets
fm-axu.4 (claimed by the coordinator). Do not edit ticket files or run bd writes.

## Skills
- `tdd` where there is code (dispatch's ready-across-repos listing: repos with tickets/ use `foreman ready --json`, repos with .beads use `bd ready`; test with fake repos of both kinds).
- `verify-before-claiming` before writing the report.
- `code-review` on your own diff against 86ec5b0e057a53869831ce5e45d1b98345549498 before printing the marker: Standards (this repo's rules, terse skills), Spec (fm-axu.4 acceptance). Run the axes one after another; spawn no subagents.

## Decisions already made
- A repo is on ticket files when it has a `tickets/` folder; otherwise beads. Skills detect this per repo, never assume.
- Publishing tickets (to-tickets) on a files repo: `foreman new` per ticket with --parent and --blocked-by, then `foreman check`; the files are committed by the coordinator. The epic body is the approved spec.
- `foreman adopt` is how a repo switches; skills mention it where they currently mention `bd init`.

## Rules
- No commits, no pushes, no bd writes, no edits outside this worktree (the house ~/dev/AGENTS.md text goes in your report as a proposal). Spawn no subagents. Use /usr/bin/rm, not rm.

## Build loop
Use `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send progress fm-axu.4 "<milestone; next step>"` at milestones; warnings never block work.

## Done when
- Every fm-axu.4 acceptance item that does not need a live dispatch holds; scripts/check.py green; tests for the ready listing green; a dry run of to-tickets' publish steps against a temp files repo (foreman new/check) shown in the report; proposed ~/dev/AGENTS.md tickets section in the report.
Work until every item above holds. Hand off early only near your context limit (above about 85%), at a clean, green point, with a precise list of what remains.

## Report back
Write drafts/sessions/sk-tickets.md: what changed per skill, evidence, the AGENTS.md proposal, review findings per axis, final check output. Run `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send report fm-axu.4 --path drafts/sessions/sk-tickets.md`. Then print SK-TICKETS DONE alone on the last line.
