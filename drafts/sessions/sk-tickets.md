# sk-tickets: fm-axu.4

Implemented for coordinator review on branch `sk-tickets`. No commits, pushes, bd writes, subagents, real ticket edits, migrations, or edits to the house AGENTS file. The coordinator's brief is unchanged. Temporary repositories contain the only ticket writes.

## Changes by skill

- `to-tickets`: detects the tracker before reading or publishing. Added `references/files.md` with the direct `new`/`check` recipe and `scripts/publish-demo.py`, which executes that recipe against the real CLI. Kept `references/beads.md` for unconverted repos and removed the old scratch-file fallback. An untracked repo now asks for approved onboarding.
- `dispatch`: briefs name the detected tracker, claims and closure use the corresponding commands, and ticket creation remains coordinator-owned. The legacy launcher flag still works. Added `scripts/ready-repos.py` and `scripts/test_ready_repos.py` for mixed-repo discovery and JSON listings.
- `wayfinder`: maps, decisions, labels, dependencies, claims, notes, body updates and closure have files and beads commands. Files use `in_progress` instead of an assignee claim. Notes preserve the question and map updates preserve existing decisions.
- `foreman`: separates direct offline ticket commands from best-effort board events. Added onboarding guidance and explicit overlay reads. Documented the existing board epic flag's compatibility with file ids.
- `flow`: routes the planning frontier through the detected tracker and distinguishes ticket writes from board events.

No edits to other skills or local tracker setup. This repo remains on beads until its own approved `foreman adopt`.

## Evidence

The initial `foreman --help` printed a usage warning pointing to the old `bb-cli.md`; it did not enumerate ticket commands. I checked `bb-files.md`, `fm-adopt.md`, the approved spec, and the current CLI source, then exercised the installed CLI. The source confirms ready requires every blocker to be closed and that `ready --parent` is not supported.

### Ready listing

The public seam is the script's process output for fake filesystem repos and fake tracker executables. The tests cover both tracker types, both directories in one repo, paths with spaces, linked-worktree `.git` files, missing CLI, warning/non-JSON responses, wrong JSON shape, healthy output after a failed repo, dependency-tree exclusions, depth limit, and files-only execution without bd installed.

Observed RED with the empty implementation: one assertion failure, `[]` instead of the two expected repo records. After routing passed, failure-handling tests produced three assertion failures: missing repo context and failure to reject a non-list response. GREEN: all three ready-list tests pass. The files-only exclusion test passed on first run; it covers existing behavior rather than claiming a separate RED.

Mutation checks rejected all three deliberate breaks: ignoring files repos, ignoring beads repos, and returning success for incomplete scans. The same fake ready ticket is preserved unchanged through both trackers.

A read-only run against the converted foreman checkout selected `files` and returned:

```text
fm-3c3.1 fm-3c3.3 fm-c2w.11 fm-c2w.14 fm-zgd.2 fm-zgd.4 fm-zgd.5
```

### Offline publish rehearsal

Reproduce with:

```bash
python3 skills/to-tickets/scripts/publish-demo.py \
  --foreman "$(command -v foreman)" \
  --erlang-bin "$(dirname "$(asdf which escript)")"
```

The script creates a disposable git repo and isolated `foreman.toml`, executes the fenced publish recipe directly from `references/files.md`, and asserts the actual stored bodies and edges. Its PATH contains the CLI, Erlang, and the required shell utilities, but no bd. The service URL points to a closed local port. No user config is changed.

The first rehearsal found missing `dirname` and `basename` in this isolated PATH. Added those Erlang launcher dependencies to the test environment. The successful rerun produced epic `demo-pxp`, Foundation `demo-pxp.1`, and Consumer `demo-pxp.2` blocked by `.1`:

```text
bd on PATH: absent; service destination: closed port
check predicate: true
frontier: demo-pxp.1
PASS: exact approved bodies, parent and blocker edges, foundation-only frontier
PASS: closing foundation makes consumer ready
{"errors":[],"valid":true}
```

The script prints the full tree and ready JSON too. Random epic ids vary on reruns. Temporary repos and config are removed after each run, with no commit.

## Proposed house AGENTS.md replacement

Replace the current **Beads is local and flat-file** bullet with this section. This is a proposal only; the house file was not edited.

