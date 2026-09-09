#!/usr/bin/env node
/**
 * authengentic MCP server
 *
 * Gives a host with no post-write hook (the Claude apps Chat tab, for example) a
 * one-call deterministic check against the authengentic ruleset, plus the review
 * and rewrite operations as user-invoked prompts.
 *
 * Transport: stdio. Package it with scripts/build-mcpb.sh, or register it by
 * hand in claude_desktop_config.json (see docs/desktop/mcp-install.md).
 *
 * The linter is the canonical evals/authengentic_lint.py, copied to
 * linter/authengentic_lint.py at pack time. This server shells out to python3
 * so there is one detector implementation, never two that drift.
 */

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  GetPromptRequestSchema,
  ListPromptsRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const LINTER = join(HERE, "..", "linter", "authengentic_lint.py");

/**
 * Pick a python interpreter. Claude Desktop bundles Node for a node server but
 * not Python, so the interpreter comes from the user's machine.
 */
function findPython() {
  const configured = process.env.AUTHENGENTIC_PYTHON;
  const candidates = configured ? [configured, "python3", "python"] : ["python3", "python"];
  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ["--version"], { encoding: "utf8" });
    if (probe.status === 0) {
      return candidate;
    }
  }
  return null;
}

const PYTHON = findPython();

/**
 * Run the linter over a piece of text and return its parsed JSON report.
 * Throws with a readable message when the environment cannot run it.
 */
function runLinter(text, type) {
  if (!PYTHON) {
    throw new Error(
      "python3 was not found on this machine. The authengentic linter needs it. " +
        "Install Python 3, then restart the host.",
    );
  }
  if (!existsSync(LINTER)) {
    throw new Error(
      `The bundled linter is missing at ${LINTER}. Rebuild the bundle with scripts/build-mcpb.sh.`,
    );
  }
  const result = spawnSync(
    PYTHON,
    [LINTER, "--type", type, "-"],
    { input: text, encoding: "utf8", maxBuffer: 8 * 1024 * 1024 },
  );
  /* The linter exits 1 when it counts violations and prints the report on
   * stdout either way. Only a missing stdout payload is a real failure. */
  if (!result.stdout) {
    throw new Error(
      `The linter did not return a report. stderr: ${result.stderr || "(none)"}`,
    );
  }
  return JSON.parse(result.stdout);
}

/**
 * The three checks that carry a graduated count rather than a pass or fail.
 *
 *   - sentence_over_limit: one sentence a word or two long is a nudge. Twelve
 *     over is a rewrite. The number is the signal.
 *   - em_dash: the linter reports this only for a real cluster (contradiction 3
 *     in SKILL.md), so a non-zero value still means "act". The count reflects
 *     total clustered dashes, not the number of clusters, so weigh the size.
 *   - consecutive_same_start: the linter cannot tell deliberate anaphora from an
 *     LLM tic. A human reads these.
 */
const WEIGH_KEYS = new Set([
  "sentence_over_limit",
  "em_dash",
  "consecutive_same_start",
]);

/**
 * formatVerdict(report) -> string
 *
 * The short line the model reads first. It applies the authengentic ladder from
 * the four contradiction resolutions in SKILL.md: every check except the three
 * in WEIGH_KEYS is fix-on-first-hit, so one banned modal, one semicolon, one
 * perfect tense, one slop word, or one curly quote is a defect to remove now,
 * not a number to tally. The three weigh keys are graduated signals to judge.
 */
function formatVerdict(report) {
  const entries = Object.entries(report.violations);
  const fixNow = entries.filter(([key, count]) => count > 0 && !WEIGH_KEYS.has(key));
  const weigh = entries.filter(([key, count]) => count > 0 && WEIGH_KEYS.has(key));

  if (fixNow.length === 0 && weigh.length === 0) {
    return (
      `Clean. 0 violations across ${report.words} words. ` +
      "Do the by-eye self-check, then deliver. No second lint call needed."
    );
  }

  const parts = [];

  if (fixNow.length === 0) {
    parts.push("No fix-now violations.");
  } else {
    const total = fixNow.reduce((sum, [, count]) => sum + count, 0);
    const list = fixNow.map(([key, count]) => `${key} ${count}`).join(", ");
    parts.push(
      `${total} fix-now violation${total === 1 ? "" : "s"} (${list}). ` +
        "Each is a defect to remove now, not a number to tally.",
    );
  }

  if (weigh.length > 0) {
    const list = weigh.map(([key, count]) => `${key} ${count}`).join(", ");
    parts.push(
      `Signals to weigh: ${list}. Judge the size. A small count on one sentence ` +
        "is a nudge. A large count is a rewrite.",
    );
  }

  parts.push(
    "Fix every instance of each in one edit pass, then call this once more. " +
      "The linter is a regex floor, not a compliance verdict.",
  );
  return parts.join(" ");
}

