# SkillOpt on house skills — research for sk-i4k

## Verdict

**Proposal: spec a manual, one-step `code-review` experiment, not nightly evolution.** SkillOpt supplies the text optimizer, split loader, reflection, and validation loop. We must supply the benchmark and a genuinely confined, hooks-on CLI runner. Neither a scratch cwd nor the upstream defaults satisfies the house safety contract by itself.

A small experiment can test whether the loop produces a useful reviewed edit; it cannot establish broad improvement across the skill set. No benchmark, baseline, trained skill, or rollout was produced in this research. The initiative's eventual spike acceptance criteria remain open.

The largest corrections to the initiative's premise:

- **Pi is supported in current SkillOpt-Sleep, but not as a built-in main-training exec backend.** Sleep's pi implementation is tool-free text replay and disables extensions. It is not a faithful pi coding-session harness with house hooks.
- **PyPI 0.2.0 is behind the inspected source.** Its wheel does not contain `PiCliBackend`; current documentation explicitly calls out post-release additions.
- **Strict gating is configurable, not universal.** Main training can disable the gate; default epoch-end slow updates are not selection-gated. Disable slow/meta updates for the small experiment, or explicitly gate slow updates later.
- **The edit budget is not a token/spend budget.** A small number of edits can still consume many rollouts and long optimizer completions.

## Scope and source pin

Inspected read-only clone: `/tmp/skillopt-src`, commit **`1a44050fc53aa4938a7a3927b6cca550491bfe51`**, commit timestamp `2026-10-18T17:03:51+00:00`. All upstream file references below resolve under this immutable [source tree][pin], not moving `main`.

Release comparison: `v0.2.0` resolves to **`51d0a4d96e88558c84dee637f98e24e3fb2d1547`**. [PyPI metadata][pypi] reports 0.2.0, Python >=3.10, MIT, Alpha classification, wheel upload `2026-07-02T14:12:04`. Downloaded the wheel without installing/importing it and verified SHA-256:

`818db802507c6f82553fd24c75aa70c953ab0a712647f60e68e4595052c4b150`

Paper: [Yang et al., *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*, arXiv:2605.23904v2][paper]. Read the method, harness discussion, optimizer-strength comparison, and cost discussion. Paper results are evidence about its benchmarks, **not** a prediction for our workflows. Table 6 reports 20.8M–213.8M training tokens for the six GPT-5.5/GPT-5.5 runs; tiny final Markdown does not imply cheap training. Section 3's gated slow-update description is stronger than current code defaults, so use source/config for implementation decisions.

[LICENSE][license], lines 1–21: MIT, Microsoft copyright, notice required in copies/substantial portions, no warranty. Benchmark data and any reused third-party skill text require their own provenance/rights checks; MIT on the engine does not license our historical session contents.

House inputs: `AGENTS.md`, `catalog.toml`, the four candidate `SKILL.md` files, `tight-spec/references/builder-check.md`, and `scripts/check.py`. House HEAD at inspection: `0984fb1060b95410dae600c27f1e9b8203a1b3d0`. These are local sources, not claims from SkillOpt.

## 1. What an environment package contains

The official [new-benchmark guide][env-guide] provides a complete `docfaithful` example; the source skeleton is `skillopt/envs/_template/{env_template,loader_template}.py`. This is a Python environment integration, **not** a discovered plugin/entry-point package just because it contains YAML.

| Piece | Required contract | Source |
|---|---|---|
| Data loader | `SplitDataLoader`; load item dicts with unique filesystem-safe `id`s. Implement `load_split_items(path)` for custom storage; optionally `load_raw_items` for ratio splitting. Pre-split directories are `train/`, `val/`, `test/`. | [datasets/base.py][loader], 260–409 |
| Adapter | Implement `build_train_env`, `build_eval_env`, `rollout`, `get_task_types`. Expose loader via `get_dataloader`, initialize it in `setup`, and implement `build_env_from_batch` for planned dataset batches. | [envs/base.py][adapter], 171–232, 234–277 |
| Rollout and scorer | Execute target with candidate skill, score externally, return result dicts. No separate `EnvAdapter.evaluate()` method. | [guide][env-guide], steps 3–4 |
| Reflection artifacts | Nonempty `predictions/<id>/conversation.json`, plus result fields such as task description/reference/prediction. Missing trajectories yield no learning patches even if scoring works. | [adapter][adapter], 234–271; [guide][env-guide], step 3 |
| Configuration | YAML `_base_` is a string path. Configure role backends, training, gradient, optimizer, evaluation, env and seed skill. | [base config][base-config]; [guide][env-guide], step 6 |
| Registration | Add lazy adapter registration to **both** `scripts/train.py` and `scripts/eval_only.py`; there is no automatic external-env registry in `envs/__init__.py`. | [guide][env-guide], step 5 |

