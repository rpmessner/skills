You are a build session in the house skill set repo (~/dev/utils/skills-house). A coordinator session (Claude Code, another tmux window) dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Read first
- AGENTS.md, catalog.toml, scripts/check.py.
- drafts/sessions/house-adopt.md (previous session's report, especially "Flagged for the coordinator").
- drafts/principles.md (principle-cut recommendations).
- Tickets: `bd show sk-81s.10`, `bd show sk-81s.12`, `bd show sk-81s.13`, `bd show sk-81s.3`. Claim each as you start it.

Sources (read-only): mattpocock ~/dev/utils/skill-sources/mattpocock-upstream (49dd158), superpowers ~/dev/utils/skill-sources/superpowers (bb92a77), pstack ~/dev/utils/skill-sources/cursor-plugins/pstack (850d7f2).

## Decisions already made by the user (apply them; do not re-ask)

### sk-81s.12 — pstack leftovers
- ADOPT `correct` (periodic sweep: make repeated agent mistakes impossible, highest rung first) and `benchmark-checklist`. Neutralize any Cursor-only bits (switch to adapt if needed). Fix principles/references/explain-the-number.md's "not in the house set" note to point at benchmark-checklist.
- DROP `architect` and `why` (catalog [[drop]] with reasons: covered by codebase-design / diagnosing-bugs; depend on pstack how/why/arena).
- Also add the missing [[drop]] entries recorded in drafts but not in the catalog: sharpen, figure-it-out (see drafts/spec-tickets.md), arena (see drafts/implement-tdd.md).

### sk-81s.13 — adapt skills that clash with the user's rules
User rules: agents never `git push` (hooks block it); commits and PRs only when the user asks; work is tracked in beads (`bd`), not GitHub issue labels.
- finishing-a-development-branch → mode adapt: options that push or open PRs become "only if the user asked; otherwise report the exact commands". Remove the "Superpowers" path naming.
- triage → mode adapt: beads-based (states as bead status/labels via `bd`), no `gh issue` workflow.
- maintain-verification-skill → its closing "one PR" becomes "a set of proven corrections reported to the user; commit/PR only if asked".
- `/setup-matt-pocock-skills` references (wayfinder, triage): replace with a one-line note that the tracker is beads (`bd`) and domain docs follow the repo's AGENTS.md; switch wayfinder to mode adapt and note the change. Also give wayfinder the beads specifics from drafts/spec-tickets.md (e.g., children need `--no-inherit-labels`).
Record every edit in the provenance comment and in your report.

### sk-81s.10 — principle cuts (apply the recommendations in drafts/principles.md)
- Cut never-block-on-the-human, exhaust-the-design-space, guard-the-context-window.
- Fold prove-it-works' distinct lines into verify-before-claiming, fix-root-causes' distinct parts into diagnosing-bugs, subtract-before-you-add into laziness-protocol; then remove those three reference files.
- Move test-behavior-not-implementation into skills/tdd/references/ and link it from tdd.
- Restore the pre-08bd59b text for encode-lessons-in-structure and laziness-protocol from pstack git history (`git -C ~/dev/utils/skill-sources/cursor-plugins log`/`show`; read-only).
- Update the principles index and every link that pointed at removed files.

### check.py rule
Add a check that every catalog `from` and `[[drop]].from` ref resolves under its source's path (globs allowed, e.g. principle-*). Write a negative test the way the scaffold did: plant a bad ref, see it fail, remove it.

### sk-81s.3 — router skill `flow`
Write skills/flow/SKILL.md (mode own, job router) replacing mattpocock ask-matt, superpowers using-superpowers and pstack poteto-mode as the single entry point. Read those three first for ideas. Content: the house flow and when each skill applies —
- New nontrivial work: tight-spec → user approval → to-tickets (beads) → rundown → user pushback → implement (tdd at seams, verify-before-claiming, code-review per ticket). Work too big for one session: wayfinder.
- Bugs: diagnosing-bugs. Design/architecture: codebase-design, improve-codebase-architecture, domain-modeling, principles. Prototypes: prototype. Research: research.
- Verification infrastructure: create-verification-skill / maintain-verification-skill. Corrections: Lessons in verify-before-claiming; periodic sweep: correct.
- Writing: writing-for-people, writing-for-agents. Git: using-git-worktrees, finishing-a-development-branch, pr. Context hand-off: handoff.
- Operating model: a coordinator Claude Code session dispatches build sessions as pi agents in named tmux windows (bin/pi-window); Claude subagents only when the user asks.
Description: one or two sentences that trigger at the start of nontrivial work or when unsure which skill applies. Keep the body a compact map, under ~60 lines.
When done, close sk-81s.3 if all its core skills exist and check.py passes.

## Rules
- No `scripts/link.py --apply`, no changes to ~/.claude or ~/.agents, no uninstalls, no commits, no pushes.
- `scripts/check.py` must end at 0 errors with the always-on budget held.
- Close each bead only with evidence.

## Report back
Write drafts/sessions/house-decide.md: what changed per ticket (tables), every edit to adopted/adapted copies, anything still open, final check.py output. Then print `HOUSE-DECIDE DONE` alone on the last line.
