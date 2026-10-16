<!-- house: merge; from: superpowers:skills/systematic-debugging/root-cause-tracing.md@bb92a77, superpowers:skills/systematic-debugging/defense-in-depth.md@bb92a77, pstack:pstack/skills/principle-fix-root-causes@850d7f2 -->

# Root-cause tracing

Bugs often surface deep in a call chain (a command run in the wrong directory, a file written to the wrong
place). Fixing where it surfaces treats the symptom.

## Trace backward

1. **Symptom**: the exact failure (`git init` ran in the source tree).
2. **Immediate cause**: the line that does it (`exec('git init', {cwd: projectDir})`).
3. **What called it, with what value?** Walk up one caller at a time (`projectDir = ''`; empty `cwd` means the
   process cwd).
4. **Keep going** until you reach the origin of the bad value (a test read a fixture field before setup filled
   it in).
5. **Fix at the origin** (make the field fail loudly if read too early).

Ask "why" at each level until the answer is a decision in code, not a consequence of one.

## When you cannot trace by reading

Log immediately **before** the suspect operation, with the inputs, cwd/env that matter, and a captured stack
(`new Error().stack`, `Process.info(self(), :current_stacktrace)`, `debugstack()`, etc.). In tests, write to
stderr so a quiet logger cannot swallow it. Tag the line (`[DEBUG-xxxx]`). Run, filter on the tag, read the
stacks for the triggering test or caller.

If you do not know which test causes a side effect, bisect: run tests one file at a time and stop at the first
that produces it.

## After the root fix: make the bug hard to reintroduce

Fixing the origin is the fix. Separately, consider validation where the bad value crosses a real boundary
(public entry point, persistence, external call) so a different path cannot reintroduce it. This is a judgement
call, not a mandate: a check at every layer is over-engineering for most bugs, and a guard that hides the
symptom without fixing the origin is still a symptom fix.
