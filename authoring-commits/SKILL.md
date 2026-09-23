---
name: authoring-commits
description: "Use this skill whenever writing a commit message: `git commit`, amending or rewording a commit, squashing a branch into a single message, or drafting a message for the user to review -- including commits made by an automated loop after each task. Also use it when the user says 'commit this', 'write the commit message', 'land this', or 'squash and merge'. Produces messages that read like a changelog entry: what the software does now and why, with no ticket ids in the subject, no list of checks that passed, and no session log."
---

# Writing Commit Messages

## Who you're writing for

Someone reading `git log` months from now, who was not in the session that
produced the commit and cannot see the plan, the ticket, the conversation, or the
branch it came from. They have the repo and nothing else.

They need two things: **what this change did to the state of the world, and
why it was made.** That's all a commit message says. Every rule below follows
from it.

## Shape

**Subject + body, always.** No bare one-liners. If a change is too small to
explain in a paragraph, it still earns a sentence saying what it affects and why
it was worth doing. A subject alone forces the reader to open the diff to learn
anything at all, which is exactly the work the message exists to save them.

**Subject:** imperative, plain, under ~70 characters. Name the change in terms of
what it does for whoever uses the software.

- Good: `Surface neglected work with a stale signal`
- Good: `Add a rate limit to the public API`
- Bad: `add stale column + filter`
- Bad: `Rate-limit in the server itself`

Plain and literal is fine. What to avoid is mechanics and jargon, not
plainness: a subject that reaches for an angle usually ends up framed against
something only you know about.

If the repo enforces a convention (conventional-commits prefixes, a required
ticket key), follow it — check `git log` before writing. Absent an enforced
convention, skip the taxonomy: `feat(db):` classifies the diff, which the reader
can already see.

**Body:** a few sentences to a few short paragraphs, wrapped at ~72 columns. Say
what the software does after this change, and where that shows up (which
commands, which screens, which API). Say what was removed and what happens to
existing data or existing callers. Explain *why* where the reason isn't obvious
from the what. Show a command or a line of output when that's the clearest way to
say it.

Match length to weight. A one-line fix gets two sentences; a feature that changes
how people work gets three paragraphs. Start a new paragraph at each new point
-- what changed, why, what it means for existing callers -- rather than running
them together into one block.

Keep lists short. A sentence that strings together more than three things hides
which one matters: name the one or two that matter, each in its own sentence.
That includes lists that look like precision -- every variant, every file
touched: "every `maturin` call" says it.

## Describe the result, not the move

Write about what exists after the change as plain fact: what it is, what it
does, why it's there. You remember the change as a move away from something --
the old code, an option you weighed, a decision made in the session. The reader
has none of that, so a sentence framed against it has nothing to attach to.

- Good: "A client that sends more than 100 requests a minute gets a 429 with a
  `Retry-After` header."
- Bad: "Rate limiting now lives in the API server instead of the gateway."
  Framed against an option the reader never saw.
- Bad: `Rate-limit in the server itself`. Answers "where, as opposed to what?",
  a question only the session asked.

