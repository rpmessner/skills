---
id: sk-81s.9
title: "Coordinator: pi/tmux build-session launcher + dispatch skill"
type: task
status: closed
priority: 1
parent: sk-81s
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: 2026-10-16
close_reason: "Acceptance passed 2026-10-16: pi-window launched 'dispatch-accept'; pi-wait detected PONG-ONE (marker also inline in the brief, not falsely matched); send-keys follow-up delivered, pi-wait detected PONG-TWO; window killed. dispatch skill + scripts in skills/dispatch."
---

Operating model (user, 2026-10-15): this Claude session coordinates; build sessions run as pi in new tmux windows named for their content; Claude subagents only on explicit request. bin/pi-window <name> <workdir> <brief-file> launches pi (via zsh -i so the Jev/TypeSafe pi() wrapper applies) with the brief as first message. Dispatch skill (coordinator-only, disable-model-invocation false?): when to launch, naming, brief template (goal, bead ids, constraints, done criteria, report-back format), monitoring via tmux capture-pane and pi session files, sending follow-ups via tmux send-keys, closing out.

## Acceptance
After pi /login: launch a trivial session, read its output from the coordinator via capture-pane, send a follow-up, see the reply; window named correctly

## Notes
Add dispatch-from-bd-ready mode: coordinator lists bd ready across repos, proposes which tickets become pi windows, launches on approval (outer loop step 1).
2026-10-16 house-sync session: bin/pi-window moved to skills/dispatch/scripts/pi-window (byte-identical; flow now points at dispatch). Added skills/dispatch/scripts/pi-wait (whole-line, whitespace-trimmed match; exit 0 DONE / 3 EXITED / 4 timeout / 2 gone / 1 usage), smoke-tested in a throwaway tmux window (inline marker + echoed command line did not match; padded standalone line did). Added skills/dispatch/SKILL.md (model-invocable, coordinator-only) incl. dispatch-from-ready. Still open: acceptance test needs the coordinator (launch a trivial pi session, capture-pane, follow-up, reply).
