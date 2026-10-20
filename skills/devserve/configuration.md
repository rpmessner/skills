# Configuration and app contract

Config lives at `~/.config/devserve/apps.toml`. `DEVSERVE_CONFIG_DIR` overrides its directory for tests.
Creating user config or changing an app's dev config requires operator approval.

```toml
[[apps]]
name = "example"
path = "/absolute/path/to/main-checkout"
ports = [4700, 4799]
start = ["/absolute/path/to/mix", "phx.server"]
env_file = "/absolute/path/to/untracked-secrets.env"
env = { APP_ROLE = "web" }
data = "copy"
source_database = "example_dev"
migrate = ["/absolute/path/to/mix", "ecto.migrate"]
main_units = ["example-web.service"]
```

`name`, `path`, `ports`, `start`, `data`, and `migrate` are required. Names are lowercase identifiers
(up to 20 characters, letters/digits/underscores). Commands are nonempty argv arrays, not shell strings;
use absolute executables or configure a non-secret PATH in `env` (services do not source shell profiles).
Paths must be absolute. App port ranges are inclusive, 1024–65535, and must not overlap.
Worktrees match by git common directory, not branch or basename.

`data = "copy"` requires `source_database`, a PostgreSQL database name, never a credential-bearing URL.
`data = "fresh"` requires `seed`, an argv array: create → migrate → seed. Copy uses
`pg_dump --format=custom` → `pg_restore --no-owner --no-acl` → migrate. A kept database is reused,
with migrations rerun but no recopy or reseed. To recopy, use `down --drop-db`, then `up`.
`env_file`, `env`, and `main_units` are optional. Unknown fields are errors.

`data = "template"` requires `template_database`, a database name up to 58 characters.
Run `base refresh <app>` to clone `source_database` into an owned base, then clone that base for each preview.
The source must have no connections during refresh; `--dump` uses pg_dump/pg_restore instead and allows a busy source.
Refresh builds a staging database and swaps names transactionally. It refuses unowned base/staging databases.
Preview migrations still run on every start. Base databases are retained by gc and down.
Templates and orphan cleanup are shared by both backends; existing copy/fresh preparation is unchanged.

## Secret transport

All config, command arrays, branch names, owner labels, and worktree paths are public metadata.
Put secrets only in the untracked `env_file` (chmod 600), using systemd EnvironmentFile syntax, not shell exports.
It may contain `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, and application secrets. PostgreSQL defaults are
localhost:5432 and the OS username. Use TCP authentication; Unix-socket DATABASE_URL generation is not supported.
On Linux/systemd, EnvironmentFile is loaded by systemd, not parsed or copied into CLI arguments.
On tmux, the worker reads a literal dotenv subset: `KEY=value`, optional `export`, blank lines and full-line comments.
Matching single/double quotes are removed. Use single quotes for literal dollar signs; shell substitution and
backslash escapes are rejected otherwise. The file must be owned by you with mode 0600.
Its values never enter the state file, tmux command arguments, or tmux server environment.
Reserve `DEVSERVE_*` and `NOTIFY_SOCKET` for the tool. `PORT`, `DATABASE_URL`, and `PREVIEW` are overridden for the app.

The worker builds DATABASE_URL in memory; database tools receive authentication via their environment.
The unit's `Environment` contains only non-secret metadata, PORT, PREVIEW, and plain `env` variables.
The EnvironmentFile path is visible in `systemctl show`; its values are not. Applications and configured
commands must not print secrets or put DATABASE_URL in subprocess argv. The tool cannot make an
arbitrary application's logging safe. Preparation errors report the executable and exit code, suppressing
potentially secret-bearing child diagnostics.

## App contract

Start and migration/seed commands receive `PORT`, `DATABASE_URL`, and `PREVIEW=1`.
The dev server must bind on the assigned port and honor DATABASE_URL. Up waits for a localhost TCP listener
(up to 30 seconds after preparation); browser/content checks remain the caller's responsibility.
An app with external writes must refuse them under PREVIEW=1, including forge writes, pushes, merges,
and launching sessions. Check this when registering an app; copied data may contain pending actions.

## Registry and cleanup

Unit names use `devserve-<app>-<sanitized-worktree>-<path-hash>.service`; databases use
`<app>_preview_<sanitized-worktree>_<path-hash>`. The path hash distinguishes same-basename worktrees.
`ls --json` previews contain `unit`, `app`, `worktree`, `branch`, `port`, `url`, `database`, `owner`,
`state`, and `missing`. Tmux entries also carry `backend = "tmux"`; older/systemd entries omit it.
Main entries contain `unit`, `app`, and systemd `state`. Systemd main units are Linux-only and read-only.

On Linux, systemd remains the default registry. RemainAfterExit retains a stopped preview as an `active/exited` unit;
its StatusText is the logical lifecycle state. `down --drop-db` drops the owned database before unloading
the unit. If dropping fails, metadata stays available for retry. Mutation commands serialize on a runtime
flock (a lock, not a registry file). Other programs can still race a port bind; startup failure rolls back
new data. Commands time out after 120 seconds; total startup waiting is bounded at 150 seconds.
Ctrl-C during startup stops the worker and rolls back new data.

On macOS, previews run in windows of the `devserve` tmux session. The private registry is
`$XDG_STATE_HOME/devserve/previews.json`, defaulting to `~/.local/state/devserve/previews.json`.
`DEVSERVE_STATE_DIR` overrides that directory. Writes use flock and atomic replacement; keep the directory mode 0700.
Logs stay beside the registry, mode 0600, and `logs -f` follows them. `down --drop-db` removes the entry and log
only after a successful database drop. Window name, server PID, pane PID and an ownership token must match
before a window is stopped or removed. Unrelated windows and the session itself are never removed.
`DEVSERVE_TMUX_SOCKET` selects a named socket or absolute socket path for isolated tests. Keep a distinct state
directory per socket; a socket mismatch fails closed. The caller's `$TMUX` does not redirect previews.

Linux commands read both registries, regardless of the selected backend. `up` reuses an existing preview's
backend; `down`, `logs`, and `gc` route to its owner. Duplicate identities across registries fail closed.
On macOS no systemd queries run. Mutations serialize across backends on the same host.

Units vanish on reboot; databases kept by `down` do not. Re-running `up` at the same path reclaims an owned
database. `gc` also discovers orphan databases by exact name and ownership comment, checks all known previews,
and retains those belonging to existing git worktrees. `gc --stopped` also removes stopped/failed previews and
orphans for existing worktrees. An orphan with active connections is never dropped. Source and base databases
are excluded. Orphan discovery uses each configured app's PostgreSQL credentials and git worktree list.
An interrupted CREATE DATABASE before its ownership COMMENT may leave an unmarked database; the tool refuses
to adopt or delete it. Inspect it manually rather than weakening the ownership check.