Use one env per materially different scoring/interaction contract, not necessarily a new engine fork per skill. Review can use seeded git diffs; ticketing needs a tracker surrogate and approval sequence; specing needs scripted user answers; dispatch needs lifecycle execution. Those are different environments even if they share fixture-loading helpers.

### Minimal house integration sketch (proposal, not executable as supplied)

This shows all four seams. `run_confined_review` and `score_review` are **house functions still to build and test**, not SkillOpt APIs. They deliberately make sandboxing and scoring explicit instead of hiding unsafe upstream defaults. Registration and imports of those two functions are omitted. No part of this example was run.

```python
# skillopt/envs/house_review/adapter.py
import json
from pathlib import Path
from skillopt.datasets.base import SplitDataLoader
from skillopt.envs.base import EnvAdapter

class ReviewLoader(SplitDataLoader):
    def load_split_items(self, split_path):
        return json.loads((Path(split_path) / "items.json").read_text())

class ReviewAdapter(EnvAdapter):
    def __init__(self, split_dir="", seed=42, workers=1,
                 analyst_workers=1, failure_only=True,
                 minibatch_size=4, edit_budget=1, **kwargs):
        self.dataloader = ReviewLoader(
            split_dir=split_dir, split_mode="split_dir", seed=seed)
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget

    def setup(self, cfg):
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size, seed, **kwargs):
        batch = self.dataloader.build_train_batch(
            batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch)

    def build_eval_env(self, env_num, split, seed, **kwargs):
        batch = self.dataloader.build_eval_batch(
            env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch)

    def get_task_types(self):
        return ["review"]

    def rollout(self, env_manager, skill_content, out_dir, **kwargs):
        rows = []
        for item in env_manager:
            # Runner stages only public fixture files in a fresh scratch
            # worktree; gold labels remain outside the child filesystem.
            # Abort on auth/runner failure rather than learning from it.
            answer, messages, audit = run_confined_review(
                item["fixture"], skill_content)
            hard, soft, feedback = score_review(answer, item["gold"], audit)
            p = Path(out_dir) / "predictions" / item["id"]
            p.mkdir(parents=True, exist_ok=True)
            (p / "conversation.json").write_text(json.dumps(messages))
            rows.append(dict(id=item["id"], hard=hard, soft=soft,
                predicted_answer=answer, task_description=item["prompt"],
                task_type="review", reference_text=feedback))
        Path(out_dir, "rollouts.json").write_text(json.dumps(rows))
        return rows
```

Validation before execution must enforce safe unique IDs, fixture path confinement, immutable gold, no answer-bearing files in target mounts, and a separate scratch worktree per rollout. This sketch does not implement those checks.

Illustrative config after registration (paths are examples in the proposed experiment workspace):

```yaml
_base_: ../_base_/default.yaml
model:
  optimizer_backend: openai_chat
  optimizer: gpt-5.5
  target_backend: claude_code_exec
  target: sonnet  # resolve/pin an exact installed CLI model before execution
  claude_code_exec_use_sdk: cli
train:
  num_epochs: 1
  batch_size: 4
  accumulation: 1
  seed: 42
gradient:
  minibatch_size: 4
  analyst_workers: 1
  failure_only: true
optimizer:
  learning_rate: 1
  min_learning_rate: 1
  lr_scheduler: constant
  skill_update_mode: patch
  use_slow_update: false
  use_meta_skill: false
evaluation:
  use_gate: true
  gate_metric: soft
  sel_env_num: 4
  test_env_num: 4
  eval_test: true
env:
  name: house_review
  skill_init: fixtures/seed/SKILL.md
  split_mode: split_dir
  split_dir: fixtures/review-split
  workers: 1
  exec_timeout: 120
  out_root: runs/review-pilot
```

