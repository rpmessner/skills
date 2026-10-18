# sk-wiring: fm-zgd.6

Text acceptance is ready for coordinator review. Live checks 5 and 9 remain for a real dispatch, as requested. No commits, pushes, ticket edits, bd writes, subagents, or harness changes.

## Changes per skill

- `skills/dispatch/SKILL.md`: the inline brief template sends unanswered build questions through direct decision asks and long waits. IDLE remains fallback detection, not a reason to interrupt a pending board wait. Close-out posts push after an authorized commit, waits for completion, then requests open_pr where the repo uses PRs. Merge requests use the existing confirmation flow when merge is next. One chat notice replaces terminal push/PR questions. Required requests resolve before ticket closure and window cleanup.
- `skills/foreman/SKILL.md`: documents all four ask kinds, the shared wait command, seconds-based timeout, UUID and JSON responses, exit-zero failure handling, and each outcome's next step. Separates approval requests from the five-second best-effort sender. Covers snapshot refresh, default-branch restrictions, forge-none, and unknown outcomes.
- `skills/flow/SKILL.md`: routes build questions and close-out through requests. Limits nonblocking warnings to telemetry. Spec interviews and grilling remain conversational.

All three retain the agents-never-push rule and point to board requests. No helper was needed: the CLI already builds the request facts. No production code changed, so TDD was not applicable.

The coordinator-owned `drafts/briefs/sk-wiring.md` was present on entry and is untouched.

## Commands for a build session

Substitute the ticket and question/options. Add `--project <configured-project>` if resolution needs it.

```sh
foreman ask decision <ticket> \
  --question "Which layout should the build use?" \
  --option "Wide" --option "Compact" --recommendation "Compact" \
  --text "Keep the existing keyboard shortcuts."
foreman wait <returned-request-id> --timeout 7200
```

The ask returns a UUID. Wait returns JSON. Only `state: answered` resumes the question-dependent work, using `outcome.answer` and `note`. A pending timeout means repeat the wait with the same ID, not the ask. Decline or withdrawal stops that work. A warning is not an answer.

For durable offline diagnostics, add `--json` to ask. The response includes `id` on acceptance or `warning` and `request_id` for a spooled ask. Plain warning output omits the spool ID. If no ID is available, report the unresolved ask before posting another.

Milestones and reports still use the best-effort sender, not the approval path:

```sh
bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send progress <ticket> "<milestone; next step>"
bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send report <ticket> --path <report>
```

## Commands for the coordinator

These are commands to run later, not actions performed in this session. Use the actual worktree, configured project, ticket, and intended destination. Keep actor/session identity set for the coordinator.

After review, gates, and an explicitly authorized commit:

```sh
bash ~/dev/utils/skills/skills/foreman/scripts/foreman-send commit <ticket> --sha <actual-commit-sha>
git -C <worktree> branch --show-current
git -C <worktree> rev-parse HEAD
foreman ask push <ticket> --project <configured-project> \
  --worktree <absolute-worktree> --branch <actual-local-branch> \
  --sha <full-sha> --remote-branch <intended-destination>
foreman wait <push-request-id> --timeout 7200
```

Run the coordinator wait through the harness's background-command facility, then consume its JSON before the next step. Tell the user once: "Close-out requests are waiting on the board." Detached HEAD, refusal, warning, or a non-done outcome blocks dependent publication. Retain the request IDs.

After push `state: done`, and after the board has observed the new remote head, request the PR where the repo uses PRs:

```sh
foreman ask open_pr <ticket> --project <configured-project> \
  --head <pushed-destination> --sha <published-full-sha> \
  --base <repo-or-stack-base> --title "<reviewed-title>" \
  --body-file <reviewed-body.md>
foreman wait <open-pr-request-id> --timeout 7200
```

Wait in the background and consume `state: done`. Inspect an existing matching PR instead of requesting a duplicate. If merging is next, use its current expected head:

```sh
foreman ask merge <ticket> --project <configured-project> \
  --pr <number> --sha <expected-head-sha>
foreman wait <merge-request-id> --timeout 7200
```

The user approves and confirms on the board. Approval alone is not completion. Failed or partial outcomes require observation before a replacement request, never an agent-side forge command.

A forge-none repo ends at commit. Default-branch pushes are only for one-off tickets without an epic. Epic work uses PRs. Do not close tickets while requests are pending. If later ticket-closure changes need publication but no eligible committed ticket remains, report that policy blocker rather than fabricating events. This wiring does not change tracker or committed-stage policy.

## Verification

`drafts/sessions/sk-wiring-cli-check.json` records 21 calls to the installed `foreman` executable against a temporary in-memory loopback API. The fixture server returned scripted responses and captured request bodies, never headers or credentials. It is stopped. No board, database, or forge write occurred.

