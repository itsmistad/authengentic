/**
 * Smoke tests for the authengentic MCP server.
 *
 * Spawns the stdio server, drives it over JSON-RPC, and checks that the linter
 * tool separates a slop fixture from a clean one. Reuses the fixture text from
 * evals/authengentic_lint.py so the two stay in step.
 *
 * Run: npm test  (from the mcp/ directory). The pretest hook copies the
 * canonical linter into linter/ first, so the server never tests a stale copy.
 */

import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import assert from "node:assert/strict";

const HERE = dirname(fileURLToPath(import.meta.url));
const SERVER = join(HERE, "..", "server", "index.js");

const SLOP =
  "Leveraging our robust retry mechanism, failed uploads are automatically " +
  "reattempted, ensuring data integrity is maintained. You should verify your " +
  "credentials; it has been checked already.";
const CLEAN =
  "The system retries a failed upload automatically. This process keeps the " +
  "data correct. If failures continue, contact support.";

/**
 * Start the server, run one tools/call, return the parsed result, then stop it.
 */
function callLint(text, type) {
  return new Promise((resolve, reject) => {
    const proc = spawn("node", [SERVER], { stdio: ["pipe", "pipe", "pipe"] });
    let buffer = "";
    const timer = setTimeout(() => {
      proc.kill();
      reject(new Error("timed out"));
    }, 5000);

    proc.stdout.on("data", (chunk) => {
      buffer += chunk;
      for (const line of buffer.split("\n")) {
        if (!line.trim()) continue;
        let message;
        try {
          message = JSON.parse(line);
        } catch {
          continue;
        }
        if (message.id === 3) {
          clearTimeout(timer);
          proc.kill();
          resolve(message.result);
        }
      }
    });
    proc.on("error", reject);

    const send = (obj) => proc.stdin.write(JSON.stringify(obj) + "\n");
    send({
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "test", version: "0" } },
    });
    send({ jsonrpc: "2.0", id: 2, method: "tools/list" });
    send({
      jsonrpc: "2.0",
      id: 3,
      method: "tools/call",
      params: { name: "authengentic_lint", arguments: { text, type } },
    });
  });
}

function reportFrom(result) {
  const jsonBlock = result.content.find((part) => part.text.startsWith("```json"));
  return JSON.parse(jsonBlock.text.replace(/```json\n|\n```/g, ""));
}

test("flags a slop fixture", async () => {
  const result = await callLint(SLOP, "descriptive");
  const report = reportFrom(result);
  assert.ok(report.violations_total >= 3, JSON.stringify(report.violations));
  assert.ok(report.violations.banned_modal >= 1);
  assert.ok(report.violations.semicolon >= 1);
});

test("passes a clean fixture", async () => {
  const result = await callLint(CLEAN, "descriptive");
  const report = reportFrom(result);
  assert.equal(report.violations_total, 0, JSON.stringify(report.violations));
});

test("rejects empty text", async () => {
  const result = await callLint("   ", "descriptive");
  assert.equal(result.isError, true);
});

test("verdict applies the ladder: a banned modal is fix-now", async () => {
  const result = await callLint("You should restart the service now.", "descriptive");
  const verdict = result.content[0].text;
  assert.match(verdict, /fix-now violation/);
  assert.match(verdict, /banned_modal 1/);
  assert.doesNotMatch(verdict, /Signals to weigh/);
});

test("verdict separates a graduated signal from a fix-now hit", async () => {
  /* A long sentence (over the 25-word descriptive limit) with one slop word. */
  const text =
    "This is a deliberately long descriptive sentence that runs well past the " +
    "twenty five word limit so the linter has to flag it as a robust example here.";
  const result = await callLint(text, "descriptive");
  const verdict = result.content[0].text;
  assert.match(verdict, /fix-now violation/);
  assert.match(verdict, /slop_word 1/);
  assert.match(verdict, /Signals to weigh: sentence_over_limit 1/);
});

test("verdict reports a clean text", async () => {
  const result = await callLint("The service restarts automatically after a crash.", "descriptive");
  assert.match(result.content[0].text, /^Clean\. 0 violations/);
  assert.match(result.content[0].text, /No second lint call needed/);
});

test("a Markdown heading does not merge with the section body", async () => {
  /* Both body sentences are short and clean. Only a heading+body merge would
   * push a unit over the limit or read as a trailing condition. */
  const text =
    "## How to roll out the change to every region\n\n" +
    "Apply the manifest to one region first and watch the error rate for ten minutes.\n\n" +
    "## Roll back the change if the error rate climbs\n\n" +
    "Delete the new manifest and re-apply the previous one from the archive folder.";
  const result = await callLint(text, "procedural");
  const report = reportFrom(result);
  assert.equal(report.violations_total, 0, JSON.stringify(report.violations));
  assert.match(result.content[0].text, /^Clean\. 0 violations/);
});
