# Spec + Tickets group — decisions

Pins: mattpocock 49dd158, superpowers bb92a77, pstack 850d7f2. Written:

- `skills/tight-spec/` (merge) — `SKILL.md`, `references/builder-check.md`
- `skills/to-tickets/` (adapt) — `SKILL.md`, `references/beads.md`
- `skills/wayfinder/` (adopt) — `SKILL.md` + `agents/openai.yaml`, byte-identical except the provenance comment

Flow: `tight-spec` → user approves spec → `to-tickets` → rundown → user pushback → publish to beads → stop.
`wayfinder` sits upstream of both for multi-session efforts with an unclear route.

## Needs action outside this group

1. **catalog.toml not edited** (as instructed), so `scripts/check.py` will fail on `to-tickets` and
   `wayfinder` ("no catalog entry"). Proposed entries:
   ```toml
   [[skill]]
   name = "tight-spec"
   job = "spec"
   mode = "merge"
   from = ["mattpocock:skills/engineering/to-spec", "mattpocock:skills/productivity/grilling",
           "mattpocock:skills/engineering/grill-with-docs", "superpowers:skills/brainstorming",
           "pstack:pstack/skills/sharpen", "pstack:pstack/skills/figure-it-out"]

   [[skill]]
   name = "to-tickets"
   job = "tickets"
   mode = "adapt"
   from = ["mattpocock:skills/engineering/to-tickets", "superpowers:skills/writing-plans"]

   [[skill]]
   name = "wayfinder"
   job = "multi-session planning"
   mode = "adopt"
   from = ["mattpocock:skills/engineering/wayfinder"]

   [[drop]]  # one per: to-spec, grill-with-docs, grill-me, brainstorming, writing-plans, sharpen,
             # figure-it-out (reasons below). interrogate/how belong to other groups.
   ```
2. **wayfinder has no beads tracker doc.** It defers every tracker operation to a "Wayfinding operations"
   section that `/setup-matt-pocock-skills` writes; without it, it falls back to local markdown, even in
   a beads repo. The original hard-codes no tracker, so per the adopt rule the skill is unchanged. A
   proposed beads section is in the appendix; it needs a home (a repo `AGENTS.md` pointer or whatever
   replaces setup-matt-pocock-skills). It also says "tell the user to run `/setup-matt-pocock-skills`",
   which won't exist in the house.
3. **wayfinder depends on `grilling`, `domain-modeling`, `research`, `prototype`** via "Call the Skill
   tool". They must exist as house skills or wayfinder breaks. "Skill tool" is Claude Code wording; pi
   reads skills by name, so it probably works, but check it.
4. **wayfinder pushes `research/<name>` branches** (charting step 5). The global hooks block agent
   `git push`. Expect a block; the user decides whether research findings go to a local branch only.
5. **The grilling job overlaps tight-spec.** tight-spec now carries its own interview rules and no longer
   calls `/grilling`. If the house keeps `grilling` (wayfinder needs it), its job should be "stress-test
   a plan or idea" with no spec output, so the two don't compete.

## tight-spec (merge)

Anchor: the user's tight-spec. Kept unchanged: the purpose line, scope-trap list, Goal / Non-goals /
Acceptance checks / Ask-first boundaries / Verification plan, the four-question completion gate,
"stop interviewing once the next step is clear and bounded", one question at a time.

### mattpocock `productivity/grilling`

