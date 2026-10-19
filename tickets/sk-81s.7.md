---
id: sk-81s.7
title: "Cutover: swap repos, relink, uninstall superpowers/pstack plugins and pi packages, verify both harnesses"
type: task
status: closed
priority: 1
parent: sk-81s
blocked_by: ["sk-81s.3","sk-81s.4","sk-81s.5","sk-81s.6"]
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: 2026-10-16
close_reason: "2026-10-16: repos swapped (house at ~/dev/utils/skills), link.py: 41 links per harness, 0 broken/non-house. Uninstalled superpowers + pstack (Claude Code) and removed pstack-local marketplace; pi remove superpowers + pstack (pi list: Jev packages only). pi check window: no using-superpowers/brainstorming/poteto-mode/unslop; all model-invocable house skills listed after quoting dispatch's description (new check.py rule). Global ~/dev/AGENTS.md skills line updated. Leftover dirs ~/dev/utils/cursor-plugins and Claude plugin caches await user deletion."
---

Move ~/dev/utils/skills -> skill-sources/mattpocock; move skills-house -> ~/dev/utils/skills; run link script; claude plugin uninstall superpowers@claude-plugins-official and pstack@pstack-local (+ remove pstack-local marketplace); pi remove superpowers and pstack packages (keep Jev extensions); verify skill lists in Claude Code and pi (pi needs /login). Ask user before editing ~/dev/AGENTS.md skill names (to-issues/to-prd etc.).

## Notes
pi trust.json is keyed by path: after moving skills-house -> ~/dev/utils/skills, add trust for the new path (remove the old key).
2026-10-16: old ~/dev/utils/skills deleted (only local content was tight-spec/verify-before-claiming originals; house versions are supersets). House repo moved to ~/dev/utils/skills; link.py --apply: 41 links in ~/.claude/skills and ~/.agents/skills, 0 broken, 0 non-house; pi trust.json key moved. Remaining: uninstall superpowers + pstack plugins (Claude Code) and pi packages, remove pstack-local marketplace, global AGENTS.md skill names (ask), verify pi.
