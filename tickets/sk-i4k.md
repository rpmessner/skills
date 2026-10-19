---
id: sk-i4k
title: "Explore training house skills with SkillOpt"
type: epic
status: open
priority: 2
parent: null
blocked_by: []
related: []
discovered_from: null
labels: ["initiative"]
created: 2026-10-18
closed: null
close_reason: null
---

## Idea (not yet specced)
Try microsoft/SkillOpt (MIT, v0.2.0, PyPI; https://github.com/microsoft/skillopt) on the house skill set. SkillOpt treats a skill document as the trainable state of a frozen agent: an optimizer model turns scored rollouts into bounded add/delete/replace edits, and keeps an edit only if a held-out validation score strictly improves. Output is a best_skill.md; no weight changes and no extra calls at inference. It runs Claude Code CLI and Codex CLI as rollout harnesses (exec backends), with a WebUI monitor and a preview nightly self-evolution mode.

## Why it might fit
Our skills are plain SKILL.md files with known failure modes we already correct by hand (lessons skill, retro findings, review rules). A scored loop could tune the ones with measurable outcomes instead of editing on anecdote.

## Questions to settle before specing (this is an initiative, not tickets yet)
- Which skills have a scoreable outcome? Candidates: code-review (findings caught on seeded diffs), to-tickets (coverage of a spec's checks), tight-spec (builder-check question count), dispatch (sessions that finish vs hand off early).
- What is a benchmark here: a skillopt env package per skill (adapter, data loader, scored rollout, YAML), built from our own past sessions, specs and diffs.
- Cost and harness: Claude Code CLI vs pi with GPT-6 Astra as the rollout agent; optimizer model choice; token budget per run.
- How optimized output re-enters the repo: as a reviewed diff to SKILL.md through the normal gates (check.py, catalog provenance, a house edit note), never auto-applied; how adapted/merged skills keep upstream sync working.
- Guardrails: rollouts in scratch worktrees only, no pushes, no real repos touched; the house hooks stay on.
- Is nightly self-evolution (SkillOpt-Sleep) wanted later, or only manual runs?

## Done when (for the initiative's first step)
A spike verdict on one skill: benchmark built, a baseline score, an optimized skill with its score, the diff reviewed, and a go/no-go for the rest.


## Notes
2026-10-18 research: research/skillopt.md (SkillOpt source pinned). Verdict: spec a manual one-step code-review experiment (12 seeded fixtures 4/4/4, one candidate, gate on, slow/meta off, ~20 Claude CLI episodes, est. $2-5 conditional, $10 ceiling), not nightly Sleep. pi is not a main-loop exec backend (custom runner needed); PyPI 0.2.0 lags the source. Needs: a scorer/dataset spec, a confined hooks-on runner (Claude defaults to bypassPermissions), pinned deps, and a user-approved paid run. Output re-enters only as a reviewed SKILL.md diff with a house-edit note.
