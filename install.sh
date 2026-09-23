#!/bin/bash
# Link every skill in this repo into the shared agent skills directory.
# Safe to re-run: links are refreshed, and links to skills that no longer
# exist here are removed. Links and directories from anywhere else are left
# alone.
#
# SKILLS_DIR overrides the target (default: ~/.agents/skills).

set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
skills_dir="${SKILLS_DIR:-$HOME/.agents/skills}"
mkdir -p "$skills_dir"

for skill in "$repo"/*/; do
  skill="${skill%/}"
  [ -f "$skill/SKILL.md" ] || continue
  name=$(basename "$skill")
  target="$skills_dir/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "warning: $target is a real directory, not a link -- skipping $name. Remove it to install this repo's version." >&2
    continue
  fi

  ln -sfn "$skill" "$target"
  echo "linked $name"
done

# Remove links into this repo whose skill is gone.
for entry in "$skills_dir"/*; do
  [ -L "$entry" ] || continue
  link=$(readlink "$entry")
  case "$link" in
    "$repo"/*) [ -f "$link/SKILL.md" ] || { rm "$entry"; echo "removed stale $(basename "$entry")"; } ;;
  esac
done
