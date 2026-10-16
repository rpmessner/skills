# Builder check

<!-- house: adapt; from: superpowers:skills/brainstorming/builder-check-prompt.md@bb92a77 -->

Once a project-size spec is written, have it read cold by someone who must build from it and can't ask
the author. Tell the user a reviewer will read it first and you may come back once with a few questions.

Dispatch a fresh read-only subagent with the prompt below (fill in the domain and the spec — a path or
the text). Without a subagent tool, read the spec as that builder yourself.

```
You are a talented [DOMAIN, e.g. "Elixir engineer", "WoW addon developer"]. You've been handed a spec
and asked to plan the build. You cannot talk to the person who wrote it.

Read [SPEC].

Report only the questions you'd still need answered before you could plan this well: places where
you'd have to guess and a wrong guess would matter. For each, give the question and why the answer
changes the plan. Rank them by importance.

Skip anything the spec explicitly leaves to the builder, anything you could reasonably decide yourself,
and wording nitpicks. If nothing important is left, say "nothing important left".
```

Sort what comes back into three piles:

- **Answered already** by the conversation or the codebase — put the answer in the spec.
- **Minor** — a sensible builder could settle it without changing what gets built. Settle it, mark it as
  an agent call.
- **Theirs** — only the user can answer it, and it changes what gets built.

Bring the "theirs" pile in one message, most important first (this is the one exception to one question
at a time). Update the spec with the answers. That is the only round the check produces.
