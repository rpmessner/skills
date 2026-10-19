You are a build session in the house skills repo (~/dev/utils/sk-devbriefs, a git worktree on branch `sk-devbriefs`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
Build sessions use devserve for browser checks instead of improvising ports, acceptance databases and servers: the dispatch brief template says to run `devserve up` in the worktree for browser checks (owner = the session name), and coordinator close-out runs `devserve down --drop-db` for that session's previews before killing the window.

## Read first
- AGENTS.md; `bd show sk-9ro.3`; docs/specs/devserve.md (Decision 8); skills/devserve (SKILL.md, configuration.md); skills/dispatch (template and close-out). Apps registered on this machine: `devserve ls` (foreman today); unregistered apps keep the current port guidance.

## Tickets
sk-9ro.3 (claimed by the coordinator; no bd writes).

## Skills
- `tdd` where there is code (e.g. a close-out helper that finds a session's previews by owner in `devserve ls --json` and drops them); check.py for text.
- `verify-before-claiming`; `code-review` against 98fc0933b8a85adcdee77a6747ce0298229e4e27 (Standards, Spec). No subagents.

## Rules
- No commits, no pushes, no bd writes. Stay inside this worktree. Do not start real previews of the user's apps except one scratch check that you stop with --drop-db. Use /usr/bin/rm, not rm.

## Build loop
Use `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send progress sk-9ro.3 "<milestone; next step>"` at milestones.

## Done when
- Template and close-out text updated; helper tested; check.py green; the report shows the exact commands a session and the coordinator run, and how check 6 (a real dispatch using devserve) will look.

## Report back
Write drafts/sessions/sk-devbriefs.md. Run `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send report sk-9ro.3 --path drafts/sessions/sk-devbriefs.md`. Then print SK-DEVBRIEFS DONE alone on the last line.
