# Slop-to-simple substitutions

This table is ours, not the ASD dictionary. It maps the words AI-generated docs overuse to plain replacements. If the word carries no fact, delete it instead of replacing it.

| Slop | Write instead |
|---|---|
| leverage, utilize | use |
| in order to | to |
| prior to | before |
| ensure | make sure that |
| it is worth noting that | (delete) |
| it's important to | (delete — state the fact) |
| simply, just, easily, seamless, seamlessly, effortlessly | (delete) |
| robust, powerful, comprehensive, performant | (delete, or give the measurable property) |
| functionality | function, feature |
| enables you to, allows you to | you can |
| is designed to, aims to | (delete — say what it does) |
| facilitate | help, make possible |
| dive into, delve into | read, examine |
| when it comes to | for |
| in the event that | if |
| due to the fact that | because |
| as needed, as necessary | (state the condition) |
| and/or | Pick one, or write "X, or Y, or both" |
| e.g. / i.e. / etc. | for example / that is / (name the items) |
| gracefully handles | (say what it does: "retries three times, then stops") |
| out of the box | by default |
| under the hood | internally |
| blazingly fast | fast (give the number) / (delete) |
| streamline | make simpler, make faster |
| plethora, myriad | many |
| addresses the issue, tackles | corrects the fault, removes the error |
| pivotal, crucial, crucially, paramount | important |
| tapestry, testament, synergy | (delete) |
| interplay | interaction (or delete) |
| intricate | complex |
| vibrant, nuanced, multifaceted | (delete, or name the parts) |
| realm, landscape (metaphorical) | area |
| groundbreaking, cutting-edge, state-of-the-art, innovative, unprecedented | new (or delete) |
| transformative, game-changer | (delete — say what changes) |
| revolutionize | change |
| showcase, underscore, emphasize | show |
| foster, empower, bolster | help, support, let |
| harness | use |
| enhance | improve |
| elevate | increase |
| furthermore, moreover | also |
| in conclusion, in summary, at the end of the day | (delete) |
| embark, endeavor | start, try |
| meticulous, meticulously | careful, carefully |
| holistic | full |
| paradigm | model |
| navigate (metaphorical) | go to |
| boasts | has |
| nestled, in the heart of | (delete — give the location or the fact) |
| bustling | busy |
| that being said, notwithstanding | but |
| I hope this helps, let's dive in | (delete) |

## Additional swaps (agent-style, humanizer, sepia)

These come from the merged catalogs and match the `slop.tsv` list the linter enforces (the entries below its `--- new ---` marker). One row per linter entry. A term already covered by the first block is not repeated here.

| Slop | Write instead |
|---|---|
| encompass | include |
| burgeoning | growing |
| keen | strong |
| adept | skilled |
| uphold | keep |
| imperative | necessary |
| ponder | consider |
| cultivate | build |
| hone | sharpen |
| embrace | adopt |
| pave | (delete, or name the action) |
| monumental | large |
| scrutinize | examine |
| vast | large |
| versatile | flexible |
| necessitates | requires |
| provenance | origin |
| nuance | (name the specific difference) |
| obliterate | remove |
| articulate | state |
| acquire | get |
| underpin | support |
| harmonize | align |
| garner | get |
| undermine | weaken |
| gauge | measure |
| facet | part |
| game-changing | (delete — say what changes) |
| reimagine | redesign |
| turnkey | ready to use |
| trailblazing | new |
| moving the needle | (name the actual metric change) |
| push the envelope | (delete, or name the specific advance) |
| circle back | return to this |
| deep dive | detailed look |
| best-in-class | (delete, or give the comparison) |
| world-class | (delete, or give the comparison) |
| next-generation | new |
| novel approach | (name the approach) |
| novel framework | (name the framework) |
| novel method | (name the method) |
| novel optimization | (name the optimization) |
| significant step forward | (delete — state the result) |
| paradigm-shifting | (delete — say what changed) |
| advance the state of the art | (state the specific improvement) |
| think outside the box | (delete) |
| level playing field | (name the specific condition) |
| low-hanging fruit | the easiest fix |
| symphony | (delete) |
| kaleidoscope | (delete) |
| journey | (name the specific process) |
| beacon | (delete) |
| camaraderie | (name the specific relationship) |
| solace | comfort |
| resilience | (name the specific behavior) |
| resonate | (say what it does) |
| transcend | go beyond |
| unravel | explain |
| ignite | start |
| grapple | work through |
| weave | combine |
| weaving | combining |
| palpable | clear |
| fleeting | brief |
| unspoken | (name what was not said) |
| the weight of | (name the specific burden) |
| hung in the air | (delete) |
| the air was thick | (delete) |
| a constant reminder of | (name what it reminds of) |
| in a world of | (delete — state the fact) |
| in a world where | (delete — state the fact) |
| cautionary tale | (state the specific lesson) |
| amidst | during |
| align with | match |
| gate | (name the specific restriction — check technical usage first) |
| highlight | show |
| key | important |
| quietly | (delete unless literal) |
| stands as | is |
| serves as | is |
| is a testament | shows |
| vital | important |
| underscores its importance | (state why it matters, specifically) |
| symbolizing | (delete, or state the fact directly) |
| marking the | (delete, or state the fact directly) |
| key turning point | (name the specific change) |
| evolving landscape | (name the specific change) |
| focal point | center |
| indelible mark | (name the specific effect) |
| deeply rooted | established |
| enhancing its | improving its |
| exemplifies | shows |
| commitment to | (state the specific action) |
| natural beauty | (name the specific feature) |
| breathtaking | (delete, or name the specific feature) |
| must-visit | (delete) |
| stunning | (delete, or name the specific feature) |

## Hyphenated pairs (conditional, not a ban)

From humanizer §26. These are not slop. The hyphen depends on position: keep it when the pair sits before the noun it modifies, drop it when the pair comes after the noun as a predicate.

- Before a noun: "a high-quality report", "a data-driven decision", "a real-time feed".
- After the noun: "the report is high quality", "the decision was data driven", "the feed is real time".

The ten pairs this applies to: third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end.
