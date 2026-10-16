# Publishing tickets

<!-- house: adapt; from: mattpocock:skills/engineering/to-tickets@49dd158 (templates), beads CLI -->

## Beads

`--deps <id>` on `bd create` means "the new ticket is blocked by `<id>`". Comma-separate several.
Use `--silent` to capture ids, and `--body-file -` with a heredoc for multi-line descriptions.

```bash
# Epic: skip if the source is an existing bead; use that id as the parent instead.
EPIC=$(bd create "<feature title>" -t epic --silent --body-file - <<'EOF'
<approved spec: Goal, Why, Non-goals, Acceptance checks, Ask-first boundaries>
EOF
)

# Tickets, blockers first.
T1=$(bd create "<ticket title>" --parent "$EPIC" --silent \
  --acceptance $'- [ ] <criterion>\n- [ ] <criterion>' \
  --body-file - <<'EOF'
## What to build
<end-to-end behavior this ticket makes work, from the user's perspective>

## Interfaces
<only if it hands a named contract to another ticket: Produces / Consumes>
EOF
)

T2=$(bd create "<ticket title>" --parent "$EPIC" --deps "$T1" --silent \
  --acceptance $'- [ ] <criterion>' --body-file - <<'EOF'
## What to build
...
EOF
)

bd graph "$EPIC"             # check the edges (children in layers)
bd ready --parent "$EPIC"    # the frontier: what can start now
```

- Type: default `task`; use `-t feature` or `-t bug` when that is what it is.
- Edge added late or wrong: `bd dep add <blocked> <blocker>` / `bd dep remove <blocked> <blocker>`.
- Don't add triage labels: `bd ready` already is the agent-grabbable frontier.

## Local fallback (no `.beads/`)

`.scratch/<feature-slug>/issues/NN-<slug>.md`, one file per ticket, numbered from `01` in dependency
order. Put the approved spec in `.scratch/<feature-slug>/spec.md`.

```markdown
# <NN>: <Ticket title>

**What to build:** the end-to-end behavior this ticket makes work, from the user's perspective, not a
layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Interfaces:** (only if it hands a named contract to another ticket) Produces / Consumes.

**Status:** open

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```

The frontier is every open ticket whose blockers are all done; for a linear chain, top to bottom.