**Not a safety configuration:** the custom runner must actually use these model/timeout settings and impose its own isolation, hook and cost policy. Setting `target_backend` does not automatically launch or constrain the custom rollout. Registering with the stock scripts requires matching their constructor/config wiring. Freeze all companion reference files and front matter; optimize only the agreed skill body. The four-task train split means one step; `batch_size: 4` alone would not limit a larger split to one step.

## 2. What a CLI rollout and score look like

A review fixture should contain a tiny git repository with a fixed base/head, local standards, a spec, and seeded mistakes (plus clean negative-control cases). The target gets the fixture, user request and candidate skill, not the expected findings. Stage the skill's `references/` too: optimizing an isolated SKILL.md while silently omitting its referenced briefs changes the task.

The stock SearchQA exec example [rollout.py][qa-rollout], 90–151, renders a skill, prepares a workspace, calls `run_target_exec`, and receives `(final_message, raw_trace)`. [codex_harness.py][harness], 48–73, 95–172, creates `.agents/skills/skillopt-target/SKILL.md` and `task.md`. **Do not call `prepare_workspace` on a pre-created worktree root: it recursively deletes an existing `work_dir`.** It also supports symlinked input directories; do not use that to expose live repos or gold.

For our runner: execute the real CLI in the disposable fixture worktree, preserve exit status, stdout/stderr, model/usage, tool events, hook evidence and before/after filesystem audit. Normalize its trace into reflection messages. Nonzero exit/auth failure is an infrastructure failure, not a skill-quality zero. The stock Claude CLI helper can return nonempty stdout even after a nonzero exit ([harness][harness], 929–954); harden rather than inherit that behavior.

Example scored result (illustrative):

```json
{
  "id": "review-003",
  "hard": 0,
  "soft": 0.6666666667,
  "task_type": "review",
  "predicted_answer": "Standards: ...\nSpec: ...",
  "task_description": "Review the supplied base-to-head diff against the spec.",
  "reference_text": "Found one of two gold findings; no false positives. Missed required input validation."
}
```

Proposal: match findings against blinded `(axis, rule, file, line-range)` labels, with deduplication and a fixed normalization policy; one of two expected findings, no false positives gives precision 1, recall 0.5, F1 2/3. `hard=1` only for all expected findings, no false positives, required axis separation, and no forbidden action. Clean cases receive 1 only when they correctly report no findings. `soft` can be F1 subject to deterministic format/action penalties. Label fixtures with evidence, not substring-only keyword rewards. Human-adjudicate ambiguous matches before trusting the scorer; do not introduce an LLM judge in the first pilot.

Guardrail violations must **reject the entire candidate outside the mean-score gate**: a higher average F1 must not compensate for an unauthorized write/push or skipped approval. Missing-base/no-spec/clean-diff cases test correct stopping behavior rather than merely finding more bugs.

Main gate compares the mean configured metric against the cached current score using strict `>`; ties reject ([gate.py][gate], 87–134, 137–235). With four validation cases, hard accuracy is coarse; soft F1 is more sensitive but does not eliminate noise/overfitting. Reusing a small selection set for many candidates turns it into tuning data. Reserve disjoint test fixtures, split by originating project/bug family, and do not feed test feedback into further edits.

## 3. Harness and optimizer choices

| Path | What the inspected source supports | House consequence |
|---|---|---|
| Main trainer + Claude Code | `claude_code_exec`, CLI or SDK; environment-specific exec rollout required. [Harness][harness], 885–1014. | Closest supported starting point, but override default permissions, explicitly use CLI, and prove hooks/isolation. |
| Main trainer + Codex | Built-in exec harness; workspace-write sandbox by default; network/web-search off by default. [backend_config.py][backends], 54–70. | Confirms extensibility, but not one of the chosen house pilot harnesses. |
| Main trainer + pi | No pi in target whitelist ([backends][backends], 160–174). | Build a custom env runner, or implement/register a first-class target exec backend. Do not pretend `target_backend: pi` works. |
| Sleep + pi (current pin) | `PiCliBackend` invokes installed authenticated `pi -p`, optional `--model`, clean temporary cwd. [sleep/backend.py][sleep-backend], 653–790. | Text replay exists, but `--no-tools`, `--no-skills`, `--no-context-files`, **`--no-extensions`** make it unsuitable as-is for hooks-on coding workflow evaluation. |
| Sleep + pi (PyPI 0.2.0) | Absent from verified wheel; [Sleep version note][sleep-doc], 159–164. | Requires newer pinned source, not `pip install skillopt==0.2.0`. |

