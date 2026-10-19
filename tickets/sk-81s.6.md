---
id: sk-81s.6
title: "skills-sync: back-import upstream ideas (script + skill)"
type: task
status: closed
priority: 1
parent: sk-81s
blocked_by: ["sk-81s.2"]
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: 2026-10-16
close_reason: "scripts/sync.py + skills/skills-sync. Test 1 (current pins, fetched): mattpocock/superpowers unchanged; pstack 850d7f2..2f83774 has 2 real in-scope commits (#633,#634) -> 6 candidates (5 merge digests, correct adopt). Test 2 (temp catalog, mattpocock pin 49dd158~5): 5 commits, diagnosing-bugs/code-review digests, wizard re-vendor. --bump verified on temp catalog (+bad commit/source errors); unmapped verified via temp catalog missing a drop; --file-beads verified against a fake bd (no real beads). Report: drafts/sessions/house-sync.md"
---

Fetch each source, diff pinned..HEAD. Adopted skills: propose pin bump. Adapted/merged: per-skill upstream diff digest + agent summary of new ideas vs house version. New upstream skills: unmapped list. File one bead per candidate idea (adopt/adapt/drop), write reports/YYYY-MM-DD.md, bump pins after decisions.
