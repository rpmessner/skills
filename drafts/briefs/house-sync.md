You are a build session in the house skill set repo (~/dev/utils/skills-house). A coordinator session (Claude Code, another tmux window) dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Read first
- AGENTS.md, catalog.toml, scripts/check.py, scripts/link.py, bin/pi-window, skills/flow/SKILL.md.
- drafts/sessions/house-decide.md (previous report).
- Tickets: `bd show sk-81s.14`, `bd show sk-81s.6`, `bd show sk-81s.9`. Claim each as you start it.

Sources (read-only except `git fetch`): mattpocock ~/dev/utils/skill-sources/mattpocock-upstream, superpowers ~/dev/utils/skill-sources/superpowers, pstack ~/dev/utils/skill-sources/cursor-plugins (sparse). Pins are in catalog.toml.

The repo now has commits. Leave your changes uncommitted; the coordinator reviews and commits per slice.

## sk-81s.14 — uncovered upstream skills (decisions made by the user; apply, do not re-ask)
- ADOPT (vendored byte-identical, provenance comment, catalog entry): mattpocock retro, wizard, wait-what, and in-progress writing-beats, writing-fragments, writing-shape. Find their paths under the pinned source. Check each one's references resolve in the house set (e.g. retro loads writing-for-agents). If one depends on something the house set lacks, or hard-codes GitHub/push, switch it to adapt and note the edit.
- DROP with reasons: to-questionnaire (rarely needed), setup-matt-pocock-skills (replaced by beads + AGENTS.md note), chief-of-staff, claude-handoff, loop-me (covered by handoff and the coordinator model), setup-ts-deep-modules (TypeScript-only), superpowers diagnosing-superpowers (superpowers is being uninstalled).
- Then scan again: no upstream skill dir may be left without a [[skill]] or [[drop]] reference. Make this a check.py rule ("coverage of upstream") so future syncs surface new skills; negative-test it by temporarily removing one drop entry.
- Note for the coordinator (do not act): wizard is also installed separately at ~/.agents/skills/wizard; the cutover must replace it.

## sk-81s.6 — skills-sync (script + skill)
- `scripts/sync.py` (Python stdlib + tomllib, same style as check.py):
  - `git fetch` each source; compare pin..origin default branch.
  - Per house skill: adopt → list changed upstream files and propose a pin bump; adapt/merge → per-skill digest (diffstat plus the diff of the referenced paths, capped) for an agent to summarize; own → skip.
  - Upstream skill dirs not referenced by any [[skill]] or [[drop]] → "unmapped" list (reuse the check.py logic, don't duplicate it).
  - Writes `reports/YYYY-MM-DD.md`. `--file-beads` creates one bead per candidate (label `sync`, parent the open sync epic or none) — default off. `--bump <source> <commit>` rewrites that pin in catalog.toml. `--catalog <path>` for tests.
- Test it: (1) at current pins the report says nothing changed (or only real upstream changes since the pin; say which); (2) with a temp catalog whose mattpocock pin is several commits older, the report lists the changes. Do not file real beads during tests.
- `skills/skills-sync/SKILL.md` (user-invoked: `disable-model-invocation: true`): run sync.py, read the digests, compare each against the house version, propose adopt/adapt/drop per idea as beads, bump pins only after the user decides, run check.py.

## sk-81s.9 — coordinator dispatch skill
- Move bin/pi-window into `skills/dispatch/scripts/pi-window` so it travels with the skill; update flow and any reference. Keep its behaviour.
- Add `skills/dispatch/scripts/pi-wait <window> <marker> [timeout-seconds]`: polls `tmux capture-pane -p -J -S -200 -t :<window>`; exits 0 printing `DONE` when a line equals the marker exactly (anchored, whole line), 3 printing `EXITED` when a line equals `[pi exited] press enter`, 4 on timeout, 2 if the window is gone. Earlier false positives came from the marker appearing inside the brief text and inside the launch command, so match whole lines only.
- `skills/dispatch/SKILL.md` (coordinator-only, model-invocable with a one-sentence description): when to dispatch (build work → pi window; Claude subagents only on user request), window naming (short kebab-case from the content), brief template (goal, read first, bead ids, decisions already made, rules, done criteria, report file, marker alone on the last line), launch, wait (pi-wait in the background), follow-ups (`tmux send-keys -t :<w> -l "<text>"` then a separate `tmux send-keys -t :<w> Enter`), close-out (read the report, re-run the repo gate yourself, verify claims, commit per slice only when the user asked, then kill the window). Dispatch-from-ready mode: list `bd ready` across repos under ~/dev with a .beads dir, propose which tickets become windows, launch on approval.
- Smoke-test pi-wait without launching pi: a throwaway tmux window running a shell that echoes the marker inline in a longer line, then alone on a line; confirm only the second matches. Kill the window after.
- Leave sk-81s.9 open (its acceptance test needs the coordinator); add a note with what is done.

## Rules
- No `scripts/link.py --apply`, no changes to ~/.claude, ~/.agents, ~/.pi, no uninstalls, no commits, no pushes.
- `scripts/check.py` must end at 0 errors with the always-on budget held.
- Close .14 and .6 only with evidence.

## Report back
Write drafts/sessions/house-sync.md: what changed per ticket (tables), every edit to adopted copies, test evidence for sync.py and pi-wait, anything open, final check.py output. Then print HOUSE-SYNC DONE alone on the last line.
