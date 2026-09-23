---
name: authoring-prs
description: "Use this skill whenever creating a pull request, writing or editing a PR description, drafting an issue, or preparing any GitHub/GitLab submission. Also use it when the user asks to 'open a PR', 'write up the PR', 'create an issue', or 'submit this'. Produces short descriptions that tell a reviewer arriving cold what the change is, why it's needed, how it works, and where it lives -- and nothing else."
---

# Authoring PRs and Issues

## Who you're writing for

A reviewer arriving with close to no context. They have the diff and CI's
results on the same page, and none of your session: not the plan, the ticket
thread, the dead ends, or the commands you ran. They open the PR asking:

1. **What is this?**
2. **Why do we need it?**
3. **How does it work?**
4. **Where does it live?** Which parts of the system it touches, and who or what
   it affects.

The description answers those four, in about that order, and stops. A sentence
that doesn't answer one of them doesn't go in.

## Describe the result, not the move

Write about what exists after the change as plain fact: what it is, what it
does, why it's there. You remember the change as a move away from something --
the old code, an option you weighed, a decision made in the session. The reader
has none of that, so a sentence framed against it has nothing to attach to.

- Good: "A client that sends more than 100 requests a minute gets a 429 with a
  `Retry-After` header."
- Bad: "Rate limiting now lives in the API server instead of the gateway."
  Framed against an option the reader never saw.

Take the *what* from the code on the branch, not from your memory of the
session. Take the *why* from the session, but write it as a reason about the
software, not about the decision: "so skills can be installed from a clone of
this repo", not "this makes the repo self-contained instead of relying on
dotfiles".

The reviewer's present is the base branch: the change isn't merged, and `main`
is the code they can open. So state the problem as a fact about `main` ("on
`main`, one client can use up the whole request budget"), and the change as
what the branch does. If the branch fixes a bug in `main`, state the bug --
it's the why. Never compare against options, plans, or decisions that only
existed in the session.

## What and why: open with the problem

The first sentence says what a person ran into, or what's wrong with the state
of the world:

- "Sessions disappear after restarting opencode in a git worktree."
- "`flyctl` used to accept `DOCKER_HOST` the same as Docker. This is now failing
  with a parse error."
- "The architecture docs describe a system that no longer exists."

Not "This PR adds...", and not the mechanics -- those come once the reader knows
what problem they're looking at. If the problem shows up as an error or bad
output, quote it in a code block right after the opening: it's the fastest way
to say what broke, and it's what someone searching for the bug will paste in.

If you can't say what the PR does and why in one plain sentence, read the diff
again before writing. Link the issue, thread, or incident if there is one.

## How: the idea, not the inventory

Explain the approach in a few sentences -- the idea a reviewer needs to read the
diff with the right model in their head. "Retries now back off per host instead
of globally, so one slow mirror can't stall every download." Not a list of what
changed; the diff is right there.

If part of the change is non-obvious, risky, or looks wrong, explain the
decision yourself: what the code does there and why. Mention an alternative
only when a reviewer would reasonably ask "why not X?", in one sentence, and
never in the title or opening. Don't point the reviewer at it ("look closely at X", "worth a careful review") -- that hands them
work the description should have done.

Show real artifacts when they're the substance: old error vs. new error, the new
config format, benchmark numbers for a performance change.

Keep lists short. A sentence that strings together more than three things
("fixes A, B, C, D, and E") hides which one matters. Lead with the one or two
that matter most, each in its own sentence, and drop or link the rest. That
includes lists that look like precision -- every variant, every file touched:
"every `maturin` call" says it.

## Where: what it touches and who it affects

Name the parts of the system the change lives in, and what happens to the
people and things around it:

- **Blast radius.** Feature flags, what deploys where on merge, migrations,
  what happens to existing data, how to roll back. "This is behind
  `COG_DOCKER_SDK_CLIENT=1`, off by default" changes the review from "is this
  safe?" to "is this correct?"
- **What it deliberately leaves alone,** and known gaps or follow-ups.
- **Bundled changes,** one sentence each, never folded into one list: "Also
  bumps `pyo3-stub-gen` so the next `pyo3` bump doesn't break stub generation."
  Present them as what else the PR does ("Also fixes..."), not as a story of what
  turned up along the way.
- **How to see it,** when the reviewer needs to do something CI can't: try it on
  staging, check a dashboard after deploy. Write it as an instruction to them.

## What doesn't answer the four questions

These slip in anyway, so name them: a report of checks you ran ("tests and lint
pass", a Verification section, a list of commands), the story of how the branch
got here, a summary of the diff, session context (task ids in the prose, "per
the plan", which agent did what), the same point said twice, and boilerplate
(a "Summary" heading, empty template sections, "N/A", filler adjectives, emoji).

Never @-mention anyone without the user's explicit approval.

If you haven't run the project's checks, run them or ask the user before
opening the PR. Don't cover the gap in prose.

## Length

Match the weight of the change. An entire PR body can be one line:

> `docker container stop` prints the container id to stdout -- ignore it

A small fix gets two to four sentences and no headings. A large change gets a
few paragraphs, and headings only where they help a reviewer find something
("Deployment", "Rollback") -- never "Summary", "Changes", "Testing", or "Test
plan".

## Templates

Check `.github/` and `CONTRIBUTING.md` for a PR template first. The template
sets the structure; this skill sets the content. Fill sections with real
content and delete the ones that don't apply. If the template requires a
testing section, one line: what CI covers, plus any manual step the reviewer
should take.

## External vs. internal PRs

**Internal** (you have write access): the reviewer trusts you and is
sanity-checking. Skip what the team already knows -- link the thread instead of
re-explaining the bug.

**External** (someone else's repo): the maintainer is weighing whether to take
on your change and can't ask you questions. Link the issue, show how to
reproduce the problem, follow their patterns, and explain your reasoning. If
their CI doesn't exercise your change, one sentence on how you checked it is
fair.

## The title

Say plainly what the PR does or fixes. Plain and literal is fine; avoid the
mechanical change and anything framed against an alternative:

- Good: "sessions lost after git init in existing project"
- Good: "Accept human-friendly memory & storage sizes"
- Good: "Add a rate limit to the public API"
- Bad: "Update project.ts to fix migration ordering"
- Bad: "Refactor Docker client initialization logic"
- Bad: "Let the API server handle its own rate limiting"

Use the repo's prefix convention (`fix(scope):`) if it has one; keep the rest
human.

## Issues

Same voice. Open with what happens and what should happen instead, then the
smallest reproduction you have: command, input, actual output. Add what you
already know about the cause, and say plainly what you don't.

## Before you publish

Reread the draft as that reviewer. For each sentence, ask which of the four
questions it answers; cut the ones that answer none. Check that no sentence
lists more than three things.

Then scan the title and every sentence for words that usually mark a
comparison: *now, no longer, instead of, rather than, itself, its own, on its
own, anymore, moves, switches, still, owns*. For each one, check what it
compares against. `main`, when the reviewer needs it, is fine.
Anything from the session -- an option weighed, a decision, where the work
could have gone -- gets restated as a plain fact.

Load `writing-voice` for tone. For commit messages, use `authoring-commits`.
