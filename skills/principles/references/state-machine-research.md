# State machines: per-stack picks and the house shape

> Research notes behind [state-machine-skeleton](state-machine-skeleton.md) (2026-10-16). The "Left to decide" items were decided there.

Research for the AGENTS.md rule "complex state → state machine skeleton". Checked 2026-10-16 against hex.pm, npm, GitHub and the official docs listed under Sources.

## Recommendation

| Stack | Pick | Why |
|---|---|---|
| **Elixir / Phoenix / LiveView** | **Roll our own pure transition table** (`transition/3` returns effects as data). Use OTP **`:gen_statem` directly** as the process runtime when a long-lived process needs state timeouts, postpone or enter calls. Use GenServer, LiveView or Ecto adapters otherwise. | gen_statem is in OTP and maintained with it, and it already returns actions as data. Its weakness is that transitions are spread across function clauses, so no single place shows the whole machine. A pure table fixes that and needs no process. Every Hex library considered is stale, tied to Ecto, tied to Ash, or forces a GenServer model (details below). |
| **Lua 5.1 (WoW addons)** | **Roll our own table-driven machine**: a rows table plus a pure `Step` function, with effects returned as a list. Validate it in a busted spec and at load time in dev. | It matches the addon AGENTS.md rules: plain data tables, module-scope pure functions, `Resolve.lua`-style pure decisions tested offline with busted. `lua-state-machine` builds callback names from strings (`onenter<state>`), adds per-instance methods and has an ASYNC protocol. Those choices cut against the house style and make the code hard to grep. |
| **C11 / Zig (form-engine)** | **Roll our own dense table**: `enum State`, `enum Event`, and `static const Cell table[STATE_COUNT][EVENT_COUNT]` holding a target, a guard id and effect ids. A pure `fsm_step()` writes effects into a fixed-capacity buffer the caller owns. Exhaustiveness is checked by `_Static_assert`, a matrix test and `-Wswitch-enum`. If the module is written in Zig, the same shape uses `std.EnumArray` plus a comptime validator. | It is sans-IO, deterministic and statically allocated, and stays inside the C ABI, which fits TigerStyle ("centralize control flow… keep leaf functions pure"). QP/C is a GPL/commercial active-object RTOS framework, far more than this needs. zigfsm is solid but Zig-only and has no guards or effects as data. SMC targets OO State patterns. |
| **TypeScript** | **No pick needed now.** The only TS in `~/dev/utils` is in third-party clones (`sandcastle`, `gascity`, `cursor-plugins`). If an owned TS app appears, use **XState v5** (5.33.2, active). | It is the only TS option with statecharts, actors, a visual editor and model-based testing. Zag (1.46.0) is for UI components, and robot3 (1.4.0) is a tiny functional FSM. |

**Statechart features (short version):** use flat machines plus guards, entry/exit effects and state timeouts. Write hierarchy only as `from: [a, b]` group rows. Get parallelism by running separate small machines side by side. Avoid history states and deep nesting.

### Left to decide

1. **Where the Elixir house module lives.** Options: copy about 120 lines into each repo, or a shared path/git dep (for example `utils/fsm_ex`). Rule 2 ("don't over-abstract") suggests copying until a second repo actually uses it, then extracting. The validator macro is the part worth sharing.
2. **Process runtime default for Elixir.** Should `:gen_statem` be mandatory for every process-backed machine, or only when timeouts or postpone are needed? (Suggested: only when needed. A GenServer that calls the pure table is fine otherwise.)
3. **Finitomata as an alternative.** It is the only Elixir library whose *source of truth is a Mermaid diagram* with compile-time validation and a property-test generator. It is single-maintainer, at 1.0.0-rc.0 since 2026-08-01, and every machine is a GenServer. Worth a prototype if writing our own validator feels like reinvention.
4. **Lua: shared lib vs per-addon copy.** ui-o-matic is a monolith, so one `core/Fsm.lua` is likely enough.
5. **Whether rendered diagrams are committed** (with a CI "regenerated diagram differs" check) or only generated on demand. Committed gives reviewers and agents a picture inside the PR.
6. **Enforcement layer:** hook vs CI vs test-only for the "status field without a transition table" lint (see Static checks).

