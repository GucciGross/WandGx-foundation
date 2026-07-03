#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-hermes-agent-starter}"
VISIBILITY="${2:-public}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required: https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Run gh auth login first." >&2
  exit 1
fi

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Initial Hermes agent starter"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" "--$VISIBILITY" --source=. --remote=origin --push
else
  git push -u origin "$(git branch --show-current)"
fi
