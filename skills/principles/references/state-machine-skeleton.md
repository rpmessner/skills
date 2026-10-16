<!-- house: own (2026-10-16). Background, options per stack, examples and sources: state-machine-research.md. -->
# State Machine Skeleton

**When:** Apply when a feature has nontrivial state mechanics: modes, lifecycles, multi-step flows, retries, timeouts, controller or input handling. Also apply when you see a status field, a set of booleans that can combine illegally, or `if state == …` checks spread across code.

Design the feature as an explicit state machine first, declared as data, and hang the behaviour off it. The table is the spec: humans and agents read and change behaviour by reading and changing rows.

**Why:** Complex behaviour spread across conditionals can't be read in one place, allows impossible combinations, and changes silently. A table makes every transition visible, checkable, and diffable.

**Shape (every stack):**
- **One table per machine, one file.** Rows of `from, event, guard?, to, effects[]`; states may list `enter`/`exit` effects. Logic lives in named guards and effects, never in the table.
- **`step(state, event, ctx)` is pure and total.** It returns the next state plus effects as data, `ignored`, or `invalid`. Every `(state, event)` pair has a row or an explicit ignore; a gap is an error.
- **An adapter runs the effects.** It is the only place that touches IO (database, game client, MIDI, processes).
- **Render and test from the table.** Generate the diagram (Mermaid `stateDiagram-v2`) and a golden matrix (one line per pair); commit both, and fail the check if regenerating changes them. Add reachability and property tests over random event sequences.
- **Statechart features:** keep guards, entry/exit effects, and timeouts (an effect that arms a timer, plus a timeout row). Write hierarchy only as group rows (`from: [a, b]` or `any`). Parallel regions become separate small machines. No history states: store a `return_to` value in the data.
- **State vs data:** if a value changes which events are handled, it is state; otherwise it is data.
- **To change behaviour,** edit the table and its golden matrix in the same change. Never add a state check outside `step`.

**Per stack (build lazily: write a stack's helper the first time a buildout in that stack needs it, not before):**

| Stack | Pick |
|---|---|
| Elixir / Phoenix / LiveView | Own pure table plus a small validator macro (compile-time checks, generates `transition/3` and the diagram). Copy it into the repo that needs it; extract a shared lib only when a second repo uses it. Use OTP `:gen_statem` as the runtime only when a long-lived process needs state timeouts or postponed events; otherwise a GenServer, LiveView or Ecto adapter calls the pure table. No library (stale, Ecto/Ash-bound, or GenServer-per-machine). |
| Lua 5.1 (WoW addons) | Own rows table plus a pure `Step`, effects looked up by name; one shared `core/Fsm.lua` in ui-o-matic. Validate in busted specs and at load time in dev. |
| C11 / Zig (form-engine) | Own dense `const` table `[STATE_COUNT][EVENT_COUNT]` of cells (target, guard id, effect ids); pure `fsm_step()` writes effects into a caller-owned fixed buffer. Exhaustiveness via a matrix test, `-Wswitch-enum -Werror`, asserts. A Zig module uses `std.EnumArray` plus a comptime validator. |
| TypeScript | Only if an owned TS app appears: XState v5. |

**Enforcement:** the gaps above (unknown names, unhandled pairs, unreachable states, ambiguous rows, unhandled effects) are caught at compile time, build time, or in specs, per [Encode Lessons in Structure](encode-lessons-in-structure.md). A lint for new status fields or `state = "…"` assignments with no machine table nearby goes in the repo's existing test or precommit gate, not a global hook.

**Stop:**
- Do not write the state logic before the table exists and the user has seen it at design time.
- Do not build a stack's helper speculatively; the first buildout that needs it builds it.

Related: [Model the Domain](model-the-domain.md) (encode the domain in a structure), [Type-System Discipline](type-system-discipline.md) (illegal states unrepresentable), [Boundary Discipline](boundary-discipline.md) (pure core, effects at the edge).
