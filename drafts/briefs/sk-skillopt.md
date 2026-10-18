You are a research session in the house skills repo (~/dev/utils/skills, main checkout). A coordinator session dispatched you and will read your output. Work autonomously; ask only when a decision is genuinely the user's.

## Goal
Answer the open questions in initiative sk-i4k (microsoft/SkillOpt on the house skill set) from primary sources, so the user can decide whether and how to spec it. This is research only: no training runs, no rollouts, nothing that calls a model.

## Read first
- AGENTS.md; `bd show sk-i4k` (the initiative and its questions); catalog.toml; the `research` skill (run it: findings as a Markdown file with sources).
- Candidate skills named in sk-i4k: skills/code-review, skills/to-tickets, skills/tight-spec, skills/dispatch.

## Tickets
sk-i4k (claimed by the coordinator). Do not close it or create beads; list proposed follow-ups in the report.

## Skills
- `research`: primary sources only (the SkillOpt repo at a pinned commit: README, docs, source of the env/adapter interface, examples, license; the PyPI release; its paper if any). Clone read-only under /tmp/skillopt-src; record the commit.
- `verify-before-claiming` before writing the report.

## Decisions already made
- Rollout harnesses would be Claude Code CLI or pi (GPT-6 Astra); outputs re-enter only as reviewed SKILL.md diffs through check.py and catalog provenance, never auto-applied; rollouts only in scratch worktrees, no pushes, hooks stay on.

## Rules
- No commits, no pushes, no bd writes. Do not pip-install into the system Python; if you must import the package to read its API, use a venv under /tmp and do not run anything that calls a model or network API beyond fetching the source. Spawn no subagents. Use /usr/bin/rm, not rm.

## Done when
- research/skillopt.md answers each sk-i4k question with sources (file paths at the pinned commit, line ranges where it matters): how an env package is built (adapter, data loader, scorer, config) with a minimal example; what a rollout and a score look like for a CLI harness; whether pi can be a harness or only Claude Code / Codex; optimizer model and token cost drivers per run, with an estimate for one small run on one skill; how output is produced (best_skill.md) and how it would fit our provenance (own vs adapted skills); guardrails it offers (sandbox, budgets).
- A ranked shortlist of house skills with a concrete scoring idea for each, and the cheapest first experiment (one skill, dataset size, expected cost), marked as a proposal.
- Open risks and unknowns listed plainly.

## Report back
The findings file is the report. Then print SK-SKILLOPT DONE alone on the last line.
