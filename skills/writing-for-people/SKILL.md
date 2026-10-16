---
name: writing-for-people
description: Write or edit prose a human reads, such as docs, READMEs, RFCs, PR descriptions, commit messages, and reports, and cut AI tells from it. Use when drafting or reviewing any of those, or when asked to unslop text.
---

<!-- house: merge; from: pstack:pstack/skills/technical-writing@850d7f2, pstack:pstack/skills/unslop@850d7f2 -->

# Writing for people

Write so a tired engineer understands on the first read. Two passes: write to the standard, then strip the slop.

## Rules above everything

- Cut every word that does no work. "In order to" is "to".
- Use the short, everyday word: "use", not "utilize".
- The codebase is the word list. Write the real symbol, file, flag, or command, not a synonym for it.
- Say what it does, not how it feels: name the mechanism or the number ("a column rename fails the build").
- When a rule makes a sentence worse, fix the sentence another way or leave it alone.

## Pass 1: write to the standard

1. **Pick the mode** (Diátaxis). One document, one mode: tutorial (learning by doing), how-to (steps to a goal), reference (facts for lookup), explanation (the why). Split and link instead of mixing. PR descriptions and commit messages skip this step; a PR body is a briefing a reviewer reads in under a minute.
2. **Write to the reader.** "You", present tense, active voice, commands for instructions, the condition before the step, the common case first, headings that carry the point in sentence case.
3. **One reading per sentence.** One thought per sentence; split instructions over ~20 words. Every "it" and "this" points at one thing. One name per thing, everywhere.

The full layered standard, with a worked example, is in [references/technical-writing.md](references/technical-writing.md). Read it for any doc longer than a PR body.

## Pass 2: strip the slop

Scan the draft against every rule in [references/slop-patterns.md](references/slop-patterns.md) and rewrite each hit, keeping the meaning and the intended tone. Rule numbers are stable ids; cite them when reporting what you changed ("rule 13: em dash").

Done when every slop rule has been checked against the text, not when it "reads fine".
