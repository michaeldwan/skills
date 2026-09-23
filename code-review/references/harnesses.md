# Harness notes

How to launch reviewers and verifiers, and which model and thinking level to
set, in each harness.

## Model tiers

The skill names tiers by role, and this table maps them to models. When new
models ship, update the table, not SKILL.md.

| Tier | Used for | Claude Code | Pi (openai-codex) |
| --- | --- | --- | --- |
| fast | nothing yet | `haiku` | `openai-codex/gpt-6-luna` |
| standard | reviewers, verifiers | `sonnet` | `openai-codex/gpt-5.6-terra` |
| strong | correctness reviewer on risky diffs (SKILL.md Step 4) | `opus` | `openai-codex/gpt-6-sol` |

Always set the model explicitly. Omitting it inherits the parent's, which is
usually the expensive implementing model.

## Claude Code

- Tool: `Agent`. Type: `general-purpose`. `Explore` and `Plan` don't receive
  CLAUDE.md, so reviewers of that type miss the user's conventions.
- Model: from the tier table. Claude Code's aliases follow the latest model in
  each family, so the table rarely needs changing.
- Launch with `run_in_background: true`. The harness notifies you as each agent
  finishes, which is when you dispatch that reviewer's verifiers.

## Pi (pi-subagents)

- Tool: `subagent`. Type: `general-purpose` (inherits AGENTS.md).
- Model: the full `provider/id` from the tier table. Don't use short names
  like `sol`; they can match more than one model generation. Only list models
  the account can actually use: a model that fails (no credits, not available
  on the plan) costs a retry before the review starts.
- `thinking`: `medium` for reviewers and verifiers, `high` for a strong-tier
  correctness reviewer. Don't use `xhigh` or `max`.
- `max_turns`: 40 for reviewers (50 when the reach includes fit), 20 for
  verifiers. This is the stop, not a wall-clock timeout.
- Launch with `run_in_background: true` and collect with
  `get_subagent_result`, dispatching a reviewer's verifiers as soon as its
  result is in.

## Anything else

Use whatever the harness has for launching parallel subagents, set the model
and thinking level explicitly where it allows, and prefer a turn limit over a
timeout. With no subagents, run each reviewer and verification as its own
sequential pass.
