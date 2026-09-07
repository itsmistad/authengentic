# Per-model prose fingerprints

**authengentic is non-fiction only; sepia's fiction narrative-layer tables are not included here.** The source file in sepia carries two layers: a *narrative layer* measured on fiction, and a *prose layer* taken from each vendor's own prompting guidance. Only the prose layer is in scope for this skill, so only the prose layer is ported. The DeepSeek and Kimi entries are dropped entirely: the source states "Prose layer: none" for both, and their only content was narrative.

## What these tables are

Each row records what a model's own vendor says its current release does at the sentence level, taken from that vendor's published prompting documentation. This is vendor guidance, not anyone's own testing. Nothing here infers a model from reading its prose.

Each table is tagged with the exact release the vendor page names. A table is **operative** for a role whose model is that release, and it is carried as a **prior** for any other release in the same family. A role with a matching release has that table operative and the family's other tables as priors. When a vendor scopes a statement to a whole series (Gemini 3) and tags the table with that series, any release inside the series matches.

### Author model and executor model

Resolve two identities before you operate, each as a family plus a release, or unknown:

- **The author model** produced the text you were given. Take it from the user or from metadata. On a `write` operation there is no author model.
- **The executor model** is the one you run on now. A direct statement of your own model outranks attribution strings such as commit trailers or signatures.

Resolve each role on its own; never compare the two. The author's prose layer acts on the text you were handed. The executor's prose layer acts on the text you produce. An unknown role, or a family with no table, loads nothing and reports `none`. Report both identities and each role's prose-layer status (`operative`, `prior`, or `none`) in every `review`.

A family alias in this file: V = vendor guidance.

## Claude

### Prose layer (V; Claude Fable 5.1 and Claude Mythos 5.1, `ANTHROPIC-FABLE-5-1-PROMPTING`)

| Vendor-stated default | Handling |
|---|---|
| Mannered prose: metaphor and flourish where a literal phrase exists | Operative for a role on Claude Fable 5.1 or Claude Mythos 5.1, a prior for any other or unknown Claude release. As the author's layer: hunt metaphor standing in for an available literal phrase in the given text. As the executor's layer: apply the same hunt to what you write. This runs the same check as Rule 1.15 (performance verbs, grandeur nouns) and Rule 2.3 (abstract-noun wrappers). |
| Denser than Fable 5: longer sentences, fewer paragraph breaks | Split the run-ons (Rule 4.1). Break a paragraph where the topic turns (Rules 6.4, 6.5). |
| Less bold, fewer headers and lists than earlier Claude | Sparse formatting is not evidence of a human author. Do not add anti-formatting rules to compensate (see Untouchables). |

The vendor's own instruction, verbatim:

```text
Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.
```

### Prose layer (V; Claude Fable 5 and Claude Mythos 5, `ANTHROPIC-FABLE-5-PROMPTING`)

| Vendor-stated default | Handling |
|---|---|
| Un-steered, elaborates past the task: "surveying options it won't pursue, explaining root causes at length, producing heavily-structured PR descriptions, or writing comments that narrate what the next line does" | Operative for a role on Claude Fable 5 or Claude Mythos 5, a prior otherwise. Hunt option surveys, root-cause essays, and structure that outweighs the content (Signs of AI writing, "Restating summaries" and "Formatting habits"; Rule 6.7 outline test). Apply to the text you write. |
| In long agentic sessions, "dense arrow-chain shorthand, deep implementation detail, references to thinking the user never saw, or overly technical phrasing" | Hunt arrow chains, hyphen-stacked compounds, and labels the reader never saw defined. Expand them into sentences (self-check 8, the read-aloud test). |

The vendor's brevity instruction, verbatim:

```text
Lead with the outcome. Your first sentence after finishing should answer "what happened" or "what did you find": the thing the user would ask for if they said "just give me the TLDR." Supporting detail and reasoning come after. Being readable and being concise are different things, and readability matters more.

The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon.
```

### Prose layer (V; Claude Opus 5, `ANTHROPIC-OPUS-5-PROMPTING`)

| Vendor-stated default | Handling |
|---|---|
| "Default user-facing responses run longer than prior Opus models'"; effort changes thinking volume, not visible length | Operative for a role on Claude Opus 5, a prior otherwise. Run the density check (Calibration principle 2, "Select, do not accumulate"; Signs of AI writing) at the role's operative or prior strength. |
| Written files "are often longer than on prior models": filler sections, redundant summaries, boilerplate | Hunt the fractal-summary shape and sections that exist for completeness (Rule 6.7; Signs of AI writing, "Restating summaries"). Vendor instruction: "Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate." |
| "Narrates readily during agentic work": announces what it is about to do; narrates corrections to earlier statements more than prior models | In produced text, cut announcements of intent and corrections that change nothing for the reader. |

The vendor's conciseness instruction, verbatim:

```text
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and spend most of the response on the main answer. When asked to explain something, give a high-level summary unless an in-depth explanation is specifically requested.
```

### Prose layer (V; Claude Opus 4.8, `ANTHROPIC-OPUS-4-8-PROMPTING`)

| Vendor-stated default | Handling |
|---|---|
| "A direct, opinionated style with minimal validation-forward phrasing and sparing emoji use" | Absence of validation openers and emoji is this release's default, not evidence of a human. Stance (Rule 10.5) is usually present; look instead at density and specificity. |
| Response length "calibrated to how complex it judges the task to be" | Length varies with the task by default; uniform length across tasks would be the tell, not variation. |

**Consulted with no prose-layer statement (2026-09-03):** the Claude Sonnet 5 page says only that "prose style on long-form writing may shift"; Claude Opus 4.7, Opus 4.6, and Sonnet 4.6 have no model-specific prompting page. Those releases have no operative row; the Claude tables above apply to them as priors.

## GPT

### Prose layer (V; GPT-5.6, `OPENAI-GPT-5-6-PROMPTING`)

| Vendor-stated default | Handling |
|---|---|
| More concise by default than GPT-5.5; brevity instructions can make answers too brief | Density fails in both directions. A short answer that dropped a required caveat or the next action is a defect (Rule 10.5; Calibration principle 4). |
| The vendor's recommended trims name the expected residue: introductions, repetition, generic reassurance, optional background, generic praise, sign-offs | Already hunted by the Signs of AI writing directions ("Inflated significance", "Restating summaries", "Collaborative leftovers"). Run them on the text at the role's operative or prior strength. |
| Editing tasks drift: the vendor's preservation snippet warns against "adding new claims, sections, or a more promotional tone" | Vendor-implied, not stated as a defect. Enforce the register-drift clause of Calibration principle 4 ("Deletion beats addition"): the only legitimate additive fix is real specificity. |

## Gemini

### Prose layer (V; Gemini 3 series, `GOOGLE-GEMINI-3-DEV-GUIDE`)

The vendor scopes its statements to the series (Gemini 3 Flash through Gemini 3.8 Flash), so any Gemini 3.x release matches this table.

| Vendor-stated default | Handling |
|---|---|
| "By default, Gemini 3 is less verbose and prefers providing direct, efficient answers"; a conversational or "chatty" persona appears only when explicitly prompted | Terse and unadorned is this series' default, so brevity is not evidence of a human here. Check density in the other direction (Rule 10.5): required caveats and next steps dropped for efficiency. |
