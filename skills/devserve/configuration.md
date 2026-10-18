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

## Secret transport

All config, command arrays, branch names, owner labels, and worktree paths are public metadata.
Put secrets only in the untracked `env_file` (chmod 600), using systemd EnvironmentFile syntax, not shell exports.
It may contain `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, and application secrets. PostgreSQL defaults are
localhost:5432 and the OS username. Use TCP authentication; Unix-socket DATABASE_URL generation is not supported.
EnvironmentFile is loaded by systemd, not parsed or copied into CLI arguments. Reserve `DEVSERVE_*` and
`NOTIFY_SOCKET` for the tool. `PORT`, `DATABASE_URL`, and `PREVIEW` are overridden for the app.

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
`state`, and `missing`. Main entries contain `unit`, `app`, and systemd `state`.

Systemd is the registry. RemainAfterExit retains a stopped preview as an `active/exited` unit;
its StatusText is the logical lifecycle state. `down --drop-db` drops the owned database before unloading
the unit. If dropping fails, metadata stays available for retry. Mutation commands serialize on a runtime
flock (a lock, not a registry file). Other programs can still race a port bind; startup failure rolls back
new data. Commands time out after 120 seconds; total startup waiting is bounded at 150 seconds.
Ctrl-C during startup stops the worker and rolls back new data.

Units vanish on reboot; databases kept by `down` do not. Re-running `up` at the same path reclaims an owned
database. `gc` only knows units still registered in systemd: it cannot discover pre-reboot orphan databases.
An interrupted CREATE DATABASE before its ownership COMMENT may leave an unmarked database; the tool refuses
to adopt or delete it. Inspect it manually rather than weakening the ownership check.
