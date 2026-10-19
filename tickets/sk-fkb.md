---
id: sk-fkb
title: "dispatch: build sessions as panes in the epic coordinator's window"
type: feature
status: in_progress
priority: 2
parent: null
blocked_by: []
related: []
supersedes: []
discovered_from: null
labels: []
created: 2026-10-19
closed: null
close_reason: null
---

Epic coordinators (foreman fm-3c3.8) put their pi build sessions in new panes of their own window instead of new windows, so an epic's work sits together. The main coordinator keeps one window per build.

## Behaviour
- `pi-window --pane <name> ...` (or an equivalent mode) splits the caller's current window (`$TMUX_PANE`'s window) instead of creating a window; the new pane is titled `<name>` and tagged with a pane option (e.g. `@build <name>`) so it is found by name, not by index; layout keeps the coordinator pane readable (builder's call, e.g. main-vertical with the coordinator as main).
- Duplicate check, `pi-wait`, the capture/send-keys recipes in SKILL.md and close-out (`kill-pane` instead of `kill-window`) all accept a pane-mode build the same way they accept a window build; window builds keep working unchanged.
- Board dispatch metadata records the pane target so foreman can focus the pane (select-window + select-pane).
- Works on any tmux server the caller is on (`$TMUX`), including `-L foreman`.

## Acceptance
- Fake-tmux tests (like test_pi_wait.py) cover pane launch, duplicate refusal, pi-wait DONE/LIMITED/IDLE/GONE on a pane target, and window mode unchanged.
- One real scratch tmux run: two pane builds in one window with stub pi, each found and waited on by name, one killed without touching the other or the coordinator pane.
- SKILL.md says when to use pane mode (epic coordinators) and when not (main coordinator).
- Repo checks green.
