# Publishing ticket files

Use in a main checkout with `tickets/`. The repo must be registered with a prefix; onboarding is a
user-approved `foreman adopt`, not an implicit publishing step. The CLI writes locally without a server.

`--body` takes text, not a filename. Keep the approved spec as the epic body; child bodies contain
What to build, Interfaces when needed, and Acceptance checkboxes. `--blocked-by` takes comma-separated
ids. Create blockers first. Use direct CLI calls: the board's best-effort sender would hide failures.

```bash
set -euo pipefail
# Skip new epic when the source is an existing ticket; keep its body unchanged.
EPIC=$(foreman new "<feature title>" --type epic --body "$(< "$SPEC")" --json | jq -er '.id')

T1=$(foreman new "<first ticket title>" --parent "$EPIC" --body "$(< "$FIRST_BODY")" --json | jq -er '.id')
T2=$(foreman new "<next ticket title>" --parent "$EPIC" --blocked-by "$T1" \
  --body "$(< "$NEXT_BODY")" --json | jq -er '.id')

foreman check --json | jq -e '.valid == true'
foreman tree "$EPIC" --json
foreman ready --json | jq --arg epic "$EPIC" '[.[] | select(.parent == $epic)]'
```

`SPEC`, `FIRST_BODY`, and `NEXT_BODY` are paths to the approved prose. The example publishes two
slices; repeat `new` for the approved breakdown. Inspect returned ids, bodies and edges: handled I/O
failures may warn with exit 0, so exit status alone is not proof of publication. Stop on missing JSON
or a refused write; inspect existing files before retrying to avoid duplicate tickets.

Late edge: `foreman dep add <blocked> <blocker>` / `foreman dep rm <blocked> <blocker>`, then
`foreman check`. Do not block a child on its own epic. Hand the files to the coordinator for an
authorized commit; publishing neither commits nor starts implementation.
