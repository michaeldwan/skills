---
name: recap
description: "Orient the user in the current session after they've lost track of it: what this session is about, what kind of work it is (planning, exploring, building, debugging, reviewing), what state it's in, and where it stopped. A short 'previously on...', not a history or a to-do list. Use when the user says 'recap', 'what were we doing', 'where were we', 'what's this session about', 'catch me up', 'I lost the thread', 'remind me what this is', or runs /skill:recap. Also use when the user comes back to a session after time away and needs to reorient."
---

# recap

The user runs many sessions at once and comes back to them after an hour, a day,
or a week. They run this when they can't remember which session this is or where
it was. Your job is orientation: give them enough to recognize the session and
find their footing. It's a "previously on...", not a history of the session and
not advice about what to do next.

## Where the material comes from

Use only the conversation already in your context: the turns you can see,
including any compaction summary the harness left.

- Don't investigate. No reading files, running searches, or checking git. You're
  describing what's already on the table.
- The one exception: run `scripts/session-times.py` from this skill's directory
  to get when the session started and when it was last active. Message
  timestamps aren't in your context, so this is the only way to know them. If it
  prints nothing or fails, leave the times out.
- Use the real names from the work: file paths, function names, ticket ids,
  terms the user and you actually used. Don't invent labels.
- If a compaction summary is your only source for the earlier part of the
  session, say so in a few words. Summaries lose detail, and the user should
  know the early part is secondhand.
- If you can't recover what the session is about (it opened mid-task, or a
  compaction dropped the original ask), say that plainly instead of guessing.

## Report the state, don't steer

- **Separate what the user decided from what you proposed.** "You chose X" and
  "I suggested X, you hadn't responded" are different states to come back to.
  Don't promote a suggestion, or a remark the user made in passing, into a
  decision.
- **No recommendations.** Don't suggest a next step or say what the user should
  do. Report where the session stopped: the last thing that happened, and
  anything waiting on someone. If your last message asked the user a question
  they never answered, say so -- that's usually the most useful line in the
  recap.
- **Recap and stop.** Print the recap and end your turn. Don't continue the work,
  even if it looks obvious.

## Output

Keep the whole recap on one screen, however long the session ran. Size it by how
much is in play now, not by how much happened. A short session can be two
sentences with no headings, plus the times.

For anything longer, use this shape:

```
**<what this session is about>** · <mode> · <repo, plus branch or worktree if it matters>
Started <start time> · last active <last active time>

**Previously:** <2-4 lines. Only the turns that changed the session's direction
or scope. Skip dead ends unless one explains the current state.>

**Now:** <what exists, what's decided, what's still open. Real names.>

**Stopped at:** <the last thing that happened; any unanswered question, and
anything still running or waiting on the user.>
```

The first line is the one that matters most. The user may have several sessions
on related topics open at once, so it should let them tell at a glance whether
this is the one they're looking for. Copy the times as the script prints them,
including the relative part ("3d ago"). Name the mode (planning, exploring,
building, debugging, reviewing) because it's often the only thing that tells two
sessions on the same topic apart.

Leave out a section you can't honestly fill rather than padding it.

Be specific. "We kept hitting the token limit on the context dump, so we
switched to streaming it" is useful. "We addressed technical challenges" isn't.
