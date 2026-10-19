---
id: sk-81s.10
title: "Decide principle cuts (24 -> ~18)"
type: decision
status: closed
priority: 2
parent: sk-81s
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: 2026-10-16
close_reason: "Cut never-block-on-the-human, exhaust-the-design-space, guard-the-context-window ([[drop]]); folded prove-it-works (process liveness) into verify-before-claiming, fix-root-causes (validate state on load) into diagnosing-bugs, subtract-before-you-add into laziness-protocol; moved test-behavior-not-implementation to tdd/references + linked; restored encode-lessons-in-structure and laziness-protocol from ea32d95 (diffed vs git show); index now 17 and matches references; all relinks resolve. check.py 0 errors."
---

From drafts/principles.md: cut never-block-on-the-human (conflicts with 'ask on ambiguous scope' and rundown->pushback), exhaust-the-design-space (covered by prototype + DESIGN-IT-TWICE), guard-the-context-window (one bullet at pin); fold prove-it-works into verify-before-claiming, fix-root-causes into diagnosing-bugs, subtract-before-you-add into laziness-protocol; move test-behavior-not-implementation into tdd references. Restore pre-08bd59b text for encode-lessons-in-structure and laziness-protocol. outcome-oriented-execution tension with 'don't break what works' (only declared migration breakage).
