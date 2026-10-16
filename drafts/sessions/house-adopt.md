# House adopt session (sk-81s.5, sk-81s.11)

Build session report for the coordinator. Nothing committed, nothing linked, `~/.claude` and `~/.agents` untouched.

## Skills added

| Skill | Mode | From | Notes |
|---|---|---|---|
| codebase-design | adopt | mattpocock:skills/engineering/codebase-design@49dd158 | |
| improve-codebase-architecture | adopt | mattpocock:skills/engineering/improve-codebase-architecture@49dd158 | its `/codebase-design` refs resolve |
| domain-modeling | adopt | mattpocock:skills/engineering/domain-modeling@49dd158 | wayfinder dep |
| prototype | adopt | mattpocock:skills/engineering/prototype@49dd158 | wayfinder dep |
| research | adopt | mattpocock:skills/engineering/research@49dd158 | wayfinder dep |
| pr | adopt | mattpocock:skills/engineering/pr@49dd158 | |
| triage | adopt | mattpocock:skills/engineering/triage@49dd158 | flagged, see below |
| grilling | adopt | mattpocock:skills/productivity/grilling@49dd158 | wayfinder dep |
| handoff | adopt | mattpocock:skills/productivity/handoff@49dd158 | |
| teach | adopt | mattpocock:skills/productivity/teach@49dd158 | |
| using-git-worktrees | adopt | superpowers:skills/using-git-worktrees@bb92a77 | |
| finishing-a-development-branch | adopt | superpowers:skills/finishing-a-development-branch@bb92a77 | flagged, see below |
| git-guardrails-claude-code | adopt | mattpocock:skills/misc/git-guardrails-claude-code@49dd158 | see "own vs adopt" below |
| setup-pre-commit | adopt | mattpocock:skills/misc/setup-pre-commit@49dd158 | same |
| scaffold-exercises | adopt | mattpocock:skills/misc/scaffold-exercises@49dd158 | same |
| migrate-to-shoehorn | adopt | mattpocock:skills/misc/migrate-to-shoehorn@49dd158 | same |
| writing-for-people | merge | pstack technical-writing + unslop @850d7f2 | model-invoked |
| writing-for-agents | merge | mattpocock productivity/writing-for-agents @49dd158 + superpowers writing-skills @bb92a77 | model-invoked |
| create-verification-skill | adapt | pstack:pstack/skills/create-verification-skill@850d7f2 | Cursor paths neutralized |
| maintain-verification-skill | adapt | pstack:pstack/skills/maintain-verification-skill@850d7f2 | Cursor paths neutralized |
| no-comments | adapt | pstack no-comments + agents/comment-sicko.md @850d7f2 | Cursor Task spawn neutralized |

Adopted copies are whole skill directories (including `agents/openai.yaml`, reference files, scripts with exec bits). A scripted `diff -r` against each pinned source shows the provenance comment as the only difference, for all 16 adopts plus the existing wayfinder.

wayfinder's dependencies (grilling, domain-modeling, research, prototype) now all exist in `skills/`.

## Edits to adopted, adapted, and merged copies

Adopted copies: none beyond the provenance comment.

create-verification-skill (adapt):
- `.cursor/skills/verify-<app>/` became `<skills-dir>/verify-<app>/`, defined once: `.claude/skills/` for Claude Code, `.agents/skills/` for pi; for a repo serving both, write under `.agents/skills/` and symlink `.claude/skills/verify-<app>`.
- The body's `/maintain-verification-skill` became "the `maintain-verification-skill` skill". The description is unchanged.

maintain-verification-skill (adapt):
- `.cursor/skills/verify-*/` became `.agents/skills/verify-*/` or `.claude/skills/verify-*/`.
- Two body `/create-verification-skill` refs became the skill name.

no-comments (adapt):
- Cursor `Task` with `subagent_type: "comment-sicko"` became a fresh-context subagent (Claude Code: Agent tool; pi: `subagent`) briefed with the bundled `references/comment-sicko.md`, with a fallback to run the brief inline and say so.
- Dropped the poteto-mode reasoning-level and speed line.
- `/how` and `/why` became "trace callers and history (`git log -S`, `git blame`)", in both the skill and the sicko brief.
- `/architect` became a single inline shape sketch.
- `principle-*` skills became the house `principles` references, which exist: `fix-root-causes.md` and `redesign-from-first-principles.md`.

writing-for-people (merge):
- New tight SKILL.md with two passes: write to the standard, then strip the slop.
- `references/technical-writing.md` is the pstack body with these changes: unslop skill refs point to `slop-patterns.md`; the Cursor-repo rule "indent code snippets with tabs" is dropped; "swarm logs" became "agent logs".
- `references/slop-patterns.md` is the unslop body verbatim, with its stable rule numbers.

