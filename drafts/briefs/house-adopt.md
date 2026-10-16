You are a build session in the house skill set repo (~/dev/utils/skills-house). A coordinator session (Claude Code, in another tmux window) dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Read first
- AGENTS.md (repo rules: one skill per job, vendored adopted copies with provenance comment, low always-on cost).
- catalog.toml (manifest, source pins) and scripts/check.py (the gate).
- `bd show sk-81s.5` and `bd show sk-81s.11` — your two tickets. Claim both with `bd update <id> --claim`.

## Sources (read-only, pinned; never edit, never link into a harness)
- mattpocock: ~/dev/utils/skill-sources/mattpocock-upstream/skills/  (pin 49dd158)
- superpowers: ~/dev/utils/skill-sources/superpowers/skills/          (pin bb92a77)
- pstack: ~/dev/utils/skill-sources/cursor-plugins/pstack/skills/     (pin 850d7f2)
- User's current local-only skills (misc/personal) live in ~/dev/utils/skills/skills/ — read-only.

## sk-81s.5 — adopt as-is, merge writing, drop Cursor-only
1. ADOPT (vendored byte-identical copy of the whole skill dir, plus a provenance comment as the first body line `<!-- house: adopt; from: <source>:<path>@<short-pin> -->`):
   - mattpocock: engineering/codebase-design, engineering/improve-codebase-architecture, engineering/domain-modeling, engineering/prototype, engineering/research, engineering/pr, engineering/triage, productivity/grilling, productivity/handoff, productivity/teach.
   - superpowers: using-git-worktrees, finishing-a-development-branch.
   - user misc (source "own", mode own): git-guardrails-claude-code, setup-pre-commit, scaffold-exercises, migrate-to-shoehorn from ~/dev/utils/skills/skills/misc/.
   wayfinder (already in the house set) depends on grilling, domain-modeling, research, prototype — confirm its references resolve after adoption.
   If an adopted skill hard-codes another tracker or `git push` steps, do NOT edit it; list it in your report for the coordinator.
2. MERGE two writing skills (mode merge, provenance comment listing every source):
   - writing-for-people: pstack unslop + pstack technical-writing.
   - writing-for-agents: mattpocock productivity/writing-for-agents + superpowers writing-skills.
   Keep each SKILL.md tight; long material in references/.
3. DROP (catalog `[[drop]]` entries with a reason): pstack setup-pstack, typescript-best-practices, make-bot-ui, poteto-mode, poteto-help, bro, ketchup, and any other pstack skill whose job is already covered or that only works in Cursor. List every pstack skill you did not adopt or merge, with the reason.

## sk-81s.11 — verification skills, no-comments, lessons practice
1. ADOPT pstack create-verification-skill and maintain-verification-skill. Before copying, check them for Cursor-only paths/tools (.cursor/, cursor-team-kit, Task subagent_type, AskQuestion). If they depend on those, switch to mode adapt and neutralize them harness-neutrally (Claude Code + pi); note each change.
2. ADOPT pstack no-comments as-is (same Cursor check).
3. EDIT skills/verify-before-claiming/SKILL.md: add a short "Lessons" section — on every user correction, pick the highest trust-ladder rung that prevents a repeat (1 make it impossible in code/architecture, 2 static analysis/lint/CI, 3 rules/skills, 4 human review), make that change or file it, and record a bead labeled `lesson` naming the rung. Keep it under ~12 lines. Context: drafts/sources/poteto-michelin-kitchen-talk.txt (timestamps 15:00–18:40 and 36:00–37:10).

## Every skill you add
- `name:` equals the directory name (lowercase, hyphens). 1–2 sentence description with concrete triggers.
- One `[[skill]]` entry in catalog.toml (name, job, mode, from).
- Run `scripts/check.py` until it reports 0 errors and the always-on budget holds.

## Rules
- Do not run scripts/link.py --apply, do not touch ~/.claude or ~/.agents, do not uninstall anything, do not commit or push.
- Close each bead only with evidence (check.py output, list of files) using `bd close <id> --reason "..."`.

## Report back
Write drafts/sessions/house-adopt.md: skills adopted/merged/dropped (table), every edit made to an adopted copy, anything flagged for the coordinator, final check.py output. Then print exactly `HOUSE-ADOPT DONE` as your last line.