---

## 1. Options per stack

### Elixir

| Option | Version / last release | Status | Verdict |
|---|---|---|---|
| `:gen_statem` (OTP stdlib) | ships with OTP 28 (agent-hub runs erlang 28.4.2 / elixir 1.19.5) | maintained with OTP | **Runtime of choice** for process machines. It has `state_timeout`, named timeouts, `postpone`, `state_enter`, and actions returned as a list. The OTP guide: "For simple state machines not needing these features, gen_server is perfectly suitable." |
| GenStateMachine | 3.0.0, 2020-10-26 | idle (last push 2024-06) | Skip. A thin wrapper that adds nothing over `@behaviour :gen_statem` in modern Elixir. |
| Machinery | 1.1.0, 2023-04-04 | idle (push 2024-05) | Skip. A from→to map on structs plus a dashboard. Stale. |
| Fsmx | 0.5.0, 2023-08-09 | idle (push 2023-09) | Skip, but borrow ideas: `transition_changeset` and `Ecto.Multi` integration, `before_transition` that can reject. Its README warns that `after_transition_multi` "still runs inside the database transaction" and side effects can't be rolled back. Same lesson: effects belong *after* commit. |
| AshStateMachine | 0.2.13, 2026-04-13 | active | N/A. "The extension for building state machines with Ash resources". None of our repos use Ash. |
| Finitomata | 1.0.0-rc.0 / 0.43.0, 2026-08-01 | active, single maintainer | Closest to our goals. Mermaid/PlantUML text *is* the FSM, validated at compile time ("has a single initial state, one or more final states, and no orphan states"). Ships `Finitomata.ExUnit` with `event_generator/1` for property fuzzing and `mix finitomata.generate.test`. Cost: each FSM is a GenServer, the callback surface is large (`on_transition/4`, `on_enter`, `on_exit`, `on_timer`, `on_failure`, `on_rollback`), and event-name suffixes (`!`, `?`) carry meaning. |
| Protean | 0.1.0, 2022-11 | abandoned | Skip. Was an XState-style statechart port. |

**LiveView-side pattern.** LiveView has no FSM primitive. Keep the machine state in an assign (`@step`) and route every `handle_event` through the pure `transition/3`. Effects come back as data (`{:push_patch, …}`, `{:persist, …}`, `{:send_after, …}`), and one small interpreter applies them to the socket. A wizard then reads as a table, and the LiveView module holds only rendering and plumbing.

**Existing code worth learning from:**
- `utils/agent-hub/lib/hub/fleet/worker.ex` + `workers.ex`: `@states ~w(idle working drained needs_attention)` with `validate_inclusion`. `set_state/2` accepts **any** target from **any** state and emits a `worker.state_changed` event. This is the exact gap a table closes: `(from, event) → to` validation, with the emitted event as an effect. `tasks/task.ex` has the same shape (`open in_progress done abandoned`).
- `music/waveform/lib/waveform/midi/clock.ex`: master and slave modes share one `State` struct with nullable fields (`master_timer`, `slave_port`, `running`), so the mode is implied by which fields are set. It is a natural `gen_statem` candidate: `stopped | master | slave` as the state, and the tick timer as a named timeout.
- `games/gw2` uses status atoms (`:done`, `:in_progress`, `:available`) as derived values, not lifecycles. It doesn't need a machine.

### Lua 5.1 (WoW)

| Option | Version | Status | Verdict |
|---|---|---|---|
| kyleconroy/lua-state-machine | rockspec 1.0.0, no tagged releases, last push 2025-06 | low activity | Skip. Events `{name, from, to}` are nice data, but behaviour hangs off string-concatenated callback names (`onbefore<event>`, `onleave<state>`, `onenter<state>`, `onafter<event>`), adds generated methods `fsm:<event>()`, and an `ASYNC` defer protocol. You can't grep from a state name to its handler, and it's method-bag OO. |
| Table-driven own | – | – | **Pick.** Fits the house rules: "Bars/elements are plain data tables; functions operate on them", `Resolve.lua` pure decisions "busted-testable without WoW", and `.luacheckrc` plus busted pinned to Lua 5.1 in CI. |

