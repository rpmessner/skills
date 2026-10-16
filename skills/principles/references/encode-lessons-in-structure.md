<!-- from: pstack:pstack/skills/principle-encode-lessons-in-structure/SKILL.md@ea32d95 (pre-#571 body, restored; pin 850d7f2 has the cut version). Edits: "brain note" -> `bd remember` (routing line) and "a note" (anti-pattern line). -->
# Encode Lessons in Structure

**When:** Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.

Encode recurring fixes in mechanisms (tools, code, metadata, automation) instead of textual instructions. Every error, human correction, and unexpected outcome is a learning signal. Capture it, route it, and close the loop.

Textual instructions are easy to miss. Structural mechanisms enforce the rule without cooperation.

**Pattern:**
When you catch yourself writing the same instruction a second time:
1. Ask: can this be a lint rule, a metadata flag, a runtime check, or a script?
2. If yes, encode it. Delete the instruction
3. If no (requires judgment), make the instruction more prominent and add an example of the failure mode

**Pick the strongest mechanism.** When more than one mechanism would work, choose the strongest the situation allows (an unrepresentable state that cannot compile, then a lint or banned API that fails CI, then a canonical helper, then a runtime check), because agents copy whatever the surrounding code already does and a weaker guard becomes the next template.

**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom.

When the human intervenes or tests fail, decide if it's a one-off or a pattern. Route it: one-off -> `bd remember`, recurring fix -> skill or lint rule, systemic issue -> principle. Close the loop: don't just record; apply now or create a concrete todo.

**Anti-patterns:**
- Acknowledging without recording ("I'll keep that in mind" does not persist)
- Recording without routing (a note about a lint rule that should exist is wasted unless the lint rule gets implemented)
- Fixing without generalizing (fixing one instance while leaving the recurring pattern intact)
