<!-- house: merge; from: mattpocock:skills/engineering/diagnosing-bugs@49dd158, superpowers:skills/systematic-debugging/condition-based-waiting.md@bb92a77 -->

# Feedback loops

## Ways to build one (roughly in order, after the end-to-end repro)

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **HTTP script** (curl) against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright/Puppeteer) asserting on DOM, console, network.
5. **Replay a captured trace**: save a real request/payload/event log to disk and replay it through the code path.
6. **Throwaway harness**: the smallest subset of the system (one service, stubbed deps) that hits the path.
7. **Property/fuzz loop** for "sometimes wrong output": many random inputs, look for the failure mode.
8. **Bisection harness**: automate "boot at state X, check" so `git bisect run` can drive it.
9. **Differential loop**: same input through old vs new version (or two configs), diff outputs.
10. **Probe read back from saved output** when the runtime is outside your control (game client, device): write
    the probe, run it, read the result from the saved file, then act.
11. **HITL script** (last resort): copy `scripts/hitl-loop.template.sh`, edit the steps, run it; the human
    follows prompts and the captured `KEY=VALUE` output comes back to you.

## Tighten the loop

Treat the loop as a product:

- **Faster**: cache setup, skip unrelated init, narrow the test scope.
- **Sharper**: assert on the specific symptom, not "didn't crash".
- **More deterministic**: pin time, seed RNG, isolate the filesystem, freeze the network.

A 30-second flaky loop is barely better than none; a 2-second deterministic one is a superpower.

## Non-deterministic bugs

The goal is a higher reproduction rate, not a clean repro. Loop the trigger 100×, parallelise, add stress,
narrow timing windows. 50% is debuggable; 1% is not, so keep raising it.

Flaky tests that sleep for a guessed duration: wait for the condition instead (poll the state/event/file with a
timeout and a clear error). A fixed delay is correct only when testing timed behaviour itself (debounce,
ticks), and then it comes after waiting for the triggering condition and carries a comment saying why.

## Forced reds

If you made the loop go red by mutating code or a fixture, `diff` against a pristine copy to prove the mutation
landed before trusting the result.
