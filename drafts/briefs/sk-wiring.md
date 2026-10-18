You are a build session in the house skills repo (~/dev/utils/sk-wiring, a git worktree on branch `sk-wiring`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
The workflow uses foreman's approvals inbox: build sessions ask build-time questions with `foreman ask decision` and wait for the answer; the coordinator's close-out posts push and open_pr requests (and merge requests when merging is the next step) instead of asking the user in the terminal, and waits for them. Agents still never push.

## Read first
- AGENTS.md (this repo); ~/dev/utils/foreman/tickets/fm-zgd.6.md; ~/dev/utils/foreman/docs/specs/approvals-inbox.md (Decision 11; Decisions 6-8 for kinds and the CLI); the CLI as built: ~/dev/utils/foreman/docs/sessions/bb-inbox.md, fm-push.md, fm-openpr.md, fm-mergereq.md (`foreman ask decision|push|open_pr|merge`, `foreman wait`, exit codes and JSON).
- skills/dispatch (SKILL.md, brief template, close-out), skills/foreman, skills/flow.

## Tickets
fm-zgd.6 (foreman ticket; coordinator-owned). No bd writes, no ticket edits.

## Skills
- `tdd` where there is code (e.g. a helper that builds the push/open_pr ask from a worktree and branch); otherwise check.py and a dry run of the documented commands against a scratch foreman API is enough.
- `verify-before-claiming` before writing the report.
- `code-review` on your own diff against 0fa47daa7a81654f4d239b496f1dfffc121e7dc2: Standards (terse skills), Spec (fm-zgd.6 acceptance items that are text and code). One axis after another; no subagents.

## Decisions already made
- Brief template: a build session with a question it cannot answer posts `foreman ask decision <ticket> --question ... --option ... --recommendation ...` and runs `foreman wait <id>` (with a long timeout) instead of asking in its pane; IDLE detection in pi-wait stays the fallback.
- Close-out after an authorized commit: post push (and open_pr where the repo's flow uses PRs; default-branch pushes only for one-off tickets) and wait; tell the user once in chat that requests are waiting on the board.
- The "agents never push" rule stays, with one line pointing at board requests.

## Rules
- No commits, no pushes, no bd writes. Stay inside this worktree. Spawn no subagents. Use /usr/bin/rm, not rm.

## Build loop
Use `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send progress fm-zgd.6 "<milestone; next step>"` at milestones.

## Done when
- The text and code acceptance items of fm-zgd.6 hold; check.py green; the report lists the exact commands a coordinator and a build session will run, and what the live checks 5 and 9 will look like (run later by the coordinator on a real dispatch).
Work until every item holds; hand off early only near your context limit (above about 85%).

## Report back
Write drafts/sessions/sk-wiring.md (changes per skill, commands, review findings, final check). Run `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send report fm-zgd.6 --path drafts/sessions/sk-wiring.md`. Then print SK-WIRING DONE alone on the last line.
