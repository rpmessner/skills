---
name: triage
description: Move beads through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs.
disable-model-invocation: true
---

<!-- house: adapt; from: mattpocock:skills/engineering/triage@49dd158. Edits: tracker is beads (`bd`): category = bead type, state = `triage:*` label (needs-info also sets status deferred), wontfix = `bd close --reason`; GitHub issue/PR workflow, external-PR triage, the AI disclaimer, and /setup-matt-pocock-skills removed; "call the Skill tool" -> run the skills. -->

# Triage

Move beads (the repo's `bd` tracker) through a small state machine of triage roles. Domain docs (glossary, ADRs) follow the repo's AGENTS.md. Pull requests are not triaged here; review them with `code-review`.

## Reference docs

- [AGENT-BRIEF.md](AGENT-BRIEF.md): how to write durable agent briefs
- [OUT-OF-SCOPE.md](OUT-OF-SCOPE.md): how the `.out-of-scope/` knowledge base works

## Roles

Two **category** roles, stored as the bead type:

- `bug`: something is broken (`-t bug`)
- `enhancement`: new feature or improvement (`-t feature`)

Five **state** roles, stored as one `triage:*` label:

- `needs-triage`: maintainer needs to evaluate (`triage:needs-triage`)
- `needs-info`: waiting on reporter for more information (`triage:needs-info`, plus `--status deferred` so it leaves `bd ready`)
- `ready-for-agent`: fully specified, ready for an AFK agent (`triage:ready-for-agent`; agents pick with `bd ready -l triage:ready-for-agent`)
- `ready-for-human`: needs human implementation (`triage:ready-for-human`)
- `wontfix`: will not be actioned (`bd close <id> --reason "wontfix: <why>"`, no label)

Every triaged bead should carry exactly one category role and one state role. If state roles conflict, flag it and ask the maintainer before doing anything else.

Change state in one call: `bd update <id> --remove-label triage:<old> --add-label triage:<new>` (add `--status open` when leaving needs-info, `--status deferred` when entering it). Use explicit labels in queries; `--label-pattern` also matched unlabeled beads in bd 1.1.0.

State transitions: an untriaged bead normally goes to `needs-triage` first; from there it moves to `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`. `needs-info` returns to `needs-triage` once the reporter replies. The maintainer can override at any time; flag transitions that look unusual and ask before proceeding.

## Invocation

The maintainer invokes `/triage` and describes what they want in natural language. Interpret the request and act. Examples:

- "Show me anything that needs my attention"
- "Let's look at sk-42"
- "Move sk-42 to ready-for-agent"
- "What's ready for agents to pick up?"

## Show what needs attention

Query beads and present three buckets, oldest first (`--sort created`):

1. **Untriaged**: open bugs and features with no `triage:*` label: `bd list -s open -t bug` and `-t feature`, each with `--exclude-label triage:needs-triage,triage:needs-info,triage:ready-for-agent,triage:ready-for-human`.
2. **`needs-triage`**: `bd list -l triage:needs-triage`.
3. **`needs-info` with reporter activity since the last triage notes**: `bd list -l triage:needs-info`, then read each one's comments (`bd comments <id>`).

Show counts and a one-line summary per item. Let the maintainer pick.

## Triage a specific bead

1. **Gather context.** Read the full bead (`bd show <id>`, `bd comments <id>`: body, comments, labels, author, dates). Parse any prior triage notes so you don't re-ask resolved questions. Explore the codebase using the project's domain glossary, respecting ADRs in the area. Run two checks against the codebase: (a) **redundancy**: search for an existing implementation of the requested behavior by domain concept (not just the request's wording), and report where you looked. If found, it's an already-implemented `wontfix` (step 5). (b) **prior rejection**: read `.out-of-scope/*.md` and surface any that resembles this request.

2. **Recommend.** Tell the maintainer your category and state recommendation with reasoning, plus a brief codebase summary relevant to the request (including whether it's already implemented). Wait for direction.

3. **Verify the claim.** Before any grilling, check that the claim holds up. For a bug, reproduce it from the reporter's steps. Report what happened: confirmed (with code path), failed, or insufficient detail (a strong `needs-info` signal). A confirmed verification makes a much stronger agent brief.

4. **Grill (if needed).** If the request needs fleshing out, run the `grilling` and `domain-modeling` skills and grill it into shape a round of questions at a time, sharpening domain terms and updating `GLOSSARY.md`/ADRs inline as decisions land.

5. **Apply the outcome:**
   - `ready-for-agent`: add an agent brief comment (`bd comments add <id> -f brief.md`, [AGENT-BRIEF.md](AGENT-BRIEF.md)) and copy its acceptance criteria to `bd update <id> --acceptance`.
   - `ready-for-human`: same structure as an agent brief, but note why it can't be delegated (judgment calls, external access, design decisions, manual testing).
   - `needs-info`: add triage notes as a comment (template below).
   - For `wontfix`, close the bead with `bd close <id> --reason "wontfix: ..."`, with the comment depending on *why*:
     - **Already implemented**: the change already exists in the codebase. Point to where it lives; do **not** write to `.out-of-scope/` (that KB is for *rejected* requests, not built ones).
     - **Rejected (bug)**: give a polite explanation, then close.
     - **Rejected (enhancement)**: write to `.out-of-scope/`, name it in the close reason, then close ([OUT-OF-SCOPE.md](OUT-OF-SCOPE.md)).
   - `needs-triage`: apply the role. Optional comment if there's partial progress.

## Quick state override

If the maintainer says "move sk-42 to ready-for-agent", trust them and apply the role directly. Confirm what you're about to do (role changes, comment, close), then act. Skip grilling. If moving to `ready-for-agent` without a grilling session, ask whether they want to write an agent brief.

## Needs-info template

```markdown
## Triage Notes

**What we've established so far:**

- point 1
- point 2

**What we still need from you:**

- question 1
- question 2
```

Capture everything resolved during grilling under "established so far" so the work isn't lost. Questions must be specific and actionable, not "please provide more info".

## Resuming a previous session

If prior triage notes exist in the bead's comments, read them, check whether the reporter has answered any outstanding questions, and present an updated picture before continuing. Don't re-ask resolved questions.
