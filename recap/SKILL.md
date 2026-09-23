---
name: recap
description: "Reconstruct the thread of the current session so the user can pick it back up after stepping away. Summarize the originating intent, walk the conversational path through to where it currently stands, and name the natural next step. Use when the user says 'recap', 'what were we doing', 'where were we', 'remind me what this session is about', 'catch me up on this conversation', 'I lost the thread', 'what's this session about', 'where am I', or runs /skill:recap. Trigger it any time the user comes back to a session they've been away from and needs to reorient."
---

# recap

Summarize the session the way you'd re-orient a person who stepped out of a conversation and walked back in: *"you asked X, we talked about Y and Z, which led us to W — so the next thing is…"*. The goal is to click them back into the thread, not to produce a status report.

## Where the material comes from

Your source is the conversation already in your context — the turns you can see, including any compaction summary the harness left. This keeps the skill identical across pi, Claude Code, OpenCode, and anywhere else Agent Skills run.

- Do **not** start fresh investigation: don't re-read the codebase, run searches, or open files to "check" things. You're summarizing what's already on the table, not re-deriving it.
- Use the **real names** from the work — file paths, function names, terms the user and you actually used. Don't invent labels for things that already have names.
- If the conversation is too short to have a thread yet (the session just started, or there's been one exchange), say so plainly rather than padding.

## Honesty about what's recoverable

Sessions meander, and that's fine — the thread isn't supposed to be a straight line, it's the path the conversation actually took. But if the **originating intent** genuinely isn't recoverable from context (it predates a compaction that dropped it, or the session opened mid-task with no stated purpose), say so: *"I can't recover the original ask from context — here's what I can see of the thread."* A reported blank beats a confident confabulation. Same for any section you can't honestly fill — leave it out rather than inventing it.

## Output

Print this template, filled in. Keep it skimmable — plain language, the length the session earns. A quick 5-turn session might be four short paragraphs; a day-long one earns more. Don't pad to fill sections.

```
# recap

## Intent
<the originating ask — why this session exists. One or two lines, plain language.
 "You came in to …". If you can't recover it, say so.>

## The thread
<walk the conversational path in order. Show the shape of the conversation —
 the topics in the sequence they actually came up, each with where it landed.
 It should read as "we talked about X, then Y, which led to Z."
 Group closely-related turns; don't enumerate every single message.
 This is the part that re-triggers "oh yeah, so …".>

## Where that left us
<concrete current state: what exists now, what changed, what's decided,
 what's open or half-done. Names of real things, not abstractions.>

## The next thing
<the natural place to pick the thread back up. The single "so …" the thread
 is pointing at — what was mid-thought, just raised, or next in line.
 If there's genuinely no clear next step, say that.>
```

## Tone

Write it the way a sharp collaborator would talk you back into a conversation, not the way a project tracker would log it. Specific beats abstract: "we kept hitting the token limit on the context dump, so we switched to streaming it" lands; "we addressed technical challenges" does not.
