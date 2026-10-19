---
id: sk-81s.2
title: "House repo scaffold: layout, catalog.toml schema, link script, checks, AGENTS.md"
type: task
status: closed
priority: 1
parent: sk-81s
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: 2026-10-15
close_reason: "Sources pinned; scaffold + check/link scripts in place (verified, negative test passes)"
---

skills/<name>/SKILL.md flat; provenance front-matter comment in adapted/merged skills; scripts/link.sh (only house skills into ~/.claude/skills and ~/.agents/skills, prunes broken links); checks: every skill has a catalog entry and vice versa, no name collisions, always-on description token budget, Agent Skills name rules (lowercase, name == dir). AGENTS.md canonical, CLAUDE.md symlink.

## Acceptance
make check (or scripts/check.sh) passes; link script dry-run lists exactly the house skills
