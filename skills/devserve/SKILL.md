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
- `gc` removes previews whose worktrees no longer exist, including owned orphan databases.
- `gc --stopped` also drops stopped/failed previews and owned orphan databases for existing worktrees.
- For template data, run `base refresh <app>` before the first preview. See [configuration.md](configuration.md).

Owner comes from `FOREMAN_SESSION`, otherwise the OS username. Main services are read-only here.
A failed start rolls back a newly created database; its failed registry entry remains for inspection and `down --drop-db`.
Only databases with the matching devserve ownership comment can be reused or dropped.

## Install (operator-approved)

Requires Python 3.11+, git, and PostgreSQL client tools matching the server.
Linux uses user systemd (255+); macOS uses tmux (3.2+). `DEVSERVE_BACKEND=systemd|tmux` overrides selection.
Keep the script beside its `devserve_tmux.py` and `devserve_data.py` modules when installing.
After approval, link the script's absolute path into `~/.local/bin/devserve` with `ln -s`.
No installation is required to use the Python invocation above.

## Verify

```sh
python3 -m unittest discover -s skills/devserve/scripts
DEVSERVE_INTEGRATION=1 python3 -m unittest discover -s skills/devserve/scripts
python3 scripts/check.py
```

Run these from the skills repo root. Integration tests require the local throwaway-test PostgreSQL login
`postgres/postgres` on localhost, tmux, and a working user systemd manager. They create only `devserve_test*`
databases, their own transient units, and scratch `tmux -L devserve-test-<pid>` servers, then clean them up.
The tmux suite runs under `DEVSERVE_BACKEND=tmux` on Linux; it does not require a macOS host.
The [lifecycle diagram and matrix](lifecycle.md) are generated from the declared table and checked by tests.
