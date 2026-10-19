# sk-piwait: fm-3c3.5

Implementation and requested checks are complete. **Hold global enablement for the Foreman outage/replay issue below.** No worktree commits, pushes, ticket edits, bd writes, subagents, or global pi configuration changes.

## Changed

- `pi/foreman-wait/index.ts` and `package.json` add the extension. A declared transition table separates active work, settled questions, UI input, permission, and usage-limit waits.
- `skills/dispatch/scripts/pi-window` exports its existing `--bead` IDs as `FOREMAN_TICKETS`. The extension needs those IDs plus `FOREMAN_ACTOR` and `FOREMAN_SESSION`; untracked sessions remain inert. Multiple tickets are supported and duplicate IDs are suppressed.
- `pi/foreman-wait/test.ts` tests event-to-CLI behavior and failure isolation. `skills/dispatch/scripts/test_pi_window.py` verifies the added launch metadata.
- `pi/foreman-wait/live-check.py` and `fixtures/prompts.ts` provide a repeatable live pi check. `README.md` records the API, enablement, clearing contract, and fallback limits.

Native pi 1.3.0 events were verified in the installed documentation, declarations, and runner implementation. `ui_prompt_start` maps `confirm` to permission and other dialog kinds to input. `ui_prompt_end` clears only the UI wait, so sibling tool activity cannot clear a still-open permission prompt. Pi emits one outer start/end pair for nested dialogs.

`agent_settled`, not `agent_end`, gates natural-language questions and provider-limit errors. This avoids waiting notices during automatic retries. A final question mark identifies a text question. Ordinary completion remains IDLE fallback. Usage-limit matching reads only assistant errors, never successful text. Requests include the error message's provider, but no reset time is guessed.

Waits use the requested `foreman ask session_waiting ...` command. Clears use `foreman session-hook UserPromptSubmit ...` with `{}` on stdin; that is the inspected CLI route to `session_resumed`. Both carry the same actor, session, and window. No tool or question text is transmitted. The extension never approves permissions or sends Continue; Foreman owns that explicit default-socket action.

## Verified

| Check | Result |
| --- | --- |
| `node pi/foreman-wait/test.ts` | 10 tests passed |
| `python3 skills/dispatch/scripts/test_pi_window.py` | 12 tests passed |
| `node pi/house-guard/test.ts` | All checks passed |
| `python3 pi/foreman-wait/live-check.py drafts/acceptance/sk-piwait` | Real pi/Codex question and resume passed; native confirmation and input dialogs passed |
| `python3 scripts/check.py` | 45 skills, about 1262/2500 description tokens, 0 errors |
| `git diff --check` | Clean |

Evidence is in [`drafts/acceptance/sk-piwait`](../acceptance/sk-piwait/). The final [live result](../acceptance/sk-piwait/result.json) records exactly one `input` ask for "Which color should I use?", followed by one clearing call after the answer. Each live UI fixture then produced one ask and one clear. The fake CLI log has six calls total. The real model's second response was "Acknowledged." and did not create a new wait. RPC emitted no extension errors and stderr was empty. Global settings hashes matched.

The live runner used an isolated agent directory and scratch cwd beneath this worktree, no tools, and no persisted session. It read existing Codex credentials through `auth check --credentials --no-refresh`; the temporary owner-only credential file was removed. Scratch agent, CLI, and cwd directories were cleaned after verification. Logs remain. No real Foreman request or tmux input was sent.

### Failing-first evidence

The test command was `node pi/foreman-wait/test.ts` for each extension slice:

- The initial empty extension failed the question assertion with `calls: []`, then passed after question posting and resumed clearing were implemented.
- UI confirmation and input tests failed because no corresponding CLI calls existed, then passed after native prompt handlers were registered.
- The usage-limit branch was removed before its test. The new assertion failed because no limit request existed, then passed with settlement classification and turn-start clearing.
- Shutdown clearing failed with the ask present but no clear, then passed after the shutdown handler.
- A child-exit safety test failed because a hung CLI outlived pi beyond 7.5 seconds. Replacing a parent-owned timer with GNU `timeout -k 1 5` fixed it. The final test observes forced termination at about six seconds even when the fake CLI ignores SIGTERM.
- Launcher identity tests failed with `FOREMAN_TICKETS` absent, then passed after the single launch-line change.

Missing-CLI, ordinary completion, abort/recovery, duplicate-ticket, and untracked-session cases are additional regression coverage, not all claimed as separate red-first slices. Three temporary source mutations were killed by assertions: confirmation mapped to input, removed limit classification, and removed resume clearing. See [mutation results](../acceptance/sk-piwait/mutations.txt).

Initial live attempts exposed two credential setup facts, now documented in the README. `--no-refresh` is supported only by `auth check`; an inline `--api-key` did not authenticate Codex in the isolated agent directory. The final live run passed after correcting the runner, without changing global configuration.

## Review scope

