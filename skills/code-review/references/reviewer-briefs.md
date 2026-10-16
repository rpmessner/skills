<!-- house: merge; from: mattpocock:skills/engineering/code-review@49dd158, superpowers:skills/requesting-code-review/code-reviewer.md@bb92a77, pstack:pstack/skills/blast-radius@850d7f2 -->

# Reviewer briefs

Every brief carries the shared rules, then its axis block. If the `reviewer` agent is installed, it already
holds the shared rules; send only the context and axis block.

## Context to include (all axes)

- What was built, in one or two sentences.
- The diff command (`git diff <ref>...HEAD`), `git diff --stat`, and the commit list.
- The axis-specific inputs listed below.

## Shared rules (paste when not using the `reviewer` agent)

- Read-only on this checkout: never change the working tree, index, HEAD, or branches. To see another revision,
  `git worktree add` it into a temp dir.
- Do the whole review yourself; never dispatch another subagent.
- Every finding cites `file:line` (or quotes the hunk), says what is wrong and why it matters, and how to fix if
  not obvious. Never comment on code you did not read.
- Severity by real effect: **Critical** (bugs, data loss, security, broken behaviour), **Important** (design,
  missing requirement, error handling, test gaps), **Minor** (style, polish). Not everything is Critical.
- **Declined to judge**: before the verdict, list each behaviour you considered and set aside as out of scope,
  one line each with the reason. Empty list means nothing set aside.
- End with a verdict: Ready / Ready with fixes / Not ready, and one sentence why.
- Under 400 words unless the axis needs more.

## Standards axis

Inputs: the list of standards files found, plus `standards-baseline.md` pasted in full.

Brief: "Report, per file/hunk, (a) each place the diff breaks a documented standard, citing the file and rule;
(b) each baseline smell or comment/suppression issue, named and with the hunk quoted. Documented-standard breaches
can be hard violations; baseline items are always judgement calls, and a documented standard overrides the
baseline. Skip what tooling enforces."

## Spec axis

Inputs: the spec text or path (bead/issue contents fetched).

Brief: "Report (a) requirements missing or partial; (b) behaviour in the diff nobody asked for (scope creep);
(c) requirements that look implemented but wrongly. Quote the spec line for each. The spec states intent, not
every condition: where it is silent, judge by what a reasonable user of this software would expect, and grade by
the effect on that user. If the spec itself looks wrong, say so separately."

## Risk axis

Inputs: the diff, and `blast-radius.md` pasted in full.

Brief: "Find what this change breaks outside the diff. Identify the one fact it is safe because of and prove it
by running real code (a script or test that fails loudly if wrong); paste the output. Report: what it does
(including the non-obvious part), the safety fact with its proof level, confirmed risks (how it breaks,
`file:line`, likelihood, cost, how to check), cleared risks, and the cheapest pre-merge check. You may write
throwaway scripts in a temp dir; do not modify the checkout."
