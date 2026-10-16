# Subagent mode: briefs

Hand artifacts over as files and ids. Everything pasted into a brief, and everything a subagent prints back, stays in the controller's context for the rest of the session.

## Implementer brief

Fill the brackets; send nothing else. Exact values (signatures, constants, test cases) live in the bead or spec, never restated here.

```
You are implementing bead [ID]: [title].

Read first, in order:
- `bd show [ID]`: your requirements and acceptance criteria. Use its exact values verbatim.
- [spec path, if any]: the authority the ticket argues from.
- [repo AGENTS.md / CLAUDE.md]: the repo's standards.

Where this fits: [one line].
Interfaces/decisions from earlier tickets you cannot know: [list, or "none"].
My resolution of ambiguities I noticed: [list, or "none"].
Agreed test seams: [list].
Work in: [cwd / worktree], branch [name]. [Commit per ticket | Do not commit.]

Rules:
- Run the `tdd` skill at the agreed seams. Watch every new test fail before making it pass.
- Build exactly the ticket. Out-of-scope work you notice: list it in your report; do not do it.
- Do not dispatch subagents, including reviewers. Review is the controller's job.
- Ask before starting if requirements are unclear. Stop with BLOCKED when the ticket needs an
  architectural choice it does not make, or you are reading file after file without progress.
  Bad work is worse than no work.
- Before reporting, read your own diff: anything missing, anything extra, tests asserting real
  behaviour, output pristine.

Write the full report to [report path]:
- what you built (or attempted), files changed
- TDD evidence: RED command + failing output and why it was the expected failure;
  GREEN command + passing output; full-suite command + result
- rulings you made, concerns, out-of-scope observations

Reply with at most 15 lines:
- Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- commits (short sha + subject), or "uncommitted"
- one-line test summary
- concerns
- report path
If BLOCKED or NEEDS_CONTEXT, put the specifics in the reply itself.
```

## Fix-round brief

Resume the original implementer when the harness can message a live subagent; otherwise dispatch a fresh one with the same brief plus:

```
Review of bead [ID] found these issues (verbatim):
[Critical/Important findings, one per bullet, with file:line]

Fix each one with a failing test first where it is behavioural. Re-run the covering tests and
the full suite. Append a fix report (changes, commands, output) to [report path], then reply
with the same short status contract.
```

From round 3 on, prefer a fresh implementer on a stronger model with the framing: "A prior implementer attempted this [N] times; you own it now. Read the report file for what was tried."

## Parallel brief additions

For parallel tickets, add to the implementer brief:

```
Your worktree must be based on [integration branch]; reset onto it if not.
Before reporting, merge the integration branch tip into your branch and re-run the suite.
Report PASS / ISSUES / BLOCKED with evidence; list every issue you can prove, not just the first.
```