Take the *what* from the code as it is after the change -- the final file or
the diff -- not from your memory of the session. Take the *why* from the
session, but write it as a reason about the software ("so one noisy client
can't starve the rest"), not about the decision ("we decided the server should
handle it", "this makes it self-contained"). Alternatives you considered don't
go in a commit at all.

The previous code is different: the reader can find it in history, and
sometimes it's the point. If the change fixes a bug, state the bug -- it's the
why ("the cleanup deleted every link it hadn't created, including other
tools'"). Say what a replacement replaced, and what changes for existing
callers or data. What never belongs is a comparison to options, plans, or
decisions that only existed in the session.

## Never assume the session

The single most common failure: writing from inside the work, so the message only
parses if you still have the branch in your head. That rules out:

- **Ticket, issue, or task ids in the subject or prose.** No `PROJ-1421 fix the
  parser`, no bare id as a subject prefix, no `(x8ze4ay2)` tacked on the end.
  When a workflow or the project wants the id recorded, it goes in a trailer at
  the bottom (`Refs: PROJ-1421`), where it's metadata, not the sentence. Only a
  repo whose history already puts ids in subjects overrides this.
- **Point-in-time context.** "Phase 2", "the remaining chunk", "as discussed",
  "per the plan", "addresses review feedback", `tmp/plan.md`, "part 3 of 5".
  These name a moment that no longer exists. Say what the change *is* instead.
- **Which agent, tool, or person did what.** Nobody reading the log is trying to
  reconstruct the process.

Two more things slip in because they feel like diligence, and neither is what
changed or why: the checks you ran ("tests pass", "Tests cover A, B, and C")
and how you got there (what you tried first, what broke along the way).

## Don't narrate the diff

`git show` already lists what changed. A message that says "change `foo` to take a
`*Conn`, update three callers, add a test" spends its space on the one thing the
reader can get for free.

The prose version of this is just as bad: "Fixed X, updated Y, added Z" is a diff
summary written in English. So is a bullet list of touched files, the same
inventory reorganized under **What changed** / **What didn't** headings, and a
sentence that strings together every feature the change touched ("Snapshots,
rollback, replay, and Undo retain the spatial context for walking, leaps, forced
movement, interruption, and large pieces"). Name the one thing that matters.

Say what the mechanical change *enabled*, and what a reader should pay attention
to: the non-obvious call, the blast radius, the tradeoff you took, the follow-up
you left.

## Style

Plain declarative sentences. No filler adjectives — "comprehensive", "robust",
"enhanced", "seamless" carry no information. No "This commit adds/ensures/
provides"; just say what it does. No emoji. No tool attribution, session links, or
generated-by trailers.

## Mechanics

Pass the message through a heredoc or a file, never `-m` with `\n` escapes,
which land in the log as literal backslashes:

```sh
git commit -F - <<'EOF'
Subject line

Body paragraph.
EOF
```

## Before you commit

Reread the message as someone running `git log` in six months. For each line,
ask whether it says what changed in the world or why; cut the ones that don't.
Check that no sentence lists more than three things, that no paragraph runs
several points together, and that the subject has no id in it.

Then scan the subject and every body line for words that usually mark a
comparison: *now, no longer, instead of, rather than, itself, its own, on its
own, anymore, moves, switches, still, owns*. For each one, check what it
compares against. The previous code, when the reader needs it, is fine.
Anything from the session -- an option weighed, a decision, where the work
could have gone -- gets restated as a plain fact.

## Squashing a branch

The squashed message describes the *whole* change as one unit, not a merged list
of the commits that led to it. Intermediate steps, reverts, fixups, and
course-corrections along the branch are invisible to the reader and should stay
that way — the branch's false starts are session context too.

Write it by reading `git diff main...HEAD` and asking what the software does
after the change, not by concatenating subjects.

## Two real examples

    Surface neglected work with a stale signal

    A thing that's been sitting untouched for over two weeks now shows up
    as stale, everywhere: things show/list/tree, the TUI tree and detail
    panes, and the web dashboard. It rides alongside the existing claimed
    marker without affecting readiness or pickability, so nothing gets
    buried by being flagged.

    Triage can now sweep neglected work directly with
    things list --filter '{"stale":true}' instead of eyeballing
    updated_at across the whole backlog.

Names the change in user terms, says where it's visible, says explicitly what it
does *not* affect, and closes with the workflow it unlocks.

    Replace facets with free-form tags

    Classify work with free-form tags instead of the old typed "facets"
    system. Tags are set directly on new/update as a top-level field, a list
    can be filtered by tags (matching things that carry all of the listed
    tags), and they show up across the CLI, the TUI tree, and the web
    dashboard.

    This removes the facets machinery entirely: the `things facets` command,
    the `properties.area` classification convention, and the web `f.<key>`
    filter scheme are gone. Existing `area` and `tags` property values
    migrate into the new tags table automatically on first run.

A replacement, so it covers both halves: what the new thing does, what the old
thing was and where it went, and what happens to data people already have.

## Related

`authoring-prs` covers PR and issue descriptions — same voice, more room. Load
`writing-voice` alongside this skill for anything the user will read.
