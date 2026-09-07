# Voice and venue

Two calibration inputs outrank the defaults in `SKILL.md`: a sample of the user's own writing, and the corpus of the venue the text goes to. This file says how to read each one, how far the override reaches, and what to do when the two disagree.

Neither input touches facts. The Untouchables and Rule 10.6 still hold: a sample or a venue changes the style, never the content. Do not add a claim, a number, a citation, or a name to match a voice.

## Matching a writing sample

When the user supplies a sample of their prior writing, read it before you draft or edit. Build a short profile first, then write to the profile.

**Read these six habits off the sample:**

1. **Sentence length and spread.** The mean length, and the range. A writer who mixes 6-word and 30-word sentences has a wide spread. Match the spread, not just the mean.
2. **Word choice.** The plain-versus-formal level. The words the writer reaches for by habit. Contractions, slang, filler the writer keeps on purpose.
3. **Paragraph openings.** How paragraphs start: with the point, with a transition, with a question, with a name.
4. **Punctuation.** The dash rate. Comma density. Parentheses, colons, lists. Straight or curly quotes in the writer's normal output.
5. **Repeated phrases.** Stock connectors, favorite verbs, a signature aside the writer uses more than once.
6. **Transitions.** How the writer moves between ideas: an explicit "but" and "so", a bare period, a repeated frame.

**Then match those habits.** Do not replace a casual word with a formal one. Do not remove a quirk the writer actually uses. Do not sand the sample's rhythm down to the even surface the rules otherwise produce. The point of the sample is that it is uneven and specific. Make the draft the same.

### The sample overrides the authengentic style defaults

A supplied sample outranks the style defaults in `SKILL.md`. Two overrides are explicit, because they reverse rules that this skill otherwise enforces on the first hit:

- **Dashes: match the sample's rate, not the cluster threshold.** `SKILL.md` "Where authengentic differs from its sources", item 3, sets the default: a lone dash is fine, and a cluster (two or more in a sentence, three or more in a paragraph) is a violation. A sample repeals the threshold. If the sample uses em-dashes or en-dashes as punctuation at a given rate, write the draft at about that rate, cluster or not. If the sample almost never uses them, keep the draft that way even where a lone dash is allowed. Numeric ranges (`5–10`), CLI flags (`--force`), and list markers still never count as dashes, sample or no sample.
- **Contractions: match the sample's rate, higher or lower.** `SKILL.md` "Where authengentic differs from its sources", item 1, makes contraction restoration a required move: instruction-tuned models under-use contractions, and the default is to put them back where a person does. A sample replaces that default with a measurement. If the sample contracts heavily, contract heavily. If the sample spells most forms out, spell them out, and do not "restore" contractions it does not use. The one part that does not bend: a banned modal stays banned in its contracted form too ("shouldn't" is still a banned modal), because that is the modal ladder, not a contraction question.

Everything else in the sample profile works the same way: where a habit in the sample contradicts a default, the sample wins, as long as the facts stay intact and no banned modal sneaks back in.

### When the sample and the venue disagree

The sample governs voice: sentence rhythm, word choice, punctuation rate, contraction rate, transitions. The venue governs structure and format: headings, section order, length norms, the conventional containers the reader expects (changelog categories, issue templates, RFC sections). Apply the sample to the first set and the venue to the second, and they rarely collide.

Where they genuinely collide on the same axis, the sample wins. The byline is the person's, and a reader who knows their writing will notice a voice that is not theirs before they notice a format that bends a house norm. State the conflict in your reply so the user can overrule you.

## Venue-corpus calibration

Before you write or edit for a specific venue, sample two or three recent, human-written artifacts from that venue: the repo's last few release notes, the team's last postmortem, a maintainer's recent issue replies. Read them for register, length norms, and formatting habits, and match what you find. The venue corpus, not this skill, defines the target voice for that venue.

This matters because machine text is measurably dense and noun-heavy and does not vary with genre (Reinhart et al. 2025, PNAS). Instruction-tuned models hold one register from the first line to the last. The venue corpus is what supplies the variation the model does not produce on its own.

**State the target register before you edit.** Name it in a phrase: a terse internal ticket, a public release announcement, a careful postmortem for an external audience, a one-line PR reply. Then edit toward that register. Do not edit toward a single universal "human" default, because there is no such thing: a human release note and a human postmortem do not sound alike, and a draft flattened to a generic "human" voice is still flat.

### When no venue corpus exists

When the venue has no readable corpus, or you are creating the venue, the baseline in the matching domain file applies instead:

| Venue | Domain file |
|---|---|
| Release notes, changelogs | `references/domains/release-notes.md` |
| PR and issue replies, review comments | `references/domains/dev-replies.md` |
| Postmortems, incident reports | `references/domains/postmortems.md` |
| Bug reports, tickets | `references/domains/tickets.md` |
| Technical articles, blog posts, announcements | `references/domains/tech-articles.md` |
| Error messages, log lines | `references/domains/error-messages.md` |
| API reference and guides | `references/domains/api-docs.md` |

The domain file is the fallback, not the ceiling. If a venue corpus exists, sample it, and let it override the domain baseline the same way a writing sample overrides the style defaults.
