<!-- house: merge; from: superpowers:skills/verification-before-completion@bb92a77, pstack:pstack/skills/blast-radius@850d7f2 -->

# What each claim needs

| Claim | Needs | Not enough |
|---|---|---|
| Tests pass | This turn's test output: 0 failures | An earlier run, "should pass" |
| Linter/format clean | Linter output: 0 errors | A partial check |
| Builds / compiles | Build exit 0, warnings read | Linter passing |
| Bug fixed | Original symptom re-run and gone | Code changed, assumed fixed |
| Regression test works | Seen red without the fix, green with it | Passes once |
| Deployed | The running target shows the new behaviour (reload, probe, screenshot) | Files copied |
| Subagent finished | VCS diff inspected, its verifier re-run | Its success report |
| Requirements met | Line-by-line check against the spec or bead | Tests passing |
| Safe to merge | The one fact it is safe because of, proven by running code | A convincing writeup |

## Regression red-green

Write test → run (pass) → revert or stash the fix → run (must fail) → restore → run (pass). If you forced the red
by mutating a file, diff against a pristine copy to prove the mutation landed.

## How sure is a claim

1. You said so. Worth nothing alone.
2. You cited the line (`file:line`, or the library's own source).
3. You walked the failure step by step and showed it cannot happen.
4. You ran a script or test against the real code that fails loudly if you are wrong.
5. You reproduced it in the running app.

Report which level each load-bearing claim reached.
