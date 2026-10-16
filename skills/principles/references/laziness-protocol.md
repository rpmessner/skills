<!-- from: pstack:pstack/skills/principle-laziness-protocol/SKILL.md@ea32d95 (pre-#571 body, restored; pin 850d7f2 has the cut version), plus the distinct lines of pstack:pstack/skills/principle-subtract-before-you-add/SKILL.md@850d7f2 (folded in as "Subtract before you add"). -->
# Laziness Protocol

**When:** Apply when refactoring, evaluating diff size, sequencing an addition, refactor, or rewrite, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem.

Aim for the most result with the least code and complexity.

- **Prefer deletion.** When asked to refactor or improve, look for removals before additions.
- **Maintain a flat call hierarchy.** Avoid deep call chains. A rich interface that hides substantial work is not a deep call chain. If answering a question requires tracing through more than 3 files or layers, flatten it.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
- **Question the threading.** If a task asks you to pass a new signal through types, schemas, pipelines, or similar layers, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread. Small leaks compound into permanent coordination costs.

**The test:** If a human developer would find the code exhausting to maintain, it is a bad solution.

## Subtract before you add

When evolving a system, remove complexity first, then build. Leave the design slightly simpler and more capable behind the same or smaller surface than you found it.

- Sequence removal before construction: dead code, redundant validators, and stub references go first, then build on the simpler base
- Cut before you polish (get to the minimum before investing in quality)
- Design for observed usage, not speculative edge cases
- No speculative validators, parsers, or guards beyond what the spec demands
- Simplify prompts (remove redundant instructions, excessive templates)
- When a reference has no novel content, delete it rather than leaving a stub
