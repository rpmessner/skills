---
name: dispatch
description: "Coordinator only: launch, watch, steer, and close out pi build sessions in named tmux windows, singly or from `bd ready` across repos."
---

<!-- house: own -->

# Dispatch

You are the coordinator: you plan, brief, verify, and commit. Build work runs in a pi session in its own tmux window, not in your context. Use Claude subagents (Agent tool, pi `subagent`) only when the user asks for them.

Scripts live in `~/dev/utils/skills/skills/dispatch/scripts/` (`$D` below). Both need to run inside tmux and target windows of the current session.

## Dispatch one session

1. **Name the window.** Short kebab-case from the content, ≤31 chars: `house-sync`, `cdo-trait-probe`. The marker is the name upper-cased plus ` DONE`: `HOUSE-SYNC DONE`.
2. **Write the brief** to `<repo>/drafts/briefs/<window>.md`, or to `/tmp/briefs/<window>.md` when the repo has no drafts dir. Fill every slot:

   ```markdown
   You are a build session in <repo> (<path>). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

   ## Goal
   <one paragraph: the outcome, not the steps>

   ## Read first
   <local AGENTS.md, then the files and prior reports this work builds on>

   ## Tickets
   <bead ids; claim each as you start it; close only with evidence>

   ## Skills
   - `tdd` at these seams: <seams agreed in the spec or ticket, or "none: <reason>">
   - `verify-before-claiming` before writing the report.
   - `code-review` on your own diff against <base sha> before printing the marker: Standards and Spec axes (Spec = the tickets above), plus Risk when the diff touches persistence, wire formats, public APIs, shared config, or concurrency. Run the axes one after another in this session; spawn no subagents. Fix every Critical and Important finding, then re-run the gate.

   ## Decisions already made
   <user decisions to apply, not re-ask>

   ## Rules
   <what is off limits: commits, pushes, deploys, paths outside the repo, harness dirs>

   ## Done when
   <checkable criteria: gate command and its expected result, tests, evidence>

   ## Report back
   Write <report path>: what changed, evidence, review findings per axis with what you fixed and what you left open, anything else open, final gate output. Then print <MARKER> alone on the last line.
   ```

   `<base sha>` is `git rev-parse HEAD` in the workdir at dispatch time. Done when every slot is filled and the marker appears only in the last line's instruction.
3. **Launch:** `$D/pi-window <window> <workdir> <brief-file> [pi-args...]`. It refuses duplicate window names; extra args go to pi (`-e <path>` loads an extension for that run).
4. **Wait in the background:** run `$D/pi-wait <window> "<MARKER>" 7200` as a background command, then keep working or return control; do not poll by hand. It matches whole lines only (whitespace-trimmed), so the marker quoted in the brief never counts. Exit codes: 0 `DONE`, 3 `EXITED` (pi quit without the marker: read the pane), 4 timeout (session still running: check the pane, re-wait), 2 window gone.
5. **Follow up** when the session asks, or when the user adds a decision. Send the text and the Enter as two separate commands, and keep the text to one line:

   ```bash
   tmux send-keys -t :<window> -l "<text>"
   tmux send-keys -t :<window> Enter
   ```

   Read the pane with `tmux capture-pane -p -J -S -200 -t :<window>`.
6. **Close out.**
   1. Read the report file.
   2. Re-run the repo's gate yourself, plus its per-ticket close-out check where it has one (form-engine: `.agents/skills/verify-form-engine/verify closeout <bead-id>` for each closed ticket).
   3. Check each claim against the diff and the evidence. A claim you cannot reproduce is open, not done.
   4. Run `code-review` on the slice's diff against the brief's base sha, axes one after another in your own context; no subagents unless the user asked for them. Send Critical and Important findings back to the session (step 5) or list them as open to the user.
   5. Commit, one commit per slice, only when the user has asked for commits.
   6. Kill the window: `tmux kill-window -t :<window>`.

   Done when the gate passes in your own run, every claim is confirmed or listed as open to the user, no Critical review finding is unresolved, and the window is gone.

## Dispatch from ready

1. List ready work in every repo under `~/dev` that has a `.beads` dir:

   ```bash
   fd -H -I -t d -g .beads ~/dev --max-depth 5 -E node_modules -E deps -E _build |
     while read -r b; do r=$(dirname "$b"); echo "== ${r#$HOME/dev/}"; (cd "$r" && bd ready); done
   ```

   A repo whose Dolt server is unreachable: report it, do not start servers.
2. Propose a table to the user: ticket, repo, window name, why it can run now. Group tickets that share files into one window. Never put two writers in the same repo working tree at once. Leave out epics, tickets that need the user live (in-game probes, logins), and tickets blocked on a decision.
3. On approval, dispatch each row as above, one brief per window.
