<!-- house: merge; from: mattpocock:skills/productivity/writing-for-agents/SKILL-MECHANICS.md@49dd158, superpowers:skills/writing-skills/SKILL.md@bb92a77 (Frontmatter, SDO, File organization sections). -->

# Skill mechanics

The skill-specific branch of [`writing-for-agents`](../SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in [`levers.md`](levers.md).

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in [`levers.md`](levers.md) apply in full).
- A **user-invoked** skill strips the description from the agent's reach: only the human typing its name can invoke it, and no other skill can. Zero context load, but it spends cognitive load: you are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing: a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference that two user-invoked skills both need can live in neither: with no descriptions, neither can fire the other. Push it to a plain file outside the skill system: external reference any skill can point at.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in [`levers.md`](levers.md)): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It can only hint, never fire them: user-invoked skills have no description, so nothing but the human can reach them.

## Frontmatter and the description

From superpowers `writing-skills`:

- `name`: lowercase letters, numbers, and hyphens; equal to the directory name. Name by what you do or the core insight, verb-first for processes (`condition-based-waiting`, not `async-test-helpers`).
- `description`: third person, under ~500 characters, front matter under 1024. It states **when** to load the skill: the triggers, symptoms, and situations an agent would see. It never summarizes the skill's workflow. Tested failure: a description saying "code review between tasks" made agents run one review and skip the body's two-stage flowchart. A workflow summary becomes a shortcut the agent follows instead of reading the body.
- Put the words an agent would search for in the description and early in the body: error strings, symptoms, tool and file names.

```yaml
# Bad: summarizes the workflow, so the agent follows this instead of the body
description: Use for TDD - write test first, watch it fail, write minimal code, refactor
# Good: triggers only
description: Use when implementing any feature or bugfix, before writing implementation code
```

## Files and cross-references

- One flat namespace: `skills/<name>/SKILL.md`. Extra files only for heavy reference (100+ lines) or reusable scripts and templates.
- Invoke bundled scripts through their interpreter (`bash scripts/x.sh`, `python3 scripts/x.py`), never by bare path: packagers can strip executable bits.
- Point at another skill by name with an explicit marker ("REQUIRED: use the `tdd` skill"). Never `@`-include a file: it force-loads into context.
- Move flag lists to the tool's `--help`; reference the other skill instead of repeating its steps; one excellent example beats several mediocre ones.
- Flowcharts only for non-obvious decisions or loops an agent might exit early. Lists and tables for everything else.
