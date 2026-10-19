---
id: sk-81s
title: "House skill set: one rationalized system from Matt Pocock, superpowers, pstack + own skills"
type: epic
status: open
priority: 1
parent: null
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: null
close_reason: null
---

Sources are read-only pinned clones in ~/dev/utils/skill-sources/. The house set (this repo, becomes ~/dev/utils/skills at cutover) is the only thing linked into ~/.claude/skills and ~/.agents/skills (pi reads the latter). catalog.toml maps every job to one house skill with provenance (source, path, pinned commit, mode adopt|adapt|merge|own|drop). One router skill. skills-sync back-imports upstream ideas as beads. Decided 2026-10-15: repurpose ~/dev/utils/skills; core flow first; track in beads.
