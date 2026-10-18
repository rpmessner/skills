---
name: foreman
description: Use when managing repo tickets, onboarding with foreman adopt, dispatching or reporting build sessions, reviewing or committing their work, or moving specs into tickets on foreman.
---

<!-- house: own -->

# Foreman

Ticket content belongs to the repo's tracker; the board owns session, progress, review and draft-epic
facts. Detect the tracker per repo: `tickets/` means files, even with `.beads/` present; otherwise beads.
Board events never replace ticket writes or git.

## Ticket content (direct CLI)

In a `tickets/` repo, run these commands directly from that checkout, **not** through `foreman-send`.
They read/write local files without a server. `--json` is available throughout. Invalid input fails;
handled I/O failures can warn with exit 0, so inspect the returned ticket and run `foreman check`.

| Operation | Files (`tickets/`) | Beads (`.beads/`, no `tickets/`) |
| --- | --- | --- |
| Inspect / list / frontier | `foreman show <id> --json` / `foreman ls --json` / `foreman ready --json` | `bd show <id>` / `bd list` / `bd ready` |
| Create | `foreman new "<title>" --type <type> --parent <epic> --blocked-by <ids> --body "<text>"` (omit unused flags) | `bd create` with `--parent`, `--deps`, `--body-file` |
| Start | `foreman update <id> --status in_progress` | `bd update <id> --claim` |
| Note / edit body | `foreman note <id> "<note>"` / `foreman update <id> --body "<full body>"` | `bd comments add <id> "<note>"` / `bd update <id> --body-file -` |
| Close / reopen | `foreman close <id> --reason "<reason>"` / `foreman reopen <id>` | `bd close <id> --reason "<reason>"` / `bd reopen <id>` |
| Block / unblock | `foreman dep add <blocked> <blocker>` / `foreman dep rm <blocked> <blocker>` | `bd dep add <blocked> <blocker>` / `bd dep remove <blocked> <blocker>` |
| Graph / validate | `foreman tree <id> --json` / `foreman check --json` | `bd graph <id>` |

File ready means open, all blockers closed, not an epic; `in_progress` is the claim (no assignee field).
Filter children from JSON by `.parent`; there is no `ready --parent` flag. New ticket ids are allocated
in the main checkout by the coordinator, not by parallel build worktrees. The coordinator also owns
closure after verification and any authorized commit. Build sessions report new work to be filed.

No tracker yet, or migrating beads: ask for user-approved `foreman adopt` in the main checkout.
It registers the repo, creates or converts `tickets/`, updates instructions and installs the check hook;
it stops before committing. Don't migrate incidentally or change config to make a command succeed.
Legacy beads repos keep their embedded-store/export workflow until adopted.

## Board events: send without blocking work

Replace the leading `foreman` in each command below with `bash <this-skill-dir>/scripts/foreman-send`.
It passes the same arguments to `foreman`, caps each call at five seconds (one more to kill), and
returns zero. Missing CLI, transport failure, timeout and refusal are warnings, never failed steps.
Continue the build, report, review or commit; don't install tools or repair the service mid-step.

The CLI itself exits 0 for handled failures (warning; writes spool to Postgres when possible),
and 3 for an out-of-order claim (current stage and allowed events). Keep that diagnostic; don't
retry blindly, fabricate intermediate events or call a warning a successful board update.
`foreman show <id> --overlay --json` can clarify a refusal later. Read calls never spool.

- **Identity:** build sessions inherit `FOREMAN_ACTOR=pi`, `FOREMAN_SESSION=<window>` from `pi-window`.
  Coordinators set `FOREMAN_ACTOR` to their harness (`claude` or `pi`) and `FOREMAN_SESSION` to their
  own session name; `--actor` / `--session` override them. Without an actor the CLI says `user`.
- **Configuration:** inherit `FOREMAN_URL` (default `http://127.0.0.1:4747`) and `FOREMAN_TOKEN_FILE`
  from the user's environment. The token file has no default. Never print credentials, add secret
  paths to tracked files, create tokens, or change config to make a board call succeed.
- **Resolution:** one ticket ID per call; repeat for each affected ticket, not the parent epic.
  Ticket prefixes resolve the repo; use `--project <configured-project>` if ambiguous or not yet
  projected. Draft slugs resolve by cwd or `--project`; use explicit project and `draft:<slug>`.
  Paths are links, not uploads: use the actual brief, spec and report paths.

## Ticket stages

| When | CLI command (through `foreman-send`) |
| --- | --- |
| After launch (`pi-window` does this) | `foreman dispatch <id> --window <window> --harness pi --model <model> --workdir <path> --branch <branch> --base <sha> --brief <path> --report <path>` |
| Build milestone: reproduced, slice green, gate passed | `foreman progress <id> "<what changed; next step>"` |
| Report file written, before the done marker | `foreman report <id> --path <report>` |
| Coordinator begins close-out, before gates/review | `foreman review <id>` |
| Review sends work back to the build session | `foreman changes <id> "<finding and required check>"` |
| Actual commit exists, user authorized it | `foreman commit <id> --sha <sha>` |
| User stops / resumes abandoned work | `foreman abandon <id>` / `foreman revive <id>` |

`changes` sends the machine's `request_changes` event. A correction cycle is changes → progress →
report → review → commit; send review again for the new report. Never emit commit for planned or
uncommitted work. Board success is not verification and grants no permission to commit or push.

## Project-size specs only

Keep one slug, configured project and spec path through `tight-spec` → `to-tickets`; carry them in
the handoff. Reuse an existing draft, not a new slug per session. A board draft is not a tracker ticket.

| When | CLI command (through `foreman-send`) |
| --- | --- |
| Sized as a project; choose the spec file | `foreman epic create draft:<slug> --project <project> --title "<title>" --spec <path>` |
| Interview starts (or settled decisions are synthesized) | `foreman epic spec draft:<slug> --project <project>` |
| User approves the written spec | `foreman epic approve draft:<slug> --project <project> --spec <path>` |
| Approved tickets published under a tracker epic | `foreman epic ticket draft:<slug> --project <project> --beads-epic-id <epic-id>` |
| User stops / resumes a draft | `foreman epic abandon draft:<slug> --project <project>` / `foreman epic revive draft:<slug> --project <project>` |

`epic spec` sends `start_spec`; `epic approve` sends `approve_spec`. The ticket flag is
`--beads-epic-id`, not `--bead`: this legacy flag accepts epic ids from either tracker. Small chat-only
specs create no draft. Without a draft or a published tracker epic, skip ticketing the board.

## Links and inspection

Use `foreman attach <ticket> --epic <epic>` / `foreman detach <ticket> --epic <epic>` for board-side
cross-repo membership; `--epic-project <project>` disambiguates the target. Ticket content stays untouched.
Use `foreman show <id> --overlay --json` for stage, allowed events and history;
`foreman ls --project <project> --stage building --json` for a filtered list.
