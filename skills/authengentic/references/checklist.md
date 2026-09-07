# Verification checklist

Run this pass on every draft before you deliver it. The checks are ordered from mechanical to judgment. This is the full audit that the `review` operation runs, and the self-check in SKILL.md is its short form.

## Mechanical checks (searchable)

Search the draft for each pattern. Every hit outside code blocks and quoted text is a violation. All of these are fix-on-first-hit, except the dash row, which counts by cluster ("Where authengentic differs from its sources", item 3).

| Search for | Violation | Fix |
|---|---|---|
| `has been`, `have been`, `had been` | Present/past perfect (Rule 3.4) | Simple past or simple present. |
| `has` / `have` + past participle | Present perfect (Rule 3.4) | Simple past. |
| `should`, `would`, `may`, `might`, `could`, `shall` | Unapproved modal (Rule 3.2, see the modal ladder in SKILL.md) | `can`, `will`, or `must`. A recommendation becomes a fact or is deleted. |
| `is being`, `are being`, `was being` | Progressive passive (Rules 3.4, 3.5) | Active, simple tense. |
| `, making`, `, allowing`, `, enabling`, `, ensuring`, `, highlighting`, `, reflecting` | "-ing" clause as verb (Rule 3.5) | New sentence with a real subject, or delete the clause. |
| `felt`, `seemed`, `realized`, `noticed`, `knew`, `watched as` | Filter word (Rule 3.8) | Render the reaction or judgment directly. State the thing. |
| `;` | Semicolon (Rule 8.1) | Two sentences. |
| `—`, `–`, or spaced `-` / `--` between two statements | Dash cluster (Section 8 dash rule; "Where authengentic differs from its sources", item 3). A cluster is 2 or more per sentence, or 3 or more per paragraph. A lone, correctly-placed dash is not a violation, and "fixing" one is itself an over-correction tell. Never count: a range (`5–10`), a CLI flag (`--force`), a list marker. | For a cluster: name the relation ("because", "but", "for example"), or write two sentences. For a lone dash: leave it. |
| `"..."`, `'...'` (curly quotes: `“ ” ‘ ’`) | Curly quote (Rule 8.8) | Straight quotes (`"` and `'`). Exception: the exact characters are the subject under discussion. |
| A heading in Title Case | Title-case heading (Rule 8.9; "Where authengentic differs from its sources", item 2) | Rewrite to sentence case. Capitalize only the first word and proper nouns. No venue or mode exception. |
| 2 or more consecutive sentences that open with the same word | Consecutive same-start (Rule 9.5) | Merge the sentences, move the new fact into the subject, or open with the action. |
| A 2nd or later paragraph-initial `Additionally`, `Furthermore`, `Moreover`, `In addition`, `What's more`, `Notably` | Transition overuse (Rule 9.6) | Delete the opener and let the period carry the connection. Keep one only for a contrast or concession the reader would otherwise miss. |
| `e.g.`, `i.e.`, `etc.` | Latin abbreviation (GR-6) | "for example", "that is", name the items. |
| `simply`, `easily`, `seamlessly`, `robust` | Filler, no fact (Rule 1.15; Signs of AI writing) | Delete, or give the measurable property. |
| `delve`, `pivotal`, `crucial`, `leverage`, `showcase`, `foster` | LLM-tell words (`references/word-swaps.md`) | Use the listed replacement, or delete. |
| ` if `, ` when ` (mid-sentence) | Trailing condition (Rule 5.4) | Move the condition to the start of the sentence, add a comma. |
| `however`, `therefore`, `since` (= because), `now` | Word choice (SKILL.md); recurring errors (`references/strict-vocabulary.md`) | but / as a result / because / at this time (better, delete). |
| `need to`, `have to` | Recurring errors (`references/strict-vocabulary.md`) | Imperative in procedures; "it is necessary to" in descriptive text. |
| `perform`, `insert`, `reach`, `avoid`, `repeat`, `acceptable` | Recurring errors (`references/strict-vocabulary.md`) | do / put / get to / prevent / do … again / permitted. |
| `the example below`, `the section above` | "below" and "above" as adverbs are not approved | Name the target, or write "…that follows". |
| ` is complete`, ` are complete` | "complete" as an adjective is not approved | completed (adjective), or full / all. |

