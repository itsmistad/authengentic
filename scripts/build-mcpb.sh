#!/usr/bin/env bash
#
# build-mcpb.sh
#
# Pack the authengentic MCP server as dist/authengentic.mcpb for one-click
# install in Claude Desktop. Open the .mcpb file with the app to install it.
#
# Steps:
#   1. Copy the canonical linter into mcp/linter/ so the bundle is self-contained.
#   2. Install production node_modules inside mcp/.
#   3. Run mcpb pack.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP="$ROOT/mcp"
OUT="$ROOT/dist/authengentic.mcpb"

echo "==> Bundling the canonical linter"
mkdir -p "$MCP/linter"
cp "$ROOT/evals/authengentic_lint.py" "$MCP/linter/authengentic_lint.py"
cp "$ROOT/evals/slop.tsv" "$MCP/linter/slop.tsv"
python3 "$MCP/linter/authengentic_lint.py" --self-test

echo "==> Installing production dependencies"
( cd "$MCP" && npm install --omit=dev --no-audit --no-fund )

echo "==> Packing"
mkdir -p "$ROOT/dist"
rm -f "$OUT"
( cd "$MCP" && npx --yes @anthropic-ai/mcpb@2.1.2 pack . "$OUT" )

echo "==> Done"
echo "    $OUT"
echo "    Open it with Claude Desktop to install, or see docs/desktop/mcp-install.md for a manual stdio setup."
