#!/usr/bin/env python3
"""Print when the current agent session started and when it was last active.

Last active is the last message before the one that asked for the recap, so
the recap itself doesn't count as activity.

Supports Claude Code, which sets CLAUDE_CODE_SESSION_ID and keeps one JSONL
transcript per session. Pass a transcript path to read a specific one. Prints
nothing and exits 1 when no transcript can be found.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_transcript():
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        return None
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    matches = list((config / "projects").glob(f"*/{session_id}.jsonl"))
    return matches[0] if matches else None


def is_user_prompt(entry):
    """A message the user typed, not a tool result or injected context."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return False
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return True
    return isinstance(content, list) and not any(
        part.get("type") == "tool_result" for part in content if isinstance(part, dict)
    )


def ago(delta):
    minutes = int(delta.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_transcript()
    if not path or not path.exists():
        return 1

    messages = []
    with path.open() as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") in ("user", "assistant") and entry.get("timestamp"):
                messages.append(entry)
    if not messages:
        return 1

    prompts = [i for i, m in enumerate(messages) if is_user_prompt(m)]
    # Everything before the latest prompt; that prompt is the recap request.
    before = messages[: prompts[-1]] if prompts else messages
    if not before:
        return 1

    def parse(m):
        return datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).astimezone()

    # Parallel tool calls can land slightly out of order, so don't trust position.
    times = [parse(m) for m in before]
    started, last = min(times), max(times)
    now = datetime.now(timezone.utc).astimezone()
    fmt = "%a %b %-d, %-I:%M%p"
    print(f"started: {started.strftime(fmt)} ({ago(now - started)})")
    print(f"last active: {last.strftime(fmt)} ({ago(now - last)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
