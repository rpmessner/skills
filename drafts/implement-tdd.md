# Draft notes: implement + tdd

Pins: mattpocock 49dd158, superpowers bb92a77, pstack 850d7f2. User's fork `~/dev/utils/skills` implement/tdd are byte-identical to Matt upstream, so no separate "own" input.

Proposed catalog entries (not written; catalog.toml is out of scope for this draft):
- `implement`: job `implement`, mode `merge`, from mattpocock implement + implement-spec, superpowers executing-plans + subagent-driven-development (+ implementer-prompt.md) + dispatching-parallel-agents, pstack swarm.
- `tdd`: job `tdd`, mode `merge`, from mattpocock tdd (+ tests.md, mocking.md), superpowers test-driven-development (+ writing-good-tests.md), pstack tdd.
- Drops: superpowers `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents`, `test-driven-development`, Matt `implement-spec`, pstack `tdd`, `swarm`, `arena` (reasons below). `arena`/`swarm` may be claimed by another job group (prototype/research); check before writing `[[drop]]`.

## Matt: implement

TAKEN
- Ticket ref → fetch, state title; ambiguous → ask → implement "Before starting" 2.
- `tdd` at pre-agreed seams → per-ticket loop 2–3.
- Typecheck + single test often, full suite at the end → loop 3 (per ticket, not per session).
- `code-review` when done → loop 7 and Finish.

LEFT OUT
- "Commit your work to the current branch" unconditionally. Conflicts with the user's commits-only-when-asked rule; made conditional.

## Matt: implement-spec

TAKEN
- Tickets are a task graph with a frontier → "Frontier" (`bd ready`).
- Context pointers, not duplicated text → subagent brief carries bead id/spec path.
- Worktree per implementer, based on the integration branch, merge integration tip before reporting → Parallel tickets + parallel brief additions.
- Final code-review over the whole branch, fix in one pass → Finish.
- Clean up worktrees → Parallel tickets.

LEFT OUT
- `/setup-matt-pocock-skills` issue-tracker bootstrap: house tracker is beads.
- Max-concurrency-by-default: implementers in the background as fast as the frontier allows. House default is inline; parallel only for independent tickets, and pi-subagents requires operator authorization for any delegation.
- Separate merger subagent: the controller merges serially and reruns the suite. One less seat, same safety.
- Exploration subagent writing notes outside the repo: optional and adds a file-management convention; the user can ask for it ad hoc (or `research`).
- Draft-PR lifecycle: PRs are an outward side effect; left to the `pr` skill when asked.

## superpowers: executing-plans

TAKEN
- "Rulings, not stalls" with `Ruling: <what> — <why> — <cost if wrong>` → loop 4, recorded as bead notes.
- The four stop conditions → loop "Stop and ask only for", with "deploy to a live client" added for WoW.
- Ledger survives compaction; trust ledger + git log over memory → "Compaction" (beads is the ledger).
- Completion contract (tests named, ran, output read) → absorbed by `verify-before-claiming` + close-with-evidence.
- Final message lists every ruling and deferred minor, exhaustively → Finish report.
- Minors don't enter the fix pass; don't fix minors "while in there" → loop 7.
- Final-review fixes each need a failing test first → loop 7 and Finish.
- No subagent tool → inline, never fabricate a dispatch → Subagent mode intro.

LEFT OUT
- `.superpowers/sdd/` workspace, `progress.md` ledger, `task-start`/`task-done`/`task-brief`/`review-package` scripts. Beads + git already are the ledger; a second ledger would drift. Plan-file "Task N" heading extraction doesn't apply to beads.
- "Continuous execution, never check in". Mostly compatible (rulings are recorded), but the user's flow is rundown → pushback *before* executing; the approval gate covers that, so mid-run check-ins are only the four stops.
- Pre-flight conflict table across tasks. Useful but heavy; the rundown/pushback step and `bd` dependencies cover cross-ticket interfaces. Revisit if cross-ticket interface bugs show up.
- Re-grading reviewer severities by effect, "Declined to judge" list: belongs to `code-review` if anywhere.
- `finishing-a-development-branch`, `using-git-worktrees`: superpowers-only skills; outward git steps are ask-first here.
- Rationalization tables and DOT graphs: always-loaded bulk; the rules are stated directly.

