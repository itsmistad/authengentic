# Signs of AI writing — the full catalog

The condensed version lives in SKILL.md's "Signs of AI writing" section. This file is the full
catalog for a `review` operation or a deep audit. Every entry names the tell, the words and phrases
to watch, why a language model produces it, and a before/after pair.

Sources: Wikipedia's "Signs of AI writing" (carried through humanizer); agent-style's rules — the
field-observed RULE-A, RULE-C, RULE-D, RULE-E, RULE-G, and RULE-H, plus canonical RULE-07 on
positive-form statements; and sepia's professional-pass checklist with its style-pass vocabulary,
syntax, and rhythm tables. Non-fiction scope only: fiction-specific tells (scene vocabulary,
narrative architecture) are left out.

**How the numbering maps to SKILL.md.** Entries #1 through #9 mirror, in order, the nine "Signs of AI
writing" directions in SKILL.md: inflated significance, negative parallelism, rule of three, vague
attribution, false ranges, restating summaries, editorializing asides, collaborative leftovers,
formatting habits. Entries #10 through #38 are the merged additions that those directions point at.
Several humanizer patterns fold into #1 through #9 rather than getting their own number, and the six
"phantom interlocutor" patterns are consolidated into #8.

**Enforcement.** Per "Where authengentic differs from its sources", item 4, every entry here is
fix-on-first-hit. The one exception in the whole ruleset is dashes, which are judged by cluster and
are covered in SKILL.md Section 8, not in this file. Do not add a dash entry here.

---

## #1 Inflated significance

**The direction:** state the fact, not how important it is.

**Watch for:** vital, crucial, pivotal, critical, essential; stands as a testament, a testament to,
plays a key role, marks a turning point, underscores its importance, reflects a broader, sets the
stage for, an enduring legacy, leaves an indelible mark; manufactured stakes ("in a world where",
"in today's fast-paced landscape", "now more than ever"); sales register (boasts, nestled, in the
heart of, breathtaking, renowned, must-visit, a rich cultural heritage, a diverse array); the stock
"Challenges and Legacy" or "Future Outlook" section bolted onto the end.

**Why it happens:** the model dresses an ordinary detail as a change, a legacy, or a promise because
that framing fits the widest range of subjects. The fact underneath is usually sound.

**Before:** The Statistical Institute of Catalonia was established in 1989, marking a pivotal moment
in the evolution of regional statistics and reflecting a broader movement to decentralize governance.
**After:** The Statistical Institute of Catalonia was established in 1989, part of a wider
decentralization of administrative functions in Spain.

Cross-ref: Rule 1.15 (inflation adjectives, grandeur nouns), Rule 2.3 (abstract-noun wrappers),
`references/word-swaps.md`. Send-off paragraphs get their own treatment at #31.

## #2 Negative parallelism

**The direction:** say what the thing is, not what it is not.

**Watch for:** not just X, it is Y; not merely X but Y; it's not X, it's Y; the reversed form "X
rather than Y"; the same contrast split over two sentences ("This does not mean X. It means Y."); a
clipped negative tail (", no guessing", ", not a hope"); "X, Not Y" as a heading.

**Why it happens:** the negative half names a claim nobody made, so the positive half sounds larger.
It adds weight without adding information. This reads as balanced and quotable, so the model reaches
for it in headings and openers.

**Before (heading):** Failure Is Committed at the First Token, Not the Last
**After (heading):** The first token commits the failure

**Before:** It's not merely a config change, it's a full rewrite of the export pipeline.
**After:** This release rewrites the CSV export pipeline. The previous version only patched the
newline crash.

Keep a contrast when the rejected alternative is specific and ruling it out tells the reader
something ("The bottleneck is disk I/O, not CPU"). The expanded treatment is at #22.

## #3 Rule of three

**The direction:** give the one fact, or the real list, or two items, or four.

**Watch for:** decorative triplets ("innovation, inspiration, and insights"); three parallel example
sentences where one would do; three short facts followed by a lesson; a forced "first, second,
third" where the content is two items or a flowing sentence.

**Why it happens:** the model has learned that a group of three feels complete, so it produces one
whether the meaning has three parts or not.

**Before:** The event features keynote sessions, panel discussions, and networking opportunities.
Attendees can expect innovation, inspiration, and industry insights.
**After:** The event has talks and panels, with time for informal networking between sessions.

Cross-ref: Rule 9.7 (recycled frames), #24 (bullet triads), sepia style-pass §2. Check that each
item carries a distinct idea. Keep three when the meaning needs three.

## #4 Vague attribution

