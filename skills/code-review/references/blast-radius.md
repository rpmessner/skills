<!-- house: adapt; from: pstack:pstack/skills/blast-radius@850d7f2 -->

# Blast radius (Risk axis)

Listing callers is not the job; grep does that in a second. The job is the breakage grep won't show. A writeup
that sounds right is worthless on its own, so prove the load-bearing fact by running code.

## Steps

1. **Read the change**: the diff, the symbols added/changed/deleted, and what now behaves differently, including
   what the diff doesn't spell out. Pull the PR description and commit messages.
2. **Find the one fact it is safe because of.** Most risky-looking changes are safe because of a single fact
   ("this call only drops already-dead cache entries"). If it holds, most risks clear at once. Spend time here,
   not on a long list of maybes.
3. **Look where grep stops**: the source of the library you call, at its pinned version and any local patch;
   when things run (async ordering, teardown, supervision/restarts); data that crosses a boundary: API JSON, DB
   columns, wire formats, saved files another program reads, feature flags, code several hops downstream.
4. **Be honest about each risk**: real likelihood and real cost. Cite real `file:line`; a search that finds
   nothing is still an answer; never invent a caller or API.
5. **Prove the fact**: a small script or test that imports what the app ships and calls the exact function in
   question. Run it and paste the output.

## Proof levels

1. Said so. 2. Cited the line. 3. Walked the failure and showed it can't happen. 4. Ran code that fails loudly
if wrong. 5. Reproduced in the running app. Say which level the safety fact reached; below 4 is "unproven".

## Hand back

- **What it does**, including the non-obvious part.
- **The safety fact**, its proof level, and the proof.
- **Risks**: how it breaks, `file:line`, likelihood, cost, how to check.
- **Cleared**: what you checked and why it is fine.
- **Before merge**: the cheapest test or repro that catches the real bug, including the script you wrote.

For a large or wide change, a second reviewer on a different model family catches different bugs; offer it, don't
spawn it unasked.
