<!-- house: adapt; from: superpowers:skills/receiving-code-review@bb92a77 -->

# Receiving review feedback

## By source

- **The user**: trusted; implement once understood, still ask if scope is unclear.
- **External reviewers and subagents**: check before implementing. Correct for this codebase and stack? Breaks
  existing behaviour? A reason for the current shape (compat, platform, legacy)? Does the reviewer have the full
  context? If you can't verify, say so: "I can't verify this without X. Investigate, ask, or proceed?"

## Push back when

- it breaks working behaviour or a test;
- the reviewer lacks context the code or history shows;
- it adds a feature nothing uses (grep first: "Nothing calls this endpoint. Remove it instead?");
- it is wrong for this stack or version;
- it conflicts with a decision the user already made (stop and ask the user).

Push back with technical reasoning and evidence, not defensiveness.

## Wording

- Correct: "Fixed: <what changed> in `file:line`." Or just fix it and show the diff.
- Disagree: "Checked: build targets X, this API needs Y; keeping the fallback. Alternatively drop X support?"
- Unclear: "Understand 1, 2, 3, 6. Need clarification on 4 and 5 before implementing."
- Wrong pushback: "Checked X; it does Y, you were right. Fixing."

Avoid "You're absolutely right!", "Great point!", and thanks: state the fix instead.

## Order for multi-item feedback

Clarify unclear items first; then blocking issues (breakage, security), simple fixes, then structural ones. Run
the relevant check after each; confirm no regressions at the end.

## Replying on GitHub

Reply in the inline comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a
top-level PR comment, and mark agent-written replies as agentic.
