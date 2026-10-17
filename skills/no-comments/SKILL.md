---
name: no-comments
description: "Run Comment Sicko over a diff, fix accepted findings, and offer encodings for claimed constraints."
disable-model-invocation: true
---

<!-- house: adapt; from: pstack:pstack/skills/no-comments@850d7f2, pstack:pstack/agents/comment-sicko.md@850d7f2. Changes: Cursor `Task`/`subagent_type` spawn -> harness-neutral subagent with bundled brief; poteto-mode reasoning-level line dropped; `/how` `/why` -> trace callers and git history; `/architect` -> inline shape sketch; principle-* skills -> house `principles` references; house edit 2026-10-16: Comment Sicko runs as an in-context pass unless the user asked for subagents. -->

# No comments

Run Comment Sicko ([references/comment-sicko.md](references/comment-sicko.md)). Act on accepted findings.

Defer to Comment Sicko's fresh perspective.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Run [references/comment-sicko.md](references/comment-sicko.md) over the scope. Default, and always inside a pi build window: run the brief yourself as a separate pass, finished and written up before step 2, and say so in the report. Only when the user asked for subagents: spawn a fresh-context subagent (Claude Code: the Agent tool; pi: the `subagent` tool) with that brief and the scope, without restating its rules. As the coordinator without that request, ask the user before spawning.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, trace their symbol: read its callers and its history (`git log -S`, `git blame`). If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, sketch it once (types, signatures, module boundaries) for the accepted set and surrounding code. Stop at the sketch. The sketch shapes. Step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The fix-root-causes and redesign-from-first-principles references in the **principles** skill guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. Unattended and eval require caller pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work.
6. Report the deletion count, restored comments, reruns, shape sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.
