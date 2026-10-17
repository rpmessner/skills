# Workflow gaps pass (2026-10-16)

The coordinator asked for this subagent run. Nothing is committed or pushed. Final gates:

- `python3 scripts/check.py` → `42 skills, always-on ~1186/2500 tokens, 0 errors`. The always-on cost was 1142 before this pass; the new `lessons` skill adds 44.
- `form-engine/.agents/skills/verify-form-engine/verify all` → `verify all: 11 pass, 0 fail, 2 skip`. The two skips are `launchkey` and `launchkey-demo`, because no device is attached.

## 1. Briefs never ask for tdd, verify-before-claiming, or code-review

`skills/dispatch/SKILL.md`:
- The brief template has a new required `## Skills` slot with three items:
  - `tdd` at named seams, or "none: <reason>".
  - `verify-before-claiming` before the report.
  - `code-review` on the session's own diff against `<base sha>` before the marker: Standards and Spec axes, plus Risk on the usual triggers. The axes run one after another in the session, with no subagents. The session fixes Critical and Important findings and re-runs the gate.
- Report back now asks for the review findings per axis, with what was fixed and what was left open.
- `<base sha>` is defined as `git rev-parse HEAD` at dispatch time.
- Close-out has a new step 4: run `code-review` on the slice diff against the base sha, sequentially and in context, with no subagents unless the user asked for them. Findings go back to the session or are listed as open to the user. Done-when now also requires that no Critical finding is unresolved.
- Step 2 now also runs the repo's per-ticket close-out check (see gap 6).
- The description is unchanged and still one sentence.

Evidence: `check.py` passes, including the YAML hazard rule.

## 2. The Lessons loop never fires

The Lessons procedure is now its own model-invoked skill, `skills/lessons/SKILL.md` (mode own). Its description triggers on corrections: "the user corrects you, says something you did or claimed was wrong, or repeats an instruction you missed". The body runs five steps:

1. Name the mistake.
2. Check for a repeat with `bd search -l lesson`, plus a grep of AGENTS.md and the skill that applied. A rule that already existed means going one rung higher.
3. Pick a rung on the trust ladder.
4. Act now, or file a follow-up.
5. Record it with `bd create ... -l lesson`.

If no `.beads` is reachable, the skill tells the user and asks where the lesson should live. If the user only changed their mind, it is not a lesson.

Other changes for this gap:
- `verify-before-claiming` keeps a one-line pointer.
- `flow` now routes "User corrected you → `lessons`".
- `catalog.toml` has a new `[[skill]] lessons` entry (own, job `correction-lessons`).
- The reason on the pstack `reflect` drop now points at `lessons`.

Proof that it binds: I ran 3 fresh pi print-mode reps (`pi -p --no-session --mode json --skill skills/lessons`) with a correction prompt in scratch repos. In all 3 reps the agent read `lessons/SKILL.md` unprompted, fixed the mistake, and gave a "Lesson:" line with a proposed rung. The scratch repos had no `.beads`, and in every rep the agent took the no-beads branch and asked where the lesson should live. I ran no control reps. The baseline failure is that no `lesson` bead exists anywhere.

**Needs the coordinator:** the new skill is not linked yet. `python3 scripts/link.py` previews 2 links, `~/.claude/skills/lessons` and `~/.agents/skills/lessons`. Run `python3 scripts/link.py --apply` after the commit.

## 3. pi build windows have no guardrails

pi supports this directly. In pi's own docs, `docs/extensions.md` says a `tool_call` handler "can mutate input or block execution" and returns `{ block: true, reason }`. Per `docs/packages.md`, `pi -e <path>` loads a package for one run without changing settings.

What I built, in `pi/house-guard/`:
- `package.json`: a local pi package whose manifest lists `./index.ts`.
- `index.ts`: on every pi `bash` call, it pipes `{"tool_input":{"command":...},"cwd":ctx.cwd}` to `~/.claude/hooks/block-dangerous-shell.sh` and `block-sensitive-commit.sh`. Those hooks stay the one source of truth. Exit 2 blocks the call, with the hook's stderr as the reason. Any other failure blocks with "house-guard could not run ..." so the guard fails closed. `HOUSE_GUARD_HOOKS_DIR` overrides the hooks directory.
- `test.ts`: 16 verdicts. The planted secrets in it are split so the file itself passes the commit guard.
- The skills repo's `AGENTS.md` has a new Layout line for `pi/house-guard/`.