Pi therefore **can be a harness**, but faithful tool-enabled main-loop integration is work, not a configuration toggle. The current Sleep integration is not evidence that GPT-6 Astra works in this deployment. Its exact provider/model identifier, availability, context limits, pricing and usage reporting remain unverified; no provider was called. No pi extension or implementation is proposed as already tested here.

Optimizer and target are independent roles. Default config names GPT-5.5 for both, with `openai_chat` role backends ([base config][base-config], 4–12). Chat backend contract is synchronous `(text, usage)` with prompt/completion/total tokens and role-specific settings ([new-backend guide][backend-guide], “Step 1”). A compatible provider can use `openai_compatible` in the inspected pin, but that too landed after v0.2.0. Use a supported optimizer/model the account actually has; the paper's stronger-vs-target-matched comparison is a reason to test optimizer quality, not a mandate to buy its most expensive option.

## 4. Cost and smallest experiment — proposal

**First experiment: `code-review`, 12 small curated fixtures: 4 train / 4 selection / 4 test.** Include clean controls and a mix of standards/spec errors. One epoch, one batch, failure-only reflection, one bounded patch, no slow/meta update, one worker, no model judge. Use sanitized past mistakes only after labeling them; synthetic small fixtures are cheaper and easier to audit initially. Keep reference files, prompt wrapper, tool set and target model fixed between baseline and candidate.

Run counts for that configuration, assuming a candidate is produced and evaluated:

- Baseline selection: 4 target episodes.
- Training batch: 4.
- Candidate selection: 4.
- Final test: initial skill 4 + best skill 4.
- **Total: about 20 target episodes**, excluding retries/preflight. Final==best reuses results. Source: [trainer.py][trainer], 2200–2403; selection initialization/candidate loop in the same file. No-patch/cache paths may be cheaper; repeated seeds, retries and extra candidates cost more.

Optimizer calls: failure minibatch reflection; merging if needed; ranking if edits exceed budget. One four-item failure minibatch can yield one reflection call; allow roughly **1–3 optimizer calls** for planning, not a hard maximum. [reflect.py][reflect], 269–377, requests up to 16,384 completion tokens in patch mode; [aggregate.py][aggregate], 28–77 and 156–260, performs hierarchical/final merges; [clip.py][clip], 25–80, bypasses ranking if within budget, otherwise requests up to 16,384 completion tokens and retries. Rewrite modes can request 64,000 tokens. A one-edit learning rate does not bound input size, generated text size or retries.

### Dollar estimate, explicitly conditional (not a price quote)

No exact current Claude/GPT-6 Astra tariff or account billing was verified. The following is an **assumption-based planning estimate**, not measured cost or a claim of current provider rates:

| Component | Assumed tokens | Assumed uncached $/million input, output | Cost |
|---|---:|---:|---:|
| 20 short Claude CLI episodes | 8k input + 1.5k output each = 160k/30k | $3 / $15 | $0.93 |
| Up to 3 optimizer calls | 20k input + 3k output each = 60k/9k | $5 / $30 | $0.57 |
| Nominal total | 220k input + 39k output | assumptions above | **$1.50** |

**Expected planning envelope: $2–$5 for this deliberately small run; propose $10 maximum authorization with an externally enforced spend policy.** This estimate is conditional on short traces and rates near the assumptions. At 3 optimizer calls each consuming the full 16,384 output-token allowance, the optimizer alone is about $1.77 under those rates, before retries. Larger inherited CLI context, multi-turn tool loops, reasoning tokens, cached/uncached differences, fallback calls or a different Astra tariff can invalidate the envelope. Subscription billing may consume quota rather than incremental dollars; quota is not free compute. Reprice from the chosen account's actual tariff before approving a run.

