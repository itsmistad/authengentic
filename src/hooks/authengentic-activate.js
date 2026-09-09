#!/usr/bin/env node

const fs = require('node:fs');
const os = require('node:os');
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

/*
 * The learning bucket. learn.py writes digest.md and learned.json here.
 * Honor AUTHENGENTIC_CONFIG_DIR first (tests set it), then CLAUDE_CONFIG_DIR,
 * then ~/.claude. This must match src/hooks/learn.py.
 */
function bucketFile(env, name) {
  const base = env.AUTHENGENTIC_CONFIG_DIR || env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
  return path.join(base, 'authengentic', name);
}

function digestPath(env) {
  return bucketFile(env, 'digest.md');
}

function readDigest(env) {
  try {
    return fs.readFileSync(digestPath(env), 'utf8').trim();
  } catch (error) {
    return '';
  }
}

const LEARNED_LABELS = {
  slop: 'Dead words to delete',
  openers: 'Filler openers to avoid',
  closers: 'Filler closers to avoid',
};

/*
 * Render learned.json as a rule extension the model reads at session start,
 * in the same shape as the core lists. The /authengentic-learn skill writes
 * learned.json. Read it fresh here so a promotion shows on the next session
 * with no build step.
 */
function readLearnedBlock(env) {
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(bucketFile(env, 'learned.json'), 'utf8'));
  } catch (error) {
    return '';
  }
  if (!raw || typeof raw !== 'object') {
    return '';
  }
  const lines = [];
  for (const key of ['slop', 'openers', 'closers']) {
    const terms = Array.isArray(raw[key])
      ? raw[key].filter((term) => typeof term === 'string' && term.trim())
      : [];
    if (terms.length) {
      lines.push(`- ${LEARNED_LABELS[key]}: ${terms.join(', ')}`);
    }
  }
  if (!lines.length) {
    return '';
  }
  return ['LEARNED IN THIS ENVIRONMENT. Treat these like the built-in lists above.', '', ...lines].join('\n');
}

function buildContext(promptText, learnedText, digestText) {
  if (!promptText) {
    return FALLBACK_CONTEXT;
  }
  const rules = HEADER + stripFrontmatter(promptText).trim();
  const learned = (learnedText || '').trim();
  const digest = (digestText || '').trim();
  const join = (parts) => parts.filter(Boolean).join('\n\n---\n\n');

  const full = join([rules, learned, digest]);
  if (full.length <= MAX_CHARS) {
    return full;
  }
  // Drop the digest first, then the learned block, then fall back.
  const noDigest = join([rules, learned]);
  if (noDigest.length <= MAX_CHARS) {
    process.stderr.write(`authengentic hook: payload is ${full.length} characters, over the ${MAX_CHARS} cap; sending the rules and the learned block without the digest\n`);
    return noDigest;
  }
  if (rules.length <= MAX_CHARS) {
    process.stderr.write(`authengentic hook: payload is ${noDigest.length} characters, over the ${MAX_CHARS} cap; sending the rules alone\n`);
    return rules;
  }
  process.stderr.write(`authengentic hook: payload is ${rules.length} characters, over the ${MAX_CHARS} cap; sending the fallback ruleset\n`);
  return FALLBACK_CONTEXT;
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
  const rules = readFirstFile(ruleCandidates(pluginRoot, __dirname));
  process.stdout.write(buildContext(rules, readLearnedBlock(process.env), readDigest(process.env)));
}

if (require.main === module) {
  main();
}

module.exports = {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  digestPath,
  readDigest,
  readLearnedBlock,
  ruleCandidates,
  readFirstFile,
  resolvePluginRoot,
  stripFrontmatter,
};