The test needed one dispatch change. `skills/dispatch/scripts/pi-window` now passes extra args after the brief through to pi, as `pi-window <name> <dir> <brief> [pi-args...]`. Args that contain quotes are rejected. Step 3 of `dispatch/SKILL.md` documents this.

Evidence:
- `node pi/house-guard/test.ts` printed `all ok`.
  - Blocked: `git push` (also after `cd`), `git reset --hard`, `git clean -fdx`, `git branch -D`, and bare `rm`.
  - Allowed: `/usr/bin/rm` and `git status`.
  - Commits: a clean commit is allowed. Commits are blocked for a private key (with `cd`, `git -C`, and cwd targeting), a secret assignment, an ssh path, and a Windows user path. With the hooks missing, the guard blocks `ls`, so it fails closed.
- Live pi run 1: `pi-window guard-test <scratch repo> brief -e .../pi/house-guard`, then `pi-wait`, which printed DONE.
  - pi listed `house-guard` among its loaded packages.
  - `git push origin main` was blocked with `BLOCKED: git push is human-controlled; ...`.
  - `rm junk.txt` was blocked with `BLOCKED: bare rm is blocked; ...`.
  - `git reset --hard HEAD` was blocked with `BLOCKED: git reset --hard destroys worktree state.`
  - The clean commit ran.
  - The planted-key commit was blocked earlier, by the third-party `pi-jev-eye`, because the key was on the command line. That means house-guard's commit path was not exercised in run 1.
- Live pi run 2: I staged the key file myself, so the command line held no secret. `git -C <repo> commit -m planted-key`, run from the parent dir, was blocked with `BLOCKED: staged diff in <repo> appears to contain private key material.` That message comes from `block-sensitive-commit.sh` through house-guard. `git log` afterwards showed no new commit.
- Known limit, the same as the Claude hook: the check reads the index before the command runs. So a staging change inside the same command line (`git reset ... && git add ... && git commit`) is judged on the old index.

**Needs the user's OK (coordinator applies it).** Add the package to `~/.pi/agent/settings.json`, first in the list so house rules decide before the third-party extensions:

```json
"packages": [
  "/home/rpmessner/dev/utils/skills/pi/house-guard",
  "npm:pi-subagents@0.69.0",
  ...unchanged...
]
```

`pi install /home/rpmessner/dev/utils/skills/pi/house-guard` would also work, but it appends the package to the end of the list. To check after the change, run `pi list`; it should show the path. Then repeat run 2 without `-e`.

Cosmetic: the hook messages say "from Claude Code" even when pi hits them.

## 4. Nothing schedules the maintenance loops

I added a `bd note` on sk-81s.8; `bd show sk-81s.8` shows it under NOTES. It gives two options:

- (a) A weekly coordinator ritual, started by one prompt, which is written out in the note. The run is report-only: skills-sync report, lesson-bead review, correct candidates, a verify-skill drift check, and retro on request. It ends with a decision table.
- (b) A user crontab running `scripts/sync.py`, with no `--file-beads` and no `--bump`, plus an optional headless `claude -p` summary. It may fetch sources and write `reports/` and `drafts/`. It may not edit skills or the catalog, touch beads, pins, commits, pushes, or harness dirs. `/schedule` cloud routines are ruled out because they cannot see `~/dev` or the local Dolt beads.

The note recommends (a). Nothing is scheduled.

## 5. The subagent rule conflicts with three skills

All three skills now follow one rule. By default, and always inside a pi build window, the skill runs its axes or passes itself, sequentially and in context. It spawns subagents only when the user asked for them. As the coordinator without that request, it asks before spawning.

- `code-review` (merge): step 3 is now "Run the axes": sequential by default, using each axis brief as a checklist, and fan-out only on request. "Fail here, not inside subagents" became "before any axis runs". I removed the old "no subagent support" fallback because the new default covers it. The provenance comment notes the house edit.
- `no-comments` (adapt): Comment Sicko runs as a separate in-context pass by default. The description and opening line say "Run" instead of "Spawn". The provenance comment lists the change.
- `maintain-verification-skill` (adapt): the source wave runs one feature at a time in context by default. "Children" became "Source reads". The description's "parallel source readers" became "a source read per feature". The provenance comment lists the change.

None of these needed an adopt→adapt switch, because they were already merge or adapt.

**Open, for the user to decide.** Other skills still default to subagents:
- `implement` (merge): subagent mode also kicks in "for long ticket sets".
- `tight-spec` (merge): "dispatch a read-only subagent for wide searches".
- Adopted skills: `grilling` (sub-agent for facts), `codebase-design` (DESIGN-IT-TWICE parallel sub-agents), `improve-codebase-architecture`, and `wayfinder` (research subagents).

