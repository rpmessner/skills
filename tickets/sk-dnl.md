---
id: sk-dnl
title: "orient skill: coordinator start-of-session assessment"
type: feature
status: closed
priority: 2
parent: null
blocked_by: []
related: []
supersedes: []
discovered_from: null
labels: []
created: 2026-10-19
closed: 2026-10-19
close_reason: "orient skill merged (ed4c4b5e3da83a1568f7abd8303cf1b086a6c036); gate green; live and foreman-down transcripts in drafts/sessions/sk-orient-evidence"
---

A house skill the coordinator runs at the start of a session (foreman's `foreman coordinator` sends it as the orient prompt, fm-3c3.6; the user can also run `/orient`).

## What it does

Gives the user a short, current picture and a recommendation, from live sources only (never memory of earlier sessions):
- foreman health: the web, worker and tmux services are up and the board answers; say what's down and how to start it, do not start it.
- Needs you: pending requests, oldest first, with what each needs.
- In flight: build sessions and their windows (pi and launched coordinators), stalled or waiting ones flagged; uncommitted or unreviewed reports waiting on the coordinator.
- Frontier: ready tickets across repos (`ready-repos.py`), grouped by epic, with the coordinator's pick for what to do next.
- Unpushed commits per repo (the user pushes).

Output is brief: a few short sections, then one recommended next step. It reads; it changes nothing (no dispatch, no ticket edits, no requests) until the user answers.

## Acceptance

- Skill follows the repo's AGENTS.md (catalog entry, house header, writing-for-agents style).
- Run against the live board, it reports the real Needs-you count, in-flight windows and frontier, matching `foreman` and tmux at that moment.
- With foreman-web stopped (on a scratch config, not the live unit), it says so and still reports what it can from ticket files.
