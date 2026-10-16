# Draft notes: `principles`

Source: pstack `pstack/skills/principle-*/SKILL.md` @ 850d7f2 (24 skills). Output: `skills/principles/SKILL.md` (index, model-invocable, ~45 always-on tokens) plus `skills/principles/references/<name>.md` (full text, loaded on demand). `catalog.toml` not touched. `scripts/check.py` fails only on "no catalog entry" for this skill.

Suggested catalog entry: `name = "principles"`, `job = "design-principles"`, `mode = "merge"`, `from = ["pstack:pstack/skills/principle-*"]`.

## Upstream state at the pin

Commit 08bd59b (#571, 2026-10-11, before the pin) cut the opening text from four principles because the always-loaded pstack description already carried the rule. At the pin these bodies are fragments:

- `encode-lessons-in-structure`: only the "if it needs judgment" fallback and the corollary are left. The main rule, "pick the strongest mechanism" ladder, and the routing/anti-pattern list are gone.
- `exhaust-the-design-space`: one sentence ("It also applies to product design...").
- `guard-the-context-window`: one bullet ("Size phases and cap scope").
- `laziness-protocol`: two bullets ("Consolidate decisions", "Minimize the diff").

The house skill does not load pstack descriptions until the reference is read, so each reference now starts with its upstream description as a `**When:**` line. That restores the thesis without importing pre-pin text. Decision for a bead: either keep pin-faithful text or restore the pre-#571 bodies (`git show 08bd59b^:pstack/skills/principle-<name>/SKILL.md`). I'd restore `encode-lessons-in-structure` (the mechanism ladder is the most useful part) and `laziness-protocol` (flat call hierarchy, question the threading). Leave the other two as they are or cut them (see below).

## Overlap with Matt / superpowers / house skills

| Principle | Overlaps | Verdict |
|---|---|---|
| prove-it-works | house `verify-before-claiming`, superpowers `verification-before-completion` | Same job. Keep the reference only for its two distinct points: "suspect the observation method before the system" and "script the check". Fold these into `verify-before-claiming` and cut this reference. |
| fix-root-causes | Matt `diagnosing-bugs`, superpowers `systematic-debugging` | The procedure belongs to diagnosing-bugs (feedback loop first). Unique bits: "restart bugs, suspect state before code", "fix the pattern not the instance", "propose the cheap always-on signal". Fold into `diagnosing-bugs`, then cut. |
| attack-the-premise | `systematic-debugging` "3+ failed fixes, question the architecture" | Keep. pstack's census-of-actors method is more concrete. |
| test-behavior-not-implementation | Matt `tdd` (tests.md, mocking.md), superpowers `test-driven-development` | Keep for now. Its "would it pass if every import returned undefined" check and the list of weak assertion shapes are sharper than either tdd. Better home is a reference inside the house `tdd`. |
| subtract-before-you-add, laziness-protocol | each other, `foundational-thinking` ("subtraction comes before scaffolding"), root AGENTS.md rule 2 (don't over-abstract) | Three principles state "delete first". Merge subtract-before-you-add into laziness-protocol. |
| minimize-reader-load | Matt `codebase-design` (deep vs shallow, interface depth) | Partial. codebase-design owns module/interface vocabulary. Reader load adds the "state to hold" axis and the 30-second test. Keep. |
| model-the-domain, type-system-discipline | each other ("illegal states unrepresentable"), Matt `domain-modeling` (which is about glossary/ADRs, not code shape) | No real overlap with domain-modeling despite the name. Keep both. |
| boundary-discipline | type-system-discipline ("parse at boundaries") | Mutual cross-reference upstream. Keep. |
| exhaust-the-design-space | Matt `prototype` (UI variants), `codebase-design/DESIGN-IT-TWICE.md` | Covered better elsewhere, and the pinned body is one sentence. Cut. |
| foundational-thinking, redesign-from-first-principles | superpowers `brainstorming`, `writing-plans` (weakly) | Keep. |
| sequence-verifiable-units | superpowers `executing-plans` / `subagent-driven-development` (task-by-task review) | Partial. Keep. The "failing test first, then fix" commit order fits the root AGENTS.md "granular commits per phase". |
| build-the-lever | none directly | Keep. |
| explain-the-number | none (pstack `benchmark-checklist` not taken) | Keep. Its link to benchmark-checklist dangles, see edits. |
| guard-the-context-window | superpowers `dispatching-parallel-agents` (isolated context), harness subagent defaults | Body is one bullet at the pin. Cut. |
| never-block-on-the-human | conflicts with root AGENTS.md: "On ambiguous scope, ask", "Plan → Linear → rundown → pushback" before executing | Cut. It contradicts the user's working agreement. Keeping it invites the agent to cite it against the user's own rule. |
| make-operations-idempotent, separate-before-serializing-shared-state, migrate-callers-then-delete-legacy-apis, experience-first | none | Keep. |
| outcome-oriented-execution | tension with root AGENTS.md rule 1 ("Don't break what works") | Keep. It covers declared, planned breakage inside a migration, not regressions. Note the scope if it is cited. |

**Recommended cuts (4):** never-block-on-the-human, exhaust-the-design-space, guard-the-context-window, and prove-it-works once its two unique lines live in `verify-before-claiming`. **Recommended merges (2):** subtract-before-you-add into laziness-protocol, fix-root-causes unique bits into `diagnosing-bugs`. With all of these, 18 principles remain. I left all 24 in the draft so the cuts are a reviewable diff.

## What came from poteto-mode / why / how / unslop

- From `poteto-mode/SKILL.md` "Non-negotiables" and "Principles": the citing discipline ("name each principle that shaped a decision and the specific choice it changed. Cite only principles whose leaf you read this session" and "read the leaf in full for any principle you apply"). It is reworded for the references layout. The category grouping (Core, Architecture, Verification, Delegation, Meta) is also taken from there.
- From `poteto-help/SKILL.md`: users steer by name ("apply prove it works"). This became the "load that file" line.
- `why`, `how`, `unslop`: no principle citations at the pin, and nothing taken. `poteto-mode/playbooks/eval.md` warns against asking eval candidates to list principles they applied. That is relevant only if this skill gets evals.
- Not taken: playbooks, autonomy rules, subagent/model routing, reply style.

## Every edit to the references

Generated by a deterministic script (regex substitutions, logged per file). All 24 files got:
1. Front matter removed (`name`, `description`, `disable-model-invocation`). The description is kept verbatim as a `**When:**` line under the title.
2. A provenance comment `<!-- from: pstack:pstack/skills/principle-<name>/SKILL.md@850d7f2 -->` added as line 1.

Body edits by file:
- attack-the-premise: 4 links `../principle-X/SKILL.md` → `X.md`.
- build-the-lever: 3 links rewritten the same way.
- explain-the-number: 1 link rewritten. `[benchmark-checklist](../benchmark-checklist/SKILL.md) skill` → "`benchmark-checklist` skill (pstack; not in the house set)".
- minimize-reader-load: 1 link rewritten.
- prove-it-works: "(the **show-me-your-work** skill)" → "(pstack's `show-me-your-work` skill; not in the house set)".
- sequence-verifiable-units: 2 × "the **X** principle skill" → "the [X](X.md) principle".
- type-system-discipline: 2 × "the **X** principle skill" → "the [X](X.md) principle". "see the `typescript-best-practices` skill." → "see pstack's `typescript-best-practices` skill (not in the house set)."
- The other 15 files: no body edits.

No Cursor-specific tool names or paths appeared in any principle body, so none were removed. All intra-reference links resolve. Open item: three dangling pstack skill references (benchmark-checklist, show-me-your-work, typescript-best-practices). Either take those skills or drop the sentences.
