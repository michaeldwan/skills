---
name: code-review
description: "Multi-agent code review of a diff. Reads each change in the context of the surrounding code and, for branch reviews, how it fits the existing codebase (reuse, sites that should have changed with it). Loads the project and language skills that match the change, runs one or a few focused reviewers in parallel, has a separate agent check every serious finding against the code, and returns one prioritized report to the caller. Sizes itself to the diff so small changes come back in a few minutes. Use whenever the user or a calling agent says 'review this', 'review my changes', '/code-review', 'review the branch', or 'recheck the fixes', or finishes a unit of work that should be checked before it's accepted — including automated loops that review each step and again at the end. Report-only: it never edits the tree."
---

# Code Review

## What a good review here is

Point any model at a diff and it finds things. The hard part is telling which
findings are real. A confident, plausible, wrong finding is worse than none: the
caller acts on it and "fixes" code that was correct.

So: **read the change in its flow, report skeptically.** Catch bugs by reading
each hunk with the code around it, not the diff in isolation. Catch design
misses by checking how the change fits the code that was already there: the
helper it duplicated, the function it should have extended instead, the sibling
that needed the same change. Report only findings that name a concrete problem
and survive a separate check against the code.

And do it fast. A review that takes 15 minutes stops getting run, or gets run
while the caller sits idle. Almost all review time is model turns, not tool
execution, and the whole review waits on its slowest agent. Every rule below
that looks like a limit exists to keep one agent from wandering for 60 turns
while the rest wait.

## Arguments

All optional. The skill decides everything else from the diff.

- **Scope** — what to review.

  | Arg | Scope |
  | --- | --- |
  | _(none)_ | Uncommitted changes (`git diff HEAD`); if none, `branch` |
  | `branch` | Current branch vs its base (`git diff main...HEAD`) |
  | `<number>` | GitHub PR (`gh pr diff <num>`) |
  | `<path>` | Uncommitted changes under that path |
  | git ref/range | That span |

- **Intent** — one sentence on what the change is for. If you're the agent that
  just made the change, pass it; don't make the review reconstruct it.

