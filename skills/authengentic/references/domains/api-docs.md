# Domain — API reference and agent instructions

Covers endpoint reference docs, SDK method docs, configuration references, and instructions written for a reader who cannot ask questions: system prompts, `AGENTS.md`, and skill files. Mode: procedural. Run with `SKILL.md`. A reference entry and a system prompt are the same genre — a procedure executed by a reader with no way to request a clarification, which is the exact reader controlled English was designed for.

## Human baseline

One instruction per sentence, so each rule is independently quotable and hard to half-follow. One word, one meaning, so "check", "verify", and "validate" are not read as three different operations. Condition first ("If the build fails, stop"), because a trailing condition gets dropped. Every parameter, default, and return type stated, not left for the reader to infer from an example.

## AI tells in this domain

| Tell | Fix |
|---|---|
| "should" in a rule: "the token should be refreshed before expiry" | A model reads "should" as optional. Write "must", or delete the rule |
| Two or three instructions welded into one sentence | One instruction per sentence |
| Trailing condition: "call `/refresh` to get a new token if the current one has expired" | Condition first: "if the token has expired, call `/refresh`" |
| Synonym rotation across the page: "pass", "supply", "provide", "send" for the same act | Pick one verb for one action and keep it |
| Parameters shown only inside a sample payload | State each parameter, its type, whether it is required, and its default in a list or table |
| Return value described as "the result" or "a response object" | Name the type and the fields, and what an error returns |
| Prose walkthrough of a call sequence | One endpoint or step per line |

## Rules

1. **One endpoint or one behavior per line** where the material allows it. A reference is a lookup surface, not an essay.
2. Parameters and return types are stated, not implied: name, type, required or optional, default, units. An example is an addition to the spec, never the spec.
3. One instruction per sentence. One word, one meaning across the whole document.
4. Conditions go first. "If X, do Y", not "do Y when X".
5. No "should". Use "must" for a requirement, "can" for a capability, or cut the sentence.
6. Breaking changes are called out the way `release-notes.md` requires: named first, with the exact migration step — the renamed field, the new required header, the removed endpoint and its replacement.
7. Error responses are documented next to the success case: status code, body shape, and the condition that produces each one.
