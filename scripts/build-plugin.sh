#!/usr/bin/env bash
#
# build-plugin.sh
#
# Package the whole plugin as one archive: the skill and its references, the
# Claude Code and Codex hooks, the output style, the plugin and marketplace
# manifests, the canonical linter, and the docs.
#
# The archive is the tracked source at a git ref (default: HEAD), so it carries
# no node_modules, no dist/, and no __pycache__. Reproduce a release asset by
# passing that release's tag.
#
# Usage:
#   scripts/build-plugin.sh            # archive HEAD
#   scripts/build-plugin.sh v1.2.0     # archive a tag
#
# Output: dist/authengentic-plugin-<version>.zip, with the plugin folder at
# authengentic/ inside the zip.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="${1:-HEAD}"

cd "$ROOT"

echo "==> Reading the version"
VERSION="$(node -p "require('./.claude-plugin/plugin.json').version")"
OUT="$ROOT/dist/authengentic-plugin-$VERSION.zip"
echo "    plugin version $VERSION, ref $REF"

echo "==> Checking the manifests parse"
node -e "JSON.parse(require('fs').readFileSync('.claude-plugin/plugin.json'))"
node -e "JSON.parse(require('fs').readFileSync('.claude-plugin/marketplace.json'))"
node -e "JSON.parse(require('fs').readFileSync('.codex-plugin/plugin.json'))"

echo "==> Checking the hook and skill targets exist"
for f in \
  src/hooks/authengentic-activate.js \
  src/hooks/lint_hook.py \
  evals/authengentic_lint.py \
  evals/slop.tsv \
  rules/core.md \
  src/hooks/learn.py \
  skills/authengentic/SKILL.md \
  skills/authengentic-learn/SKILL.md \
  output-styles/authengentic.md \
  hooks/hooks.json; do
  if [ ! -f "$f" ]; then
    echo "missing required file: $f" >&2
    exit 1
  fi
done

echo "==> Checking the generated rule surfaces match rules/core.md"
node scripts/build-rules.mjs --check

echo "==> Self-testing the canonical linter"
python3 evals/authengentic_lint.py --self-test

echo "==> Writing $OUT"
mkdir -p "$ROOT/dist"
rm -f "$OUT"
git archive --format=zip --prefix="authengentic/" "$REF" -o "$OUT"

echo "==> Done"
echo "    $OUT"
unzip -l "$OUT" | tail -1
