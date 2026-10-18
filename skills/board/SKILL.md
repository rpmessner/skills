---
name: board
description: Use when dispatching or reporting build sessions, reviewing or committing their work, or moving project-size specs into tickets on beads-board.
---

<!-- house: own -->

# Board

Keep beads-board current at the workflow step that creates the fact. Beads owns ticket content;
the board owns session, progress, review and draft-epic facts. Board calls never replace `bd` or git.

## Send without blocking work

Replace the leading `board` in each command below with `bash <this-skill-dir>/scripts/board-send`.
It passes the same arguments to `board`, caps each call at five seconds (one more to kill), and
returns zero. Missing CLI, transport failure, timeout and refusal are warnings, never failed steps.
Continue the build, report, review or commit; don't install tools or repair the service mid-step.

The CLI itself exits 0 for handled failures (warning; writes spool to Postgres when possible),
and 3 for an out-of-order claim (current stage and allowed events). Keep that diagnostic; don't
retry blindly, fabricate intermediate events or call a warning a successful board update.
`board show <id> --json` can clarify a refusal later. Read calls never spool.

- **Identity:** build sessions inherit `BOARD_ACTOR=pi`, `BOARD_SESSION=<window>` from `pi-window`.
  Coordinators set `BOARD_ACTOR` to their harness (`claude` or `pi`) and `BOARD_SESSION` to their
  own session name; `--actor` / `--session` override them. Without an actor the CLI says `user`.
- **Configuration:** inherit `BOARD_URL` (default `http://127.0.0.1:4747`) and `BOARD_TOKEN_FILE`
  from the user's environment. The token file has no default. Never print credentials, add secret
  paths to tracked files, create tokens, or change config to make a board call succeed.
- **Resolution:** one ticket ID per call; repeat for each affected ticket, not the parent epic.
  Ticket prefixes resolve the repo; use `--project <configured-project>` if ambiguous or not yet
  projected. Draft slugs resolve by cwd or `--project`; use explicit project and `draft:<slug>`.
  Paths are links, not uploads: use the actual brief, spec and report paths.

## Tickets

| When | CLI command (through `board-send`) |
| --- | --- |
| After launch (`pi-window` does this) | `board dispatch <id> --window <window> --harness pi --model <model> --workdir <path> --branch <branch> --base <sha> --brief <path> --report <path>` |
| Build milestone: reproduced, slice green, gate passed | `board progress <id> "<what changed; next step>"` |
| Report file written, before the done marker | `board report <id> --path <report>` |
| Coordinator begins close-out, before gates/review | `board review <id>` |
| Review sends work back to the build session | `board changes <id> "<finding and required check>"` |
| Actual commit exists, user authorized it | `board commit <id> --sha <sha>` |
| User stops / resumes abandoned work | `board abandon <id>` / `board revive <id>` |

`changes` sends the machine's `request_changes` event. A correction cycle is changes → progress →
report → review → commit; send review again for the new report. Never emit commit for planned or
uncommitted work. Board success is not verification and grants no permission to commit or push.

## Project-size specs only

Keep one slug, configured project and spec path through `tight-spec` → `to-tickets`; carry them in
the handoff. Reuse an existing draft, not a new slug per session. A board draft is not a beads ticket.

| When | CLI command (through `board-send`) |
| --- | --- |
| Sized as a project; choose the spec file | `board epic create draft:<slug> --project <project> --title "<title>" --spec <path>` |
| Interview starts (or settled decisions are synthesized) | `board epic spec draft:<slug> --project <project>` |
| User approves the written spec | `board epic approve draft:<slug> --project <project> --spec <path>` |
| Approved tickets published under a beads epic | `board epic ticket draft:<slug> --project <project> --beads-epic-id <epic-id>` |
| User stops / resumes a draft | `board epic abandon draft:<slug> --project <project>` / `board epic revive draft:<slug> --project <project>` |

`epic spec` sends `start_spec`; `epic approve` sends `approve_spec`. The ticket flag is
`--beads-epic-id`, not `--bead`. Small chat-only specs create no draft. Without a draft or a published
beads epic, skip ticketing the board; local fallback ticket files aren't beads IDs.

## Links and inspection

Use `board attach <ticket> --epic <epic>` / `board detach <ticket> --epic <epic>` for board-side
cross-repo membership; `--epic-project <project>` disambiguates the target. Beads stays untouched.
Use `board show <id> --json` for stage, allowed events and history;
`board ls --project <project> --stage building --json` for a filtered list.
