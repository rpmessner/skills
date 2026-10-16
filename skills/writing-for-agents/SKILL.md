---
name: writing-for-agents
description: Write or edit documents agents read, such as skills, AGENTS.md or CLAUDE.md, prompts, and subagent briefs. Use when creating or editing a skill, changing AGENTS.md or CLAUDE.md, or checking whether guidance actually changes agent behavior.
---

<!-- house: merge; from: mattpocock:skills/productivity/writing-for-agents@49dd158, superpowers:skills/writing-skills@bb92a77 -->

# Writing for agents

A document an agent reads is a lever on its process, not its output: the same wording should send every run down the same path. Skills, `AGENTS.md` lines, prompts, and briefs follow the same rules; only the packaging differs.

Vocabulary used below (context pointer, the two loads, information hierarchy, completion criterion, leading word, sediment) is defined in [references/levers.md](references/levers.md). Read it before a non-trivial edit. When the document is a skill, also read [references/skill-mechanics.md](references/skill-mechanics.md).

## Steps

1. **Name the failure.** Say what agents do wrong today that this document should change. For behavior-shaping guidance, watch it happen first: run the tempting task without the guidance, in fresh context (a subagent or a raw call), 5+ reps, beside a no-guidance control. If the control does not fail, there is nothing to write: stop. Pure reference skips this; test retrieval instead. Method: [references/testing-skills.md](references/testing-skills.md).
2. **Pick the form that fits the failure.**

   | Baseline failure | Form |
   |---|---|
   | Knows the rule, skips it under pressure | Prohibition, a rationalization table, red flags |
   | Complies, but the output has the wrong shape | Positive recipe: what the output is, its parts, in order |
   | Omits a required element | A required slot in the template it fills in |
   | Behavior should depend on a condition | A conditional keyed to an observable predicate |

   Prohibitions backfire on shape problems: they put the banned behavior in context. No nuance clauses ("unless it matters"); state a real exception as its own conditional.
3. **Write the pointer.** The skill description or the `AGENTS.md` line decides when the material is reached. Front-load the leading word, one trigger per branch, triggers only, never a workflow summary.
4. **Place each piece.** In-file steps first, in-file reference next, disclosed reference behind a pointer. Inline what every branch needs; disclose what only some branches reach. Keep a concept's rules and caveats under one heading.
5. **End every step on a completion criterion** the agent can check, demanding enough to force the legwork ("every modified model accounted for", not "produce a list").
6. **Prune.** One source of truth per meaning. Do not restate what the environment answers in one lookup (`--help`, config, layout). Delete whole sentences that do not change behavior versus the default. Replace a spelled-out idea with a leading word where one exists.
7. **Prove it binds.** Rerun the step-1 scenarios with the document present. Reps that converge on one shape mean the wording binds; divergent reps mean tighten the form before adding words. A new rationalization gets an explicit counter, then rerun.

Report the baseline failure, the form chosen, and the before and after reps.
