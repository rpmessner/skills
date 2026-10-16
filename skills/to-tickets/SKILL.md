---
name: to-tickets
description: "Break an approved spec, plan, or conversation into tracer-bullet tickets with blocking edges and acceptance criteria, published to beads under an epic. Use for /to-tickets or after tight-spec approval."
disable-model-invocation: true
---

<!-- house: adapt; from: mattpocock:skills/engineering/to-tickets@49dd158, superpowers:skills/writing-plans@bb92a77, pstack:pstack/skills/figure-it-out@850d7f2 -->

# To Tickets

Break a spec, plan, or conversation into **tickets**: tracer-bullet vertical slices, each declaring the
tickets that **block** it, published to beads (`bd`). Then give a short rundown and stop for pushback.
This skill plans; it never starts implementing.

## 1. Gather context

Work from the conversation. If the user passes a reference (a bead id, a spec path), read its full body,
comments, and children (`bd show <id>`, `bd list --parent <id>`).

Check the tracker: if the repo has a `.beads/` directory, publish to beads. Otherwise fall back to local
files (step 5); don't run `bd init` without asking.

## 2. Explore the codebase

If you haven't already, explore enough to know the current state. Use the project's glossary vocabulary
in titles and descriptions, and respect ADRs in the area. Look for prefactoring that makes the work
easier: "make the change easy, then make the easy change."

## 3. Draft vertical slices

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT
  a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice fits in a single fresh context window.
- A ticket is the smallest unit that carries its own test cycle and is worth a reviewer's gate. Fold
  setup, config, scaffolding, and docs into the ticket whose deliverable needs them; split only where a
  reviewer could reject one ticket while approving its neighbor.
- Prefactoring goes first. Among independent slices, put the riskiest unknown first.

</vertical-slice-rules>

Give each ticket its **blocking edges**: the tickets that must complete before it can start. Only real
gates — a ticket with no blockers can start immediately, and parallel work stays parallel.

When one ticket hands a named contract to another (a function, message, schema, event), note it under
**Interfaces** in both: what it produces, what it consumes. Names and shapes, not file paths.

**Wide refactors are the exception.** One mechanical change whose blast radius fans across the codebase
(rename a column, retype a shared symbol) can't land green as a vertical slice. Sequence it
expand–contract: expand (add the new form beside the old) → migrate call sites in batches sized by blast
radius, each blocked by the expand → contract (delete the old form), blocked by every batch. If batches
can't stay green alone, they share an integration branch and all block a final integrate-and-verify
ticket; green is promised only there.

**Self-check before showing the user:**

- **Coverage** — every spec acceptance check and decision maps to a ticket. Add tickets for gaps.
- **Failure modes** — inputs or conditions the spec implies but no ticket exercises get an acceptance
  criterion on the ticket that owns that code.
- **No empty lines** — "handle edge cases", "add validation", "TBD" decide nothing. Replace or delete.
- **Proportion** — tickets carry decisions, not transcripts of the code.

## 4. Rundown and pushback

Present the breakdown as a numbered list. For each ticket:

- **Title** — short, descriptive
- **Blocked by** — which tickets (if any)
- **What it delivers** — the end-to-end behavior it makes work

Ask:

- Does the granularity feel right (too coarse / too fine)?
- Is each blocking edge a genuine gate?
- Should any tickets merge or split?

Iterate until the user approves. Do not publish before approval.

## 5. Publish

Publish in dependency order (blockers first) so each `--deps` names a real id. Commands and templates are
in `references/beads.md`.

- **Epic.** If the source is an existing bead, it is the parent: don't close or rewrite it. Otherwise
  create an epic whose description is the approved spec (Goal, Non-goals, Acceptance checks, Ask-first
  boundaries) so every ticket inherits it from one place.
- **Tickets.** One `bd create` per ticket with `--parent <epic>`, `--deps <blocker-ids>`, a description
  (what to build, from the user's perspective, plus Interfaces if any), and `--acceptance` (a checklist).
- **No `.beads/`** — write one file per ticket under `.scratch/<feature-slug>/issues/NN-<slug>.md`,
  numbered from `01` in dependency order, using the local template in `references/beads.md`. Never a
  single combined file.

Avoid file paths and code snippets in tickets — they go stale. Exception: a prototype snippet that pins a
decision better than prose (state machine, schema, type shape), trimmed and labeled.

## 6. Hand back

Report the epic and ticket ids with titles, and the frontier (`bd ready --parent <epic>`): what can start
now, and what could run in parallel. Then stop. Implementation starts only when the user says so.
