You are a build session in the house skills repo (~/dev/utils/sk-piwait, a git worktree on branch `sk-piwait`). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
A pi extension that tells foreman when a pi build session is waiting: when the session stops for a question to the user, a permission/confirmation prompt, or a provider usage limit, it posts `foreman ask session_waiting <ticket> --reason input|permission|usage_limit` (window and session from FOREMAN_SESSION/FOREMAN_ACTOR), and clears it when the session works again; pi-wait's IDLE/LIMITED stay the fallback.

## Read first
- AGENTS.md (this repo); ~/dev/utils/foreman/tickets/fm-3c3.5.md; ~/dev/utils/foreman/docs/sessions/fm-waiting.md (the session_waiting kind, CLI flags, clearing, Continue for pi windows on the default socket); the existing pi extension pi/house-guard/ (structure, how it hooks pi events, its test); pi's extension API as installed (read its docs/types from the installed pi package; do not guess event names).

## Tickets
fm-3c3.5 (foreman ticket; coordinator-owned; no ticket edits, no bd writes).

## Skills
- `tdd` at these seams: event-to-request mapping (question, permission, usage-limit error) and clearing on resumed activity, against a fake foreman CLI on PATH; never blocking or failing the pi session when foreman is absent (best-effort, bounded).
- `verify-before-claiming`; `code-review` against 4a024fa36a56530825197f950a4b928cf55db083 (Standards, Spec, Risk: the extension must never stall or crash pi). No subagents.

## Decisions already made
- Best-effort and bounded like foreman-send; an absent foreman is one warning, never an error.
- Enabled the same way as house-guard (path in ~/.pi/agent/settings.json packages) only by the coordinator after review; this session does not edit ~/.pi.

## Rules
- No commits, no pushes, no bd writes, no edits outside this worktree (no ~/.pi changes). Use /usr/bin/rm, not rm.

## Build loop
Use `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send progress fm-3c3.5 "<milestone; next step>"` at milestones.

## Done when
- Tests green with a fake foreman; a live check: `pi -e <this extension>` in a scratch dir with a prompt that makes pi ask a question shows one session_waiting request in a scratch foreman (or the fake CLI's log) and its clearing; check.py green; the report gives the exact settings.json change for enabling it.

## Report back
Write drafts/sessions/sk-piwait.md. Run `bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send report fm-3c3.5 --path drafts/sessions/sk-piwait.md`. Then print SK-PIWAIT DONE alone on the last line.
