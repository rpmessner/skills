# sk-fkb — pane-mode dispatch

## Changed

- `skills/dispatch/scripts/pi-window`: `--pane <name>` splits the caller's `$TMUX_PANE` window, sets pane-local `@build` and title, tiles the window and retains coordinator focus. Duplicate checks reject existing windows or tagged build panes. Default window launch/output remains unchanged.
- `skills/dispatch/scripts/pi-pane`: resolves exactly one tagged build in the current session to a stable `%pane-id`; missing/ambiguous names fail closed.
- `skills/dispatch/scripts/pi-wait`: `--pane` resolves once, captures that pane, and checks its continued existence. Existing marker baseline, limit, trust, idle and exit handling is shared without changing window targeting.
- `skills/dispatch/SKILL.md`: epic coordinators use panes; main coordinator keeps windows. Added name-based capture/input and cleanup-before-`kill-pane` recipes. Preview cleanup itself is unchanged: its exact owner is the logical build name in either mode.
- `skills/foreman/SKILL.md`: documented the metadata contract. The existing CLI accepts `--window`, not `--pane`; pane dispatch sends `%pane-id` through `--window`. `FOREMAN_SESSION` remains the logical name. Board focus implementation belongs to fm-3c3.8.
- Fake-tmux tests cover pane launch metadata, tag/title/target, duplicate refusal in both modes, DONE/LIMITED/BLOCKED/IDLE, missing/disappearing panes and ambiguous tags. Existing window tests still run.
- Added `skills/dispatch/scripts/scratch-pane-check.py`, a repeatable real-tmux probe using a unique `tmux -L pane-check-*` server, stub pi and config-free zsh. It never connects to default or foreman servers.

## Evidence

Failing-first slices:

1. Pane launch test failed with `2 != 0: window name must be short kebab-case: --pane`; adding pane launch made the pi-window suite pass.
2. Duplicate-pane test failed with `0 != 1`; adding tagged-pane duplicate refusal made it pass for both launch modes.
3. Pane wait suite failed all 12 cases before implementation (usage rejection instead of expected status); adding pane resolution/targeting made the inherited wait contracts pass.

Two mutation checks on disposable copies rejected removing the pane tag and replacing the resolved wait target with the window target.

Final gate command:

```bash
python3 scripts/check.py
python3 -m unittest discover -s skills/dispatch/scripts -p 'test_*.py'
python3 skills/dispatch/scripts/scratch-pane-check.py
foreman check
bash -n skills/dispatch/scripts/pi-window skills/dispatch/scripts/pi-wait skills/dispatch/scripts/pi-pane
git diff --check
```

Final gate output (full transcript: `drafts/sessions/sk-pane-mode-gates.txt`):

```text
46 skills, always-on ~1290/2500 tokens, 0 errors
Ran 50 tests in 24.228s
OK
build-one: found %1, wait DONE
build-two: found %2, wait DONE
duplicate build-one refused
build-one killed: GONE; build-two and coordinator intact; one window
scratch acceptance PASS
tickets valid
```

Shell syntax and diff whitespace checks exited 0 without output. The scratch probe additionally asserts both titles/tags, a single shared window, and unchanged coordinator focus before teardown. All scratch resources are removed in `finally`.

## Sequential self-review against f7c91ac

Base: `f7c91ac441fa3303307303cd1dcfe02920302730`. HEAD is still the base: no commits were made. Per the brief, reviewed the working-tree diff against that base plus both new script files rather than an empty committed three-dot diff. Axes ran in this session, without subagents.

### Standards

Reviewed root instructions, skill-writing references and review baseline. No Critical or Important findings. The launch mode is a fixed option with no transitions; existing wait lifecycle semantics were preserved rather than refactored. New helper has a single job: resolve pane tags. No remaining Minor findings.

Declined to judge: refactoring the pre-existing wait loop into a new state-machine implementation; not part of this adapter change.

Verdict: Ready.

### Spec

Checked each sk-fkb behavior/acceptance item against tests and scratch assertions. Fixed a stale phrase in `skills/dispatch/SKILL.md` that said only duplicate windows were refused; it now says duplicate build names. Explicit pane launch/wait flags, name resolution recipes, per-pane teardown and metadata are present. Tiled layout is the chosen readable layout, preserving coordinator focus. No Critical/Important findings or remaining Minor findings.

Declined to judge: board select-window/select-pane implementation, explicitly assigned to fm-3c3.8.

Verdict: Ready.

### Risk

Safety fact: pane operations bind stable IDs resolved from exact tags and close-out kills only that pane; they do not target the coordinator window. Proof level 4: shipped scripts exercised against real scratch tmux, with assertions that the sibling and coordinator remain after teardown. Fake tests enforce `%12` capture targets and unchanged `:build` window targets. Added disappearing-pane and ambiguous-tag tests to strengthen the failure boundary; all 50 tests pass. Metadata tests verify `%12` is sent through the existing CLI field and unchanged window calls keep their exact metadata arguments.

Cleared: accidental window teardown, wrong capture target, ambiguous tag capture, window wait regression, and logical preview-owner changes. No Critical/Important findings remain.

Declined to judge: live pi provider behavior and actual board focus UI (pi is intentionally stubbed; board focusing is separate scope). Existing duplicate-check/launch operations are not atomic across concurrent launchers; docs require sequential dispatch. No new concurrency lock was added.

Verdict: Ready. Cheapest pre-merge checks are the dispatch unittest suite and scratch probe above.

## Open / not verified

- No in-scope acceptance gaps or new tickets requested.
- Live tmux servers, real pi sessions, board focus UI and real devserve teardown were intentionally not exercised. Fake process-boundary tests cover board arguments and existing preview cleanup behavior; scratch tmux covers real targeting and teardown.
- No installs, harness linking, sync, repository commits or pushes. Existing tests use isolated fixture Git repositories.
- Ticket remains `in_progress`; coordinator owns closure and any authorized commit.
