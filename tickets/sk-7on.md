---
id: sk-7on
title: "preview-cleanup reports failure when devserve ls runs during an async drop"
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

## What happened
2026-10-20, closing out fm-doclinks and fm-docpanel: `preview-cleanup.py <name>` printed "Preview cleanup failed; keep the session window: devserve ls --json returned non-zero exit status 1" for both. The journal shows both previews were stopped and their `-cleanup` (`_drop`) units started at that moment, so `down --drop-db` succeeded and the re-list failed. A retry a minute later listed nothing and passed. First seen right after the cross-platform devserve merge (sk-99j); unknown whether it predates it.

## What to build
Reproduce: `devserve ls --json` while a preview's async drop holds the devserve lock. `ls` should wait for or not need the lock, or preview-cleanup should retry the re-list briefly. Capture ls's stderr in the cleanup failure message.

## Acceptance
- [ ] A test reproduces ls failing during a drop (or proves another cause) before the fix.
- [ ] preview-cleanup passes on the first run for a preview with a database.