## superpowers: subagent-driven-development (+ implementer-prompt.md)

TAKEN
- Fresh implementer per ticket, controller doesn't write code → Subagent mode.
- Brief = pointers + interfaces from earlier tasks + controller's ambiguity resolutions + report path; no pasted history → references/subagent-mode.md.
- Implementer never dispatches subagents (esp. reviewers) → brief rules.
- Status contract DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT, short reply + full report file, TDD RED/GREEN evidence → brief.
- BLOCKED means something must change; never retry identical brief → Subagent mode.
- "Over your head → escalate; bad work worse than no work" → brief.
- Resume original implementer for fixes; escalate to fresh + stronger model later → fix-round brief.
- Model selection, always name the model explicitly → "Model tier".
- Batch small same-shape work → Subagent mode.
- Never parallel implementers in one tree → "one writer per worktree".

LEFT OUT / CHANGED
- Separate task-reviewer and re-reviewer prompt templates. The house `code-review` skill is the review; the controller runs it on BASE..HEAD. Avoids a reviewer subagent that itself spawns code-review's parallel subagents (nested dispatch).
- 5-round fix cap → 3 rounds then rule/escalate. Simpler, and the escalation-to-stronger-model step still happens at round 3. Judgment call; flag for pushback.
- "Never dispatch parallel implementers" (absolute) → relaxed to independent tickets in separate worktrees, per Matt implement-spec. **Disagreement between sources**, resolved by requiring disjoint files + no blocking relation + commit permission.
- Bounded-wait / polling guidance: harness behaviour. pi notifies on async completion; Claude Code notifies on background agents. Not needed.
- "Turn count beats token price" detail: compressed into the tier line.

## superpowers: dispatching-parallel-agents

TAKEN
- Parallel only for independent domains with no shared state → Parallel tickets.
- Focused, self-contained briefs with explicit output → brief template.
- After return: check conflicts, run full suite → serial merge + suite after each merge.

LEFT OUT
- Standalone skill for parallel debugging of unrelated test failures. Not a separate house job; it's a mode of `implement` (tickets) or `diagnosing-bugs` (failures). Recommend `[[drop]]` with reason "folded into implement parallel mode".

## superpowers: test-driven-development (+ writing-good-tests.md)

TAKEN
- Watch it fail; fail for the right reason, not an error → RED.
- Minimal GREEN, no YAGNI options → GREEN.
- Fix code, not test → GREEN.
- Full project suite, not just your file; report failures you didn't cause; pristine output → loop end.
- Code-before-test → "Stash or revert", softened from "delete".
- Bug → failing reproduction test first → Bug fixes.
- Rationalizations → compressed "Red flags" line.
- Name-the-break gate, independent expectations, no change detectors, your-code-not-the-framework, mock-earns-no-assertions, learn side effects before mocking, mirror real data, specific doubles, test-only methods in helpers, mutation check, warning signs → RED + Good tests + references/good-tests.md.

LEFT OUT / CHANGED
- "Iron law, no exceptions without permission" and "delete means delete" absolutism. Kept test-first as the default and the skip as the user's call, but added pstack's "doesn't fit" branch. **Disagreement**: superpowers says always; pstack says only when cheap and requested; Matt says only at agreed seams. Resolved: default yes, at agreed seams; skip only for named reasons with an alternative executable check.
- REFACTOR as a loop phase. **Disagreement**: superpowers refactors after green; Matt says refactoring is not in the loop (belongs to review). Resolved as optional TIDY limited to code the slice touched, while green; anything wider goes to `code-review`/a new bead. Matches the user's no-"while I'm here" rule.
- TypeScript/jest examples → pseudocode; language-agnostic injection examples (behaviour/protocol, vtable/function pointer, Zig interface struct, Lua module param).
- "Fails, not errors" → made explicit for compiled languages: compile/link error or missing symbol is not RED; stub and re-run.
- `superpowers:writing-skills` pointer for testing docs: out of this job.