- **Prior review** — the report from an earlier review of this change (the text
  or a path to it). Pass it whenever you're asking for a review after fixing
  findings, especially when the review runs in a fresh subagent that can't see
  the earlier one. It turns the run into a [Recheck](#recheck) instead of a
  full review.

A caller can also say in plain words that it wants something lighter or more
thorough than the defaults below ("just a sanity check", "go deep on the
concurrency"). Honor it; nobody has to.

## Step 1: Resolve scope and intent (you, under a minute)

Do this yourself with a few commands. No subagent.

1. Resolve the scope, confirm it's non-empty, and write the diff to a file in a
   temp directory (the harness scratchpad if it has one). Reviewers read that
   file instead of re-running git.
2. Get `git diff --numstat` for the same scope. Note changed lines and files of
   non-test code, excluding lockfiles, generated files, vendored code, and
   snapshots.
3. Intent: use what the caller passed. Otherwise the commit messages
   (`git log <base>..HEAD`) or PR body. Ask the human for one sentence only if
   none of those exist.
4. **Recheck?** If the caller passed a prior review, or this conversation holds
   one from this skill and the caller is asking again after fixes, go to
   [Recheck](#recheck) instead.
5. State scope, size, shape (Step 2), and skills (Step 3) in one line.

## Step 2: Pick the shape

Two things set the shape: the scope decides how far the review reads, and the
size decides how many reviewers split the work.

**Scope sets the reach.**

- **Uncommitted changes** (usually a check before committing): review the change
  and its immediate flow — enclosing functions, direct callers and callees.
- **Branch, PR, or range** (the change as a whole): also review how it fits the
  existing code. Search the codebase for what the change should have reused or
  adjusted: an existing function that does the same thing, a function that
  should have been extended instead of a new one added next to it, callers or
  sibling code paths that needed the same change, established patterns it
  ignores. A diff-only read can't find these.

**Size sets the number of reviewers.** What limits a reviewer is how much code
it can read in flow within its tool budget, so size by the changed code a
reviewer has to read: non-test, non-generated code, and the number of files and
areas it spans. Tests are covered through the intent-and-fit reviewer's
coverage check; docs get skimmed.

- **One reviewer, covering every lens,** when the changed code is small enough
  for one agent to read end to end with its callers in about 20–30 tool calls —
  roughly up to 1000 lines in 10–15 files. A reviewer covering every lens on a
  small diff finishes in a few minutes; splitting it across lenses adds agents
  that all re-read the same code, and a wait on the slowest, with no gain in
  findings.
- **Three reviewers, one per lens group below,** when it's bigger.
- **Split correctness by area** only when one reviewer still couldn't read all
  of it: two or more correctness reviewers, each with a similar amount of code
  (by lines and files, not by layer). An uneven split just moves the wait to
  whoever got the most.

These numbers are starting points; adjust them from how long reviewers actually
take.

Lens groups for multi-reviewer runs:

1. **Correctness in flow** — logic, error handling, broken invariants, missed
   cases, anything locally fine but wrong in its caller or callee. Security,
   concurrency, and data/migration concerns go here when the diff touches them.
2. **Intent and fit** — does the change do what the intent says; sites the
   intent implies should have changed but didn't; existing code it should have
   reused or extended; whether new paths and edge cases are tested.
3. **Maintainer** — conventions from AGENTS.md/CLAUDE.md and project skills,
   needless complexity, and AI-generated cruft: restated comments, premature
   abstraction, unused flexibility. Would someone inheriting this resent it?

Don't add a lens the change has no surface for; an empty lens invents findings
to justify itself.

## Step 3: Pick skills

From the skills available in this session, pick the ones that match what the
diff actually touches. Judge from the descriptions you already have; don't open
every skill to decide.

- For each language, framework, and concern present in the diff, the skill(s)
  specific to it. A diff touching Go and TypeScript gets skills for both.
- Within a family of skills, the specific ones that match: a Go change that adds
  goroutines gets the concurrency skill, not every Go skill installed.
- Repo-local skills whenever the change is in their territory.
- Route each skill to the reviewer whose lens uses it. The test: would loading
  it change a finding on this diff?
- Never pass this skill or writing-voice to a reviewer. Reviewers get their
  instructions from `references/reviewer.md`; writing-voice is for your report.

## Step 4: Dispatch reviewers — all in one message

Send every reviewer in a single message with parallel tool calls. Dispatching
one per turn adds 15 seconds or more per reviewer before the last one starts.

Each reviewer's prompt is short, because the rules live in a file:

```
You are a code reviewer. First read <this skill's dir>/references/reviewer.md
and follow it.

Repo: <repo path>
Diff: <path to diff file>   (scope: <scope>)
Intent: <one sentence>
Reach: <change and immediate flow | also fit with existing code>
Lens: <lens group, or "all lenses">; for a correctness split, the files in this reviewer's area
Skills to load: <names, or none>
```

Add a line only for context the reviewer can't get itself (a known constraint,
a related prior decision, a caller's "go deep on X"). Don't paste the diff,
AGENTS.md, or rules into the prompt — the reviewer reads the file, and the
harness already gives it your AGENTS.md/CLAUDE.md.

**Agent and model.** Use a general-purpose agent, not an explore-only type,
which may not see AGENTS.md/CLAUDE.md. Set the model and thinking level
explicitly on every dispatch; `references/harnesses.md` has the mapping per
harness. Reviewers run on the standard tier. Use the strongest model only for
the correctness reviewer when the diff touches auth, secrets, shared-state
concurrency, or a migration that can lose data. Never let reviewers silently
inherit a top-tier parent model.

Don't set short wall-clock timeouts on reviewers. A reviewer killed at 120
seconds returns nothing, and the whole batch is wasted. Bound work with turn
limits where the harness has them and the budget in `reviewer.md`.

If a reviewer or verifier fails for a reason outside the code (a network or API
error, not its turn limit), dispatch that one agent again, once. Never re-run
the agents that succeeded. If it fails a second time, list its lens or finding
under Coverage gaps as not reviewed and finish without it.

## Step 5: Verify serious findings as they arrive

Every Blocking or Important finding gets checked by a fresh agent before it's
reported. The finder is attached to its finding; the verifier's job is to
refute it.

- **Start verifying as each reviewer returns.** Don't wait for the whole batch;
  if the harness notifies you when background agents finish, dispatch that
  reviewer's verifiers right away.
- One verifier per finding, all of a reviewer's verifiers in one message, same
  agent type and tier as the reviewers.
- Prompt:

  ```
  You are verifying one code-review finding. First read
  <this skill's dir>/references/verifier.md and follow it.

  Repo: <repo path>
  Diff: <path to diff file>
  Intent: <one sentence>
  Finding: <the finding, verbatim, with file:line and stated failure>
  ```

- Verdicts: **CONFIRMED** → report. **PLAUSIBLE** → report, marked unconfirmed.
  **REFUTED** (with the quoted code that refutes it) → drop, or demote to a
  Suggestion if something minor remains.
- Nits and Suggestions skip verification.

Don't investigate findings yourself — no reading files, running tests, or
driving the app to settle a finding. Don't add passes the skill doesn't call
for: no extra adjudication round, and no more reviewers after the first batch,
even when the findings suggest an area deserves a closer look. If a verdict
looks wrong, report the finding as PLAUSIBLE with both views in one line and
let the caller decide. If an area deserves a closer look, say so in the report
("the retry path needs a concurrency review"); the caller can ask for one.

## Step 6: Report

1. **Dedupe** findings from different reviewers; note when more than one raised
   the same issue.
2. **Rank:**
   - **Blocking** — a real bug, security hole, broken contract, or missing test
     for a new code path. Must be addressed.
   - **Important** — a clear correctness risk short of a definite bug, a missed
     reuse or companion change that will cause drift, or a maintainability
     problem that will bite.
   - **Nit** — small style or clarity fix.
   - **Suggestion** — an observation; no action requested.

Every Blocking and Important finding names a concrete problem: for a bug, the
input or state that leads to the wrong outcome; for a fit issue, the existing
code it duplicates or the site that was missed. A finding that can't is a
Suggestion.

```
Reviewed: <scope> at <HEAD sha>, <with | without> uncommitted changes

## What changed and why
<one paragraph>

## Findings
### Blocking
- <file:line> — <issue>. Failure: <input/state → wrong outcome>. Fix: <fix>. [confirmed | unconfirmed]
### Important
### Nits
### Suggestions

## Coverage gaps
<sites the intent implies should have changed; missing tests>
```

Keep each finding to a sentence or two plus the fix. If nothing survives, say
so — "no blocking issues found" is a real result. Load writing-voice for the
report. Return it to the caller and stop.

## Recheck

For the review after fixes. A full review of the whole change again is the
slowest way to confirm three fixes.

1. Take the prior report's findings (the Prior review argument, or the earlier
   report in this conversation) and diff the fixes: what changed since the SHA
   on its `Reviewed:` line. If that review included uncommitted changes, there's
   no commit that holds the reviewed state; use the diff from that SHA and tell
   the reviewer to focus on the code around the prior findings.
2. Dispatch one reviewer with the fix diff, the prior findings, and
   `Lens: recheck` — it confirms each prior finding is resolved and reviews
   the fix diff for new problems.
3. Verify only new Blocking findings. Report: each prior finding as resolved or
   still open, then any new findings.

## Conventions

- **Report-only.** Neither you nor any reviewer or verifier edits the tree. The
  caller decides what to apply.
- **Parallel means one message.** Reviewers in one batch; each reviewer's
  verifiers in one batch.
- **No subagents below reviewers.** Reviewers and verifiers don't spawn agents.
- **Without subagents,** run each reviewer and each verification as its own
  sequential pass with the same instructions files. Slower, same output. Don't
  collapse them into one read.
- **No files** beyond the temp diff, unless the caller asks.
