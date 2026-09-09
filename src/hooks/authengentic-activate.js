#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');

// Claude Code caps hook stdout at 10,000 characters. Anything above that is
// written to a file and replaced by a preview, which defeats the hook.
const MAX_CHARS = 9500;

const FALLBACK_CONTEXT = `AUTHENGENTIC SKILL ACTIVE AUTOMATICALLY

Write plain, human-sounding technical and professional prose: short sentences, active voice, one term for one meaning, conditions before commands, sentence-case headings. Restore contractions where a person would use them. A lone dash is fine; only dash clusters need fixing. Do not change code, identifiers, commands, or quoted errors.`;

const HEADER = [
  'AUTHENGENTIC SKILL ACTIVE AUTOMATICALLY',
  '',
  'Follow these writing rules without waiting for the user to name the skill. The full skill, with the rule catalog and the check mode, is at skills/authengentic/SKILL.md in this plugin. Read it for a compliance check or for the four-operation model (write/review/refactor/recreate).',
  '',
].join('\n');

function candidates(pluginRoot, hookDirectory, relative) {
  const roots = [];
  if (pluginRoot) {
    roots.push(pluginRoot);
  }
  roots.push(path.join(hookDirectory, '..', '..'), path.join(hookDirectory, '..'));
  return roots.map((root) => path.join(root, ...relative));
}

function ruleCandidates(pluginRoot, hookDirectory) {
  return candidates(pluginRoot, hookDirectory, ['rules', 'core.md']);
}

function readFirstFile(list) {
  for (const candidate of list) {
    try {
      return fs.readFileSync(candidate, 'utf8');
    } catch (error) {
      // Missing, unreadable, or a directory: try the next candidate.
    }
  }
  return '';
}

function stripFrontmatter(content) {
  return content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
}

function buildContext(promptText) {
  if (!promptText) {
    return FALLBACK_CONTEXT;
  }
  const out = HEADER + stripFrontmatter(promptText).trim();
  if (out.length > MAX_CHARS) {
    process.stderr.write(`authengentic hook: payload is ${out.length} characters, over the ${MAX_CHARS} cap; sending the fallback ruleset\n`);
    return FALLBACK_CONTEXT;
  }
  return out;
}

/*
 * Resolve the plugin root from whichever variable the host sets. Claude Code
 * uses CLAUDE_PLUGIN_ROOT, Codex uses PLUGIN_ROOT. If both are set, prefer
 * CLAUDE_PLUGIN_ROOT to match the shell command in hooks/hooks.json. If a host
 * leaves the token unexpanded (the value still contains "${"), skip that value
 * and try the next one, then fall back to the path derived from __dirname.
 */
function resolvePluginRoot(env) {
  for (const value of [env.CLAUDE_PLUGIN_ROOT, env.PLUGIN_ROOT]) {
    if (value && !value.includes('${')) {
      return value;
    }
  }
  return '';
}

function main() {
  const pluginRoot = resolvePluginRoot(process.env);
  process.stdout.write(buildContext(readFirstFile(ruleCandidates(pluginRoot, __dirname))));
}

if (require.main === module) {
  main();
}

module.exports = {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  ruleCandidates,
  readFirstFile,
  resolvePluginRoot,
  stripFrontmatter,
};
