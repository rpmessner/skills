# Debug + Verify + Review: rationalization notes

Pins: mattpocock 49dd158, superpowers bb92a77, pstack 850d7f2. Output: `skills/diagnosing-bugs`,
`skills/verify-before-claiming`, `skills/code-review`, `agents/reviewer.md`.

## Proposed catalog entries (not applied; catalog.toml left untouched)

```toml
[[skill]]
name = "diagnosing-bugs"
job = "debug"
mode = "merge"
from = ["mattpocock:skills/engineering/diagnosing-bugs", "superpowers:skills/systematic-debugging", "pstack:pstack/skills/principle-fix-root-causes"]

[[skill]]   # mode changes own -> merge
name = "verify-before-claiming"
job = "verify"
mode = "merge"
from = ["superpowers:skills/verification-before-completion", "pstack:pstack/skills/principle-prove-it-works", "pstack:pstack/skills/show-me-your-work"]

[[skill]]
name = "code-review"
job = "review"
mode = "merge"
from = ["mattpocock:skills/engineering/code-review", "superpowers:skills/requesting-code-review", "superpowers:skills/receiving-code-review", "pstack:pstack/skills/blast-radius", "pstack:pstack/agents/comment-sicko.md"]
```

Drops: `superpowers:systematic-debugging`, `verification-before-completion`, `requesting-code-review`,
`receiving-code-review`; `pstack:principle-fix-root-causes`, `principle-prove-it-works`, `show-me-your-work`,
`blast-radius`, `agents/comment-sicko.md`, each reason "merged into <house skill>". `agents/` is not covered by
check.py today; decide whether the catalog should track agent definitions (see Open questions).

`scripts/check.py` currently fails only on missing catalog entries for my two new dirs (other failures belong to
other job groups).

## Per source

### mattpocock diagnosing-bugs → `diagnosing-bugs` (spine)
- TAKEN: feedback loop as "the skill" and its completion checklist (SKILL Phase 1); 10 loop types, tightening,
  non-determinism (references/feedback-loops.md); reproduce+minimise; 3–5 ranked falsifiable hypotheses shown
  to user; one-variable probes, tagged `[DEBUG-xxxx]` logs, perf = measure then bisect; regression test only at a
  correct seam, "no seam is a finding"; cleanup checklist; redaction; HITL template (scripts/, byte-identical copy).
- LEFT OUT: `agents/openai.yaml` (Codex UI metadata, not used by Claude Code or pi). Verbose motivational lines.