The dry run checked:

- Exact decision, push, open_pr, and merge fact shapes, plus inherited actor/session and explicit project.
- UUID ask output and JSON ask output. The PR body retained its trailing newline.
- `wait --timeout 0` returned pending without treating it as completion.
- `wait --timeout 7200` polled pending then returned answered or done for each kind.
- Approved, executing, declined, withdrawn, failed, and superseded JSON stayed distinguishable, including notes.
- A creation refusal returned a warning with exit 0. Unavailable wait returned a warning with exit 0.

All 21 commands exited 0 and their response assertions passed. This proves CLI syntax, serialization, and outcome handling, not the board's guards, worker execution, or agent compliance. The four implementation reports and current CLI source supplied those contracts. No fresh-context behavioral repetitions were run because this brief prohibits subagents and explicitly assigns live behavior checks to the coordinator. The reported unseen pane questions in the approved spec are the existing failure evidence.

## Standards review

Baseline `0fa47daa7a81654f4d239b496f1dfffc121e7dc2` equals HEAD. The three-dot diff and commit list are empty. As requested, self-review covered the uncommitted skill diff against that baseline. Standards ran before Spec, in this session without subagents.

The skills keep one owner for CLI details and outcome rules: `foreman`. Dispatch owns ordering and the brief. Flow remains a router. Descriptions stay trigger-based, and no new skill or abstraction was added.

Fixed during review:

- The new Foreman section initially described sender output as swallowed. `foreman-send` preserves output and masks exit status; the text now says that.
- It initially implied plain ask warnings preserved the spool ID. Current CLI formatting omits it. The text now requires JSON for offline receipts.

No open Critical or Important Standards finding. Declined to judge unrelated skills and existing sender/launcher implementation. Verdict: ready for text review.

## Spec review

Checked fm-zgd.6 and approved Decisions 6–8 and 11 after Standards completed.

- Brief decision ask and wait: present, with no pane question and no exit-zero-as-answer shortcut.
- Close-out push and PR asks: ordered after authorized commit and before closure. Push completion precedes open_pr creation. Merge is conditional on the workflow's next step.
- All kinds and wait: documented in Foreman with exact shipped flag names.
- Agents never push: retained. No hook or agent-side publication command was added.
- check.py: passed, output below.

Review clarified that a request blocker leaves close-out open and the window available. Ticket-file closure can create another publication obligation; the text reports that policy blocker instead of bypassing committed-stage guards.

No open Critical or Important text/code finding. Declined to judge live checks 5 and 9, installed deployment, and actual worker actions, all reserved for coordinator verification. Verdict: ready for coordinator live checks, not full ticket closure.

## Live checks for the coordinator

### Check 5: real build decision

Dispatch a real pi session using the updated brief template and a genuine bounded question. Record the ask ID and the pane waiting on `foreman wait`. Answer through Needs you, without tmux input. Capture the pane receiving `state: answered` with the chosen answer and continuing the dependent work. Record request JSON, pane transcript, and resulting artifact. An IDLE notification during the wait must not cause a duplicate ask or pane answer.

### Check 9: real dispatch close-out

Use the next eligible committed ticket on a forge-enabled feature branch. Record its branch and full SHA. Follow the push request, board approval, and completed wait. Confirm the remote branch at that exact SHA. Then request the PR, approve on the board, wait, and confirm head/base/title/body and the observed PR stage. Preserve request IDs and audit evidence. The terminal should contain one board-wait notice and no push or PR approval question.

Prove the existing hook blocks an agent's direct push using a locally controlled, no-network fixture through the actual agent bash tool. A safe probe is `git -C <local-scratch-repo> push --dry-run <local-bare-remote> HEAD:refs/heads/hook-probe`. Require the hook's denial, not a Git configuration error. Dry-run and a local bare remote prevent an accidental network write if the hook regresses. Do not disable or edit the hook. This probe was not run here because this session forbids pushes and reserves check 9 for the coordinator.

## Final gate

Fresh run after the edits and both review axes:

```text
$ python3 scripts/check.py
45 skills, always-on ~1262/2500 tokens, 0 errors
exit 0

$ git diff --check
no output
exit 0

CLI evidence assertions
21 exit-zero calls, all four request kinds
```

Changed: dispatch, foreman, and flow guidance, plus this report and the CLI transcript.
Verified: the skill gate, whitespace check, CLI dry run, and sequential self-review.
Not verified: real pi continuation, real close-out publication, and direct-push hook denial. The coordinator owns live checks 5 and 9 and ticket closure.