writing-for-agents (merge):
- New SKILL.md with 7 steps: name the failure with a baseline and a control, pick the form that fits the failure, write the pointer, place each piece, set a completion criterion, prune, prove it binds.
- `references/levers.md` is the mattpocock body verbatim.
- `references/skill-mechanics.md` is mattpocock SKILL-MECHANICS plus the superpowers frontmatter, discovery, and file-organization rules (description gives triggers, not a workflow summary; scripts run through an interpreter; no `@` includes).
- `references/testing-skills.md` is superpowers testing-skills-with-subagents. Its `superpowers:test-driven-development` ref now points to house `tdd`, and the CLAUDE_MD_TESTING example pointer is dropped.
- `references/persuasion-principles.md` is verbatim.
- Not taken: anthropic-best-practices.md (1150 lines, an external doc that goes stale), graphviz-conventions.dot, render-graphs.js, examples/. The superpowers "Iron Law, delete untested skills" absolutism is softened to "baseline first for behavior-shaping guidance; pure reference tests retrieval".

verify-before-claiming (own merge), sk-81s.11:
- Added a 12-line `## Lessons` section before the report format. On each user correction, pick the highest rung: 1 impossible in code/types/data, 2 static analysis/lint/CI, 3 AGENTS.md/skill, 4 human review. Make the change or file it, then record `bd create "<mistake> -> <prevention>" -l lesson -d "rung <n>: ..."`.

## Dropped (catalog `[[drop]]`)

| pstack skill | Reason |
|---|---|
| setup-pstack | Cursor-only model-role config |
| typescript-best-practices | language style guide; belongs in repo AGENTS.md and lint |
| make-bot-ui | Grok Bot webhook UI, poteto-specific |
| poteto-mode | personal style bundle; parts covered by principles, verify, writing, implement |
| poteto-help | pstack onboarding |
| bro | covered by writing-for-people |
| ketchup | covered by handoff |
| in-your-own-words | tight-spec step 2 "Restate and size" |
| teach | same job as adopted mattpocock teach; needs pstack how/why |
| automate-me | Cursor-only (.cursor/, Cursor create-skill, transcripts) |
| recall | reads Cursor agent-transcripts; covered by handoff and beads |
| reflect | reads Cursor agent-transcripts; covered by the Lessons section |

## Every other pstack skill not adopted or merged here

| pstack skill | Status |
|---|---|
| interrogate, how, principle-*, show-me-your-work, blast-radius, swarm, tdd | already merged by sk-81s.3 and sk-81s.4 (catalog `from`) |
| sharpen, figure-it-out | dropped in drafts/spec-tickets.md; that session owns the `[[drop]]` entries (none in catalog yet) |
| arena | dropped in drafts/implement-tdd.md; same, no `[[drop]]` entry yet |
| **correct** | **UNDECIDED.** A repo-wide sweep that makes repeated agent mistakes impossible (architecture, then types, then lint, then tests, then docs) plus a rule-to-enforcer table. Not Cursor-only. The Lessons section covers per-correction encoding but not the periodic sweep. Candidate: adopt as-is (32 lines, no Cursor refs) next to Lessons. |
| **benchmark-checklist** | **UNDECIDED.** Not Cursor-only, not covered. `principles/references/explain-the-number.md` already points at it as "not in the house set". Candidate: adopt (39 lines). |
| **architect** | **UNDECIDED.** Depends on pstack how, why, and arena. Partly covered by codebase-design and tight-spec. Lean drop. |
| **why** | **UNDECIDED.** MCP-discovery evidence hunt for design rationale and regressions; 399 lines; mentions Cursor. Partly covered by diagnosing-bugs. Lean drop. |
| agents/poteto-agent.md | not a skill; not taken |

I left these four for the coordinator because they are neither Cursor-only nor clearly covered.

## Flagged for the coordinator

1. **Own vs adopt for misc.** The four misc skills in `~/dev/utils/skills/skills/misc/` are byte-identical to `mattpocock-upstream/skills/misc/` at the pin (`~/dev/utils/skills` HEAD is mattpocock 49dd158). I cataloged them as `adopt` from `mattpocock:skills/misc/*` instead of `own`, so sync tracks upstream. Flip to `own` if you prefer.
2. **finishing-a-development-branch** hard-codes `git push -u origin` and PR creation (options 2 and 1-of-worktree). This conflicts with "agent git push blocked / PRs only when asked". It also mentions "Superpowers" worktree paths at line ~171. Not edited.
3. **triage** assumes a GitHub-issues label workflow (`gh issue list --label`, agent brief posted on a GitHub issue or PR) and tells the user to run `/setup-matt-pocock-skills`. The user tracks in beads and Linear. Not edited.
4. **`/setup-matt-pocock-skills`** is referenced by wayfinder and triage and is not in the house set, so the reference dangles. Either adopt it, or point both at a house tracker doc (that needs an adapt).
5. **maintain-verification-skill** ends with "one PR of proven corrections". That implies branch, push, and PR. Not edited beyond paths.
6. **git-guardrails-claude-code** overlaps the user's existing global hooks in `~/.claude/hooks/`. It is a setup skill, so it is kept.
7. `check.py` does not verify that `from` paths exist in the sources. I checked separately: every `from` and drop ref in the catalog resolves under its pinned source. That could become a check.py rule.

## Follow-up beads

- sk-81s.12: decide pstack correct, benchmark-checklist, architect, why.
- sk-81s.13: adopted skills that hard-code GitHub or push, and the dangling `/setup-matt-pocock-skills` reference.

## Final check

```
$ python3 scripts/check.py
30 skills, always-on ~997/2500 tokens, 0 errors
```
