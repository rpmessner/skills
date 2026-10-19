---
id: sk-tjc
title: "pi-wait detects provider usage limits (exit LIMITED)"
type: task
status: closed
priority: 1
parent: null
blocked_by: []
related: []
discovered_from: null
labels: []
created: 2026-10-18
closed: 2026-10-18
close_reason: "pi-wait exit 5 LIMITED with the line; 6 fake-tmux tests; real pane baseline checked; dispatch skill documents it."
---

## What to build
On 2026-10-18 both build sessions stopped on "Error: Codex error: The usage limit has been reached" and sat idle; pi-wait would only have timed out hours later. pi-wait should notice and return at once so the coordinator can tell the user. Board-side request and Continue button: beads-board fm-3c3.2.


## Acceptance
- [ ] pi-wait recognises provider-limit lines printed after it starts (Codex usage limit reached, Anthropic extra-usage refusal, HTTP 429 / rate limit) and exits 5 printing LIMITED and the matching line
- [ ] DONE still beats LIMITED; only lines printed after the wait started count (same baseline rule as markers)
- [ ] dispatch skill: on LIMITED, tell the user (and, once foreman session_waiting exists, post it with --reason usage_limit); re-wait after the session continues
- [ ] Tests with a fake tmux pane; check.py green
