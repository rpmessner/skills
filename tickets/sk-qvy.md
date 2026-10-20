---
id: sk-qvy
title: "devserve integration tests assume no other previews exist"
type: task
status: open
priority: 2
parent: null
blocked_by: []
related: []
supersedes: []
discovered_from: null
labels: []
created: 2026-10-20
closed: null
close_reason: null
---

## What to build
The real-service integration tests (systemd and tmux) assert on `devserve ls --json` rows without filtering to their own scratch app, so any live preview on the machine (e.g. a foreman build's preview) fails three tests: copied-preview lifecycle (row count), port-range exhaustion (ports list) and backend override (rows[0] backend). Filter rows to the test's app in the shared helper.

## Acceptance
- [ ] With an unrelated preview running, `DEVSERVE_INTEGRATION=1` suite passes (41/41).
- [ ] No test asserts on rows from other apps.
