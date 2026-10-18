<!-- house: merge; from: mattpocock:skills/engineering/code-review@49dd158, pstack:pstack/agents/comment-sicko.md@850d7f2  ; house edit 2026-10-17: binding state-machine rule -->

# Standards baseline

Applies even when a repo documents nothing. Paste this whole file into the Standards brief.

Two binding rules:

- **The repo overrides.** A documented repo standard wins; where it endorses something below, suppress the flag.
- **Always judgement calls.** Each item is a labelled heuristic ("possible Feature Envy"), never a hard
  violation. Skip anything tooling already enforces.

## House rule: stateful features are built on a state machine (binding, not a heuristic)

The one exception to "always judgement calls" (user's standing rule; principle `state-machine-skeleton`).
Scope: workflows (lifecycles, multi-step flows, retries, sync and job pipelines), stateful UI (modes,
dialogs, wizards, input handling, anything that changes what it accepts), and program business-logic flow:
the code most likely to be hallucinated or drift, where a declared machine is the app's deterministic
skeleton. Those must be built on a declared machine: states, events, transitions, guards and effects as a
table or the stack's DSL (Zig kit, `Board.Fsm`, shared `Fsm.lua`), with a pure step that returns effects as
data and the behaviour hung off it. Report as **Important**:

- state tracked as booleans, status strings or nullable fields that a `case`/`if` cascade interprets, where
  a machine would declare it;
- a transition decided outside the machine (code that sets the state directly, or skips `step`);
- a new stateful feature with no machine, or a machine whose table misses a pair the code handles;
- effects performed inside the step instead of returned as data.

Not a finding: computation (numeric cores, parsers, formatters, pure transforms), plumbing and adapters,
a single flag with no transitions, or data that changes no handled event (show it as data, per the
principle).

## Smells (Fowler, *Refactoring* ch. 3): what it is → fix

- **Mysterious Name**: name doesn't reveal what it does or holds → rename; no honest name means murky design.
- **Duplicated Code**: same logic shape in more than one hunk or file → extract the shared shape.
- **Feature Envy**: a function reaches into another object's data more than its own → move it to the data.
- **Data Clumps**: the same few fields/params travel together → bundle into one type.
- **Primitive Obsession**: a primitive standing in for a domain concept → give it its own small type.
- **Repeated Switches**: same `switch`/`if`-cascade on the same type recurs → one map or polymorphism.
- **Shotgun Surgery**: one logical change forces scattered edits → gather what changes together.
- **Divergent Change**: one module edited for several unrelated reasons → split by reason to change.
- **Speculative Generality**: abstraction, params, or hooks the spec doesn't need → delete, inline back.
- **Message Chains**: long `a.b().c().d()` navigation → hide the walk behind one call.
- **Middle Man**: a function or class that mostly delegates → call the real target.
- **Refused Bequest**: an implementer ignoring most of what it inherits → composition instead.

Also flag a "universal" function merging cases that have individual behaviour: keep divergent cases separate
until a shared pattern is proven.

## Comments and suppressions in the diff

A comment survives only if it is one of:

- a legal/license header;
- non-obvious behaviour forced by something we cannot reshape (external dependency, platform, vendor, protocol);
- a doc comment defining a public API contract;
- an issue/RFC link explaining a constraint code cannot express;
- a formatter directive, or a lint suppression whose rule is style-only or wrong for this case.

Flag everything else that the diff adds: narration of what the next line does, banners, commented-out code, and
workaround justifications. A comment explaining a surprise in *our own* code is a refactor target: name the
symbol that should be renamed, extracted, or retyped so the comment becomes unnecessary. A long justification for
a workaround usually means the code is wrong. Suppressions of rules that catch real bugs (`@ts-ignore`,
`eslint-disable` on correctness rules, `# noqa` on undefined names, etc.) are findings, with the guilty symbol
named.

Flag, don't fix: the reviewer reports, the author changes code.