```markdown
## Tickets

- Detect the tracker per repo: `tickets/` means ticket files, even if `.beads/` remains; otherwise use beads. Read the `foreman` skill for commands. Ticket content commands run directly; only board events use the best-effort sender.
- Files: `foreman ready`, `show`, `new`, `update`, `note`, `close --reason`, and `dep` read/write this checkout without a server. Run `foreman check` after edits. `tickets/` is the record in git; no export or Dolt sync. Create ids in the main checkout. Build sessions report new work; the coordinator creates and closes tickets after verification and any authorized commit.
- Beads repos keep `bd` until migrated. Embedded store only: no `--server`, Dolt remotes, or `bd dolt push/pull`. Keep the existing export hook; for a ticket-only commit, export and stage `.beads/issues.jsonl` before committing. Ignore generated Dolt-sync advice.
- Onboarding and migration use user-approved `foreman adopt` in the main checkout. It installs ticket files, instructions and the check hook, then stops before committing. Never initialize or migrate a tracker incidentally. Commits and pushes still require permission.
```

Also proposed, to avoid a contradictory router: change the existing **Plan → Linear → rundown → pushback** bullet to **Plan → tickets → rundown → pushback**, using the repo's detected tracker. Leave the WoW beads guidance intact until those repos migrate.

## Standards review

Reviewed first against the root and local AGENTS files, writing-for-agents guidance, and the code-review baseline. Base `86ec5b0e057a53869831ce5e45d1b98345549498` equals HEAD; the three-dot diff and commit list are empty. The user requested a self-review without commits, so this review covers the working-tree diff and new files, excluding the coordinator's brief.

- Minor, fixed: the foreman description only advertised dispatch and reporting, despite becoming the ticket-command reference. Added ticket management and onboarding triggers.
- The listing is a read-only subprocess adapter, not a new lifecycle. A state machine would add no transitions. It preserves tracker records rather than inventing a shared ticket model.
- Adapted skill provenance remains intact. No adopted skill, catalog entry, harness link, or upstream source changes.
- The ready-list routing and failure handling have observed assertion failures followed by passing tests. The real publish rehearsal executes the Markdown recipe itself. It is verification code, not a replacement ticket implementation.

Declined: unrelated skills, existing launcher/waiter internals, and fresh-context agent behavior trials. This task updates command reference recipes; spawning agents is prohibited. Retrieval and execution checks replace behavior trials, not a claim of statistical agent compliance.

Verdict: Ready. No open Critical or Important standards finding.

## Spec review

Reviewed second against fm-axu.4 and Decisions 5, 9, and 10, with the coordinator's explicit transition rules taking precedence over the ticket's older wording.

- All five requested skills now detect the tracker per repo. `tickets/` wins over `.beads/`; an unconverted repo keeps beads. Literal removal of every `bd` reference would violate this brief, so compatibility commands remain in labelled branches.
- Publishing uses `foreman new`, parent and blocker ids, then `foreman check`. The real recipe preserves the approved spec as the epic body and acceptance checkboxes in child bodies. Existing source tickets remain unchanged. Files go to the coordinator for authorized commits.
- Ready discovery uses the selected CLI's JSON unchanged, with files precedence, dependency-directory exclusions, per-repo failure reporting, and no fallback on a failed files read. Fake repos with the same ready records produce the same frontier through either tracker. This proves routing parity, not an independent audit of both trackers' readiness algorithms.
- Board stage reads use `--overlay`, avoiding the new local-file `show` behavior. Existing `--bead` launcher and `--beads-epic-id` board flags are retained because those are the actual CLI spellings for either tracker.
- Minor, fixed: the foreman reference said "no open blockers," which could imply an in-progress or deferred blocker did not block. It now says "all blockers closed," matching the CLI.

Declined: a real dispatch close-out, live board draft publication, a production beads/files equivalence run, and editing the house AGENTS file. The brief reserves the live dispatch and requires the house text as a proposal only. No real repo was migrated. The offline publish rehearsal covers the CLI half of the requested end-to-end check, not a live `/to-tickets` conversation.

Verdict: Ready for coordinator review within the revised brief. No open Critical or Important implementation finding. The original ticket cannot be marked fully verified until the coordinator applies the house text and performs the live check.

## Final check output

Fresh run after the review corrections:

