---
id: sk-osj
title: "Board wiring: tight-spec and to-tickets epics, coordinator close-out"
type: task
status: closed
priority: 2
parent: null
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-18
closed: 2026-10-18
close_reason: "Live: bb-zgd.1 moved dispatched -> progress -> reported from the pi session and review/changes/commit from close-out through the board CLI (2026-10-18)."
---

## What to build
Part of beads-board epic bb-c2w (in ~/dev/utils/beads-board; spec Decisions 8, 12). Blocked by bb-c2w.7 (the board CLI).
The planning and review half of the workflow reports to the board too, so epics show their stage before tickets exist and tickets show review and commit.


## Acceptance
- [ ] tight-spec creates a draft epic (slug, project, spec link) for project-size specs only and sends start_spec and approve_spec
- [ ] to-tickets sends ticket with the new beads epic id
- [ ] Coordinator close-out (dispatch skill close-out and flow) sends review, request_changes and commit
- [ ] check.py passes; /tight-spec then /to-tickets walks a draft epic idea to ticketed on the board (beads-board check 6)

## Notes
- 2026-10-18 Ryan Messner: Merged 7315cb7 (slice 42068d6). Script seams tested with a fake board (12 tests); live card movement (beads-board checks 3 and 6) waits for the board install. Close after that check.