- TAKEN: facts are the agent's job and decisions are the user's; dispatch a subagent to look things up and
  ask the independent questions meanwhile (§3). Every question carries a recommended answer worded so
  "yes" accepts it (§3 format). Dependency ordering, as in the design tree (§3 "ask in dependency
  order").
- LEFT OUT: asking the whole frontier per round as a numbered batch. **Disagreement:** grilling batches
  questions; the user's tight-spec and superpowers brainstorming ask one at a time. **Went with one at a
  time** (the user's stated preference). The only batch is the builder check's "theirs" pile, a single
  ranked list. Also left out: the "❓/➡️" emoji format (house: no emojis) and the "design tree / frontier"
  vocabulary, which belongs to wayfinder.

### mattpocock `engineering/to-spec`

- TAKEN: use glossary vocabulary and respect ADRs (§1); the synthesize-without-interviewing path when the
  conversation already settled things (§1); no file paths or code in the spec, with the prototype-snippet
  exception (spec template, Decisions); test seams: existing first, highest possible, fewest wins,
  confirmed with the user (Verification plan); Out of Scope → Non-goals.
- LEFT OUT: the "extremely extensive" user-stories list (bloat; conflicts with terse, measurable specs;
  acceptance checks do the same work); publishing the spec to the tracker with a `ready-for-agent` label
  (to-tickets publishes the spec as the epic body; beads `bd ready` replaces triage labels);
  `/setup-matt-pocock-skills` dependency.

### mattpocock `engineering/grill-with-docs`, `productivity/grill-me`

- Both are one-line routers (call grilling, plus domain-modeling). TAKEN: the "with docs" idea, as an
  offer to record sharpened terms/ADRs via `domain-modeling` (§3 end). LEFT OUT: the routers
  themselves. They are aliases, and the house rule is one skill per job.

### superpowers `brainstorming`

- TAKEN: the skip path for requests that already hold everything (§1); sizing small / project /
  split-into-several (§2, plus "too big → wayfinder", which is ours); anchored question examples and
  "a guess they can correct beats a question" (§3); think wide privately, drop options that fight the
  why, show 2–3 only at real forks (§3 design alternatives); playback with your guesses marked as yours,
  and "a default they never heard is one they couldn't reject" (§3); Why and anti-goals (spec
  template); the hard gate, including the spike exception and "keeping a spike is a new request" (top);
  "'sounds good' to an idea isn't approval" (§5); the builder check, adapted into
  `references/builder-check.md` (fresh read-only subagent; answered / minor / theirs piles; one round).
- LEFT OUT: the visual companion (a node server with branding/telemetry, `.superpowers/` dirs, and
  per-harness launch notes; too heavy for the always-loaded skill; the house `prototype` skill covers
  "show, don't tell"). Also left out: the "You MUST use this before any creative work" auto-trigger
  (fights low always-on cost and the user's ask-on-ambiguity rule; tight-spec stays user-invoked); the
  first-message ritual and "no process jargon" persona aimed at non-technical users; saving designs to
  `docs/superpowers/specs/` and committing them (user: commits only when asked; the spec lives in the
  beads epic); routing to `superpowers:writing-plans`.
- **Disagreement on recon:** brainstorming *offers* to look and lets the user decide; grilling just
  looks. **Went with grilling** for read-only exploration. The user's "Probe, don't guess" rule and
  "don't ask what you can look up" both favor it.

### pstack `sharpen`

- TAKEN: "loosen constraints that don't serve the goal as readily as you add ones that do" (scope traps);
  "better, not bigger" (§3 end); keep one outside check that the result is right (Acceptance checks:
  "at least one check from outside the code under change"). LEFT OUT: "don't narrate, just do the work".
  It conflicts with tight-spec's explicit spec-and-approve gate.

### pstack `figure-it-out`

- TAKEN: done as a falsifiable predicate and capturing a baseline before the change, "old value vs new
  value" (Acceptance checks). Riskiest-unknown-first ordering went to to-tickets.
- LEFT OUT: the playbook/phase machinery, todolist, and the poteto-mode / arena / architect /
  show-me-your-work / principle-skill dependencies (pstack-internal; none exist here); rigor-level
  scaling (implicit in sizing); committing an audit trail (commits only when asked).

### pstack `interrogate`, `how`

- Not spec skills. interrogate is multi-model adversarial code review and belongs to a review group. Its
  "state the intent in one paragraph first" step is already tight-spec §2. how is codebase explanation;
  its explorer → explainer fan-out is a reasonable way to run §3's fact-finding subagent, but it is its
  own job and wasn't pulled in. Both hard-code Cursor specifics (`~/.cursor/rules/pstack-models.mdc`,
  `subagent_type: generalPurpose`, `readonly: true`, Cursor model slugs). None of that went in.

## to-tickets (adapt)

Base: mattpocock `engineering/to-tickets`. Kept: gather → explore → vertical slices → quiz → publish,
vertical-slice rules, blocking edges, prefactor-first, the expand–contract wide-refactor section
(condensed), the no-file-paths rule with the prototype exception, the per-ticket local template,
"never one combined file", "don't close/modify the parent".

- CHANGED: the tracker is beads. One `bd create` per ticket, with `--parent <epic>`, `--deps <blockers>`
  (verified in a scratch repo: `--deps X` means "blocked by X"), and `--acceptance` (checklist). Tickets
  are published blockers-first so deps name real ids. The approved spec becomes the epic description, so
  it lives in one place. The frontier is `bd ready --parent <epic>`, and the edges are checked with
  `bd graph <epic>` (verified; `bd dep tree <epic>` doesn't show children's edges). The fallback is the
  local `.scratch/` files only when there is no `.beads/`, and never a `bd init` without asking.
- CHANGED: dropped the `ready-for-agent` triage label. `bd ready` already is the agent-grabbable frontier.
- ADDED: step 6, hand back the ids and the frontier, then **stop**. That matches the user's plan →
  tickets → rundown → pushback flow. The "quiz" step is now "rundown and pushback", and nothing is
  published before approval.
- LEFT OUT: `/setup-matt-pocock-skills` and the GitHub/Linear branches.

### superpowers `writing-plans`

- TAKEN: task right-sizing, "smallest unit that carries its own test cycle and is worth a reviewer's
  gate; fold setup/config/docs into the ticket that needs them; split only where a reviewer could reject
  one and approve its neighbor" (slice rules). The Interfaces produces/consumes block, so tickets worked
  by separate agents agree on names (§3, template). The self-review: spec coverage, failure modes as
  acceptance criteria (Review Focus, condensed), "lines that decide nothing", proportion (§3 self-check).
  Global Constraints are covered by putting the spec in the epic.
- LEFT OUT: exact file paths, line ranges, and code per step. **Disagreement:** writing-plans wants
  exact paths and signatures; Matt says no paths because they go stale. **Went with Matt**, since
  tickets are durable tracker objects, but kept interface *names* via Interfaces. Also left out:
  step-level TDD scripts (the `tdd` skill's job); "Commit" as a step (commits only when asked);
  `docs/superpowers/plans/` files; the execution-method handoff (subagent-driven vs native); the
  "announce at start" line.

### pstack `figure-it-out`

- TAKEN: riskiest unknown first; scaffolding and verification before features (slice rules: prefactor
  first, riskiest first).

## wayfinder (adopt)

`SKILL.md` and `agents/openai.yaml` are copied from mattpocock 49dd158. The only change is the provenance
comment after the front matter (`diff` shows those two lines only). `agents/openai.yaml` is Codex UI
metadata that SKILL.md doesn't reference. It came along so the directory stays identical to the source,
and it's harmless to Claude Code and pi. **No tracker commands changed**, since the original hard-codes
none (see "Needs action" 2–4). Claude-specific wording kept as-is: "Call the Skill tool".

## Neutralized harness-specifics

- Cursor (pstack): `~/.cursor/rules/pstack-models.mdc`, the Task tool's `subagent_type`/`readonly`/model
  slugs, and poteto-mode reasoning-level guidance. None was carried over. Subagents are described
  generically ("dispatch a read-only subagent") and work in Claude Code (Agent) and pi (pi-subagents).
- superpowers: `superpowers:` namespaced skill refs, "your human partner", `.superpowers/` dirs,
  Codex/Gemini/Copilot launch notes. None carried over.
- Claude: tight-spec and to-tickets name skills (`to-tickets`, `wayfinder`, `domain-modeling`) without
  "call the Skill tool". `disable-model-invocation: true` is kept on both (Claude Code and pi honor it),
  which keeps them off the always-on budget. wayfinder keeps its Claude wording (adopt rule).

## Appendix: proposed beads "Wayfinding operations" (for wayfinder)

Not written into the skill (adopt rule). Placement is undecided.

- **Map**: `bd create "<effort>" -t epic -l wayfinder:map --body-file -` (Destination / Notes /
  Decisions so far / Not yet specified / Out of scope).
- **Child ticket**: `bd create "<question title>" --parent <map> -t decision --no-inherit-labels
  -l wayfinder:<type> --body-file -`. **Gotcha:** without `--no-inherit-labels`, children inherit
  `wayfinder:map`.
- **Blocking**: native edges, `bd dep add <blocked> <blocker>`, wired in a second pass after all ids exist.
- **Frontier**: `bd ready --parent <map> --unassigned`; first in map order wins.
- **Claim**: `bd update <id> --claim`, the session's first write.
- **Resolve**: `bd comments add <id> "<answer>"`, then `bd close <id> --reason "<gist>"`, then rewrite the
  map body with `bd update <map> --body-file -` to append the Decisions-so-far line.
- **Out of scope**: `bd close <id> --reason "out of scope: <why>"`, plus a line in the map's Out of scope.
