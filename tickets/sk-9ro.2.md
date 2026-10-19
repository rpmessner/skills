---
id: sk-9ro.2
title: "foreman as the first devserve app"
type: feature
status: closed
priority: 2
parent: sk-9ro
blocked_by: ["sk-9ro.1"]
related: []
discovered_from: null
labels: ["initiative"]
created: 2026-10-18
closed: 2026-10-19
close_reason: "Guard merged (foreman 70c7f83); registration added with user approval (local ~/.config/devserve, MIX_HOME/LANG fixed); live: a preview of the real foreman data started, served, stopped and cleaned up from the sheet (fm-c2w.14); approved push refused in preview (scratch copy)."
---

## What to build
Make foreman previewable through devserve and safe to preview with copied data. The foreman code changes land in the foreman repo (ticketed here because they are this epic's contract). Spec Decisions 4, 6, 8a; acceptance checks 1 and 7. foreman's preview button (fm-c2w.14) builds on this.

## Interfaces
Consumes: the devserve preview contract (ticket 1).


## Acceptance
- [ ] foreman (repo ~/dev/utils/foreman): dev config honours PORT and DATABASE_URL
- [ ] With PREVIEW=1 foreman refuses every external write: forge writes, pushes, merges, tmux launches; reads still work; tests for each
- [ ] foreman's apps.toml entry (data = copy from the installed foreman database, migrate command, main_units foreman-web/foreman-worker) added to the user's dotfiles with their approval
- [ ] Live: devserve up in a foreman worktree shows the user's real tickets; a code edit reloads the page (check 1)
- [ ] Live: a copied approved push request does not push in the preview and no GitHub write happens (check 7)
- [ ] Waits for foreman push requests (fm-zgd.3) to merge so the guard covers them

## Notes
2026-10-18: guard and dev config merged in foreman 70c7f83 (scratch-copy check passed: refused in preview, zero external calls). Open: user-approved apps.toml registration in dotfiles, then live checks 1 and 7 on the installed database copy.
