# Domain — technical articles and blog posts

Covers engineering blog posts, tutorials, architecture write-ups, experience reports. The richest domain: run `SKILL.md` (article-like weighting), the outline test in Rules 6.7 and 10.7, and `references/ai-tells.md`.

## Human baseline

Motivated by a real problem the author actually hit. Uneven by design — deep where it got interesting, one line where it did not. Contains at least one dead end, at least one opinion a reader can disagree with, and numbers with their conditions attached. First person and contractions are normal.

## AI tells in this domain

| Tell | Fix |
|---|---|
| The topic-survey opening: "In the world of distributed systems…" or a definition of the thing everyone reading already knows | Open at the incident, the bug, the number that made you look |
| Listicle in a trench coat: prose that is secretly "The first… The second… The third…" | Either honest structure (a real list or table) or real prose with an argument |
| Fractal summaries: every section announces, tells, recaps | Say it once, at the level where it lives |
| Invented concept labels: "the observability paradox", "configuration drift syndrome" coined mid-post | Plain description, or an established term |
| Symmetric coverage: every alternative gets a paragraph, none gets a verdict | Commit to a recommendation and state the evidence that changes it |
| No failure anywhere: every step worked, benchmarks confirm the thesis | Include what broke, what you tried first, what to skip next time — models systematically omit the dead end, and it's the part readers trust |
| Generic code examples (`foo`, `my_service`) that were never run | Real, runnable, tested snippets from the actual work — or say explicitly they're sketches |
| Benchmarks with no conditions | Machine, version, dataset size, number of runs — or do not print the number |
| The both-sides conclusion plus future outlook | End on the recommendation or the open question you actually have |

## Rules

1. **The problem before the topic.** First paragraph: the concrete situation that forced the question. If there is no real situation, the honest genre is "notes on X", not a war story — never fabricate the incident.
2. One opinion minimum, stated as yours, with the disagreement condition ("if your writes are under 1k/s, ignore all of this").
3. Depth budget by interest, not symmetry: the section that surprised you gets 5x the words of the setup steps.
4. Numbers carry conditions, claims carry links, code carries a "this runs" guarantee or a disclaimer.
5. Outline check (Rules 6.7 and 10.7): if the section-question sequence reads *what is X, why X matters, how to X, conclusion*, restructure around what actually happened.
6. Voice: first person, contractions, an aside or two. The measured human markers (stance, unevenness, lived specifics) are the same ones expert readers use to judge "a person wrote this."