The fixed point `4a024fa36a56530825197f950a4b928cf55db083` is HEAD. `git diff <base>...HEAD` and the commit list are empty because this session cannot commit. Review therefore covers the explicitly requested working-tree changes and new deliverables. The coordinator-owned `drafts/briefs/sk-piwait.md` is excluded. Axes ran sequentially without subagents.

## Standards

Read the root AGENTS.md, existing house-guard code/tests, and the standards baseline. There are no deeper pi instruction files. The waiting lifecycle is declared as a table with a pure step and effects returned as data. The adapter starts no processes in the extension factory, has no runtime package dependency beyond Node, and uses the installed event names. Launcher work is limited to ticket identity propagation.

No open Standards finding. Declined to judge unrelated skills and the existing launcher architecture. Verdict: Ready.

## Spec

All requested executable checks passed. The CLI receives `input`, `permission`, and `usage_limit`, plus the specified session/window identity. Resumed activity clears settled waits; UI answers clear UI waits. There is one warning rather than an exception when the CLI is absent. The global installation remains untouched, as requested.

Fallback limits are explicit. Text questions must end in a question mark, allowing closing Markdown or quotes. Unknown provider error wording falls back to pi-wait. A custom/select permission UI is classified as input because pi's event supplies a UI kind, not a permission classification. Core project-trust UI is outside extension dialog events. Abrupt exit can lose a queued clear, so Foreman's window/activity reconciliation is still required.

No open finding against the stated executable acceptance checks. Declined to judge actual account exhaustion, installed deployment, and Foreman's Continue UI, which this task does not change. Verdict: Ready for coordinator review, with fallback limits documented.

## Risk

The safety fact is that no pi event handler waits for Foreman. `pi/foreman-wait/index.ts:25-45` uses asynchronous spawn, catches process failures, discards CLI output, and lets GNU timeout own the five-second deadline plus one-second kill grace. The one-warning notifier also catches UI failures. There is one serialized sender with a latest desired state, not an unbounded queue. Argument arrays avoid shell interpolation.

Proof level 4 for failure isolation. The fresh focused run passed all three checks in [risk-tests.txt](../acceptance/sk-piwait/risk-tests.txt): missing CLI, hung CLI with an immediately returning handler, and termination after the parent pi process exits. The latter fake ignores SIGTERM and still terminates at about six seconds. Proof level 5 for native question/UI event delivery comes from the real pi RPC run.

**Important: resolve before global enablement.** The ask at `pi/foreman-wait/index.ts:81` uses Foreman's ordinary overlay command. In the inspected Foreman source, `lib/foreman/cli_transport.ex:9` bypasses spooling only for transient or read requests, while `lib/foreman/cli.ex:88` marks only the session-hook route transient. The clear at `pi/foreman-wait/index.ts:83` uses that route. If an ask is spooled during an outage and the clear is dropped, replay can create a stale waiting card after pi resumes. This is likely only during service outages, but it can wrongly offer Continue later. Make `session_waiting` asks transient in Foreman, or add a supported transient ask option and use it here. An outage/recovery regression belongs in the Foreman repo; no out-of-worktree fix was made.

Cleared: blocking event callbacks, unhandled missing executable, indefinite child lifetime after parent exit, repeated warning spam, shell interpretation of CLI arguments, duplicate ticket IDs, and permission waits cleared by sibling activity. Remaining best-effort limits are lost shutdown clears and exit-zero CLI refusals, which cannot be treated as delivery acknowledgment.

Declined to judge real board outage/replay behavior end to end, malicious replacement of PATH executables, actual quota exhaustion, and browser Continue behavior. Verdict: **Not ready for global enablement until the upstream replay issue is resolved or explicitly accepted.** No Critical finding. Cheapest repeat safety gate: `node pi/foreman-wait/test.ts`.

Review summary: Standards 0 findings; Spec 0 executable-acceptance findings with documented fallback limits; Risk 1 Important integration finding.

## Coordinator next steps and exact enablement change

1. Resolve or explicitly accept the Foreman transient-ask mismatch. Keep pi-wait IDLE/LIMITED fallback enabled.
2. Review and integrate the uncommitted files. Relaunch build windows through the updated `pi-window` so they inherit `FOREMAN_TICKETS`.
3. Append this exact string to the existing `packages` array in `~/.pi/agent/settings.json` after integration into the canonical skills checkout:

```json
"~/dev/utils/skills/pi/foreman-wait"
```

For this worktree instead, the exact package entry is `"~/dev/utils/sk-piwait/pi/foreman-wait"`. Preserve every existing package entry. This session made neither settings change.

Changed: the extension, launcher metadata, tests, live-check runner, README, and evidence/report files listed above.

Verified: 10 extension tests, 12 launcher tests, existing house-guard checks, real pi question/resume and UI dialogs against fake Foreman, three mutation checks, check.py, and diff whitespace.

Not verified: real Foreman delivery/outage recovery, real provider exhaustion, terminal rendering, installed enablement, or browser Continue. The live UI check used native RPC dialogs rather than a TUI screenshot. All verification pi processes exited and temporary credentials were removed.
