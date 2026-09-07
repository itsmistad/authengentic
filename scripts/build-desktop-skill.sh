#!/usr/bin/env bash
#
# build-desktop-skill.sh
#
# Stage the authengentic skill as a self-contained folder and zip it for upload
# to the Claude apps (Chat and Cowork tabs), claude.ai, or any Agent Skills
# client that takes a zip.
#
# The canonical linter stays at evals/authengentic_lint.py. This script copies
# it and slop.tsv into the staged skill under scripts/, so the sandbox that runs
# the skill has the linter without a second copy living in git.
#
# Output: dist/authengentic-skill.zip, with the skill folder at the zip root.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_SKILL="$ROOT/skills/authengentic"
LINTER="$ROOT/evals/authengentic_lint.py"
SLOP="$ROOT/evals/slop.tsv"
STAGE="$ROOT/dist/skill-stage"
OUT="$ROOT/dist/authengentic-skill.zip"

DESC_LIMIT=1024

echo "==> Checking sources"
for f in "$SRC_SKILL/SKILL.md" "$LINTER" "$SLOP"; do
  if [ ! -f "$f" ]; then
    echo "missing required file: $f" >&2
    exit 1
  fi
done

echo "==> Checking the SKILL.md description length"
python3 - "$SRC_SKILL/SKILL.md" "$DESC_LIMIT" <<'PY'
import re, sys, pathlib
path, limit = sys.argv[1], int(sys.argv[2])
text = pathlib.Path(path).read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    sys.exit("SKILL.md has no YAML frontmatter")
fm = m.group(1)
block = re.search(r"description:\s*\|\n(.*?)(?=\n[A-Za-z_-]+:)", fm, re.S)
one_line = re.search(r"description:\s*(.+)", fm)
desc = " ".join(l.strip() for l in block.group(1).splitlines()) if block else (one_line.group(1) if one_line else "")
if not desc:
    sys.exit("could not read the description field")
print(f"    description is {len(desc)} characters")
if len(desc) > limit:
    sys.exit(f"description is over the {limit}-character Agent Skills limit; trim it")
PY

echo "==> Staging the skill"
rm -rf "$STAGE"
mkdir -p "$STAGE/authengentic"
# rsync keeps the references/ tree and drops any local build artifacts.
rsync -a --delete \
  --exclude '.DS_Store' \
  --exclude '__pycache__' \
  --exclude 'scripts/' \
  "$SRC_SKILL/" "$STAGE/authengentic/"

echo "==> Bundling the linter under scripts/"
mkdir -p "$STAGE/authengentic/scripts"
cp "$LINTER" "$STAGE/authengentic/scripts/authengentic_lint.py"
cp "$SLOP" "$STAGE/authengentic/scripts/slop.tsv"

echo "==> Self-testing the bundled linter"
python3 "$STAGE/authengentic/scripts/authengentic_lint.py" --self-test

if command -v skills-ref >/dev/null 2>&1; then
  echo "==> Validating with skills-ref"
  skills-ref validate "$STAGE/authengentic"
else
  echo "==> skills-ref not on PATH; skipping spec validation"
  echo "    install it from https://github.com/agentskills/agentskills to enable this check"
fi

echo "==> Writing $OUT"
mkdir -p "$ROOT/dist"
rm -f "$OUT"
( cd "$STAGE" && zip -q -r "$OUT" authengentic )

echo "==> Done"
echo "    $OUT"
echo "    Upload it in the Claude apps: Customize -> Skills -> + -> upload the zip."
echo "    Code execution must be on: Settings -> Capabilities -> Code execution and file creation."
