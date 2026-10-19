# sk-devbriefs — sk-9ro.3

## Changed

- `skills/dispatch/SKILL.md`: required browser-check brief slot, registered-app devserve command with explicit session ownership, URL/owner/evidence reporting, and unregistered-app fallback to separate ports/own databases. Coordinator cleanup is required before window teardown, including when the report mentions no previews.
- `skills/dispatch/scripts/preview-cleanup.py`: exact-owner selection from `devserve ls --json`; `down <unit> --drop-db` for every match; re-list verification. Missing CLI, invalid/failed listing, failed drop, and remaining previews return nonzero. No main-unit or other-owner cleanup. No shell interpolation. Failed cleanup leaves the window available for recovery.
- `skills/dispatch/scripts/test_preview_cleanup.py`: six CLI-boundary tests with a stateful fake devserve executable.
- Existing `drafts/briefs/sk-devbriefs.md` was present at start and untouched.

No commits, pushes, bd writes, subagents, config changes, or real app previews were performed.

## Commands sessions and coordinators run

For a registered app, from its dispatched worktree (example window `foreman-browser`):

```sh
FOREMAN_SESSION=foreman-browser devserve up
devserve ls --json
```

Open the printed URL for browser checks. Confirm the preview's worktree and owner, then record unit, URL, database and actual browser evidence in the report. `pi-window` already exports FOREMAN_SESSION; spelling it out prevents an OS-username fallback. Registration is determined from config, not solely from currently running units. On this machine `devserve ls` lists foreman main services.

Coordinator, after review and before killing the window:

```sh
D=~/dev/utils/skills/skills/dispatch/scripts
python3 "$D/preview-cleanup.py" foreman-browser && tmux kill-window -t :foreman-browser
```

The helper executes `devserve ls --json`, `devserve down <unit> --drop-db` for each exact owner match, then `devserve ls --json` again. A failure blocks the kill. Stop browser work first; concurrent new preview creation is not synchronized by this adapter.

## Verification

TDD seam: helper CLI versus devserve subprocess boundary. The first stub returned success without cleanup: the test failed because both owned previews remained. After implementation it passed. Additional tests then failed on empty owner and malformed listing (including a partial drop before discovering an invalid row); validation was added before mutation.

Final commands and results:

- `python3 -m unittest discover -s skills/dispatch/scripts`: **34 tests, OK** (15.960s).
- `python3 scripts/check.py`: **45 skills, always-on ~1262/2500 tokens, 0 errors**.
- `git diff --check`: exit 0, no output.
- `python3 skills/dispatch/scripts/preview-cleanup.py sk-devbriefs`: exit 0, `Cleaned previews for sk-devbriefs`.
- Real `devserve ls --json` after that check: `previews: []`; foreman-web.service and foreman-worker.service both active.

Tests cover multiple exact-owner matches including a failed preview, a similar-but-different owner, main-unit exclusion, idempotent empty cleanup, malformed JSON/schema, missing CLI, failed listing/drop, and a successful down that nevertheless leaves a preview registered. Actual nonempty systemd/Postgres cleanup was not exercised in this session; its CLI contract is consumed rather than reimplemented.

## Standards review

Reviewed sequentially against `98fc0933b8a85adcdee77a6747ce0298229e4e27`, including the requested uncommitted implementation and both new files. HEAD has no commits beyond that base, so a committed three-dot review alone would be empty. Applied AGENTS.md, writing-for-agents guidance and the review standards baseline.

No remaining code findings. The helper is a stateless CLI adapter; the existing devserve lifecycle remains the state-machine authority. Selection is exact, mutations use argv arrays, input is validated before dropping, errors block teardown, and tests observe the public CLI boundary.

Declined to judge: repeated fresh-agent behavior trials (no subagents authorized). The baseline gap is visible in the old template: no browser-check slot or preview teardown. The chosen form is a required slot plus an observable registration condition and an executable teardown gate. No claim of measured before/after agent compliance.

Verdict: Ready for coordinator review on Standards.

## Spec review

Decision 8 and the first two ticket criteria are implemented. The prior generic template contained no literal “use another port” sentence to replace; the new slot selects devserve for registered apps and preserves that guidance only for unregistered apps. Gate criterion passes.

**Important / open: acceptance check 6 is not yet verified.** The ticket explicitly requires the next real dispatched build to use the preview and leave no preview/database. This skills-only dispatch is not an app browser check. Keep sk-9ro.3 open until that evidence exists; do not count the empty-registry smoke check or fake CLI tests as check 6.

Declined to judge: app-specific preview write isolation and devserve database ownership implementation (prior tickets, unchanged here).

Verdict: implementation ready for coordinator review; full ticket acceptance pending check 6. Findings: Standards 0; Spec 1 Important verification gap.

## Check 6: next real dispatch

1. Dispatch actual browser-related work in a registered foreman worktree with the new brief slot and a unique session/window name. Run the session commands above there.
2. Capture the preview unit, database, owner, worktree and URL from `devserve ls --json`. Open the printed URL using the normal browser tool; save screenshot/DOM evidence of the ticket's browser check, not just TCP health.
3. Coordinator reproduces the browser claim and records the exact database name before teardown. Run the helper and require exit 0 before killing the window.
4. Save the final `devserve ls --json` showing no owner matches. Using the operator's existing authorized PostgreSQL connection (without logging secrets), query `pg_database` for each captured database name and require zero rows. Confirm the captured unit is gone and main services remain active.
5. Attach those artifacts to sk-9ro.3; only then close its remaining acceptance criterion.

Residual limitations inherited from devserve: reboot can erase systemd registry metadata while leaving a kept database; this helper does not discover such orphan databases. Do not infer orphan absence from an empty registry after reboot. No scratch preview was needed or started.