General formula: `cost = sum_role(input_tokens * input_rate + output_tokens * output_rate) / 1e6`, adding provider-specific reasoning/tool charges and distinguishing cached input. Target episode count grows roughly with epochs × train items plus validation items per candidate; additional epochs can also add paired slow-update rollouts and meta calls. Bigger datasets, long tool traces, optimizer minibatches, hierarchical merges, retries, full rewrites and final-test repeats are the main drivers. Concurrent workers change peak spend, not the intrinsic per-episode work.

A first **paid baseline** should verify trace/usage accounting before releasing the rest of the budget. A stop/go result is useful even if no patch improves selection. A four-case test is only a smoke signal: require a larger untouched holdout and repeated-seed comparison before broadly adopting an edit. Do not use a second look at the same test as new evidence of generalization.

## 5. Ranked skill shortlist

This ranking is a proposal based on the local skill contracts, not experimental results.

| Rank | Skill / catalog mode | Concrete outcome and score | Why this position / main trap |
|---|---|---|---|
| 1 | `code-review` / merge | Seeded diffs; per-axis finding precision/recall/F1, clean-case false positives, correct fixed-point handling, no edits, no unsupported Critical findings. | Read-only task, cheap fixtures, objectively seeded defects. Free-text matching and undocumented valid findings need adjudication. Include Spec/Standards separation and selected Risk cases, not only bug recall. |
| 2 | `to-tickets` / adapt | Approved spec with hidden acceptance-check map; score coverage, genuine dependency edges/DAG, interface agreement, independently verifiable vertical slices; zero premature publication/implementation. | Most structure is machine-checkable. Verticality/appropriate granularity needs human gold. Use a fake `bd` or disposable tracker, plus a scripted approval turn; never production beads. Counting tickets alone rewards fragmentation. |
| 3 | `tight-spec` / merge | Scripted user decisions and codebase facts; score required decision coverage, preservation of non-goals, falsifiable acceptance checks, unresolved **material** builder questions, no unauthorized build. | Real multi-turn behavior, difficult gold and simulator bias. Raw builder-question count can be gamed by vague specs, invented decisions or an agreeable reviewer; pair it with a fixed ambiguity inventory. Mock foreman effects. |
| 4 | `dispatch` / own | Fake tmux/pi/foreman lifecycle scenarios first: correct brief, window/marker identity, permission handling, wait/usage-limit recovery, verified report and no premature close. | Real end-to-end success depends on child/model/tool work and is expensive/confounded. “Sessions finish” rewards fake success or skipping gates; score verified deliverables and safety transitions, not marker emission. Live child launches would be separately authorized future work. |

Do not optimize all four with one generic “quality” judge. `tight-spec` and `to-tickets` explicitly stop for user decisions; a reward for autonomy or minimum questions would train against their purpose. `dispatch` is a lifecycle protocol with external effects, not a standalone prose-generation task.

## 6. Output and house provenance

Main training writes selection-best text to `<out_root>/best_skill.md`, alongside rollout/evaluation/checkpoint artifacts. It is not a diff and not necessarily an improvement: the best may remain the seed. Current vs best can diverge when ungated paths are enabled; final test separately evaluates seed/best/final with reuse when equal ([trainer][trainer], 2200–2403; [training-loop guide][loop], “Why current and best are separate”). No extra optimizer call is needed to use the exported document, although a longer skill still costs target context tokens.

Proposed re-entry process:

1. Keep seed, dataset hashes/split membership, SkillOpt pin, house base SHA, model identifiers, CLI versions, resolved config, hook/sandbox evidence, full usage, per-item scores and final artifact outside installed skill directories. Redact sensitive logs before tracking.
2. Export an ordinary **reviewed SKILL.md body diff**, never execute `adopt`, overwrite installed links or auto-copy `best_skill.md` into the repo. Preserve front matter, name/description, provenance comment and companion-reference paths. Inspect every edit for benchmark-specific answers, weakened approval/safety requirements, stale CLI advice and verbosity regressions.
3. `own` (`dispatch`): remain `mode="own"`; add a house-edit note with run/report identity. Using an optimizer as a tool does not make its implementation an upstream source of the skill text.
4. `adapt` (`to-tickets`) and `merge` (`code-review`, `tight-spec`): **keep existing `from` refs and upstream pins**; add a dated house-edit note and evidence link. Do not label trained text as an upstream revision or change upstream pins to the SkillOpt commit. Future upstream sync must reconcile that local edit normally. If substantial SkillOpt prompt/source text is actually copied, separately preserve its MIT notice and provenance.
5. If later optimizing an `adopt` skill, it is no longer byte-identical: convert to `adapt`, retain original upstream `from` and pin, update the provenance comment. None of the four current candidates is `adopt`.
6. Run `python scripts/check.py`, review Standards and Spec axes, validate referenced files/front matter, and run the benchmark holdout. Only a human-authorized normal commit may land it.

`check.py` is necessary but not sufficient: lines 91–163 validate manifest refs, directory coverage, names, front matter and description budget. It does **not** establish behavioral improvement, enforce semantic safety, or validate the truth/completeness of provenance comments. The `to-tickets` comment currently lists a pstack source not in its catalog `from`; preserve existing state and resolve that discrepancy in review rather than silently changing lineage during optimization.

## 7. Guardrails: offered versus still required

| Concern | Upstream behavior at this pin | Required house policy |
|---|---|---|
| Selection | Strict `>` under enabled gate; hard/soft/mixed; gate can be disabled. Slow update defaults on and selection-gating defaults off. [gate][gate]; [base config][base-config], 99–127. | Gate on; slow/meta off initially. Reject any safety violation independently of mean score. No semantic-density bonus for adding MUST/NEVER words. |
| Sandbox | Codex sandbox/network controls; Claude uses `bypassPermissions` by default in SDK and CLI. Allowed tools default `Read,Bash`. [harness][harness], 834–846, 895–910; [backends][backends], 54–70. | Disposable scratch worktrees **plus OS-level filesystem/network confinement**, explicit permission policy and hooks. A Bash allowlist name is not command confinement. No live repo mounts, push credentials or production tracker endpoints. |
| Workspaces | `prepare_workspace` deletes an existing directory, copies files, optionally symlinks dirs. [harness][harness], 95–172. | Never point it at live repos/worktree roots; no mutable external symlinks; house runner owns scratch allocation and cleanup. A worktree's Git metadata can point to the source repository, so filesystem isolation must cover that too. |
| Hooks | Main exec helper does not prove our hooks loaded. Sleep pi explicitly disables extensions; Sleep Claude may use `--bare` with API-key auth. [sleep backend][sleep-backend], 705–740, 846–876. | Reject those Sleep defaults for the chosen contract. Prove a planted prohibited action is blocked and a clean read succeeds in the exact runner; keep house guard configuration active. |
| Budget | Main config has epochs/batches/edit limits and call timeout; token summaries are accounting, not a verified global dollar cap. Sleep's current nightly token control checks before model-work stages and **does not interrupt in-flight work**. [sleep/cycle.py][sleep-cycle], 704–709; [budget.py][sleep-budget], 15–77. | External spend/episode/time ceilings; single worker initially; account for retries/in-flight overshoot and descendants. Do not equate `max_tokens` parameters with CLI-enforced limits: pi `_call` accepts that argument but does not pass an output-token limit. |
| Sensitive data | Reflection consumes target traces/reference feedback; optimizer is another model boundary. | Sanitize past sessions; keep gold from target; avoid unrelated source trees, secrets and personal data in prompts/logs. Approve provider exposure before paid work. |
| Auto-adoption | Sleep offers staging and explicit adoption commands. [Sleep docs][sleep-doc], 146–164. | Never use automatic adoption in house skill dirs; reviewed diffs only. |

**Nightly Sleep recommendation: defer.** Its harvest → mine → replay → consolidate → staged adoption flow is useful later, but the pilot needs fixed labels, stable splits and faithful hooks-on execution first. “Offline” here means outside the live user session, **not** without model/network calls. Nightly use is a user decision after evidence of benefit; it is not necessary to answer this initiative's first spike.