**The direction:** name the source or drop the claim.

**Watch for:** studies show, research suggests, experts argue, observers have noted, critics say,
industry reports indicate, it is well known that, many believe; a person propped up by a list of
prestige outlets ("cited in The New York Times, BBC, Financial Times"); "an active social media
presence with over N followers" used as a credential.

**Why it happens:** an unnamed authority is the cheapest way to make a claim sound backed. The model
samples these transition phrases at the rate they appear in review articles, without the specific
citation a human writer has in mind.

**Before:** Experts believe the Haolai River plays a crucial role in the regional ecosystem.
**After:** Researchers and conservationists study the Haolai River for its unusual water chemistry.

Cross-ref: Rule 10.6 (never fabricate a source), #10 (fabricated citations), #23 (vague connection).
A missing citation alone is not a tell. Most writing is unsourced.

## #5 False ranges

**The direction:** give the numbers, or list the items.

**Watch for:** ranging from X to Y, from X all the way to Y, anywhere from X to Y, spanning X to Y,
where X and Y are not the two ends of a real scale ("workloads ranging from simple lookups to
complex analytics", "users from beginners to experts").

**Why it happens:** the "from A to B" frame signals breadth without the writer having to name what
sits between A and B, or confirm that A and B bound anything.

**Before:** The connector handles workloads ranging from simple key lookups to complex multi-table
analytical queries.
**After:** The connector runs single-key lookups and multi-table joins. It has no query planner, so
queries over four joins are slow.

If the two points really are the ends of a measured range, give the range as a number (`5–10`,
Rule 8.5). If they are just two examples, say "such as" and name a third.

## #6 Restating summaries

**The direction:** end when the content ends.

**Watch for:** In conclusion, In summary, Overall, Taken together, To sum up, The key takeaway is;
a closing sentence in a body paragraph that restates the paragraph in different words ("Thus, the
architecture suits our caching strategy"); generic forward-looking closers ("we will continue to
improve the platform"); the nested announce-then-state-then-recap shape at every heading level.

**Why it happens:** expository training corpora put "topic sentence, body, summary sentence" on every
paragraph. The closer signals "I am finishing this thought" and adds nothing.

**Before:** We trained on 50k query-passage pairs and evaluated on five benchmarks. The model reaches
0.79 recall@10 on the held-out set. Overall, these results show the method is effective.
**After:** We trained on 50k query-passage pairs and evaluated on five benchmarks. The model reaches
0.79 recall@10 on the held-out set.

Cross-ref: Rule 6.7 (outline test), agent-style RULE-E. A summary closer is correct for the final
paragraph of a long piece a reader will skim. Test: delete the closer. If the paragraph still makes
its point, the closer was noise. Heading echoes are #32. Announcing the next point is part of #8.

## #7 Editorializing asides

**The direction:** say it directly.

**Watch for:** It is important to note that, It's worth noting that, Interestingly, Notably, It
should be mentioned that, Importantly; a parenthetical that grades the fact it follows ("(a strong
result)"); "Here's the thing", "The truth is".

**Why it happens:** the aside performs the work of judgment without committing to one. It is filler
that sounds like emphasis.

**Before:** It is important to note that the cache expires after 60 seconds.
**After:** The cache expires after 60 seconds.

Cross-ref: Rule 1.15, `references/word-swaps.md` ("it is worth noting that" → delete). The forced
punchline and the false reveal are #21 and #20.

## #8 Collaborative leftovers and the phantom interlocutor

**The direction:** a colleague does not talk like a support desk, and does not argue with people who
are not in the room.

**Watch for, wrappers:** I hope this helps, Let me know if you need anything, Great question,
Certainly, Of course, You're absolutely right, Would you like me to, Want me to, Should I continue.
**Watch for, staged candor:** Honestly?, Look,, Here's the thing, Let's be honest, Real talk, as a
standalone opener before a routine claim.
**Watch for, announcing:** Let's dive in, Let's explore, Let's break this down, Here's what you need
to know, Without further ado, Now let's look at.
**Watch for, arguing with no one:** To be clear, Don't get me wrong, This is not to say, Some might
say X but, A tempting approach would be, One might be tempted to, You might think X but.

**Why it happens:** the text invents a conversation partner so it can perform a dialogue instead of
stating its content: someone to thank, to agree with, to reassure, to correct, to talk down from a
bad idea. These are six versions of one tell (humanizer's chatbot residue, over-agreeableness,
next-point announcements, fake-candid openers, answering unraised objections, and rejecting fake
alternatives). Treat them as one cluster.

**Before:** Great question! Let's dive into token rotation. A tempting approach would be to restart
the auth service on a cron job, but that would drop every active session. I hope this helps!
**After:** Session tokens rotate every 24 hours, in place. Clients refresh without a visible
interruption.

Cross-ref: SKILL.md "Your reply to the user". Keep an objection the text attributes and answers in
full, and keep an alternative a reader would actually weigh.

## #9 Formatting habits

**The direction:** formatting marks real structure, not decoration.

**Watch for:** bold on words that are not defined terms; every list item with a bold label and a
colon; emoji or arrows as bullets or section markers; a heading over a two-sentence section; a
horizontal rule between every section; sections of near-identical length; lists of exactly three
everywhere.

**Why it happens:** clean, uniform formatting reads as organized, so the model applies it to every
item regardless of whether the content is a genuine list.

**Before:**
> ## Overview
>
> This section gives an overview of the parser.
>
> - **Speed:** It is fast.
> - **Safety:** It rejects bad input.
**After:** The parser handles 40 MB/s and rejects malformed input instead of guessing at it.

The individual formatting tells have their own entries: bold text #25, bold mini-headings #26, title
case #27, emoji and rules #28, uniform section length #34. The absence of these is not evidence of a
human writer. Which formatting a model over-uses changes with each release (see
`references/model-fingerprints.md`).

---

## #10 Fabricated or handwavy citations (critical)

**Severity: critical.** This is agent-style RULE-H, given its own top-billed entry. An uncited claim
is unverifiable. A fabricated citation is worse, because it destroys reader trust permanently once
found.

**Watch for:** prior work shows, recent studies suggest, it is well known that, many researchers
believe, several studies have demonstrated; a plausible-looking "Author Year" reference that has not
been verified; "our pilot results look promising" with no numbers.

**Why it happens:** these phrases are transition filler in academic introductions, and the model
samples them without the specific attribution. Models also generate citations that match author,
year, and venue conventions but point to no real paper.

**Before:** Prior work has shown that late-interaction retrieval improves over lexical retrieval.
**After:** Khattab and Zaharia 2020 (ColBERT) report MS MARCO passage-ranking MRR@10 of 0.360 for
ColBERT against 0.187 for BM25-Anserini. `[UNVERIFIED: not checked against the paper this session.]`

Verify every citation before you write it. If you cannot verify it in this session, mark it
`[UNVERIFIED]` and say so in the reply. Where a number is missing, ask the user or leave a TODO.
Never fill it. Cross-ref: Rule 10.6.

## #11 Shallow "-ing" riders

**Watch for:** a trailing comma-`-ing` phrase that restates the main clause in loftier terms:
highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to,
fostering, encompassing, showcasing.

**Why it happens:** the rider makes a plain fact sound deeper. Attaching it to a named source does
not make its claim true.

**Before:** The scheduler retries a failed job three times, ensuring reliability and reflecting the
team's commitment to uptime.
**After:** The scheduler retries a failed job three times.

**Fix:** delete the clause, do not paraphrase it. Cross-ref: Rule 3.5.

## #12 Avoiding is, are, and has

**Watch for:** serves as, stands as, functions as, operates as, acts as, marks, represents; boasts,
features, offers, maintains, houses; the long verb where "is" or "has" carries the fact.

**Why it happens:** the performance verb makes a plain statement of fact sound like an achievement.

**Before:** Gallery 825 serves as the association's exhibition space and boasts over 3,000 square
feet.
**After:** Gallery 825 is the association's exhibition space. It has four rooms and about 3,000
square feet.

Cross-ref: Rule 1.15 (copula avoidance).

## #13 Stock vocabulary in clusters

**Watch for:** delve, underscore, foster, harness, navigate, resonate, elevate, embrace, transcend,
unravel, weave; tapestry, testament, landscape, realm, journey, beacon, nuance, myriad; intricate,
vibrant, palpable, profound, seamless, robust, transformative; additionally, moreover, crucial, key,
highlight, showcase, meticulous. The full map is in `references/word-swaps.md`.

**Why it happens:** models use these words far more often than people do, and in groups.

**Why it is one entry, not forty:** the *authorship* signal is density, not any single word. Three
or more from the list in a paragraph, or the same one twice on a page, is what points to a machine
(a lone technical "robust" can be correct on its own). "One entry" means one catalog entry to check,
not a licence to tally and wait: as a rule, each slop word is still fixed on the first hit (Rule
1.15, "Where authengentic differs from its sources" item 4). Cross-ref: the note at the end of the
false-positive whitelist.

**Before:** We harness state-of-the-art embeddings to unlock the full potential of a robust retrieval
pipeline, delving into the intricate interplay of recall and latency.
**After:** We use OpenAI text-embedding-3-large. Recall@10 rose 7 points over our previous model,
and median query latency held at 40 ms.

If a word carries no fact, delete it rather than swapping it. Cross-ref: Rule 1.15,
`references/word-swaps.md`.

## #14 Passive voice and dropped subjects

**Watch for:** "the results are preserved automatically", "no configuration file needed", "errors
are logged on restart", "it was decided that" — any sentence that hides who acts or drops the
subject.

**Why it happens:** token-by-token generation from a formal corpus over-produces the passive, which
reads as authoritative. For a postmortem or a bug report this is actively harmful, because "the
error was raised" leaves the caller unnamed.

**Before:** No configuration file needed. The results are preserved automatically.
**After:** You do not need a configuration file. The system saves the results for you.

**Fix:** repair an agentless passive with "you" (the reader) or "we" (your team). Cross-ref:
Rule 3.6.

## #15 Consecutive same-start sentences

**Watch for:** two or more sentences in a row opening with the same word. `The ... The ...`,
`This ... This ...`, `We ... We ...`, `It ... It ...` are the usual offenders. This covers
agent-style RULE-C and humanizer's repeated-openings pattern.

**Why it happens:** once an opener works, the next-token distribution for the following sentence
starts the same way, because the prefix has become likely given the topic.

**Before:** This release adds OAuth support. This release fixes a CSV export crash. This release
cuts startup time.
**After:** OAuth support lands in this release. The CSV export crash is fixed. Startup time drops
from 4.2s to 1.8s.

**Fix:** merge the sentences, move the new fact into the subject, or open with the action. The
surviving sentence may still start with "The". A deliberate rhetorical repetition ("She came. She
saw. She conquered.") is not this tell. Cross-ref: Rule 9.5.

## #16 Transition-word overuse

**Watch for:** a sentence-initial Additionally, Furthermore, Moreover, In addition, What's more, or
Notably, used more than once in a paragraph, or where the connection is already obvious from the
content. This is agent-style RULE-D.

**Why it happens:** formal essay corpora over-represent explicit transitions. The result is the
sentence-initial cadence that readers recognize as machine-paced.

**Before:** We cache embeddings for 24 hours. Additionally, we invalidate on source-document update.
Furthermore, we rebuild the cache nightly.
**After:** We cache embeddings for 24 hours, invalidate them when the source document changes, and
rebuild the cache nightly.

**Fix:** a period ends the prior sentence and the next one connects by content. Keep an explicit
transition only for a contrast or concession the reader would otherwise miss. Cross-ref: Rule 9.6.

## #17 Stacked qualifiers

**Watch for:** to be fair, it's also possible that, could potentially, might arguably, in some cases
it may, this is an inference; two or more hedges on one claim ("it could potentially possibly be
argued that").

**Why it happens:** repeated editing adds one qualifier after another to repair an earlier
overstatement, until every claim sounds uncertain.

**Before:** It could potentially possibly be argued that the policy might have some effect on
outcomes.
**After:** The policy can affect outcomes. We have not measured how much.

**Fix:** keep one qualifier per genuinely fragile claim, where the source supports the doubt. Keep
scope statements, legal notices, and real corrections. Ordinary hedges ("about", "roughly") are
human habits. Cross-ref: Rule 10.5 ("Hedge once per genuinely fragile claim").

## #18 Knowledge-limit disclaimers and hedged guesses

**Watch for:** as of my last update, up to my training cutoff, while specific details are limited,
based on available information, not widely documented; a gap filled with a plausible guess ("the
project likely began in the 1990s", "she likely grew up in a middle-class household", "it is
believed that").

**Why it happens:** the model notes where its knowledge ends, then fills the gap so the sentence
still reads as complete.

**Before:** While specific details about the company's founding are not well documented, it appears
to have been established sometime in the 1990s.
**After:** The company's founding date is not in the available sources. (Or cut the sentence.)

**Fix:** state what the source does not show, or delete the sentence. Never present a guess as a
fact. Cross-ref: Rule 10.6 (the hedged gap-fill and the knowledge-limit disclaimer as filler).

## #19 Formulaic sayings and aphorisms

**Watch for:** X is the Y of Z ("symmetry is the language of trust"); the currency of, the
architecture of, the language of; X becomes a trap; X is not a tool but a mirror; a career can look
promising and fail — the manufactured maxim.

**Why it happens:** an ordinary point is dressed as an aphorism because the aphoristic shape reads
as insight.

**Before:** Efficiency becomes a trap when teams forget the human layer.
**After:** Teams can over-optimize a workflow and miss how people actually use it.

**Fix:** replace the saying with the specific claim.

## #20 Pretending to reveal a deeper truth

**Watch for:** the real question is, at its core, in reality, what really matters, fundamentally,
the deeper issue, the heart of the matter, here's what's really going on; a one-line paragraph that
announces a hidden truth before the content arrives.

**Why it happens:** the reveal frame promises the reader that the next sentence is the one that
counts. Usually the next sentence is ordinary.

**Before:** The real question is whether teams can adapt. At its core, what really matters is
organizational readiness.
**After:** Whether teams can adapt depends mostly on whether the organization will change its
habits.

Cross-ref: #7 (editorializing asides), #21 (dramatic fragments).

## #21 Forced punchlines and dramatic fragments

**Watch for:** a one-sentence paragraph that restates the paragraph before it; "That is the real
win.", "Read that again.", "Let that sink in."; a row of fragments ("No aesthetic prior. No
nostalgia."); one word in capitals, or periods between words ("every. single. time.").

**Why it happens:** the line asks the reader to pause on a claim instead of adding to it. A model
applies the beat by rule.

**Before:** Then AlphaEvolve arrived. It had no preference for symmetry. No aesthetic prior. No
nostalgia for human taste. The old rules were gone.
**After:** AlphaEvolve changed the search because it did not favor symmetry or human-looking
designs, which made some older assumptions less useful.

**Fix:** cut a closer that repeats. Merge a row of fragments into one sentence with a specific
claim. One short sentence is fine when it carries a new fact. Cross-ref: Rule 4.1.

## #22 Not X but Y (expanded)

This is the catalog treatment of the direction at #2.

**Watch for, every form:** not X but Y; not just / not only / not merely X, but Y; it's not X, it's
Y; X rather than Y; the contrast split across two sentences ("This does not mean X. It means Y.");
the clipped negative tail (", no guessing", ", not a hope", ", not the last"); "X, Not Y" as a
section heading.

**Why it happens:** the construction is high-reward in the op-ed and manifesto corpora the model
trains on. It reads as balanced and quotable, so the model reaches for it in headings, abstracts,
and openers. When the negative half is vague or a strawman, the "not Y" tail is cadence, not
content.

**Before (split across sentences):** This does not mean every choice is equal. It means there is no
external system that confirms which choice is right.
**After:** No external system confirms which choice is right, though the choices still carry
different consequences.

**Keep the contrast** only when the rejected alternative is specific and ruling it out informs the
reader: "The bottleneck is disk I/O, not CPU." Cross-ref: Rule 3.6, agent-style RULE-07.

## #23 Vague connection or association

**Watch for:** associated with, in association with, connected to, in connection with, linked to,
tied to, affiliated with — where the sentence does not say how.

**Why it happens:** "He was associated with the leadership of ExampleCorp" hides whether he was the
chief executive, a board member, or a paid consultant. The vague verb lets the model state a
relationship it cannot specify.

**Before:** He is associated with the Rajhans Orchestra, and the concerts were organised in
connection with Pakistan's 50th anniversary.
**After:** He founded and conducts the Rajhans Orchestra. The concerts were part of Pakistan's 50th
anniversary celebrations.

**Fix:** name the relationship the source gives. If the source does not say, keep the vague wording
rather than inventing a role. Cross-ref: #4, Rule 10.6.

## #24 Bullet points in place of connected prose

**Watch for:** a list whose items are sentence shards with the connective tissue stripped out
("Because this improves recall", "Which matters for RAG"); a bulleted causal chain; a "three
strengths" list that is really one sentence. This is agent-style RULE-A.

**Why it happens:** bullets read as organized, so the model converts reasoning into them. The
argument then has to be reassembled from the shards.

**Before:**
> Our approach:
> - Trains a contrastive embedder
> - Because this improves retrieval recall
> - Which matters for RAG pipelines
**After:** Our approach trains a contrastive embedder, which improves retrieval recall for the RAG
pipeline downstream.

**Fix:** keep prose in paragraphs when ideas connect by cause, argument, or sequence. Use bullets
only for genuinely parallel enumerations: API endpoints, configuration options, checklist steps.
Test: if reading the first few words of each item recovers the meaning, it is a real list. Cross-ref:
Rule 4.3, #3.

## #25 Bold as decoration

**Watch for:** bold on words that are not defined terms, not UI labels, and not the first use of a
key concept; a whole clause in bold for emphasis.

**Why it happens:** the model bolds to signal that a phrase matters, the way a slide deck does.

**Before:** It blends **OKRs**, **KPIs**, and visual tools such as the **Business Model Canvas** and
the **Balanced Scorecard**.
**After:** It blends OKRs, KPIs, and visual tools such as the Business Model Canvas and the Balanced
Scorecard.

**Fix:** remove the bold. Keep it only for a genuine UI label ("click **Save**") or a term at its
first definition, if the venue's own style does that.

## #26 Bold mini-headings on list items

**Watch for:** a vertical list where every item opens with a bold label and a colon, and the label
carries no information the sentence does not ("**Performance:** Performance has been improved").

**Why it happens:** the label-colon shape reads as structured. It is the list form of #25.

**Before:**
> - **User experience:** The interface has been redesigned.
> - **Performance:** Load times are faster through optimized queries.
> - **Security:** End-to-end encryption has been added.
**After:** The update redesigns the interface, cuts dashboard load time from 820 ms to 240 ms
through query changes, and adds end-to-end encryption.

**Fix:** turn the list into prose when the labels are just topic words. Keep a labeled list only when
each label is a real key the reader will scan for (a glossary, a config reference).

## #27 Title case in headings

**Watch for:** a heading with every major word capitalized: "## Experimental Results And Analysis",
"## Getting Started With The API".

**Why it happens:** agent-style's RULE-G asks for title case in academic and engineering venues, and
some model output follows that convention. Humanizer §17 and authengentic overrule it.

**Before:** ## Strategic Negotiations And Global Partnerships
**After:** ## Strategic negotiations and global partnerships

**Fix:** sentence case, in every mode and every venue. Capitalize the first word and any proper noun,
nothing else. Proper nouns and code identifiers inside the heading keep their own case. Cross-ref:
Rule 8.9, "Where authengentic differs from its sources" item 2.

## #28 Emoji, arrows, and rules as decoration

**Watch for:** emoji as list bullets or section markers (🚀, 💡, ✅); arrows (→) as decoration
rather than notation; a horizontal rule between every section; a document that opens with a
top-level heading repeating its own title.

**Why it happens:** the model decorates structure to make it look considered.

**Before:**
> 🚀 **Launch phase:** the product ships in Q3
> 💡 **Key insight:** users prefer simplicity
**After:** The product ships in Q3. User research showed a preference for simpler defaults.

**Fix:** remove the decoration. Let the title stand once. A horizontal rule is for a real section
break, not every one.

## #29 Curly quotation marks

**Watch for:** curly quotes (`“ ” ‘ ’`) and the curly apostrophe (`’`) in Markdown, code, commit
messages, or documentation.

**Why it happens:** a paste artifact from chat interfaces and word processors, which auto-curl.

**Before:** He said “the project is on track” but the burndown didn’t agree.
**After:** He said "the project is on track" but the burndown didn't agree.

**Fix:** straight quotes (`"` and `'`). The exception is narrow: when the exact characters are the
subject (a bug report about smart-quote handling), reproduce them. Cross-ref: Rule 8.8. Curly quotes
alone are a weak signal, since most editors auto-curl.

## #30 Hyphenated pairs in every position

**Watch for:** third-party, cross-functional, client-facing, data-driven, decision-making,
well-known, high-quality, real-time, long-term, end-to-end — hyphenated whether they sit before a
noun or after it.

**Why it happens:** the model applies the hyphen by rule, not by position.

**Before:** The team is cross-functional, the report is high-quality, and the methodology is
data-driven.
**After:** The team is cross functional, the report is high quality, and the method is data driven.

**Fix:** keep the hyphen before the noun it modifies ("a high-quality report"), drop it after the
noun as a predicate ("the report is high quality"). This is a position rule, not a ban. Cross-ref:
`references/word-swaps.md`, "Hyphenated pairs" section.

## #31 Generic positive send-offs

**Watch for:** a closing paragraph of forward-looking optimism: the future looks bright, exciting
times ahead, a step in the right direction, they continue their journey toward excellence, poised
for growth.

**Why it happens:** the model ends on an upbeat note that fits any subject.

**Before:** The future looks bright for the company. Exciting times lie ahead as they continue their
journey toward excellence.
**After:** (Cut the paragraph. End on the last concrete fact.)

**Fix:** delete it. If the source states real, dated plans, report those instead. Cross-ref: #1, #6.

## #32 A heading echoed by its first sentence

**Watch for:** a heading followed by a one-line paragraph that restates it before the content
begins.

**Why it happens:** the model treats the heading as a prompt and answers it with a paraphrase.

**Before:**
> ## Performance
>
> Speed matters.
>
> When users hit a slow page, they leave.
**After:**
> ## Performance
>
> When users hit a slow page, they leave.

**Fix:** delete the echo sentence. Cross-ref: #6, sepia professional-pass check 6.

## #33 Writing about the previous version

**Watch for:** documentation or code comments that describe what the text replaced instead of the
current behavior: "This function was added to replace the old approach of iterating through all
items."

**Why it happens:** the model narrates the change it just made, as if the reader were reviewing a
diff.

**Before:** This function was added to replace the previous approach of iterating through all items,
which caused O(n²) performance.
**After:** This function uses a hash map for O(1) lookups.

**Fix:** describe the current behavior. Mention the previous version only in a changelog, a release
note, or a migration guide, where change is the subject.

## #34 Uniform rhythm: same sentence and paragraph lengths

**Watch for:** three or more adjacent sentences of about the same length; every paragraph the same
size; no one-line paragraph anywhere, and no long one either. This is sepia professional-pass
check 9.

**Why it happens:** the spread of sentence lengths inside a text is measurably narrower in machine
prose than in human prose. A model holds one rhythm from the first line to the last.

**Before (four sentences, all about 22 words):** The ingestion pipeline processes incoming records
in batches of one thousand items and stores them in the primary document store. Each batch is
processed by the ingest worker, which runs every five minutes. The document store maintains an index
on the timestamp field, which enables range queries. Query performance is acceptable for batch sizes
up to fifty thousand records per minute.
**After (8 + 22 + 12 + 8 words):** The ingest worker handles records in batches. Every five minutes
it pulls up to a thousand records and writes them to the primary document store. The store keeps a
timestamp index for range queries. At fifty thousand records per minute, performance holds.

**Fix:** break the run by moving words, never by adding them: split one long sentence, merge two
short ones, or delete a clause. Do not shorten everything, since uniform short sentences are the same
defect from the other side. This check needs running prose of at least a paragraph. A one-line reply,
a bullet list, a table, or a commit-style release note has no rhythm to measure. Cross-ref: Rule 4.1.

## #35 Templatedness: one sentence frame recycled

**Watch for:** the same sentence frame repeated down a list or a section: "X, a Y at Z, said that
...", three times over; "Redis was upgraded to improve stability. Postgres was upgraded to improve
stability." This is sepia professional-pass check 8.

**Why it happens:** the model fills a frame it locked into, the way a form gets filled in.

**Before:** Redis was upgraded to 7.2 to improve stability. Postgres was upgraded to 16.1 to improve
stability. Nginx was upgraded to 1.25 to improve stability.
**After:** Three services moved to new majors: Redis 7.2, Postgres 16.1, and Nginx 1.25. The Redis
upgrade fixed the keyspace-notification leak. The other two were routine.

**Fix:** vary the frames, or move the repeated fields into a table, where repetition is correct.
Cross-ref: Rule 9.7.

## #36 Awkward word choice

**Watch for:** a word used slightly off its meaning or register; "seem to" plus a verb where the
verb alone is meant and no uncertainty is real; an unclear pronoun; a passive where an actor exists.
In the professional-editor taxonomy sepia cites, this is the single largest category of fixes at 28%
(sepia style-pass §1, artifact 1).

**Why it happens:** the model picks a word that is close to right and fits the sentence rhythm, not
the exact word.

**Before:** The service seems to reject requests that appear to lack a valid token.
**After:** The service rejects any request without a valid token.

**Fix:** replace the misused or off-register word. Drop "seem to" and "appear to" unless the
uncertainty is genuine and worth stating.

## #37 Run-on sentence structure

**Watch for:** two or more independent thoughts joined into one long sentence with commas and "and";
a sentence that carries a main claim plus three qualifications inline. This is artifact 2 in the
same taxonomy, "poor sentence structure", at 20% of fixes (sepia style-pass §1).

**Why it happens:** next-token generation rewards continuing a well-formed sentence over stopping and
starting a new one.

**Before:** The replica had been failing health checks for three days and was never promoted because
of a misconfigured priority setting and this was the direct cause of the outage.
**After:** The replica caused the outage. It had failed health checks for three days, and a
misconfigured priority setting had blocked promotion.

**Fix:** one tangled thought becomes two plain sentences. Cross-ref: Rule 4.1, Rule 10.3.

## #38 Redundant exposition (trailing participial restatement)

**Watch for:** the shape "[main clause], [trailing participial phrase that restates the main
clause]": "The scheduler retries three times, providing resilience against transient failures." This
is artifact 3 in the taxonomy, "redundant exposition", at 18% of fixes (sepia style-pass §1).
Participial clauses of this kind are among the part-of-speech shapes sepia reports as 2 to 5 times
overrepresented in machine prose against human prose, the participial row specifically at up to five
times (sepia style-pass §2).

**Why it happens:** the model adds a clause that re-expresses the fact in more abstract terms, which
feels like completion.

**Before:** The cache holds entries for 60 seconds, ensuring that stale data does not persist and
keeping memory pressure predictable.
**After:** The cache holds entries for 60 seconds.

**Fix:** delete everything after the comma. If the trailing clause carries a real second fact, break
it into its own short sentence with a finite verb. Cross-ref: Rule 3.7, #11.

---

## The false-positive whitelist

Do not flag these as machine tells. Over-correction is itself a detectable fingerprint, and
"correcting" a clean sentence is logged as one. This section merges humanizer's "When not to act"
and "Keep the details that carry the writer's voice", sepia's style-pass §7, and sepia's
professional-pass whitelist.

| Not evidence of AI | Why |
|---|---|
| Clean grammar and correct punctuation | Plenty of people write cleanly. Injecting typos to look human is a detectable gimmick. |
| A single, correctly-placed em-dash | Not a violation and not evidence of AI. Dashes are the one cumulative rule in authengentic: only a cluster counts. See the note on clusters below. |
| One semicolon, one "delve", one "however" in isolation | Not by itself proof a machine wrote the text; the authorship tell is density, not the lone instance. But authengentic still fixes each on the first hit (Rule 8.1 for the semicolon, Rule 1.15 for the slop word; "Where authengentic differs from its sources" item 4). This row is about authorship evidence, not about which rules apply. |
| Curly quotes on their own | Most editors and word processors auto-curl. Weak signal alone. |
| A formal register in a formal venue | Register match beats forced casualness. A grant proposal is allowed to sound like one. |
| One short sentence for emphasis | Human, when it carries a new fact. The tell is the closer that repeats (#21). |
| Useful disclaimers, legal and safety notices, scope statements, real corrections | These carry information. The tell is the knowledge-limit disclaimer used as filler (#18). |
| A named alternative a reader would actually weigh, or an objection the text attributes and answers in full | The tell is the invented objection and the strawman alternative (#8). |
| An unsourced but plausible claim outside a citation-bearing genre | Most writing is unsourced. The tell is the fake attribution ("studies show") and the fabricated citation (#4, #10). |
| Conventional containers: changelog categories, issue and PR templates, RFC sections, runbook formats | Formulaic by convention. The reader expects them. Slop is the filler inside the structure, not the structure. |
| Terse, unadorned replies in a developer venue | Brevity is the human default there, not a tell. |
| The author's own verified habits from a writing sample | If the sample uses em-dashes, "moreover", or a high contraction rate, those stay. Edit toward the author's voice, not a generic "human" one. |
| Moderate ordinary sentences, a plain paragraph, an underdeveloped thought | Slack is human. Do not sand every surface to distinctiveness. |
| Text written before 2022-11-30 | Not AI-written. Salutations and sign-offs on letters and comments predate chatbots too. |
| A watched phrase inside a quotation, a title, a proper name, or a passage discussing the phrase | Quoted material keeps its own texture. |
| Punctuation density, comma or period counts, paragraph count, average paragraph length, em-dash frequency as a model-agnostic rule | Measured directions contradict across corpora and across model releases. Em-dash rate is a release property (10.62 per 1,000 words for one model, 0.00 for another), not a blanket tell. |
| A specific unusual detail, mixed feelings, a dated reference, a first-person choice the writer can explain, a genuine aside or self-correction | These carry the writer's voice. Keep them unless they hurt the meaning. |

**The one place clusters are counted, not instances.** Dashes are the single mechanically
cumulative rule in authengentic: two or more dashes as punctuation in one sentence, or three or more
in one paragraph, is a violation, and a lone clean dash is not (SKILL.md Section 8, "Where
authengentic differs from its sources" item 3). Every other pattern in this file is fix-on-first-hit
(item 4). When this file says a tell "counts only alongside other hits" (for example the stock
vocabulary at #13 or the uniform rhythm at #34), that is a judgment about whether the pattern is
really present, not a licence to tally and wait. Once you are satisfied the pattern is there, fix the
first occurrence.
