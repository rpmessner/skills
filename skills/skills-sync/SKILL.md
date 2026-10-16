---
name: skills-sync
description: Back-import upstream skill changes into the house set, from fetch through decision beads to pin bumps.
disable-model-invocation: true
---

<!-- house: own -->

# Skills sync

Run from `~/dev/utils/skills-house`. Upstream sources are read-only: never edit them; `git fetch` is the only write.

1. **Report.** Run `scripts/sync.py`. It fetches each source and writes `reports/YYYY-MM-DD.md`, then prints the candidates. Zero candidates: tell the user, stop.
   Done when the report exists and you have its candidate list.
2. **Read each digest against the house version.** For every adapt/merge section, read the diff and the current `skills/<name>/` files. Name each upstream idea in one line, then classify it:
   - **adopt**: the house skill lacks it and it fits as written.
   - **adapt**: worth having, but it needs house edits (beads instead of GitHub issues, the house skill names, no push).
   - **drop**: already covered, contradicts the house `AGENTS.md`, or harness-specific. Say which.
   Pure deletions upstream count as ideas too: decide whether the house copy keeps the cut text.
   For adopt sections, the action is fixed: re-vendor byte-identical and keep the provenance comment. Unmapped skills need a `[[skill]]` or `[[drop]]` decision. Vanished refs need re-pointing or a drop.
   Done when every candidate has a one-line verdict per idea.
3. **Propose as beads.** Show the user the verdict table. On approval, file one bead per idea that changes a house skill (`bd create ... -l sync`, parented to the open sync epic if one exists). `scripts/sync.py --file-beads` files one bead per candidate instead, when the user wants coarse tracking.
   Done when every accepted idea is a bead and every drop has a reason the user saw.
4. **Apply and bump after the decision.** Work the beads. Re-vendor adopted skills, update adapted and merged skills and their provenance pin (`@<short sha>`), and add any `[[skill]]`/`[[drop]]` entries. Only when every candidate from a source is decided, run `scripts/sync.py --bump <source> <commit>`. A pin ahead of an undecided change hides that change from the next sync.
5. **Gate.** Run `scripts/check.py` and fix the cause of any error until it reports 0 errors within the budget. Then rerun `scripts/sync.py --no-fetch`. Every bumped source must report no changes.
