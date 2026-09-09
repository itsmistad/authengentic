#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  ruleCandidates,
  resolvePluginRoot,
  stripFrontmatter,
} = require('./authengentic-activate.js');

test('ruleCandidates tries the plugin root first, then paths from __dirname', () => {
  const list = ruleCandidates('/plug', '/repo/src/hooks');
  assert.equal(list[0], path.join('/plug', 'rules', 'core.md'));
  assert.equal(list[1], path.join('/repo', 'rules', 'core.md'));
  assert.ok(list.every((p) => p.endsWith(path.join('rules', 'core.md'))));
});

test('resolvePluginRoot reads PLUGIN_ROOT when Codex sets it', () => {
  assert.equal(resolvePluginRoot({ PLUGIN_ROOT: '/a/b' }), '/a/b');
});

test('resolvePluginRoot reads CLAUDE_PLUGIN_ROOT when Claude Code sets it', () => {
  assert.equal(resolvePluginRoot({ CLAUDE_PLUGIN_ROOT: '/c/d' }), '/c/d');
});

test('resolvePluginRoot prefers CLAUDE_PLUGIN_ROOT when both are set', () => {
  assert.equal(resolvePluginRoot({ CLAUDE_PLUGIN_ROOT: '/c/d', PLUGIN_ROOT: '/a/b' }), '/c/d');
});

test('resolvePluginRoot skips an unexpanded token and falls through to the next value', () => {
  assert.equal(resolvePluginRoot({ CLAUDE_PLUGIN_ROOT: '${CLAUDE_PLUGIN_ROOT}', PLUGIN_ROOT: '/a/b' }), '/a/b');
  assert.equal(resolvePluginRoot({ CLAUDE_PLUGIN_ROOT: '${CLAUDE_PLUGIN_ROOT}' }), '');
  assert.equal(resolvePluginRoot({}), '');
});

test('buildContext returns the fallback when promptText is empty', () => {
  assert.equal(buildContext(''), FALLBACK_CONTEXT);
});

test('stripFrontmatter removes a leading YAML block', () => {
  const input = '---\nname: authengentic\nversion: "1.0.0"\n---\nBody text.\n';
  assert.equal(stripFrontmatter(input), 'Body text.\n');
});

test('stripFrontmatter leaves text with no frontmatter untouched', () => {
  const input = 'Body text with no frontmatter.\n';
  assert.equal(stripFrontmatter(input), input);
});

test('buildContext includes the header and the stripped body', () => {
  const input = '---\nname: authengentic\n---\nWrite plainly.';
  const out = buildContext(input);
  assert.match(out, /AUTHENGENTIC SKILL ACTIVE AUTOMATICALLY/);
  assert.match(out, /Write plainly\./);
  assert.doesNotMatch(out, /^---/);
});

test('buildContext falls back when the payload exceeds MAX_CHARS', () => {
  const huge = '---\nname: authengentic\n---\n' + 'x'.repeat(MAX_CHARS + 500);
  assert.equal(buildContext(huge), FALLBACK_CONTEXT);
});

test('MAX_CHARS stays under the Claude Code 10,000-character hook cap', () => {
  assert.ok(MAX_CHARS < 10000);
});

test('FALLBACK_CONTEXT never mentions banning contractions (contradiction 1)', () => {
  assert.doesNotMatch(FALLBACK_CONTEXT.toLowerCase(), /no contractions|ban contractions/);
});
