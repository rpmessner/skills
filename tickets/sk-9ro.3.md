---
id: sk-9ro.3
title: "Build sessions use devserve for browser checks"
type: task
status: in_progress
priority: 2
parent: sk-9ro
blocked_by: ["sk-9ro.1","sk-9ro.2"]
related: []
discovered_from: null
labels: ["initiative"]
created: 2026-10-18
closed: null
close_reason: null
---

## What to build
Wire devserve into the dispatch workflow so build sessions stop improvising ports, acceptance databases and servers. Spec Decision 8, acceptance check 6.

## Interfaces
Consumes: devserve CLI (ticket 1); a configured app (ticket 2).


## Acceptance
- [ ] dispatch brief template: 'run devserve up for browser checks' replaces 'use another port and your own databases'; the preview's owner is the session name
- [ ] dispatch close-out: devserve down --drop-db for the session's previews before killing the window
- [ ] The next real dispatch runs its browser check on a devserve preview and close-out leaves no preview or database (check 6)
- [ ] check.py green

## Notes
Merged adbeffa: brief template and close-out cleanup. Open: check 6 on the next real dispatch of a registered app (foreman).
