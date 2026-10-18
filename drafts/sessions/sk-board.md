# sk-board workflow wiring

Implementation report for sk-5o2 and sk-osj. No commits, pushes, bd commands, subagents, installs or harness edits.

## Review scope

Baseline `b2a36c995f97c57b1471629c83e0ff9050f8e4b4` resolves to HEAD; the three-dot diff and commit list are empty. The requested implementation is uncommitted, so review covers the working-tree diff against that baseline plus new board/test files. The pre-existing coordinator brief is excluded. Axes run sequentially in this session.

## Standards

Reviewed root/local AGENTS, the standards baseline, existing skill style, manifest, scripts and new files. No Critical or Important finding. One new own skill carries the CLI contract; workflow skills point to it at the relevant step. The sender is a bounded stateless adapter, not a second workflow state machine. Existing provenance stays intact. Descriptions remain within the manifest budget.

Declined to judge: upstream source contents and existing skill instructions unrelated to board wiring. Fresh-context agent compliance repetitions were not run because this build explicitly forbids subagents; text wiring is inspected, not claimed behaviorally proven across model runs.

Verdict: Ready.

## Spec

Reviewed second against both tickets from the local read-only JSONL export, the user brief, CLI contract, and Decisions 8/11/12. The CLI prerequisite bb-c2w.7 is closed in beads-board's export; no bd commands were used.

- Important, fixed: `skills/dispatch/SKILL.md`, Tickets template, previously let builders close tickets before reporting. The board treats bead closure as done, making later claimed report/review events invalid. The coordinator now owns closure after review and any authorized commit, with board commit sent before closure.
- Important, fixed: the close-out correction path could fall through to commit/kill while the session was still working. It now explicitly waits for the new report and restarts close-out.
- Settled-conversation specs still size/create/start the draft before synthesis; small specs create none. The spec is saved at the linked path, approval carries that link, and ticket publication carries the same slug/project to the beads epic.
- Contract reconciliation: one ID per invocation (loop for grouped sessions); `epic spec` = start_spec, `epic approve` = approve_spec, `changes` = request_changes; epic ticket uses `--beads-epic-id`, not the brief's `--bead` shorthand.

Declined to judge: live card movement (ticket acceptance / beads-board checks 3 and 6) cannot be verified without an installed CLI/service. Fake CLI tests establish dispatch arguments and failure isolation, not persisted stages. No board-side behavior was modified.

Verdict: Implementation ready; live acceptance remains for the coordinator after deployment. No open Critical or Important implementation finding.

## Risk

Reviewed third. The safety fact is that board delivery runs after tmux launch and every board invocation is bounded and fail-open. Proof level 4: the shipped scripts run against executable fakes, with real zsh parsing but no user startup config.

- Confirmed and fixed during implementation: a missing CLI produced four diagnostic lines for two tickets. Dispatch now warns once and leaves the session running.
- Confirmed and fixed during implementation: a hung board exceeded the test's ten-second deadline. The shared sender now uses `timeout --kill-after=1s 5s` and exits zero, including when timeout itself is unavailable.
- Confirmed and fixed during implementation: a brief path containing shell quotes prevented pi from starting. The launcher now quotes the complete inner command and treats the brief path as literal data. The regression executes real zsh without loading user config.
- Cleared: CLI exits 1, 3 and 127 do not fail dispatch or skip the next ticket. A refused report under `bash -e` cannot suppress the done marker. Failed or duplicate tmux launches emit no dispatch. Non-git workdirs still launch with explicit unknown metadata. Relative report paths resolve against the workdir. Credentials are inherited, never read or logged by the adapter.
- Residual: a forced timeout can interrupt an uncertain delivery; the warning is not a receipt. There is no automatic retry. Older launches without ticket metadata still work but cannot produce a dispatch claim. Skills require explicit IDs, report path and chosen model for tracked launches.

Declined to judge: HTTP authentication, Postgres spool replay and live dashboard changes belong to beads-board and require its running deployment. Actual pi startup wrappers and tmux pane lifecycle are not exercised by the fakes. Model compliance across fresh contexts is unverified because subagents were forbidden.

Verdict: Ready with those verification limits. No open Critical or Important implementation finding. Cheapest gate is `python3 skills/dispatch/scripts/test_pi_window.py` plus `python3 scripts/check.py`.

## Changes per skill

