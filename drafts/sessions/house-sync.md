# House sync session (sk-81s.14, sk-81s.6, sk-81s.9)

Nothing is committed and nothing was linked. I didn't touch ~/.claude, ~/.agents, or ~/.pi. The only writes to the sources were `git fetch` (via sync.py).

## sk-81s.14: uncovered upstream skills (closed)

| Upstream | Action | House |
|---|---|---|
| mattpocock:skills/engineering/retro | adopt | skills/retro |
| mattpocock:skills/engineering/wizard | adopt | skills/wizard |
| mattpocock:skills/productivity/wait-what | adopt | skills/wait-what |
| mattpocock:skills/in-progress/writing-beats | adopt | skills/writing-beats |
| mattpocock:skills/in-progress/writing-fragments | adopt | skills/writing-fragments |
| mattpocock:skills/in-progress/writing-shape | adopt | skills/writing-shape |
| mattpocock:skills/productivity/to-questionnaire | drop | Rarely needed. |
| mattpocock:skills/engineering/setup-matt-pocock-skills | drop | Replaced by beads plus the AGENTS.md tracker note. |
| mattpocock:skills/in-progress/chief-of-staff, claude-handoff, loop-me | drop (3 entries) | Covered by handoff and the coordinator model. |
| mattpocock:skills/in-progress/setup-ts-deep-modules | drop | TypeScript-only. |
| superpowers:skills/diagnosing-superpowers | drop | superpowers is being uninstalled. |
| **pstack:pstack/automations/benny** | **drop (provisional)** | The new scan found 3 SKILL.md dirs here (setup-benny, triage-issue-reports, reproduce-and-fix-issues). They are dormant Cursor automations for Slack bug reports. They weren't on the user's list, so the coordinator should confirm. |

**Edits to adopted copies.** Each adopted copy got only the provenance line `<!-- house: adopt; from: mattpocock:<path>@49dd158 -->` and a blank line after the front matter, the same format as handoff. `diff` against upstream shows only those two added lines for each SKILL.md. Every other file (`agents/openai.yaml`, wizard's `template.sh`) is identical (`diff -r` clean). None needed switching to adapt:
- retro: loads `writing-for-agents`, which the house set has. Like the other adopted skills, it says "Call the Skill tool"; pi resolves that through its own skill system. Its CODING_STANDARDS.md and reviewer-agent advice is general and pushes nothing.
- wizard: the `gh secret`/`gh variable` helpers in `template.sh` are optional. Without gh they fall back to a "set it manually" warning. Nothing commits or pushes. The skill commits a wizard only if the user wants a repeatable path.
- wait-what: uses `GLOSSARY.md` and `GLOSSARY-MAP.md`, both defined by the house domain-modeling skill.
- writing-*: self-contained (writing-fragments mentions grilling, which the house set has).

**check.py coverage rule.** New `upstream_skill_dirs(source, files=None)`, `ref_covers(pattern, path)` and `unmapped(catalog, source, dirs)`. Every dir holding a SKILL.md inside the source's checkout must be covered by some `[[skill]]`/`[[drop]]` ref, either as the dir itself or an ancestor, globs allowed. Without this, the rule would also count the other Cursor plugins as pstack upstream, so `[sources.pstack]` gained `scope = "pstack"` (only that subtree is the pstack plugin). sync.py feeds `upstream_skill_dirs` from `git ls-tree` at the new head, so the two scripts share one rule. I updated AGENTS.md to describe the rule and `scope`.

Negative test: I temporarily removed the to-questionnaire and benny drops, then restored them and confirmed with `cmp`:
```
FAIL upstream: mattpocock:skills/productivity/to-questionnaire has no [[skill]] or [[drop]] entry
FAIL upstream: pstack:pstack/automations/benny/skills/reproduce-and-fix-issues has no [[skill]] or [[drop]] entry
FAIL upstream: pstack:pstack/automations/benny/skills/setup-benny has no [[skill]] or [[drop]] entry
FAIL upstream: pstack:pstack/automations/benny/skills/triage-issue-reports has no [[skill]] or [[drop]] entry
39 skills, always-on ~1107/2500 tokens, 4 errors      (exit 1)
```

**Router.** flow gained lines for retro*, writing-fragments* → writing-shape*/writing-beats*, wizard (on its own description), wait-what*, and skills-sync*.

**Note for the coordinator (not acted on):** wizard is also installed at `~/.agents/skills/wizard`, a symlink to `~/dev/utils/skills/skills/engineering/wizard`. It is byte-identical to upstream. The cutover must replace it. `link.py` dry run already shows `relink ~/.agents/skills/wizard -> …/skills-house/skills/wizard` (same for ~/.claude and for retro).

## sk-81s.6: skills-sync (closed)

| File | What |
|---|---|
| scripts/sync.py | Fetches each source, resolves `origin/HEAD`, diffs `pin..head` limited to `scope`, and writes `reports/YYYY-MM-DD.md`. **adopt**: changed files plus a proposed `--bump`. **adapt/merge**: diffstat plus a diff of the referenced paths, capped by `--cap` (default 300 lines). **own**: skipped. **Unmapped**: reuses check.py's `unmapped`/`upstream_skill_dirs` on `git ls-tree head`. **Refs gone at the new head** is listed too. Flags: `--file-beads` (default off; label `sync`, parent is the open epic labelled `sync` if one exists), `--bump SOURCE COMMIT` (verifies the commit and writes the full sha into that source's block only), `--catalog`, `--out`, `--no-fetch`. |
| skills/skills-sync/SKILL.md | User-invoked (`disable-model-invocation: true`). Steps: report → read each digest against the house skill with a verdict per idea (adopt/adapt/drop) → beads after the user approves → apply, then bump the pin only when every candidate from that source is decided → check.py and a `--no-fetch` rerun. |
| catalog.toml | `scope` on pstack, plus `[[skill]] skills-sync` (own). |
| AGENTS.md | sync.py line rewritten to describe what it does. |

