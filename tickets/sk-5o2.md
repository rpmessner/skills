---
id: sk-5o2
title: "Board wiring: board skill, dispatch and the brief template"
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
Part of beads-board epic bb-c2w (in ~/dev/utils/beads-board; spec Decision 12). Blocked by bb-c2w.7 (the board CLI); cross-repo edges are not modelled, so check that ticket is closed before starting.
Wire the board into the dispatch path so build sessions keep their tickets current as a side effect of following their brief.


## Acceptance
- [ ] New board skill teaches the verbs and when each workflow step sends them
- [ ] dispatch (pi-window) runs board dispatch with window, harness, model, workdir, branch, base, brief, report; sets BOARD_ACTOR and BOARD_SESSION
- [ ] Brief template has build sessions send board progress at milestones and board report before the done marker
- [ ] Never blocks a session: a board failure is a warning, never a failed step
- [ ] check.py passes; a real dispatch moves its card dispatched, building, reported with no manual board call (beads-board check 3)

## Notes
- 2026-10-18 Ryan Messner: Merged 7315cb7 (slice 42068d6). Script seams tested with a fake board (12 tests); live card movement (beads-board checks 3 and 6) waits for the board install. Close after that check.