**Existing code worth learning from:** `ui-o-matic/modules/cooldowns/retail/RegionEditor.lua` tracks `state.active`, `state.built`, `state.drag`, `state.hoverRegion` as independent flags, so impossible combinations (dragging while inactive) are representable and get cleared by hand (`if state.drag then state.drag = nil end`). It is a good first conversion: `closed → editing → dragging`, with combat lockdown as a guard. The addon rule "Discover state from events; render from timestamps" already matches the step/effect split: events drive `Step`, and renderers read state.

### C11 / Zig (form-engine)

| Option | Version | Status | Verdict |
|---|---|---|---|
| Dense table, own | – | – | **Pick.** Sans-IO, static, exhaustive by construction. |
| cryptocode/zigfsm | pushed 2026-04 | active | Good library: "Never allocates", comptime `StateMachineFromTable`, Graphviz import/export, supports "Zig 0.16 all the way down to Zig 0.12.x" (we use 0.15). It is Zig-only (not usable from the C11 core), handles transitions only (handlers are callbacks that can cancel), and has no guard or effect data. Borrow the ideas (comptime import, DOT export). Don't take the dependency. |
| Quantum Leaps QP/C + QM | qpc pushed 2026-10-13 | active | Skip. A full active-object RTOS framework, dual GPL/commercial. Its fastest QMsm strategy "requires the use of the QM Model-Based Design tool" and is not hand-maintainable. Too much for one sans-IO core. |
| SMC (State Machine Compiler, Rapp) | old, SourceForge | dormant | Skip. Generates OO State-pattern classes. Java toolchain. |

The form-engine repo has no code yet (beads epic `fe-lwp`: Launchkey driver `fe-lwp.4`, MIDI probe `fe-lwp.3`), so the shape can be set before the first machine exists.

### TypeScript (for completeness)

XState v5 5.33.2 (published 2026-09-15, very active), @zag-js/core 1.46.0, robot3 1.4.0. We have no owned TS code, so nothing to decide.

---

## 2. Flat FSM vs statecharts

Statecharts (Harel 1987) add hierarchy, orthogonality (parallel regions) and broadcast to FSMs to fight state explosion. SCXML standardises them, adding history and entry/exit semantics. What earns its place here:

| Feature | Verdict | How we express it |
|---|---|---|
| Guards | **Keep.** Essential. | A named pure predicate referenced by id in the row (`guard: :in_combat?`), never an inline lambda. An agent can list every guard. |
| Entry/exit actions | **Keep.** | An effect list on the state (`enter: [...]`, `exit: [...]`), concatenated by `step` as exit ++ transition ++ enter. gen_statem has `state_enter`. |
| Delayed / `after` events, state timeouts | **Keep.** Common in MIDI and lifecycles. | An effect `{:arm_timeout, name, ms}`. The runtime turns it into a `:timeout` event (`state_timeout` in gen_statem, `C_Timer.NewTimer` in Lua, a scheduler tick in C). The timeout is still a row in the table. |
| Hierarchy (nested states) | **Limited.** One level only. | Group rows: `from: [:a, :b, :c]` or `from: :any` for shared exits ("Esc cancels from any capture step"). Deeper nesting makes "what happens on event E in state S" depend on walking ancestors, which hurts both human and agent reading. |
| Parallel regions | **Avoid inside one machine.** | Run **separate small machines side by side** (pad-mode machine, capture-flow machine). Stately's own guidance: parallel regions suit "related but independent concerns", and you should "avoid transitions between regions". Separate machines enforce that. |
| History states | **Avoid.** | Store it explicitly in data (`return_to: :session`) and transition to it. Invisible implicit memory is the worst readability offender. |
| Extended state in data vs state | Rule from the OTP guide | "If a change in the value changes the set of events that is handled, the value should be in the State." Everything else is data. |