**Test 1, current pins (fetched).** mattpocock `49dd158..49dd158` and superpowers `bb92a77..bb92a77`: "No upstream changes since the pin." pstack `850d7f2..2f83774`: **real upstream changes**, 2 in-scope commits: `e5136d8` (restate four overspecified principles as reasoning, #633) and `99743e9` (cut marginal sections from four skills, #634). Those give 6 candidates: merge digests for tight-spec (interrogate/references/lead-judgment.md), principles (4 principle files), diagnosing-bugs, implement (swarm), tdd, and a re-vendor for adopted `correct` (1 line). The quickbooks commits elsewhere in the repo are excluded by `scope`; before I added the scoping, the log showed 11 commits. The report is in `reports/2026-10-16.md` (uncommitted). **No beads were filed.** Triage this pending pstack sync through `/skills-sync`.

**Test 2, temp catalog with the mattpocock pin at `49dd158~5` (`5b7cade`), `--no-fetch --out /tmp`.** It found 5 commits and 12 files changed. It produced digests for diagnosing-bugs (`f3fc563`) and code-review (`3da8c01`), plus `wizard (adopt): re-vendor, then sync.py --bump mattpocock 49dd158d1076` with stat `skills/engineering/wizard/template.sh | 28 +++…`. It also reported "9 changed file(s) outside any house skill's refs".

Other checks, all against temp catalogs or a fake `bd`:
- `--bump mattpocock 49dd158` on the temp catalog rewrote only the `[sources.mattpocock]` pin to the full sha. A bad commit (`deadbeef`) and an unknown source both exited with an error. The real catalog.toml still has the `49dd158d10…` pin.
- Unmapped: a temp catalog without the to-questionnaire drop produced an `### Unmapped upstream skills` section and a "decide new upstream skill" candidate.
- `--file-beads` against a fake `bd` on PATH: it queried `bd list --type epic --status open --label sync --json`, then ran one `bd create <title> -d "<changed files…> Report: <path>" -l sync --silent --parent <epic>` per candidate. Running `bd list --label sync` on the real tracker afterwards returned "No issues found."

## sk-81s.9: dispatch (left open, note added)

| File | What |
|---|---|
| skills/dispatch/scripts/pi-window | Moved from `bin/pi-window`, byte-identical (`diff` against `HEAD:bin/pi-window` is clean). `bin/` is now gone. |
| skills/dispatch/scripts/pi-wait | `pi-wait <window> <marker> [timeout=3600]`. Polls `tmux capture-pane -p -J -S -200 -t :<window>` every `PI_WAIT_INTERVAL` seconds (default 5). A line matches only if, trimmed of leading and trailing whitespace (per the coordinator follow-up), it equals the marker or `[pi exited] press enter`. Prints and exits 0 `DONE`, 3 `EXITED`, 4 `TIMEOUT`, 2 `GONE`, 1 usage or blank marker. If both lines are present, DONE wins. |
| skills/dispatch/SKILL.md | Model-invocable, one-sentence coordinator-only description. Covers: when to dispatch (pi window; Claude subagents only on user request), naming and marker convention, a brief template with every slot, launch, waiting with pi-wait in the background, follow-ups (`send-keys -l` then a separate `Enter`, one line), close-out (report → gate yourself → verify claims → commit only if asked → kill-window), and dispatch-from-ready (`fd … .beads` loop over `~/dev`, proposal table, no two writers per worktree). |
| skills/flow/SKILL.md | The operating-model line now points to `dispatch` instead of `bin/pi-window`. |
| catalog.toml | `[[skill]] dispatch` (own). |

Other references to `bin/pi-window` exist only in the historical briefs `drafts/briefs/house-decide.md` and `house-sync.md`. I left them as they are.

**pi-wait smoke test**, in throwaway window `piwait-smoke` (interactive bash, no pi). I typed `echo "brief: print SMOKE-DONE alone when done"; sleep 10; echo "   SMOKE-DONE  "; sleep 600` into it, so the marker appeared in the echoed command line and inside a longer output line:
```
phase 1 (t≈2s, timeout 4): TIMEOUT  exit=4   # pane had only the command line + "brief: print SMOKE-DONE alone when done"
phase 2 (timeout 30):      DONE     exit=0   # pane line 3 = "   SMOKE-DONE  " (leading spaces kept by capture-pane)
"  [pi exited] press enter " line (plus an inline mention): EXITED exit=3
after kill-window:         GONE     exit=2
pi-wait onlyone:           usage    exit=1;  blank marker: exit=1
```
After the test, `tmux list-windows | grep -c piwait` returned 0. `bash -n` passes on both scripts (shellcheck isn't installed). pi-window's argument checks still exit 2 from the new path (bad name, missing brief).

**Open:** the sk-81s.9 acceptance test needs the coordinator: launch a trivial pi session, read it with capture-pane, send a follow-up, and see the reply. The new SKILL.md wording hasn't been tested with fresh-context reps, which the writing-for-agents step 7 calls for; that needs subagents, which the user hasn't requested.

## Open / for the coordinator

- Confirm the provisional `pstack/automations/benny` drop.
- `reports/2026-10-16.md` holds 6 real pstack candidates (pins unchanged). Run `/skills-sync` to triage them, or delete the report if reports shouldn't be committed yet.
- `scripts/__pycache__/*.pyc` is tracked in git. sync.py imports check, which rewrites `check.cpython-314.pyc` and creates `sync.cpython-314.pyc`. I suggest untracking it and adding `__pycache__/` to .gitignore. I didn't do either.
- `.beads/interactions.jsonl` changed because of the bd claim/close/note calls.
- Always-on budget: ~997 → ~1142 tokens out of 2500 (wizard and dispatch are model-invocable; the rest are user-invoked).

## Final check.py

```
$ python3 scripts/check.py
41 skills, always-on ~1142/2500 tokens, 0 errors
```
