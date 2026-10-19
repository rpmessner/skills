# foreman-wait

Best-effort attention notices for tracked pi build sessions. Requires pi 1.3.0's
`ui_prompt_start`, `ui_prompt_end`, and `agent_settled` events, Foreman's
`session_waiting`/`session-hook` CLI, and GNU `timeout` on PATH.

## Enable after review

Append `"~/dev/utils/skills/pi/foreman-wait"` to the existing `packages` array in
`~/.pi/agent/settings.json` after integrating this worktree. Do not replace the
array. For a single run from this worktree:

```sh
FOREMAN_ACTOR=pi FOREMAN_SESSION=my-window FOREMAN_TICKETS='fm-123' \
  pi -e ./pi/foreman-wait
```

`pi-window --bead <id>` now exports its IDs as whitespace-separated
`FOREMAN_TICKETS`, including multiple tickets. No IDs, actor, or session means
no notifications. Existing pi processes need a relaunch with this metadata.
The extension never infers a ticket from prompt text or the current branch.

## Event mapping

| Pi observation | Foreman action |
| --- | --- |
| Blocking `confirm` dialog | `ask session_waiting <ticket> --reason permission` |
| Blocking `select`, `input`, `editor`, or `custom` dialog | Same, with `--reason input` |
| Successful settled assistant text ending in `?` (optional closing Markdown/quotes) | Same, with `--reason input` |
| Settled assistant error mentioning usage/rate limit, quota, extra usage, or HTTP 429 | Same, with `--reason usage_limit` and the message's provider |
| Dialog ends | `session-hook UserPromptSubmit <ticket>`, stdin `{}` |
| Agent/turn starts after a settled question or limit | Same clearing hook |
| Session shuts down | Best-effort clearing hook |

Every command includes `--session`, `--window` (both `FOREMAN_SESSION`) and
`--actor` (`FOREMAN_ACTOR`). The clearing hook is Foreman's existing CLI route
to `session_resumed`; there is no direct `session_resumed` CLI verb.

No question text, command text, error text, credentials, or arbitrary terminal
input is sent. This extension never approves a prompt or sends Continue.
Foreman owns Continue, including its explicit default tmux socket selection.

UI waits survive unrelated parallel tool activity. Only `ui_prompt_end` clears
them. Pi's runner emits one outer prompt start/end pair for nested dialogs.
Settlement, rather than `agent_end`, prevents notices during automatic retries.
Repeated identical waits are suppressed. A single asynchronous sender serializes
requests and coalesces intermediate states; it does not accumulate an event queue.

Handlers never await the CLI. Each call has a five-second deadline plus one second
for forced termination, owned by `timeout` even if pi exits. Missing executables,
nonzero exits, and timeouts produce at most one UI warning per extension runtime.
CLI stdout/stderr are discarded; an exit-zero Foreman refusal is not confirmation
of delivery. There are no delivery retries or persistent extension files.

## Limits and fallback

- Natural-language detection is deliberately narrow. Questions without a final
  question mark, non-English punctuation, and unknown provider-limit wording fall
  back to pi-wait's IDLE/LIMITED detection. Ordinary completion does not post a wait.
- `confirm` means permission; other dialog kinds mean input. Pi supplies no semantic
  permission tag for a custom/select dialog. Startup project-trust UI is not an
  extension dialog and remains a coordinator/fallback concern.
- Shutdown clearing can be lost if pi exits while an earlier delivery is in flight.
  Foreman's window/activity reconciliation remains necessary.
- **Coordinator follow-up before enabling:** the inspected Foreman CLI can spool
  `ask session_waiting` during an outage, but `session-hook UserPromptSubmit` is
  transient. A late replay can recreate a stale wait. Foreman should make
  `session_waiting` asks transient too; this repo cannot change that CLI contract.

## Verify

```sh
node pi/foreman-wait/test.ts
python3 skills/dispatch/scripts/test_pi_window.py
python3 pi/foreman-wait/live-check.py drafts/acceptance/sk-piwait
python3 scripts/check.py
```

The live check runs real pi and Codex with a fake foreman, then exercises native
confirmation/input dialogs over RPC. It checks one question request and its
clearing, then one request/clear pair per dialog. It uses a scratch agent directory,
no tools, no persisted session, and checks that global settings are unchanged.
It requires a currently valid Codex login: `auth check --credentials --no-refresh`
reads it without refreshing. `--no-refresh` is not supported by the credential-print
subcommands despite the broad CLI documentation. Codex needs an OAuth credential;
`--api-key` alone did not authenticate it in the isolated agent directory. The
runner creates an owner-only temporary credential file and removes it on exit.
Do not interrupt it with SIGKILL while that file exists.