## Matt: tdd (+ tests.md, mocking.md)

TAKEN
- Behaviour through public interfaces; tests as spec → Good tests.
- Seams, confirmed with the user before any test, with catches/misses note → section 1.
- `codebase-design` for interface shape; GLOSSARY/ADR → section 1 / intro.
- Anti-patterns: implementation-coupled, tautological, horizontal slicing → RED, section 3, references.
- Vertical slices / tracer bullets → section 3.
- Mock at system boundaries; dependency injection; SDK-style per-operation functions → references.

LEFT OUT
- TS-specific examples; "Type safety per endpoint" bullet.

## pstack: tdd

TAKEN
- Skip when the test path is expensive/unclear; use closest executable check; "prefer no new test over a bad test" → section 2.
- Run the new test before fixing; must fail for the intended reason → RED / Bug fixes.
- Don't change tests to match wrong implementation; don't weaken assertions → Bug fixes.
- Flaky → deterministic, name the signal → Bug fixes.
- Report failing-before and passing-after evidence, or why not → Report.

LEFT OUT
- "Use only when explicitly asked" trigger. House tdd is model-invocable and the default under `implement`; the skip branch handles the cases pstack worried about.
- "Land focused regression, then consider sibling coverage": scope creep risk; sibling coverage is a new bead.

## pstack: swarm

TAKEN
- Every brief stands alone; PASS / ISSUES / BLOCKED with evidence; list every provable issue → parallel brief.
- Dropouts and missing evidence are gaps, not passes; respawn once → Parallel tickets.

LEFT OUT
- Cloud workers, `environment`, `cloud_base_branch`, model slugs from `~/.cursor/rules/pstack-models.mdc`, `subagent_type: generalPurpose`: Cursor-specific.
- Race shapes (first pass / rank all / best-of): not an implementation pattern for tickets; belongs to exploration/prototype if anywhere.
- Mandatory phase todolist: house tracks in beads.

## pstack: arena

LEFT OUT entirely from implement. Racing N candidates and grafting is design exploration ("one attempt would lock in the wrong shape"), not ticket execution, and costs N× implementations against a ticket that already passed pushback. Ideas worth keeping for a `prototype`/design job: a rubric fixed before fan-out, cross-family judge, graft by hand rather than paste, "wild divergence means the framing was under-specified". Also depends on pstack principle skills and Cursor model config.

## pstack: agents/poteto-agent.md

LEFT OUT. It is a pointer that makes a delegate load `poteto-mode` from `~/.cursor/plugins/`. The useful idea, a delegate reads the house playbook before working, is covered by the brief's "read first" list (bead, spec, repo AGENTS.md) and by `tdd` being named explicitly.

## Harness-specific bits neutralized

- "Call the Skill tool with X" (Matt) → "run the `X` skill".
- `Subagent (general-purpose)`, `model:` fields (superpowers), Task tool params, `run_in_background`, cloud env, Cursor model slugs (pstack) → "dispatch with the harness's subagent tool (Claude Code: Agent/Task; pi: `subagent`)", model named by tier.
- Harness todos / TodoWrite → beads.
- superpowers per-platform references (`using-superpowers/references/`) → not needed.
- pi-subagents' own rule (delegate only when the operator asked) is satisfied by making subagent mode opt-in.

## Open questions for pushback

1. Fix-round cap 3 vs superpowers' 5.
2. `implement` is `disable-model-invocation: true` (user-invoked, like Matt and tight-spec); `tdd` is model-invocable (costs ~60 always-on tokens). OK?
3. Parallel mode requires commit permission. Acceptable, or should parallel lanes leave uncommitted worktrees for the user to merge?
4. Should `dispatching-parallel-agents`' "parallel debugging of unrelated failures" land in `diagnosing-bugs` instead of being dropped?
