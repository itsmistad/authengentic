# Domain — incident postmortems

Covers incident reports, outage retrospectives, RCA documents. Run with `SKILL.md` (article-like weighting: relevance, density, stance) plus the outline test in Rules 6.7 and 10.7.

## Human baseline

Blameless toward people, merciless toward mechanisms. The real document has absolute timestamps, exact failure mechanics (the query, the config line, the race window), honest dead ends ("we spent 40 minutes on the wrong hypothesis"), and action items someone actually owns. A team's incident template is a fine container — the tell is filler inside it.

## AI tells in this domain

| Tell | Fix |
|---|---|
| Agentless fog: "mistakes were made", "the change was deployed" with no actor anywhere | Blameless is not agentless. Name systems and roles: "the deploy pipeline promoted the config before validation ran" |
| Generic lessons: "we will improve monitoring and communication" | An action item is a change with an owner and a date: "add alert on queue depth > 10k (owner: infra, due 09-15)" |
| Every template section filled to similar length for completeness | Sections earn their length. "What went well: N/A-grade prose" becomes one honest line or a deletion |
| Self-praise adverbs: "the team swiftly identified…" | Timestamps carry the speed judgment. Let them |
| Hedged root cause: "a combination of factors may have contributed" | Commit to the causal chain you believe, and mark the genuinely unknown part as unknown |
| Moralizing conclusion about reliability culture | End at the action items |
| Round, sourceless numbers | Real duration, real blast radius, real user and request counts — from the actual incident data, never estimated to sound complete |

## Rules

1. **Timeline with absolute times and timezone**, including the wrong turns — the 40 minutes on the bad hypothesis is the most instructive part, and models systematically omit failure-within-the-failure.
2. The failure mechanism at code or config level: the exact query, flag, limit, or race. If you, the writer, do not know it, that's a question for the team, not a blank to prose over.
3. Counterfactuals stated honestly: name the safeguard that was missing, and why it did not exist. No "the system worked as designed" face-saving.
4. Contributing factors as a causal chain, not a bullet cloud — each factor says what it enabled.
5. Impact in numbers first (duration, requests failed, users affected, money if known), narrative second.
6. Stance check (Rule 10.5): a postmortem that admits no wrong judgment anywhere has not been written yet.
