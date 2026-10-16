---
name: principles
description: Index of 17 one-rule engineering principles. Use when making or reviewing a nontrivial design or implementation decision, or when the user names a principle or asks which one applies.
---

<!-- house: merge; from: pstack:pstack/skills/principle-*@850d7f2 (17 kept; encode-lessons-in-structure and laziness-protocol restored from ea32d95, pre-#571). sk-81s.10: cut never-block-on-the-human, exhaust-the-design-space, guard-the-context-window; prove-it-works -> verify-before-claiming, fix-root-causes -> diagnosing-bugs, test-behavior-not-implementation -> tdd/references, subtract-before-you-add -> laziness-protocol. -->

# Principles

Match the decision to the lines below. Before you apply or cite a principle, read `references/<name>.md` in full. Cite only principles you read this session. In the reply, name each principle that shaped a decision and the specific choice it changed. When the user steers by name ("apply laziness protocol"), load that file. For done-claims use `verify-before-claiming`; for debugging, `diagnosing-bugs`; for test quality, `tdd`.

**Core**

- `laziness-protocol`: refactoring, sizing a diff, sequencing an addition, tempted to add layers or thread a signal → delete first, remove dead weight before building, smallest change that works.
- `foundational-thinking`: before writing logic → data shapes and scaffold first, ask what concurrent actors share.
- `redesign-from-first-principles`: integrating a new requirement → redesign as if it were there from day one, don't bolt on.
- `attack-the-premise`: two+ fixes sharing one premise failed the same gate → write the premise down, census the actors, question it.
- `minimize-reader-load`: code is hard to trace → count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.
- `outcome-oriented-execution`: planned rewrite or migration with phase boundaries → converge on the target, no throwaway compat states.
- `experience-first`: product, UX, or scope tradeoff → user delight over implementation convenience, fewer polished features.
- `build-the-lever`: any nontrivial edit, migration, analysis, or check → build the script or codemod that does or proves it.

**Architecture**

- `model-the-domain`: stateful logic, heavy branching, repeated shape assumptions → encode the domain in a structure, not conditionals.
- `boundary-discipline`: wiring validation, errors, adapters → guards at system boundaries, trust internal types, pure core.
- `type-system-discipline`: designing types or signatures → illegal states unrepresentable, brand primitives, no lying casts.
- `make-operations-idempotent`: commands or loops that face crashes and retries → converge to one end state on rerun.
- `migrate-callers-then-delete-legacy-apis`: new internal API with old callers → migrate and delete in the same wave.
- `separate-before-serializing-shared-state`: concurrent writers to one file, branch, or key → eliminate sharing before locking.

**Verification**

- `sequence-verifiable-units`: multi-step work, commit and PR stacking → small units each ending green, ordered as proof.
- `explain-the-number`: trusting or reporting a measured number → name the limiter, rule out what else it measured.

**Meta**

- `encode-lessons-in-structure`: writing the same instruction twice → make it a lint, check, flag, or script instead.
