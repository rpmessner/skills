---
name: devserve
description: Use when starting, inspecting, or cleaning up a worktree app preview, or configuring an app for isolated browser checks.
---

<!-- house: own -->

# devserve

Run `python3 scripts/devserve up [worktree]` and open the printed URL for browser checks.
The app must already be registered in `~/.config/devserve/apps.toml`; configuration and the app contract are in [configuration.md](configuration.md).

- `ls --json` returns `previews` and `main_units`; select your preview by `worktree` or `owner`.
- `logs <unit> -f` follows the preview; `logs <app>` tails that app's installed main units.
- `down <unit>` stops the app and keeps its database for the next `up`.
- At session close-out, run `down <unit> --drop-db` and confirm the unit disappeared from `ls --json`.
- `gc` removes registered previews whose worktree directories no longer exist.

Owner comes from `FOREMAN_SESSION`, otherwise the OS username. Main services are read-only here.
A failed start rolls back a newly created database; its failed registry entry remains for inspection and `down --drop-db`.
Only databases with the matching devserve ownership comment can be reused or dropped.

## Install (operator-approved)

Requires Linux user systemd (255+), Python 3.11+, git, and PostgreSQL client tools matching the server.
After approval, link the script's absolute path into `~/.local/bin/devserve` with `ln -s`.
No installation is required to use the Python invocation above.

## Verify

```sh
python3 -m unittest discover -s skills/devserve/scripts
DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts
python3 scripts/check.py
```

Run these from the skills repo root. Integration tests require the local throwaway-test PostgreSQL login
`postgres/postgres` on localhost and a working user systemd manager. They create only `devserve_test*`
databases and their own transient units, and remove them in cleanup.
The [lifecycle diagram and matrix](lifecycle.md) are generated from the declared table and checked by tests.
