# Domain — error messages and CLI output

Covers error strings, stack-trace preambles, exit-code explanations, CLI warnings, and status lines. Mode: procedural. Run with `SKILL.md`. This is the highest-value target in the whole skill: an error message is a 2 a.m. instruction to a stressed reader who cannot ask a follow-up question.

## Human baseline

Three parts, in order: state what happened in the past simple, state the cause if it is known, give the command or the condition that fixes it. Nothing else. The reader wants to be unblocked, not reassured. A good error names the failing component, the value that was wrong, and the next action.

> **Before:** Oops! Something went wrong while attempting to establish a connection. Please ensure your credentials are properly configured and try again.
>
> **After:** Connection to the database failed. The password for user `app` was not correct. Set `DB_PASSWORD` and connect again.

## AI tells in this domain

| Tell | Fix |
|---|---|
| Vague failure ("Oops! Something went wrong") with no cause or fix | Name the failure, the cause if known, the fix |
| Apology and reassurance filler: "we're sorry for the inconvenience", "don't worry" | Delete. The reader wants the next step, not sympathy |
| Present perfect that hides timing: "an error has occurred" | Past simple: "the request failed at 14:02" |
| Trailing condition: "try again if the problem persists after checking your settings" | Condition first: "if the retry also fails, check `~/.config/app/settings.toml`" |
| "Please ensure your credentials are properly configured" — abstract, no target | The exact variable, file, or flag: "set `DB_PASSWORD`" |
| One wall-of-text sentence covering cause and three possible fixes | One sentence per fact, one fix per line |

## Rules

1. **State what happened first**, in the past simple, naming the component that failed.
2. State the cause when it is known. When it is not, say "cause unknown" rather than guessing in prose.
3. Give the fix as a command or a condition the reader can act on, not a category of things to review.
4. One instruction per line. If there are two possible fixes, list two lines, most likely first.
5. No apology, no "please", no reassurance. The message ends at the fix.
6. Exit codes and log lines follow the same three parts: what failed, why, what to do.
