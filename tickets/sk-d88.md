---
id: sk-d88
title: "orient and dispatch honour board priority overrides and Jump to front"
type: task
status: open
priority: 3
parent: null
blocked_by: []
related: []
supersedes: []
discovered_from: null
labels: []
created: 2026-10-21
closed: null
close_reason: null
---

After foreman fm-c2w.30 lands (priority overrides and Jump to front on the board, exposed by `foreman ls --overlay`): orient's frontier and dispatch-from-ready order candidates by effective priority, with jumped tickets first, reading the overlay rather than the ticket file's priority alone.

## Acceptance
- [ ] ready-repos.py (or its caller) orders by effective priority from the overlay when the board is reachable, and by file priority when it is not
- [ ] orient's Frontier section and dispatch's proposal table show that order
- [ ] Verified against a live board with one override and one jump