## 8. Open risks, unknowns and proposed follow-ups

No beads created; these are proposed follow-ups for the coordinator:

1. **Spec the scorer and dataset** for code-review, including clean cases, blind labels, human adjudication, grouped splits and invariant gates. Decide whether only giving-review is in scope (recommended), leaving receiving-review for later.
2. **Spec a confined hooks-on Claude CLI runner**, or explicitly choose pi and fund its main-loop integration. Verify no main checkout/real tracker writes; test process cleanup, refusal behavior, auth errors, usage capture and environment leakage with no-model fakes first.
3. **Pin execution dependencies and account choices.** Research used source inspection, not installed-package compatibility testing. Resolve exact Claude model and optimizer availability/rates; GPT-6 Astra availability/rates are unknown. Current main fixes cannot be assumed present in 0.2.0.
4. **Approve a finite paid experiment**, after repricing: proposed 12 fixtures, one candidate step, $10 authorized ceiling, with the $2–$5 conditional envelope above. The scorer/harness development cost is not included.
5. **Review the artifact even if score improves.** Small-set noise, benchmark answer leakage, omitted reference files, instruction weakening, free-text scoring errors, model-version drift and repeated selection-set tuning can all generate false wins.
6. **Require broader validation before adoption**, then separately decide whether any nightly Sleep experiment is wanted. Do not infer cross-harness or cross-skill transfer from the paper's unrelated tasks.

## Verification record

- **Changed:** only this research report intentionally. No skill, catalog, engine, configuration or tracker edits; no commits/pushes, subagents, package installs, model calls or rollouts.
- **Read-only evidence:** inspected pinned clone, env/loader/scorer interfaces, exec command construction, gate/trainer output logic, Sleep pi and budget code; fetched PyPI metadata and wheel bytes and verified wheel hash/no pi backend; fetched paper v2 HTML. Source checkout remained clean.
- **House gate:** `python scripts/check.py` returned exit 0 again after report creation: `44 skills, always-on ~1222/2500 tokens, 0 errors`. This validates the existing skill set, not the hypothetical integration.
- **Report checks:** a local Python check passed for Markdown reference-label resolution, all pinned GitHub source paths and line-anchor bounds against the clone, and syntax parsing of the illustrative Python block (no imports or execution). Reviewed the report against every requested question; source search confirmed the five rollout groups behind the 20-episode estimate. `git diff --check -- research/skillopt.md` returned 0, but the report is untracked, so that command alone is not whitespace evidence.
- **Not verified:** actual harness execution, sandbox/hook enforcement, target/provider authentication or pricing, runtime token counts, benchmark quality, trained outputs or improvement. All require the separately approved spike.
- Existing `.beads/interactions.jsonl` modification and `drafts/briefs/sk-skillopt.md` were present at initial status inspection and were not edited here.

## Primary-source links

[pin]: https://github.com/microsoft/SkillOpt/tree/1a44050fc53aa4938a7a3927b6cca550491bfe51
[pypi]: https://pypi.org/pypi/skillopt/0.2.0/json
[paper]: https://arxiv.org/html/2605.23904v2
[license]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/LICENSE
[env-guide]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/docs/guide/new-benchmark.md
[loader]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/datasets/base.py#L260-L409
[adapter]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/envs/base.py#L171-L277
[base-config]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/configs/_base_/default.yaml
[qa-rollout]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/envs/searchqa/rollout.py#L90-L151
[harness]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/model/codex_harness.py
[gate]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/evaluation/gate.py
[backends]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/model/backend_config.py
[sleep-backend]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt_sleep/backend.py
[sleep-doc]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/docs/sleep/README.md
[backend-guide]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/docs/guide/new-backend.md
[reflect]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/gradient/reflect.py#L269-L377
[aggregate]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/gradient/aggregate.py
[clip]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/optimizer/clip.py#L25-L80
[trainer]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt/engine/trainer.py#L2200-L2403
[loop]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/docs/guide/training-loop.md
[sleep-cycle]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt_sleep/cycle.py#L704-L709
[sleep-budget]: https://github.com/microsoft/SkillOpt/blob/1a44050fc53aa4938a7a3927b6cca550491bfe51/skillopt_sleep/budget.py