Editing the adopted ones would switch them to adapt. Another option is one global line in `flow` saying the subagent rule overrides skill defaults.

## 6. form-engine: the feature map was prose only

- `.agents/skills/verify-form-engine/verify` has a new check, `closeout <bead-id> | --base REF [--no-feature-change "<reason>"]`. It is not part of `all`.
  - The base is the last first-parent commit before the bead's `started_at`, or REF.
  - The change set covers commits, staged, unstaged and untracked files since the base.
  - Code means `core/ shell/ cli/ tools/ build.zig`.
  - The check FAILs when code changed and nothing under `features/` did. The escape needs a non-empty reason and prints it in the PASS line.
- The verify `SKILL.md` describes the check under "Keeping the map honest", with commands and the run-it-before-`bd close` rule, and has a new row in the check table.
- form-engine's `AGENTS.md` has one added sentence on the verify line.
- Dispatch close-out step 2 runs the check per closed ticket.

Evidence:
- In the real repo:
  - `verify closeout fe-lwp.18` → `PASS closeout: 23 code paths and feature map (build-gates.md launchkey.md platform.md probe.md README.md ui.md) changed since a544c76`.
  - `--base HEAD` → `PASS ... no code paths changed since d90fb88`.
  - `closeout fe-lwp.16`, which was never claimed → `FAIL ... has no started_at ...; pass --base REF`, exit 1.
  - An empty reason → FAIL.
  - No args → exit 2.
- In a scratch clone at 18491c2, a code commit with no feature map change:
  - `closeout --base HEAD^` → `FAIL closeout: 22 code paths changed since a544c76 (first: build.zig) but nothing under features/; ...`, exit 1.
  - With `--no-feature-change "rename only; ..."` → `PASS ... feature map unchanged: rename only; ...`, exit 0.
  - With an untracked new file under `features/` → PASS.
- `verify all` gives 11 pass, 0 fail, 2 skip.

Heads-up: `docs/briefs/fe-linux.md`, which is untracked and not yet launched, has that session edit the verify skill too. Commit this change before dispatching fe-linux.

## 8. Catalog mismatch on tight-spec

`drafts/spec-tickets.md` says tight-spec took ideas from to-spec, grilling, grill-with-docs, brainstorming, sharpen and figure-it-out. It also says interrogate and how were not taken, and that grill-me is a router that was left out.

- tight-spec's `from` list in `catalog.toml` now names exactly those six sources.
- I removed the `[[drop]]` entries for sharpen and figure-it-out.
- I added drops for `pstack interrogate`, `pstack how` and `mattpocock grill-me`, each with a reason that cites the draft.
- The tight-spec provenance comment now also names the three upstream skills that were not taken.

Evidence: `check.py` reports 0 errors, so upstream coverage holds. The pending `reports/2026-10-16.md` sync digest lists "tight-spec (interrogate/references/lead-judgment.md)", and that entry no longer applies to tight-spec. Re-run sync, or ignore that line.

## Other

- `AGENTS.md` said `link.py --dry-run`, but the script has no such flag: it dry-runs by default and takes `--apply`. I fixed the line.
- pi print mode hung until timeout when stdin was left open. `pi -p ... </dev/null` works.

## git status --short

`~/dev/utils/skills`:
```
 M AGENTS.md
 M catalog.toml
 M skills/code-review/SKILL.md
 M skills/dispatch/SKILL.md
 M skills/dispatch/scripts/pi-window
 M skills/flow/SKILL.md
 M skills/maintain-verification-skill/SKILL.md
 M skills/no-comments/SKILL.md
 M skills/tight-spec/SKILL.md
 M skills/verify-before-claiming/SKILL.md
?? drafts/sessions/gaps.md
?? pi/
?? skills/lessons/
```

`~/dev/music/form-engine`. `docs/briefs/fe-linux.md` was untracked before this pass.
```
 M .agents/skills/verify-form-engine/SKILL.md
 M .agents/skills/verify-form-engine/verify
 M AGENTS.md
?? docs/briefs/fe-linux.md
```

Suggested commit slices for the skills repo:
1. catalog/tight-spec consistency
2. dispatch brief and close-out review
3. lessons skill
4. sequential-by-default subagent rule
5. pi/house-guard plus the pi-window args change
6. AGENTS.md lines
