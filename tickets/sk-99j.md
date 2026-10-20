---
id: sk-99j
title: "devserve: tmux backend for macOS beside the systemd backend on Linux"
type: feature
status: closed
priority: 2
parent: null
blocked_by: []
related: []
supersedes: []
discovered_from: null
labels: []
created: 2026-10-20
closed: 2026-10-20
close_reason: "Merged 67dc0ed. Coordinator rerun: 41/41 integration tests pass when rows from two concurrent foreman previews are filtered; unfiltered, 3 fail on those unrelated previews (pre-existing test isolation gap, filed sk-qvy). check.py 0 errors. Native macOS untested."
---

Make devserve cross-platform: keep the systemd user-unit backend on Linux exactly as it works today, and add a tmux backend used on macOS (no systemd). One CLI and one contract (up, ls --json, logs, down --drop-db, gc, owner from FOREMAN_SESSION); the backend is chosen by platform, with an explicit override for tests.

A tmux backend already exists in the user's work fork of this repo (devserve rewrite: previews in tmux windows on a devserve session, a state-file registry, orphan gc including databases with no state entry, gc --stopped, base refresh for data = "template" apps). The coordinator provides a sanitised copy of that code as a reference; port its logic as the macOS backend and leave the Linux systemd path unchanged. Shared improvements (orphan-database gc, template base databases) may apply to both backends where they fit; say which.

Acceptance: on this Linux machine, existing previews and the unit/integration tests behave as before (systemd); the tmux backend's tests pass under the override on Linux; ls/down/gc work across both registries; SKILL.md, configuration.md and lifecycle.md describe both backends; no work repo names, paths or accounts in code or tests; python3 scripts/check.py clean.

## Notes
- 2026-10-20 user: Documents:
- [Report](docs/sessions/sk-devserve-mac.md)
- [Brief](docs/briefs/sk-devserve-mac.md)
- [Skill](skills/devserve/SKILL.md)
- [Configuration](skills/devserve/configuration.md)