---

## 3. The house shape

One shape in every language:

```
rows:   [ {from, event, guard?, to, effects[]} ... ]      -- data, one place
states: [ {name, enter?[], exit?[], final?} ... ]
step(state, event, ctx) -> {next_state, effects[]} | :ignored | :invalid   -- pure
run(effects)  -- the only place IO happens (adapter: gen_statem / LiveView / WoW frames / C shell)
```

Rules:
1. **One table per machine, one file.** Behaviour is a row. Logic lives in named guards and named effects, never in the table.
2. **`step` is pure and total.** Every `(state, event)` resolves to a row, an explicit `ignore` row, or `:invalid`. `ignore` must be written down. Silence is a lint error.
3. **Effects are data.** `step` returns `[{:notify, …}, {:arm_timeout, …}]`. The adapter executes them after commit. This is the gen_statem actions-list idea and the sans-IO idea, and it keeps `step` testable with no process, no WoW and no MIDI.
4. **Guards are pure predicates of `(data, event)`**, referenced by name. Rows with the same `(from, event)` are tried in order, and the last one should be unguarded (or the validator flags non-exhaustive guards).
5. **Render from the table.** `to_mermaid(machine)` generates `stateDiagram-v2` text (`A --> B: event [guard] / effects`). Optionally commit the output and fail CI if regenerating it changes the file.
6. **Test from the table** (see Static checks): a matrix golden test, a reachability test and property tests over random event sequences.

How agents edit it safely: the table is the spec, so an agent changing behaviour changes a row, and the golden matrix and diagram diff show exactly what moved. The rule for the AGENTS.md line: *"To change state behaviour, edit the table and its golden matrix in the same change. Never add a state check (`if state == …`) outside `step`."*

### Elixir example: agent-hub worker lifecycle

```elixir
defmodule Hub.Fleet.WorkerMachine do
  use Hub.Fsm   # house macro: compile-time validation + to_mermaid/0 + transition/3

  initial :idle
  state :idle
  state :working
  state :drained, final: true
  state :needs_attention

  #     from                      event          guard              to                 effects
  row   :idle,                    :assign,       nil,               :working,          [:emit_changed]
  row   :working,                 :finish,       :queue_empty?,     :idle,             [:emit_changed]
  row   :working,                 :finish,       nil,               :working,          [:pull_next]
  row   [:idle, :working],        :drain,        nil,               :drained,          [:emit_changed]
  row   :working,                 :stuck,        nil,               :needs_attention,  [:emit_changed, :notify_operator]
  row   :needs_attention,         :resume,       nil,               :working,          [:emit_changed]
  ignore :drained,                :any

  def queue_empty?(data, _event), do: data.queue == []
end

# Pure:
{:ok, :drained, effects} = WorkerMachine.transition(:working, :drain, data)
# Adapter (Workers.set_state/2 becomes Workers.dispatch/2): changeset → Repo.update → run effects after commit.
```

