# House skills

One rationalized agent skill set for Claude Code and pi, built from pinned upstream sources plus my own skills. This repo is the only skill source linked into `~/.claude/skills` and `~/.agents/skills` (pi reads the latter).

## Layout

- `skills/<name>/SKILL.md` — flat, one dir per house skill. `name:` in front matter must equal the dir name (lowercase, hyphens).
- `catalog.toml` — the manifest. Every house skill has exactly one `[[skill]]` entry: `job`, `mode` (`own` | `adopt` | `adapt` | `merge`), and `from` (source refs `source:path`). Upstream skills deliberately not taken are `[[drop]]` entries with a `reason`. `[sources.*]` pin each upstream to a full commit; optional `scope` limits it to a subtree.
- `scripts/check.py` — the gate: manifest ↔ dirs coverage, every `from`/drop ref resolves under its source path (globs allowed), every upstream SKILL.md dir in scope is covered by a `[[skill]]` or `[[drop]]` ref, no name collisions, name rules, always-on description token budget. Run before any commit.
- `scripts/link.py` — links exactly the house skills into the harness dirs and prunes links that point into this repo but no longer exist. Dry run by default; `--apply` makes the changes.
- `scripts/sync.py` — fetches sources and writes `reports/YYYY-MM-DD.md`: pin bumps for adopted skills, diff digests for adapted/merged ones, unmapped upstream skills. `--file-beads` files one bead per candidate; `--bump <source> <commit>` rewrites a pin. Driven by the `skills-sync` skill.
- `pi/house-guard/` — pi extension that runs the Claude Code hooks in `~/.claude/hooks/` (the one source of truth) on every pi `bash` call and blocks what they block; fails closed if a hook cannot run. Test: `node pi/house-guard/test.ts`. Try for one run: `pi -e ~/dev/utils/skills/pi/house-guard`; enabled for every run by its path in the `packages` list of `~/.pi/agent/settings.json`.

## Rules

- Sources live read-only in `~/dev/utils/skill-sources/`; never edit them, never link them into a harness.
- Adopted skills are vendored copies, byte-identical to the pinned source except a provenance comment. Adapted and merged skills carry a provenance comment listing every source ref and pin.
- One skill per job. Before adding a skill, check `catalog.toml` for an existing job; extend that skill instead.
- Keep always-on cost low: descriptions are one or two sentences with concrete triggers. Long reference material goes in files the skill loads on demand.
- Decisions about what to take from upstream are tickets (`foreman new` in `tickets/`), not ad hoc notes.



<!-- BEGIN FOREMAN -->
## Tickets

Use the globally linked `foreman` skill (`~/.agents/skills/foreman/SKILL.md`).
<!-- END FOREMAN -->
