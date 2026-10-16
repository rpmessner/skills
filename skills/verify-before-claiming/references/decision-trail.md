<!-- house: adapt; from: pstack:pstack/skills/show-me-your-work@850d7f2 -->

# Decision trail (long or unattended runs)

Use when a run is long, multi-phase, or reviewed by the user after stepping away. Skip it for ordinary turns.

One TSV file, one row per decision, append-only. Default location `decisions.tsv` in the work dir (or
`.audit/<task-slug>.tsv` when several efforts run at once), kept out of git unless the user wants the trail
committed.

Columns: `ts  phase  decision  why  evidence  result`

- **decision**: what was chosen or done, one line, plain words.
- **why**: the reason in plain words.
- **evidence**: a pointer, never prose: commit SHA, `file:line`, artifact/screenshot path, command.
- **result**: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

Log forks, completed units with their verification result, pivots and reverts with their trigger, and blockers.
Not every action. Keep cells single-line and escape cells that start with `= + - @` (prefix a `'`) if any content
is generated or user-supplied.

A wrong row is superseded by a new row, never edited. Before handing back, walk your rows against what actually
happened: every row maps to a real action, every evidence pointer resolves, and any pivot that shaped the work is
logged.

Durable follow-ups go in beads, not in the trail.