## Countable checks

1. **Sentence length.** Count words in each sentence. Procedural limit: 20. Descriptive limit: 25. Notes: 25.
   Backticked commands, numbers with units, and identifiers count as one word each (Rule 8.6).
   In a vertical list, the lead-in colon ends a sentence and each item that follows counts as a new sentence with its own budget (Rule 8.4).
2. **Sentence-length variety.** In each paragraph, scan for a run of three or more sentences of about the same length. Break it by moving words, not by adding them (Rule 4.1).
3. **Paragraph size.** Maximum six sentences per paragraph (Rule 6.6).
4. **Multi-word nouns.** Any noun chain over three words → break it with prepositions (Rule 2.1).
5. **Instructions per sentence.** One, unless the actions are simultaneous (Rule 5.2).
6. **List mechanics.** Colon on the lead-in. Each item starts with an uppercase letter. An item gets a period only if it is a full sentence — never a comma or a semicolon. The last item gets a period. No nested lists. Instructions and facts never in the same list (Rule 4.3). Every item in the same grammatical form (Rule 10.2).

## Judgment checks

7. **Classification.** Is each passage cleanly procedural or descriptive? Procedures in imperative, descriptions never in imperative.
8. **Voice.** Any passive sentence: is the agent truly unknown, and is the passage descriptive? Otherwise make it active (Rule 3.6). For an unknown agent, prefer "you" (the reader) or "we" (your team) over the passive.
9. **Condition placement.** Every "if/when" stands before its command, with a comma (Rule 5.4).
10. **Synonym rotation.** One term per concept across the whole document (Rules 1.11, 9.4). Scan for check/verify/confirm, config/settings, run/execute. Do not expand an abbreviation a second time.
11. **Warnings.** Command or condition first, risk second (Rules 7.2, 7.3). If a passage risks both injury and damage, use WARNING (Rule 7.1).
12. **Limits with actions.** A result or limit comes directly after its action in the work step, not in a note (Rules 5.2, 5.5).
13. **Notes test.** Delete all notes, then read the procedure. The reader must still be able to do it correctly (Rule 5.5).
14. **Completeness and contractions.** Articles present, "that" present after "make sure", no telegraph style (Rule 4.2). Then read the draft back: are there contractions where a person would use one? A draft with none reads machine-written. Add them (Rule 4.2, "Where authengentic differs from its sources", item 1). Never contract a banned modal.
15. **Plain words.** Each technical term has a definition at its first use where the reader needs it (Rule 1.2). Common words replaced jargon where a common word exists.
16. **Reader named?** Is there a one-phrase intended reader for this artifact (Rule 10.1)? Read the draft as that person. Would they stop to infer an undefined term? Is there a one-sentence map at the top of any multi-paragraph argument?
17. **Stance and claims.** Does the main verb match the evidence (Rule 10.5)? Where the document exists to reach a verdict, does it reach one: a review with a recommendation, a comparison with a pick, a postmortem with an admitted mistake? No fabricated source, citation, or specific; no "studies show", no hedged gap-fill; unverified claims marked `[UNVERIFIED]` (Rule 10.6).
18. **Middle of the document.** For anything over three sections, run the outline test (Rule 6.7): extract the first sentence of every paragraph. If they form a clean standalone summary, the structure is machine-shaped. Then check the middle third (Rule 10.7): it carries one finding the opening does not telegraph, and the texture varies between sections.
19. **Read-aloud test.** Read every rewritten sentence aloud. Grammatically correct but unsayable is its own defect. If nobody would say it, and nobody would write it in an email, redo it in speech-shaped syntax.
20. **Strict mode only.** Run the two tables in `references/strict-vocabulary.md` against the draft.
21. **Untouchables intact.** Code, identifiers, quoted errors, UI labels, proper nouns, numbers with units, and quoted material are unchanged. Do not "fix" a lone clean dash, and do not inject errors to look human.

## When reporting violations (review operation)

For each violation give: the rule number, the offending text, and a compliant rewrite. Cite only rule numbers that appear in SKILL.md.

End the report with this statement, one time per conversation, when the user asked for STE compliance: "No tool can guarantee ASD-STE100 compliance. Final approval rests with the writer. The official standard is a free download at asd-ste100.org."
