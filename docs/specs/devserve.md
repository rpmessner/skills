# devserve: worktree previews as systemd user services

Status: approved 2026-10-18. Skills initiative sk-9ro; board draft epic `draft:devserve` (project skills).

## Goal

One command, `devserve up`, runs a worktree's app as a preview: a transient systemd user service on a port from the app's range, with its own database copied from the app's main data, logs in journald, and `devserve ls / logs / down` to see, follow and remove previews; build sessions use it for browser checks and foreman's preview button (fm-c2w.14) builds on it.

## Why

The user wants to try branches without tmux windows full of servers and without previews left running; build sessions today improvise ports (4766, 4771, 4779), acceptance databases and hand-run servers in every brief. A shared tool makes previews quick, realistic and always cleaned up.

## Non-goals

- Installing or updating apps' main versions (user, Q3). Mains keep their own units (foreman's are the model); devserve only lists and tails them.
- A per-repo devserve file (user, Q2).
- Remote access, TLS, multiple users.
- Auto-starting previews at login, or restarting them after a reboot (they are transient).
- foreman's preview button and stage-tied cleanup: that is fm-c2w.14 in the foreman repo, built on this.

## Decisions

1. **Previews run the dev server from source** (user, Q1): the app's dev start command (for Phoenix, `mix phx.server`) in the worktree, with live reload; no release builds.
2. **One central config** (user, Q2): `~/.config/devserve/apps.toml`, kept in dotfiles, with no secrets. Per app: `name`, `path` (main checkout; worktrees are matched by git common dir), `ports` (an inclusive range, ranges may not overlap across apps; checked on load), `start` (command), `env_file` (absolute path to an untracked file with secrets, optional), `env` (extra plain variables, e.g. a role), `data` (`copy` or `fresh`), `source_database` (for `copy`), `migrate` (command), `seed` (command, for `fresh`), `main_units` (names of the app's installed units, listed in `ls` and tailed by `logs`).
3. **Previews only** (user, Q3): commands `up [worktree]`, `ls`, `logs <preview|app> [-f]`, `down <preview> [--drop-db]`, plus `gc` to remove previews whose worktree is gone. No `install`.
4. **Data: a copy of the app's main data** (user, Q4, "for now"): `up` dumps `source_database` and restores it into `<app>_preview_<worktree>` (dump/restore, so it works while the main app runs), then runs `migrate`. `data = "fresh"` (create, migrate, seed) stays available per app.
5. **systemd is the registry** (agent call). A preview is a transient user unit `devserve-<app>-<worktree>` started with `systemd-run --user`, carrying its app, worktree path, branch, port, database and owner (user or a session name) as unit environment and description; `ls` reads them back from systemd. No state file.
6. **Ports and the app contract** (agent call). `up` takes the first port in the app's range that no unit claims and nothing listens on. devserve sets `PORT` and `DATABASE_URL` for the preview; each app's dev config must honour both (a one-line change per app, made in that app when it is added to apps.toml; foreman first). Secrets come only from `env_file` via the unit's EnvironmentFile; never in unit names, arguments or the description.
7. **Cleanup** (agent call). `down` stops the unit and keeps the database; `down --drop-db` also drops it; `gc` stops units and drops databases of previews whose worktree no longer exists. Previews never outlive a reboot. `ls` marks previews whose worktree is gone.
8. **Build sessions use devserve** (user, Q5). The dispatch brief template replaces "use another port and your own databases" with "run `devserve up` for browser checks"; the session's preview carries the session name as owner; coordinator close-out runs `devserve down --drop-db` for it before killing the window.
8a. **Previews never write outside themselves** (agent call, from the builder check). Copied data can hold approved-but-unrun actions (foreman's inbox pushes and merges), so a preview must not act on them. devserve sets `PREVIEW=1` for every preview; an app that performs external writes must refuse them when it is set (foreman: no forge writes, pushes or merges, and no tmux launches; reads are fine). Adding an app to apps.toml includes checking this.
9. **Where it lives** (agent call). A `devserve` skill in the skills repo (`own`) with its script (`devserve`, Python 3 standard library, like the dispatch scripts) and a short SKILL.md; linked into `~/.local/bin` by the skill's install note. Preview lifecycle (absent, starting, running, failed, stopped) is a small declared table in the script with a pure step, per the house state-machine rule.

## Acceptance checks

1. In a foreman worktree, `devserve up` prints a URL within the app's range; the page loads with the user's real tickets (copied data); a code edit reloads the page.
2. Two worktrees of the same app get different ports and databases; a third app's range is never used; overlapping ranges in apps.toml are refused on load.
3. `devserve ls` shows each preview's app, branch, port, URL, owner, state and the app's main units; `logs -f` follows a preview's output.
4. `down` stops the unit and keeps the database; `down --drop-db` removes both; `gc` cleans a preview whose worktree was deleted; nothing remains in `systemctl --user list-units 'devserve-*'` or in Postgres afterwards.
5. No secret value appears in `systemctl --user show` output of a preview, in its unit name, or in `ps` arguments.
6. A real dispatched build session runs its browser check against `devserve up`, and close-out leaves no preview or database behind.
7. A foreman preview whose copied data holds an approved push request does not push (the request fails as refused in preview), and makes no GitHub write of any kind.

## Verification plan

- Unit tests of the script's pure parts (config validation, port choice, naming, lifecycle step) with no systemd.
- Integration tests against a real `systemd-run --user` and a throwaway Postgres database, using a tiny stub app (an HTTP server that reads `PORT` and `DATABASE_URL`), cleaned up by the test.
- A live run on a foreman worktree for checks 1-4, and check 6 on the next real dispatch.

## Ask-first boundaries

- Editing the user's dotfiles to add `~/.config/devserve/apps.toml`, and changing any app's dev config beyond the `PORT`/`DATABASE_URL` contract.
- Dropping any database not created by devserve.
- Installing anything into `~/.local/bin` outside the skill's own link.

## Left to the builder

- Exact CLI flags and output format (`--json` included).
- How the dump/restore runs (pg_dump/pg_restore options), and timeouts.
- Slicing into tickets.