`Hub.Fsm` would be about 120 lines: `row/5` accumulates into a module attribute, and `@before_compile` validates (section 4) and defines `transition/3` as a lookup over the rows. Process machines (waveform's MIDI clock) use `@behaviour :gen_statem` with `callback_mode() :: [:handle_event_function, :state_enter]`, and `handle_event/4` just calls `transition/3` and maps effects to gen_statem actions (`{:state_timeout, …}`, `{:reply, …}`).

### Lua 5.1 example: ui-o-matic region editor mode

```lua
-- modules/cooldowns/retail/RegionEditorMachine.lua
local M = {}

M.initial = "closed"
M.states = { closed = {}, editing = { enter = { "ShowOverlay" }, exit = { "HideOverlay" } }, dragging = {} }

--          from                       event            guard            to          effects
M.rows = {
  { from = "closed",   event = "TOGGLE",       guard = "NotInCombat", to = "editing",  fx = {} },
  { from = "editing",  event = "TOGGLE",                              to = "closed",   fx = { "SaveLayout" } },
  { from = "editing",  event = "DRAG_START",                          to = "dragging", fx = { "BeginProxy" } },
  { from = "dragging", event = "DRAG_STOP",                           to = "editing",  fx = { "CommitDrop" } },
  { from = { "editing", "dragging" }, event = "COMBAT_START",         to = "closed",   fx = { "CancelDrag", "SaveLayout" } },
  { from = "closed",   event = "COMBAT_START", ignore = true },
}

M.guards = { NotInCombat = function(ctx) return not ctx.inCombat end }

return M
```

```lua
-- core/Fsm.lua (shared, pure, Lua 5.1, no metatables)
local function matches(from, s) if type(from) == "table" then for i = 1, #from do if from[i] == s then return true end end return false end return from == s end

local function Step(machine, state, event, ctx)
  for i = 1, #machine.rows do
    local r = machine.rows[i]
    if r.event == event and matches(r.from, state) then
      if r.ignore then return state, nil end
      if not r.guard or machine.guards[r.guard](ctx) then
        local fx = {}
        if r.to ~= state then for _, e in ipairs((machine.states[state].exit) or {}) do fx[#fx+1] = e end end
        for _, e in ipairs(r.fx) do fx[#fx+1] = e end
        if r.to ~= state then for _, e in ipairs((machine.states[r.to].enter) or {}) do fx[#fx+1] = e end end
        return r.to, fx
      end
    end
  end
  return nil, "invalid"   -- unhandled: caller asserts in dev builds
end
```

The frame code keeps one `state.mode` string, calls `Step` from event handlers, and runs effect names through a `Effects[name](ctx)` dispatch table. The busted spec loads the machine file offline and runs the validator plus the matrix golden.

### C11 example: Launchkey pad-mode machine (form-engine)

Illustrative only. Real Launchkey MK4 modes and messages come from the Novation programmer's reference during `fe-lwp.4`.

```c
/* launchkey_mode.h — pure, sans-IO */
typedef enum { LK_OFF, LK_DAW_PLAY, LK_FREEZE_PICK, LK_REROLL_PICK, LK_CAPTURE_ARMED, LK_STATE_COUNT } LkState;
typedef enum { EV_CONNECT, EV_DISCONNECT, EV_FREEZE_BTN, EV_REROLL_BTN, EV_CAPTURE_BTN,
               EV_PAD, EV_CANCEL, EV_TIMEOUT, LK_EVENT_COUNT } LkEvent;
typedef enum { FX_NONE, FX_ENTER_DAW_MODE, FX_LIGHT_PICK_PADS, FX_LIGHT_PLAY_PADS, FX_FREEZE_CELL,
               FX_REROLL_CELL, FX_ARM_TIMEOUT, FX_START_TAKE, FX_STOP_TAKE, FX_OLED_TEXT, FX_COUNT } LkEffect;
typedef enum { G_NONE, G_PAD_HAS_CELL, G_COUNT } LkGuard;

#define LK_FX_MAX 4
typedef struct { uint8_t target; uint8_t guard; uint8_t fx[LK_FX_MAX]; uint8_t defined; } LkCell;

/* launchkey_mode.c */
#define T(to, g, ...) { .target = (to), .guard = (g), .fx = { __VA_ARGS__ }, .defined = 1 }
#define IGNORE(s)     { .target = (s), .guard = G_NONE, .fx = { FX_NONE }, .defined = 1 }

static const LkCell lk_table[LK_STATE_COUNT][LK_EVENT_COUNT] = {
  [LK_OFF] = {
    [EV_CONNECT]    = T(LK_DAW_PLAY, G_NONE, FX_ENTER_DAW_MODE, FX_LIGHT_PLAY_PADS),
    [EV_DISCONNECT] = IGNORE(LK_OFF), [EV_FREEZE_BTN] = IGNORE(LK_OFF), [EV_REROLL_BTN] = IGNORE(LK_OFF),
    [EV_CAPTURE_BTN]= IGNORE(LK_OFF), [EV_PAD] = IGNORE(LK_OFF), [EV_CANCEL] = IGNORE(LK_OFF), [EV_TIMEOUT] = IGNORE(LK_OFF),
  },
  [LK_DAW_PLAY] = {
    [EV_FREEZE_BTN] = T(LK_FREEZE_PICK, G_NONE, FX_LIGHT_PICK_PADS, FX_OLED_TEXT, FX_ARM_TIMEOUT),
    [EV_REROLL_BTN] = T(LK_REROLL_PICK, G_NONE, FX_LIGHT_PICK_PADS, FX_OLED_TEXT, FX_ARM_TIMEOUT),
    [EV_CAPTURE_BTN]= T(LK_CAPTURE_ARMED, G_NONE, FX_START_TAKE, FX_OLED_TEXT),
    /* ... every other event explicitly IGNORE or T ... */
  },
  [LK_FREEZE_PICK] = {
    [EV_PAD]     = T(LK_DAW_PLAY, G_PAD_HAS_CELL, FX_FREEZE_CELL, FX_LIGHT_PLAY_PADS),
    [EV_CANCEL]  = T(LK_DAW_PLAY, G_NONE, FX_LIGHT_PLAY_PADS),
    [EV_TIMEOUT] = T(LK_DAW_PLAY, G_NONE, FX_LIGHT_PLAY_PADS),
    /* ... */
  },
  /* ... */
};
_Static_assert(LK_STATE_COUNT <= 255 && LK_EVENT_COUNT <= 255, "fits uint8_t");

typedef struct { LkEffect fx[LK_FX_MAX]; uint8_t count; } LkEffects;

/* Pure: returns next state; writes effects into caller-owned buffer. Never allocates. */
LkState lk_step(LkState s, LkEvent e, const LkCtx *ctx, LkEffects *out) {
  assert(s < LK_STATE_COUNT); assert(e < LK_EVENT_COUNT);
  const LkCell *c = &lk_table[s][e];
  assert(c->defined);                         /* negative space: no silent holes */
  out->count = 0;
  if (c->guard != G_NONE && !lk_guard(c->guard, ctx, e)) return s;
  for (int i = 0; i < LK_FX_MAX && c->fx[i] != FX_NONE; i++) out->fx[out->count++] = c->fx[i];
  assert(c->target < LK_STATE_COUNT);
  return (LkState)c->target;
}
```

Why a dense 2D array and not a sparse row list: every `(state, event)` cell must be written, so holes are a test failure (`defined == 0`). Lookup is O(1) on the real-time MIDI path, and the table is const data in `.rodata`. Guard and effect *execution* are a `switch` over the enum compiled with `-Wswitch-enum -Werror`, so adding an effect without handling it fails the build. Shift-held, pad-bank and transport each get **their own** small table (separate machines, not regions).

**Zig version (if the module moves to Zig):** `std.EnumArray(State, std.EnumArray(Event, Cell))` built at comptime, with a `comptime { validate(table); }` block that does the reachability and completeness checks as `@compileError`. That is the strongest static check on any of our stacks. Export through `extern fn lk_step(...) callconv(.c)` to keep the C ABI.

---

## 4. Static checks we can enforce

Ordered by the trust ladder (impossible → compile → test → lint → prose):

| Check | C11 | Zig | Elixir | Lua |
|---|---|---|---|---|
| Unknown state/event name in table | impossible (enums) | impossible | compile (`@before_compile` raises) | busted spec + dev load-time assert |
| **Unhandled (state, event)** (must be a row or explicit `ignore`) | matrix test over `defined` | `@compileError` | compile | spec |
| Unreachable state (BFS from initial over rows) | test | `@compileError` | compile | spec |
| Dead-end non-final state (no outgoing row) | test | `@compileError` | compile | spec |
| Ambiguous rows (same `from, event` with an unguarded row not last) | n/a (one cell) | n/a | compile | spec |
| Unknown guard/effect name | impossible (enum) + `-Wswitch-enum` | exhaustive `switch` | compile (`function_exported?` on guards; effect names checked against adapter's declared list) | spec |
| Effect not handled by runtime | `-Wswitch-enum -Werror` | exhaustive switch | adapter test runs every effect atom | spec iterates `Effects` table |
| Behaviour drift unnoticed | golden matrix file | golden matrix | golden matrix (`test/fsm/<name>.matrix`) | golden matrix |
| Invariants under random sequences | fuzz `lk_step` with random events, assert invariants | `std.testing.fuzz` | StreamData 1.4.0 (`check all events <- list_of(member_of(events))`) | seeded random loop in busted |
| State mutated outside `step` | grep lint (no `->mode =` outside fsm file) | same | Credo custom check / grep for `state:` writes outside the machine module's adapter | luacheck can't. Grep lint in CI for `state.mode =` |
| Diagram out of date | CI regenerate-and-diff | same | same (mix task) | same |

The **golden matrix** is the most useful single artefact for agents. It is a generated plain-text file with one line per `(state, event) → outcome [guard] / effects`, checked in. Any behaviour change shows up as a reviewable diff, and an agent asked "what happens when X in Y" reads one line.

A cross-repo lint worth a hook or CI step: flag new `@statuses ~w(...)`/`Ecto.Enum` status fields, or new `state = "..."` string assignments, in modules that have no adjacent machine table. It is cheap with ripgrep, and it turns the AGENTS.md prose rule into a caught mistake.

---

## Sources

- Erlang/OTP `gen_statem` reference: https://www.erlang.org/doc/apps/stdlib/gen_statem.html (callback modes, `state_enter`, `state_timeout`/named timeouts, `postpone`, actions list)
- Erlang/OTP design principles, gen_statem: https://www.erlang.org/doc/system/statem.html ("For simple state machines not needing these features, gen_server is perfectly suitable"; "If a change in the value changes the set of events that is handled, the value should be in the State")
- Hex API (versions/dates): https://hex.pm/api/packages/{gen_state_machine,machinery,fsmx,ash_state_machine,finitomata,protean,stream_data}
- GenStateMachine: https://github.com/ericentin/gen_state_machine
- Machinery: https://github.com/joaomdmoura/machinery
- Fsmx README: https://github.com/subvisual/fsmx
- AshStateMachine docs: https://ash-state-machine.hexdocs.pm/readme.html
- Finitomata docs: https://finitomata.hexdocs.pm/readme.html and repo https://github.com/am-kantox/finitomata
- lua-state-machine README: https://github.com/kyleconroy/lua-state-machine
- zigfsm README: https://github.com/cryptocode/zigfsm
- QP/C product page: https://www.state-machine.com/products/qp ; repo https://github.com/QuantumLeaps/qpc
- SMC: https://smc.sourceforge.net/
- TigerStyle: https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md ("Centralize control flow", "Keep leaf functions pure", "No memory may be dynamically allocated … after initialization", "tests must test exhaustively")
- Stately/XState parallel states: https://stately.ai/docs/parallel-states ; npm registry for xstate 5.33.2, @zag-js/core 1.46.0, robot3 1.4.0
- D. Harel, "Statecharts: A visual formalism for complex systems", *Science of Computer Programming* 8(3), 1987, https://doi.org/10.1016/0167-6423(87)90035-9
- W3C SCXML Recommendation (2015): https://www.w3.org/TR/scxml/
- Mermaid state diagrams: https://mermaid.js.org/syntax/stateDiagram.html
- GCC `-Wswitch-enum`: https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html
- Local: `~/dev/AGENTS.md` (Design preferences), `utils/agent-hub/lib/hub/fleet/{worker,workers}.ex`, `music/waveform/lib/waveform/midi/clock.ex`, `games/wow-addons/AGENTS.md`, `games/wow-addons/ui-o-matic/modules/cooldowns/retail/RegionEditor.lua`, `ui-o-matic/.github/workflows/check.yml`, form-engine beads `fe-lwp.*`
