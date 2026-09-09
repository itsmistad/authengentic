#!/usr/bin/env node
/*
 * Compose every rule surface from the single source rules/core.md.
 *
 * Right now one surface is generated: output-styles/authengentic.md. The
 * SessionStart hook (src/hooks/authengentic-activate.js) reads rules/core.md
 * directly, so it needs no generation. skills/authengentic/SKILL.md is the
 * deep catalog and stays hand-maintained.
 *
 * Usage:
 *   node scripts/build-rules.mjs            write the generated files
 *   node scripts/build-rules.mjs --check    exit 1 if a generated file is stale
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, relative } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CORE = join(ROOT, 'rules', 'core.md');

const OUTPUT_STYLE_FRONTMATTER = `---
name: authengentic
description: Write all non-fiction prose so it reads as written by a person, in the spirit of ASD-STE100 Simplified Technical English
keep-coding-instructions: true
---
`;

/*
 * The lint hook skips a file that carries this marker in its first 1000
 * characters. A rule surface must name the banned words to teach them, so
 * a zero-baseline lint of it is always a false positive.
 */
const GENERATED_NOTICE = [
  '<!-- authengentic-lint: ignore -->',
  '<!-- Generated from rules/core.md by scripts/build-rules.mjs. Do not edit the rules here. -->',
].join('\n');

function coreText() {
  return readFileSync(CORE, 'utf8').trim();
}

function outputStyle() {
  return `${OUTPUT_STYLE_FRONTMATTER}\n${GENERATED_NOTICE}\n\n${coreText()}\n`;
}

const TARGETS = [
  { path: join(ROOT, 'output-styles', 'authengentic.md'), render: outputStyle },
];

const check = process.argv.includes('--check');
let stale = 0;

for (const target of TARGETS) {
  const want = target.render();
  let have = '';
  try {
    have = readFileSync(target.path, 'utf8');
  } catch {
    have = '';
  }
  const name = relative(ROOT, target.path);
  if (want === have) {
    console.log(`ok    ${name}`);
    continue;
  }
  if (check) {
    console.error(`stale ${name} (run: node scripts/build-rules.mjs)`);
    stale += 1;
    continue;
  }
  writeFileSync(target.path, want);
  console.log(`wrote ${name}`);
}

process.exit(stale > 0 ? 1 : 0);
