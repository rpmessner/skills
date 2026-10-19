---
id: sk-9ro
title: "devserve: stable and per-worktree app servers as systemd user services"
type: epic
status: open
priority: 2
parent: null
blocked_by: []
related: []
discovered_from: null
labels: ["initiative"]
created: 2026-10-18
closed: null
close_reason: null
---

## Idea (not yet specced)
House tooling so web apps run without tmux server windows: each app's main runs as an installed release under systemd user units on a fixed port (beads-board's two units on 4747 are the model), and each worktree branch can run as a transient preview server (systemd-run --user) on a port from the app's range, with its own dev database. Logs stay in journald and can be followed in a tmux pane on demand.

Sketch of the CLI: devserve up <app> [worktree] (pick a port, start, print the URL), devserve ls (all apps: branch, port, URL, state), devserve logs <name> (journalctl --user -f), devserve down <name> [--drop-db]. systemd is the registry: unit names and their environment hold app, branch and port; no extra state file.

## Why
The user wants to use their apps (beads-board, we-go-next, gw2) day to day on stable ports while trying features from worktrees on others, without tmux windows full of servers, and still be able to tail a server like an in-pane server.

## Questions for the spec
- Per-app entries: where they live (a TOML in the skills repo or each app's own file), port ranges, start command per app type (mix phx.server, release), database naming and cleanup.
- Previews: dev server from source vs a built release; env and secrets (no secrets in unit names or args; untracked env files only).
- Integration: dispatch briefs use devserve instead of "pick another port"; build sessions take screenshots from a real preview; beads-board shows a preview link per ticket or PR later.
- Lifecycle: previews stop when the worktree is removed; stale previews listed by devserve ls.
- Stable installs: a shared helper for release install and update (beads-board README steps generalised) or per-app only.


## Notes
2026-10-18 (user): previews are never started automatically (not by dispatch, not by sessions). The board launches a preview from the ticket sheet on demand and stops it when the ticket moves forward (past review: merged, done or abandoned), so no orphan servers. devserve is the mechanism the board calls; the board owns when.
