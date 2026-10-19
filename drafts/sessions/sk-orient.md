# sk-dnl — orient

## Changed

- Added `skills/orient/SKILL.md`: fresh reads on every invocation, including resumed conversations; health, Needs you, sessions/reports, epic-grouped frontier, branch ahead counts, one recommendation. No action taken by the skill.
- Registered the own skill in `catalog.toml`; added its coordinator entry to `skills/flow/SKILL.md`.
- Claimed sk-dnl as requested. Left closure to the coordinator. No production script added; no script TDD seam.

## Evidence

[Acceptance transcripts](sk-orient-evidence/transcripts.md) contain live and unreachable-board assessments and link their command evidence.

Live: Needs you **0**, **2 pi builds**, all **5 windows** accounted for across default and foreman servers. Frontier: **219 raw rows, 208 non-epics, 2 already in flight**, across 7 repos. Branch ahead counts come from git, with missing/gone upstreams marked unknown.

Down: scratch configuration plus unreachable URL; curl failed, overlay warned with exit 0, local list returned **25 tickets**, local ready returned sk-81s.8, and cross-repo ready still returned the identical frontier IDs. No live service stopped or started.

Observed API gotchas are recorded in the skill: bare `ls` is local; inbox verbs are absent in the installed CLI, so use the rendered inbox; `in_review` is a stage, `review`/`request_changes` are events.

## Standards review

Reviewed first, sequentially in this session against c88228eae3bdf47192f23f3032e75106422e6d8c, using AGENTS.md, writing-for-agents and the review baseline. The committed three-dot diff is empty because commits were prohibited; reviewed the explicitly requested working-tree diff and new skill/evidence files instead.

No Critical or Important findings. Chose a positive read recipe with required output slots, not a new orchestration layer. No abstraction or runtime state introduced. Declined to judge cross-model prompt reliability: no fresh-context A/B repetitions were run under the no-subagent instruction. This is a direct execution/retrieval check, not a claim of measured behavior improvement. Verdict: Ready.

## Spec review

Ran after Standards, against sk-dnl. **Important, fixed:** the initial In flight recipe named `review`/`request_changes` as stages. Source inspection showed `in_review` and a changes event returning to building; corrected the recipe and reran both report-stage reads (empty).

All requested sections and both acceptance scenarios have evidence. Corrected the transcript's local ticket count from 28 to the measured 25. No remaining Critical/Important findings. Declined to judge fm-3c3.6's launcher integration: parallel work outside this ticket. Verdict: Ready.

## Final gate

[Full output](sk-orient-evidence/final-gate.txt), combined exit **0**:

- `python3 scripts/check.py`: 46 skills, ~1288/2500 always-on tokens, 0 errors.
- `foreman check`: tickets valid; `git diff --check`: clean.
- Dispatch unittest discovery: **34 passed**.
- devserve unit tests: **7 passed**.
- `node pi/house-guard/test.ts`: all ok.
- `node pi/foreman-wait/test.ts`: **10 passed**.

## Open / not verified

No implementation follow-up to file. No install, sync, commit or push performed in this worktree. Harness activation and launcher delivery await coordinator integration. The live inbox was empty, so multi-request ordering was not exercised with live pending requests. No live service-control or devserve integration tests run; those would violate this brief's service restriction. Git publication counts use cached refs, deliberately without fetching.