- `board`: new own skill and `catalog.toml` entry. Documents CLI verbs, machine-event aliases, one-ID calls, actor/session identity, project resolution, credentials, refusal handling and the shared fail-open sender at `skills/board/scripts/board-send`.
- `dispatch`: repeated `--bead` and `--report` metadata before the optional `--` separator; all remaining args go to pi. `pi-window` records every ticket after launch, exports build identity, captures branch/base, and records the explicit pi model. The brief adds progress and report instructions. Close-out adds review, changes and commit, and defers closure until those stages finish.
- `flow`: coordinator close-out points to the board verbs and fail-open rule.
- `tight-spec`: project-only draft creation, interview start, saved spec path, approval event, and draft identity in the handoff. Settled decisions still pass through draft creation/start before synthesis.
- `to-tickets`: after beads publication, links the existing draft to the new or reused epic. Local fallback files and specs without drafts skip that board transition.
- `skills/dispatch/scripts/test_pi_window.py`: 12 process-boundary tests. No change to `pi-wait`, upstream sources or harness links. The existing `drafts/briefs/sk-board.md` remains untouched.

## Verb-to-step map

Every command below uses the best-effort sender. Grouped sessions send one call per affected ticket.

| Verb | Caller / workflow step |
| --- | --- |
| `dispatch` | `pi-window`, after successful launch; window, harness, model, workdir, branch, base, brief and report |
| `progress` | Dispatch brief's Build loop, at milestones |
| `report` | Dispatch brief's Report back, after writing the report and before the marker |
| `review` | Coordinator close-out step 1, before gates/review; repeated after a correction report |
| `changes` / request_changes | Coordinator close-out step 4, before returning findings |
| `commit --sha` | Coordinator close-out step 5, after an authorized successful commit |
| `epic create` | tight-spec step 2, project size only |
| `epic spec` / start_spec | tight-spec step 3, interview start or before synthesis |
| `epic approve` / approve_spec | tight-spec step 5, actual user approval |
| `epic ticket --beads-epic-id` | to-tickets step 5, after beads publication |

The board skill also teaches `abandon`, `revive`, `epic abandon`, `epic revive`, `attach`, `detach`, `show` and `ls`. These are user-directed lifecycle/link/inspection operations, not unconditional workflow calls.

## Test evidence

Failing-first observations from `python3 skills/dispatch/scripts/test_pi_window.py`:

1. Identity test failed because pi inherited `inherited` / `old` rather than `pi` / `slice`. Exporting identity made it pass.
2. Metadata test saw only the pi launch, not the two dispatch calls. Adding explicit inputs and per-ticket dispatch made it pass.
3. Missing CLI test expected one warning and got four lines. The availability guard made it pass.
4. The hung CLI hit the ten-second test-runner timeout. The bounded sender brought the full suite back in about six seconds.
5. Quoted brief path test saw no pi process and a shell syntax error. Quoting the launch command made it pass.

Compatibility and guard coverage added afterward checks exit codes, report-marker survival, model spellings, relative paths, non-git workdirs, missing timeout and failed/duplicate launches. Those checks do not claim separate failing-first evidence.

Mutation checks ran copies of the scripts in temporary fixtures. All three deliberately wrong variants failed assertions:

```text
Caught mutation: wrong actor
Caught mutation: wrong dispatch verb
Caught mutation: lost model
```

The guide uses reference tables, required brief slots and conditional project-size steps. Baseline inspection found no board calls in the original workflow. Fresh-context behavior repetitions were not permitted; this report does not claim that agents reliably obey the text beyond the script seams tested here.

## Final checks

All commands exited 0:

```text
python3 skills/dispatch/scripts/test_pi_window.py -v
Ran 12 tests in 6.474s
OK

python3 scripts/check.py
43 skills, always-on ~1223/2500 tokens, 0 errors

bash -n skills/dispatch/scripts/pi-window skills/board/scripts/board-send
(no output)

git diff --check
(no output)
```

A real best-effort progress attempt returned `warning: board not installed; continuing` and exit 0. No delivery or dashboard state is claimed.

Changed: the five workflow skills, manifest, sender, launcher and tests listed above.
Verified: 12 process tests, three mutation checks, manifest gate, shell syntax and diff whitespace.
Not verified: live dispatch-to-committed card movement and draft idea-to-ticketed movement. The CLI is not installed; no deployment, credentials, bd state, git commit or harness configuration was changed. The coordinator retains both tickets and should run beads-board acceptance checks 3 and 6 after installation before closing their live-acceptance gap.