const PROMPTS = {
  "authengentic-review": {
    description:
      "Diagnose a piece of non-fiction text against the authengentic ruleset. Report only. Change nothing.",
    arguments: [
      { name: "text", description: "The text to review.", required: true },
    ],
    render: (args) =>
      "Review the text below against the authengentic ruleset. This is the review " +
      "operation: name every violation with its rule, and propose a fix for each. " +
      "Do not deliver a rewritten version.\n\n" +
      "Run the authengentic_lint tool on the text first, then read every hit by eye " +
      "for the rules a regex cannot catch: altitude, parallelism, end weight, " +
      "evidence-matched claims, and unsayable syntax.\n\n" +
      `--- TEXT ---\n${args.text ?? ""}`,
  },
  "authengentic-rewrite": {
    description:
      "Rewrite a piece of non-fiction text in place so it follows the authengentic ruleset, keeping structure and voice.",
    arguments: [
      { name: "text", description: "The text to rewrite.", required: true },
      {
        name: "type",
        description: '"procedural" for steps, "descriptive" for explanation. Default: descriptive.',
        required: false,
      },
    ],
    render: (args) =>
      "Rewrite the text below with the authengentic refactor operation: a minimal " +
      "in-place revision that keeps the structure and the voice. Classify it as " +
      `${args.type || "descriptive"} first. Apply the plain-English rules, then run ` +
      "the authengentic_lint tool on your draft and fix what it reports before you " +
      "return it. Keep code, identifiers, commands, file paths, and quoted errors " +
      "exact.\n\n" +
      `--- TEXT ---\n${args.text ?? ""}`,
  },
};

const server = new Server(
  { name: "authengentic", version: "1.2.5" },
  { capabilities: { tools: {}, prompts: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "authengentic_lint",
      description:
        "Count deterministic authengentic violations in a piece of non-fiction text: banned modals, " +
        "perfect tense, -ing clauses, semicolons, dash clusters, slop words, title-case headings, " +
        "curly quotes, over-limit sentences, repeated sentence openers, and more. Returns the JSON " +
        "report and a short verdict. Call it once on the whole text, not section by section; the " +
        "verdict says whether a second call is needed. A regex pass, not a grammar parser or a " +
        "compliance verdict.",
      inputSchema: {
        type: "object",
        properties: {
          text: { type: "string", description: "The text to check." },
          type: {
            type: "string",
            enum: ["procedural", "descriptive"],
            description:
              'Sentence-length limit to apply: "procedural" (20 words) for steps, "descriptive" (25) for explanation.',
            default: "descriptive",
          },
        },
        required: ["text"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "authengentic_lint") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }
  const args = request.params.arguments ?? {};
  const text = typeof args.text === "string" ? args.text : "";
  const type = args.type === "procedural" ? "procedural" : "descriptive";
  if (!text.trim()) {
    return {
      isError: true,
      content: [{ type: "text", text: "No text was passed to authengentic_lint." }],
    };
  }
  try {
    const report = runLinter(text, type);
    return {
      content: [
        { type: "text", text: formatVerdict(report) },
        { type: "text", text: "```json\n" + JSON.stringify(report, null, 2) + "\n```" },
      ],
    };
  } catch (error) {
    return {
      isError: true,
      content: [{ type: "text", text: String(error.message ?? error) }],
    };
  }
});

server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: Object.entries(PROMPTS).map(([name, prompt]) => ({
    name,
    description: prompt.description,
    arguments: prompt.arguments,
  })),
}));

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const prompt = PROMPTS[request.params.name];
  if (!prompt) {
    throw new Error(`Unknown prompt: ${request.params.name}`);
  }
  return {
    description: prompt.description,
    messages: [
      {
        role: "user",
        content: { type: "text", text: prompt.render(request.params.arguments ?? {}) },
      },
    ],
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  /* stderr is safe for logs. stdout carries the JSON-RPC stream. */
  process.stderr.write(
    `authengentic MCP server ready. python: ${PYTHON ?? "NOT FOUND"}. linter: ${LINTER}\n`,
  );
}

main().catch((error) => {
  process.stderr.write(`authengentic MCP server failed to start: ${error}\n`);
  process.exit(1);
});