### superpowers systematic-debugging → `diagnosing-bugs`
- TAKEN: read the full error/stack (Phase 0); check recent changes (Phase 0, merged with the user's "inspect the
  last change first" rule); find working analogue + list differences (Phase 3); multi-component boundary logging
  (Phase 4); single fix, no bundled refactor; **3 failed fixes → question architecture with the user** (Phase 5);
  red flags and user signals ("stop guessing", "we're stuck?") (Stop signals); "no root cause" handling (Phase 6);
  backward tracing (references/root-cause-tracing.md); condition-based waiting (feedback-loops.md, condensed).
- LEFT OUT: Iron-law/rationalization tables and "violating the letter" framing (token cost; the phase gates carry
  it). `find-polluter.sh` and `condition-based-waiting-example.ts` (JS/npm-specific; the bisect idea is kept in
  prose). `test-*.md`, `CREATION-LOG.md` (skill authoring artefacts). Defense-in-depth as a mandate: kept only as
  an optional judgement call, because "validate at every layer" conflicts with the user's anti-over-abstraction
  rule and with fix-root-causes' "no guards".

### pstack principle-fix-root-causes → `diagnosing-bugs`
- TAKEN: no symptom guards; paragraph-long justification = wrong code; grep for the pattern and fix all
  instances; propose the cheap always-on signal (all Phase 5); restart bugs = stale state first (Phase 0).
- LEFT OUT: nothing substantive.

### User rules (AGENTS.md) → `diagnosing-bugs`
- Phase 0 encodes "absent a stack trace, reproduce end-to-end close to the user's experience first" and "wrong
  behaviour ≠ an error, don't go log-hunting", plus "don't break what works: inspect the last change first". The
  WoW-style "probe, read back from saved output" is loop type 10 in feedback-loops.md.

### own verify-before-claiming → `verify-before-claiming` (spine)
- TAKEN: name, Verifier-layer framing, rule, lowest-faithful-verifier ladder, report format
  (Changed/Verified/Not verified), "failed verifier is a blocker", links to diagnosing-bugs and tdd.
- Description rewritten to add triggers (commit, closing a bead, trusting a subagent report). Check the token
  budget still fits (~40 tokens).

### superpowers verification-before-completion → `verify-before-claiming`
- TAKEN: "fresh evidence from this turn"; the 4-step gate; paraphrase coverage ("should work", "Done!"); claim →
  required-evidence table (references/claims.md, extended with Deployed and Safe-to-merge rows); regression
  red-green recipe; agent reports are claims → check the diff; requirements line-by-line.
- LEFT OUT: rationalization table, "lying" rhetoric, red-flag list (overlaps with the gate; costs tokens).

### pstack principle-prove-it-works → `verify-before-claiming`
- TAKEN: real artifact not proxy; suspect observation method first; script the check and keep the output
  (section "Check the real thing").
- LEFT OUT: `disable-model-invocation` (the house skill must auto-trigger).

### pstack show-me-your-work → `verify-before-claiming/references/decision-trail.md`
- TAKEN: TSV format, columns, append-only supersede rule, what to log, formula-injection escaping, self-audit of
  rows. Opt-in only for long/unattended runs.
- LEFT OUT: `scripts/log.sh` (small; a printf suffices and the reference states the escaping rule; can vendor
  later if wanted). Transcript audit via Cursor `agent-transcripts/` (Cursor-specific path). Mandatory
  cross-model review + "Attention" section (costly default; offered in blast-radius for wide changes instead).
  `start`-row multi-run protocol (over-engineered for a local trail). References to `unslop`,
  `encode-lessons-in-structure`, `poteto-mode` (not in house set). Durable follow-ups go to beads.

### mattpocock code-review → `code-review` (spine)
- TAKEN: pin + validate fixed point (three-dot), spec discovery order, standards discovery, Fowler smell baseline
  with "repo overrides / judgement call" rules (references/standards-baseline.md), parallel axis subagents, axis
  briefs, "don't rerank across axes" aggregation.
- CHANGED: spec lookup adds beads (`bd show`); `/setup-matt-pocock-skills` tracker dependency removed.
- LEFT OUT: `agents/openai.yaml`.

### superpowers requesting-code-review (+ code-reviewer.md) → `code-review`, `agents/reviewer.md`
- TAKEN: precisely crafted context, never session history; read-only reviewer with worktree rule; "you do not
  dispatch subagents"; "spec is a vision document / reasonable-user expectation" (Spec brief); "declined to
  judge" list; severity calibration Critical/Important/Minor; file:line + why + fix; verdict.
- LEFT OUT: "mandatory after each task in subagent-driven development" (that workflow isn't in this group;
  review is on request). Strengths section and "acknowledge what was done well" (noise for this user; findings
  only). Generic checklist (architecture/security/production readiness) — partly covered by Risk axis.

### superpowers receiving-code-review → `code-review` "Receiving" + references/receiving.md
- TAKEN: read-all → clarify unclear first → verify → respond → implement one at a time; source-specific trust;
  YAGNI grep; push-back conditions; no performative agreement/thanks; correcting wrong pushback; GitHub inline
  replies (plus the user's "mark agentic comments" rule).
- LEFT OUT: "your human partner" framing and "explicit instruction-file violation" aside (CLAUDE.md-specific).

### pstack blast-radius → Risk axis (references/blast-radius.md)
- TAKEN: "listing callers isn't the job"; the one safety fact; look where grep stops; honest risk grading; proof
  ladder (also reused in verify's claims.md); hand-back format.
- NEUTRALIZED: Solid vs React → generic "async ordering, teardown, supervision"; `how`/`why`/`arena`/`unslop`
  skill references removed (not in house set); `arena` reduced to "offer a second model for wide changes".
- Not a separate skill: "what could this break" is a review question; one skill per job.

### pstack comment-sicko → baseline comment rules + reviewer rule
- TAKEN: keep-list (license, external constraint, public API doc, issue link, formatter/style suppressions);
  narration/banners/dead code/workaround sermons are findings; our-code surprises → name the symbol to reshape;
  correctness-rule suppressions are findings; report-only.
- LEFT OUT: the persona and fixed opening line ("Yes... Ha ha ha"), "when unsure the comment dies" (too
  aggressive as a default; made a judgement call), `MUST KILL` label (plain severity instead), reliance on
  `/how` `/why`.

## Harness-specific bits neutralized
- Claude Code `Task`/`general-purpose` → "dispatch a subagent"; `reviewer` agent used if installed, else a
  general subagent with the brief pasted; no-subagent fallback = run axes sequentially in-session.
- Cursor transcript paths, `disable-model-invocation`, `openai.yaml` dropped.
- **pi**: core pi has no subagent tool. With `pi-subagents` installed, its `subagent` tool runs the axes
  (parallel mode) and can load agent definitions from markdown with the same front matter shape, so
  `agents/reviewer.md` should be linkable into pi's agents dir. UNVERIFIED: pi-subagents is not installed here
  (`npm ls -g` shows only `@earendil-works/pi-coding-agent@1.2.0`); probe its agent-dir path and whether it honours
  `tools:` before wiring `link.py`. Without it, the skill's sequential fallback applies.
- `tools: Read, Grep, Glob, Bash` is Claude Code naming; pi tool names are lowercase built-ins. Read-only is
  enforced in prose, not by the tool list (Bash is needed for git).

## Disagreements between sources (and resolution)
- **One hypothesis vs 3–5 ranked** (superpowers vs Matt): ranked list, tested one at a time.
- **Reproduce first vs read errors first**: Phase 0 split by report type: stack trace → read it; wrong behaviour →
  E2E repro first (user rule).
- **Defense in depth vs no guards** (superpowers vs pstack + user): root fix is the fix; boundary validation is
  an optional judgement call.
- **Severity ranking vs no reranking** (superpowers vs Matt): severity within an axis, never across axes.
- **Reviewer praise** (superpowers wants strengths): dropped.
- **Review cadence** (superpowers: mandatory after every task; Matt: on request): on request, plus whatever the
  implement/workflow skill decides.
- **Cross-model review** (pstack mandatory for trails; arena for blast-radius): offered, not automatic.
- **Comment hostility** (comment-sicko kills when in doubt vs Matt's judgement calls): judgement calls.

## Open questions
- Should `catalog.toml`/`check.py`/`link.py` track `agents/*.md` (Claude: `~/.claude/agents`, pi: pi-subagents
  dir)? Needs a bead.
- Description of `code-review` is the longest of the three (~55 tokens); trim if the budget gets tight.
