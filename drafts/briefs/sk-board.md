You are a build session in the house skills repo (~/dev/utils/sk-board, a git worktree on branch `sk-board`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
Wire beads-board into the house workflow so the board stays current as a side effect of following the skills: a new `board` skill teaches the CLI verbs; `dispatch` records each session; the brief template has build sessions send progress and their report; the coordinator's close-out sends review, request changes and commit; `tight-spec` and `to-tickets` move epics from idea to ticketed. Never blocks: a board failure is a warning, never a failed step.

## Read first
- AGENTS.md (this repo's rules: catalog.toml, check.py, provenance comments, one skill per job), skills/flow/SKILL.md, skills/dispatch/SKILL.md and scripts/, skills/tight-spec/SKILL.md, skills/to-tickets/SKILL.md and references.
- The CLI contract: ~/dev/utils/beads-board/docs/sessions/bb-cli.md (verbs, flags, exit codes, BOARD_ACTOR, BOARD_SESSION, BOARD_TOKEN_FILE, BOARD_URL); spec Decisions 8, 11, 12 in ~/dev/utils/beads-board/docs/spec.md.

## Tickets
sk-5o2 and sk-osj (the coordinator claimed both; do not run bd here).

## Skills
- `tdd` at these seams: dispatch's pi-window and the brief template are scripts and text: test the script parts (pi-window passes BOARD_ACTOR/BOARD_SESSION, calls board dispatch with the right arguments, and still launches when board is missing or fails) with a fake board on PATH; check.py must stay green.
- `verify-before-claiming` before writing the report.
- `code-review` on your own diff against b2a36c995f97c57b1471629c83e0ff9050f8e4b4 before printing the marker: Standards (this repo's AGENTS.md, the writing style of existing skills: terse, concrete triggers), Spec (both tickets' acceptance), Risk (every skill run now touches an external tool: it must never block or fail a step). Run the axes one after another in this session; spawn no subagents. Fix every Critical and Important finding.

## Decisions already made
- One new skill `board` (job: keep beads-board current; catalog entry mode own); other skills reference it at the step where a verb is due, one line each, not long prose. Keep always-on cost low.
- pi-window: runs `board dispatch <ids> --window ... --harness pi --model ... --workdir ... --branch ... --base ... --brief ... --report ...` after launching, and exports BOARD_ACTOR=pi and BOARD_SESSION=<window> into the pi session; tolerates board being absent (one warning line).
- The brief template's Report back slot says to run `board report <ids> --path <report>` before printing the marker, and the build loop to send `board progress` at milestones; the coordinator's close-out steps add review / changes / commit.
- tight-spec: create a draft epic only for project-size specs (`board epic create` with slug, project, spec link), start_spec at the interview, approve_spec on approval; to-tickets: `board epic ticket <slug> --bead <epic-id>` after publishing.
- The CLI is not installed yet on this machine; the skills must read naturally either way.

## Rules
- No commits, no pushes, no bd commands. Stay inside this worktree; do not edit ~/.claude, ~/.agents, ~/.pi or the beads-board repo. Run scripts/check.py; do not run scripts/link.py --apply. Use /usr/bin/rm, not rm. Spawn no subagents.

## Done when
- check.py green; the pi-window tests green with a fake board; each changed skill reads cleanly; the report lists every verb now called and where.
- Work until every item holds; hand off early only near your context limit (above about 85%).

## Report back
Write drafts/sessions/sk-board.md: what changed per skill, the verb-to-step map, test evidence, review findings per axis, final check output. Then print SK-BOARD DONE alone on the last line.