```text
$ python3 scripts/check.py
45 skills, always-on ~1265/2500 tokens, 0 errors
exit 0

$ python3 -m unittest discover -s skills/dispatch/scripts -p 'test_*.py'
Ran 25 tests in 14.101s
OK
exit 0

$ python3 skills/to-tickets/scripts/publish-demo.py --foreman "$(command -v foreman)" --erlang-bin "$(dirname "$(asdf which escript)")"
bd on PATH: absent; service destination: closed port
true
[tree and ready JSON: demo-hj7 with children .1 and .2; only .1 ready]
PASS: exact approved bodies, parent and blocker edges, foundation-only frontier
PASS: closing foundation makes consumer ready
{"errors":[],"valid":true}
exit 0

$ git diff --check
[no output]
exit 0
```

Changed: the five named skills, the files publishing reference and rehearsal, and the mixed-repo ready listing with tests. Verified: skill gate, all 25 dispatch tests including three new ready-list tests, three rejected routing/error mutations, actual files-repo read, and offline publishing without bd. Standards and Spec were reviewed sequentially; both have zero open Critical or Important findings.

Not verified: live dispatch close-out and board draft linkage, full conversational `/to-tickets`, or real beads/files algorithm parity. No bead writes were allowed. The coordinator must apply the proposed house text, run the live check, and decide when to commit and close fm-axu.4. No other follow-up implementation is known within this brief.

## Coordinator correction: complete frontier, main checkouts only

The coordinator found two Important gaps in the initial ready listing. Both are fixed. This section supersedes the initial report's linked-worktree inclusion and its claim that the listing preserved the complete beads frontier.

A real pre-fix scan reproduced both findings: ui-o-matic returned 100 of 188 ready tickets with a cap warning, and fe-adr, fe-teach, and sk-tickets duplicated their main checkouts. Exit status was 0 despite that incomplete frontier. My small fixtures never crossed the beads default cap, and I had treated linked-worktree support as useful discovery rather than duplicate work.

`ready-repos.py` now passes `--limit 0` to `bd ready`. Foreman's current `TicketCLI` ready path filters, sorts, and returns every matching ticket without a cap, so no extra flag is needed there. Discovery skips and prunes directories whose `.git` is a file. `skills/dispatch/SKILL.md` now states these rules.

Two fake-repo regressions failed before the fix:

- The capped beads fixture returned 100 records instead of the expected 188.
- The main-checkout fixture returned four rows instead of two, including both files and beads worktree duplicates.

After the fix, all five ready-list tests pass. The fake beads CLI models the real default cap and only returns the full fixture when requested; the fake foreman CLI accepts its existing uncapped command. Both main checkout and linked worktree fixtures carry the same frontier, so the duplicate check asserts the user-visible result.

### Real listing after correction

Command: `python3 skills/dispatch/scripts/ready-repos.py ~/dev`. The summary below is derived from the actual JSON, not fixture data. Exit 0, empty stderr, no truncation warning.

| Repo relative to `~/dev` | Tracker | Ready tickets |
| --- | --- | ---: |
| dotfiles | beads | 2 |
| games/wow-addons/cooldown-o-matic | beads | 9 |
| games/wow-addons/ui-o-matic | beads | 188 |
| games/wow-addons/we_go_next_dev | beads | 10 |
| music/form-engine | beads | 7 |
| utils/foreman | files | 7 |
| utils/skills | beads | 5 |

Assertions also confirmed ui-o-matic's count is 188 and that fe-adr, fe-teach, and sk-tickets are absent.

### Correction review and gates

Standards, reviewed first: changes stay in the read-only adapter, regression fixtures, and its command reference. No new abstraction or lifecycle. Spec, reviewed second: both coordinator findings now have failing-first regressions and real-run confirmation. No open Critical or Important finding in this correction. Declined: separate-git-dir main checkouts, which the requested `.git`-file exclusion intentionally skips, and the previously reserved live dispatch close-out.

```text
$ python3 -m unittest discover -s skills/dispatch/scripts -p 'test_*.py'
Ran 27 tests in 13.983s
OK
exit 0

$ python3 scripts/check.py
45 skills, always-on ~1265/2500 tokens, 0 errors
exit 0

$ git diff --check
[no output]
exit 0
```

Lesson: tiny fixtures hid pagination, and accepting every checkout duplicated dispatch candidates. Prevention is executable: unlimited beads reads, main-checkout-only discovery, and regressions that cross the cap and include duplicate worktrees. The read-only lesson search returned no matching ready-list lesson. No lesson bead was created because this session forbids bd writes; the coordinator can record it from this report. No commits or real ticket edits.
