---
id: sk-81s.8
title: "Optional: weekly scheduled report-only skills-sync agent"
type: task
status: open
priority: 3
parent: sk-81s
blocked_by: ["sk-81s.6","sk-81s.7"]
related: []
discovered_from: null
labels: []
created: 2026-10-15
closed: null
close_reason: null
---

## Notes
Proposal (2026-10-16, gaps pass): who runs the maintenance loops (skills-sync, correct, retro, maintain-verification-skill). Nothing is scheduled yet.

(a) Weekly coordinator ritual, triggered by the user with one prompt in the coordinator session:

  Weekly upkeep, report-only: change nothing until I approve each item. 1) skills-sync: fetch and write this week's report; list candidates, file no beads, bump no pins. 2) Lessons: list `lesson` beads from the past week in every repo with .beads (dispatch's fd loop, `bd list -l lesson`); flag any mistake that repeated or sits at rung 3-4 and propose a higher rung. 3) correct: name the repo with the most corrections this week and the mistake classes you would fix there; do not fix. 4) maintain-verification-skill: for each repo with a verify skill, say whether code changed without its feature map (form-engine: `verify closeout --base <last week's sha>`) and whether a pass is due. 5) retro: only on a session I name. End with one table: loop, finding, proposed change, needs my decision (y/n).

(b) Automated weekly report-only run: a user crontab entry (WSL cron must be running; a laptop asleep or WSL shut down skips the week) that runs `python3 ~/dev/utils/skills/scripts/sync.py` (no --file-beads, no --bump) and writes reports/YYYY-MM-DD.md, optionally followed by a headless `claude -p` that reads the report and the week's lesson beads and writes a summary under drafts/. May: fetch sources, write reports/ and drafts/. May not: edit skills or catalog.toml, file or close beads, bump pins, commit, push, touch harness dirs. Claude Code cloud routines (/schedule) do not fit: they cannot see ~/dev, local skill-sources, or the local Dolt beads.

Recommendation: (a). Only skills-sync's fetch-and-diff is mechanical; correct, retro and maintain-verification-skill need judgment and the user's decisions, and their output is a decision list the user has to read anyway. (b) adds a cron dependency on WSL being up, and a headless run whose summary still waits for the user. Revisit (b) for sync.py alone if the ritual gets skipped for weeks.
2026-10-18 user: (a) a weekly ritual the user triggers with one prompt in a coordinator session; report-only; no scheduled cloud agent.
