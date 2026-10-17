---
name: lessons
description: "Use when the user corrects you, says something you did or claimed was wrong, or repeats an instruction you missed; turns the correction into a prevention and a lesson bead."
---

<!-- house: own; moved from the Lessons section of verify-before-claiming (2026-10-16) so it triggers on corrections, not on done-claims -->

# Lessons

Every user correction is a lesson. Fix what the user pointed at first, then run these steps before your next task. If the user changed their mind rather than caught a mistake, it is not a lesson: skip them.

1. **Name it** in one line: what you did, what the user wanted, and what made the wrong move look right.
2. **Check for a repeat:** `bd search "<key word>" -l lesson`, and grep the local `AGENTS.md` and the skill that applied. A rule that already existed and did not stop you means guidance is too weak here: start the next step one rung higher than that rule.
3. **Pick the highest rung that stops a repeat:**
   1. **Impossible**: change code, types, or data structures so the mistake cannot be written.
   2. **Static analysis**: a lint, compiler check, CI gate, or hook whose error names the fix.
   3. **Guidance**: a rule in `AGENTS.md` or a skill edit (`writing-for-agents`).
   4. **Human review**: only when nothing above can catch it.
4. **Act:** make the change now if it is in the current task's scope; otherwise file a follow-up bead for it.
5. **Record** in the repo the prevention lands in (the current repo when it has no `.beads`):
   `bd create "<mistake> -> <prevention>" -l lesson -d "rung <n>: <change or follow-up id>"`.

Done when the lesson bead exists and you have told the user, in one line, the rung and the change or follow-up id. No `.beads` anywhere reachable: tell the user the lesson line instead and ask where it should live.

For a repo-wide sweep of repeated mistakes, the user runs `correct`.
