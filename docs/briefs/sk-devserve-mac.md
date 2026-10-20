You are a build session in the skills repo (~/dev/utils/sk-devserve-mac, branch sk-devserve-mac, a worktree of ~/dev/utils/skills). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
devserve becomes cross-platform: the systemd user-unit backend stays exactly as it works on Linux today, and a tmux backend runs previews on macOS. Full scope and acceptance: ticket sk-99j.

## Read first
AGENTS.md; `foreman show sk-99j`; skills/devserve/ (SKILL.md, configuration.md, lifecycle.md, scripts/devserve and its tests). Reference implementation of the tmux backend, sanitised by the coordinator: /tmp/claude-1000/-home-rpmessner-dev-music/b034bdad-1084-4b73-8da7-bdfb1f4e577b/scratchpad/devserve-tmux-reference/ (read only; port its logic, not its wholesale replacement of systemd).

## Tickets
sk-99j (ticket files). Start with `foreman update sk-99j --status in_progress`. The coordinator files new tickets and closes this one; report new work instead of filing it.

## Skills
- `tdd` at the seams: backend selection (platform plus explicit override), each backend's start/stop/list/gc against the shared registry contract, the lifecycle table (house state-machine skeleton; keep lifecycle.md generated from it).
- `verify-before-claiming` before writing the report.
- `code-review` on your own diff against aee2388: Standards, Spec (sk-99j), Risk (any change to Linux/systemd behaviour; deleting databases or windows that aren't devserve's). Run the axes one after another; spawn no subagents. Fix every Critical and Important finding.

## Rules
- Do not disturb running previews or the installed devserve: tests use scratch tmux servers (`tmux -L devserve-test-<pid>`), transient units and `devserve_test*` databases only, cleaned up after.
- No work-identifying names, paths or accounts in code, tests or docs. Do not use the `gh` CLI (it is logged in to a different account).
- No commits, no pushes. Stay inside this worktree. Use /usr/bin/rm, not rm.

## Build loop
Use the `foreman` skill's best-effort sender for `foreman progress sk-99j "<milestone; next step>"` at milestones.
For a build-time question you cannot answer, run `foreman ask decision sk-99j --question "<question>" --option "<A>" --option "<B>" --recommendation "<A>"` directly, then `foreman wait <returned-request-id> --timeout 7200` in your shell. Resume only with `state: answered`.

## Done when
Every sk-99j acceptance item holds with evidence: existing unit and `DEVSERVE_INTEGRATION=1` integration tests pass unchanged on Linux (systemd); tmux backend tests pass under the override; `python3 scripts/check.py` clean; docs describe both backends.
Work until every item above holds. Hand off early only near your context limit (above about 85%), at a clean, green point, with a precise list of what remains.

## Report back
Write docs/sessions/sk-devserve-mac.md: what changed, which shared improvements apply to which backend, evidence, review findings per axis, anything open. Use the `foreman` skill's best-effort sender for `foreman report sk-99j --path docs/sessions/sk-devserve-mac.md`. Then print SK-DEVSERVE-MAC DONE alone on the last line.
