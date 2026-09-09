#!/usr/bin/env python3
"""Deterministic authengentic violation counter, merged from SimpleEnglish's
ste_lint.py and agent-style's detectors_mech.py.

Counts mechanical violations a regex can catch. Known ceiling: this is a
regex pass, not a grammar parser. Numbers from this tool are comparable
between two texts run through the same version; they are not a compliance
verdict. No tool can guarantee full-catalog compliance.

Differs from both sources per the four contradiction resolutions:
  1. No `contraction` check — contractions are encouraged, not banned.
  2. `title_case_heading` flags a heading that IS title case (sentence
     case is required); this is the INVERSE of agent-style's RULE-G check.
  3. `em_dash` is cumulative: it only fires on a cluster (>=2 in one
     sentence, or >=3 in one paragraph), never on a lone dash.
  4. Every other check is fix-on-first-hit, unchanged from SimpleEnglish.

Usage:
  python3 authengentic_lint.py --type procedural file.md
  cat text.md | python3 authengentic_lint.py --type descriptive -
  python3 authengentic_lint.py --self-test
"""
import json
import os
import pathlib
import re
import sys

BANNED_MODALS = re.compile(r"\b(should|would|may|might|could)\b", re.I)
PERFECT = re.compile(r"\b(has|have|had)\s+been\b|\b(has|have)\s+\w+ed\b", re.I)
ING_CLAUSE = re.compile(r",\s*(mak|allow|enabl|ensur|highlight|creat|provid|offer|help|reduc|improv|lead|caus|result)ing\b", re.I)
LATIN = re.compile(r"\b(e\.g\.|i\.e\.|etc\.?)(?=[\s,)]|$)", re.I)
SLOP_CORE = re.compile(
    r"\b(simply|seamlessly|effortlessly|robust|leverag\w*|utiliz\w*|"
    r"comprehensive|powerful|blazingly|streamlin\w*|facilitat\w*|"
    r"performant|plethora|myriad|delve|crucial|pivotal)\b", re.I)
SLOP_TSV = pathlib.Path(__file__).resolve().parent / "slop.tsv"
FILTER_WORDS = re.compile(r"\b(felt|seemed|realized|noticed|knew)\b|\bwatched as\b", re.I)
CURLY_QUOTE = re.compile(r"[“”‘’]")
EMOJI = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]"
)
BOLD_MINI_HEADING = re.compile(
    r"^\s*[-*]\s+\*\*[^*]+:\*\*|^\s*[-*]\s+\*\*[^*]+\*\*:", re.M
)
_TRANSITION_OPENERS = ("Additionally", "Furthermore", "Moreover", "In addition", "What's more", "Notably")
_TRANSITION_RE = re.compile(
    r"(?:^|[.!?]\s+)(" + "|".join(re.escape(t) for t in _TRANSITION_OPENERS) + r")\b",
)


"""Slop terms that must match as an exact word, with no trailing-letter
wildcard. "key" and "gate" are common technical words (keyword, keyboard,
keys; gateway); the `\\w*` suffix the other terms carry would drag those
in as false positives."""
_SLOP_EXACT_TERMS = frozenset({"key", "gate"})


def _learned_slop_terms():
    """Extra dead words the /authengentic-learn command promoted. Read from
    `${AUTHENGENTIC_CONFIG_DIR or CLAUDE_CONFIG_DIR or ~/.claude}/
    authengentic/learned.json`. A missing or malformed file returns
    nothing. Tests set AUTHENGENTIC_CONFIG_DIR to isolate this.
    """
    if os.environ.get("AUTHENGENTIC_DISABLE_LEARN"):
        return []
    base = os.environ.get("AUTHENGENTIC_CONFIG_DIR") or os.environ.get("CLAUDE_CONFIG_DIR")
    root = pathlib.Path(base) if base else pathlib.Path.home() / ".claude"
    try:
        raw = json.loads((root / "authengentic" / "learned.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(raw, dict) or not isinstance(raw.get("slop"), list):
        return []
    return [
        item.strip().lower()
        for item in raw["slop"]
        if isinstance(item, str) and item.strip()
    ]


def slop_pattern():
    """Union of the measured core list, evals/slop.tsv (term, source, swap),
    and the learned terms from learned.json.

    Falls back to the core list when both sources are empty. Comment lines
    (leading '#') and blank lines in the TSV are skipped.
    """
    terms = []
    if SLOP_TSV.exists():
        for line in SLOP_TSV.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            term = line.split("\t")[0].strip().lower()
            if term:
                terms.append(term)
    terms.extend(_learned_slop_terms())
    patterns = []
    for term in terms:
        pattern = re.escape(term).replace(r"\ ", r"\s+")
        if term not in _SLOP_EXACT_TERMS:
            pattern += r"\w*"
        patterns.append(pattern)
    if not patterns:
        return SLOP_CORE
    return re.compile(SLOP_CORE.pattern[:-len(r")\b")] + "|" + "|".join(patterns) + r")\b", re.I)


SLOP = slop_pattern()
TRAILING_COND = re.compile(r"\s(if|when)\s", re.I)
# Every dash occurrence (not yet filtered to "casual punctuation only");
# ranges, flags, and list markers are excluded the same way ste_lint did.
DASH = re.compile(r"—|(?<!\d)–(?!\d)|(?<= )--(?= )|(?<=[^\s\d]{2}) - (?=[^\s\d]{2})")
ROTATION_SETS = [
    ("check-verify", re.compile(r"\b(check|verify|confirm|validate|ensure)\w*\b", re.I)),
    ("config-settings", re.compile(r"\b(config|configuration|settings)\b", re.I)),
]
LIMITS = {"procedural": 20, "descriptive": 25}
_LC_WORDS = frozenset({"a", "an", "the", "and", "but", "or", "nor", "of", "in", "on", "to", "for", "by", "at", "with"})


_HEADING = re.compile(r"^\s*#{1,6}\s")


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", " CODESPAN ", text)  # one word per SE Rule 8.6
    text = re.sub(r"https?://\S+", " URL ", text)
    return text


def sentences(text):
    """Split prose into sentence-ish units.

    Two kinds of line are dropped before the split, because neither is prose
    and both corrupt the sentence count:

      * A Markdown table row (a line whose first non-space character is `|`,
        including the `|---|` separator). Leaving the pipes in turns a whole
        table into two or three giant "sentences" that trip
        `sentence_over_limit`.
      * A Markdown ATX heading (`## ...`). A heading carries no terminal
        punctuation, so the sentence splitter cannot break after it. The
        heading then merges with the first sentence of the section body and
        inflates that sentence's length (a false `sentence_over_limit`) and
        can drag an `if` or `when` in the heading into a false
        `trailing_condition`. Headings have their own dedicated checks
        (`title_case_heading`, `emoji_decoration`), which read the raw text,
        so dropping them here loses no coverage.
    """
    lines = [
        ln
        for ln in text.splitlines()
        if not re.match(r"^\s*\|", ln) and not _HEADING.match(ln)
    ]
    text = "\n".join(lines)
    text = re.sub(r"^\s*([-*]|\d+\.)\s+", "", text, flags=re.M)  # list markers
    parts = re.split(r"(?<=[.!?:])\s+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


_LIST_OR_ROW = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|\|)")


def paragraph_units(text):
    """Split text into the units the two cumulative checks count within.

    A blank line ends a unit, as in the plain "paragraph = blank-line
    block" model. On top of that, each Markdown list item (`- `, `* `,
    `1. `) and each table row (`| ... |`) is its own unit. Without this,
    a six-item list or a three-row table where every item carries one
    lone, correct dash trips the ">=3 dashes in one paragraph" threshold
    (contradiction 3), and adjacent table rows with the same first cell
    trip `consecutive_same_start`.
    """
    units = []
    buf = []

    def flush():
        if buf:
            units.append("\n".join(buf))
            buf.clear()

    for line in text.splitlines():
        if not line.strip():
            flush()
            continue
        if _HEADING.match(line):
            # A heading ends the unit before it and starts nothing. It is not
            # prose, so its words never join the section body, and a dash in a
            # heading ("## Section 1 — Words") never counts toward a cluster.
            flush()
            continue
        if _LIST_OR_ROW.match(line):
            flush()
            units.append(line)
        else:
            buf.append(line)
    flush()
    return units


def _rule_title_case_heading(text):
    """Flag a Markdown heading that IS title case (sentence case wanted).

    The signal comes from non-first, non-phrase-initial "content" words.
    Three exclusions keep proper-noun and structured headings clean:

      * The first word of the heading is capitalized in both styles.
      * A phrase boundary (an em-dash, an opening paren, or a colon)
        starts a new phrase, and the first word after it is capitalized
        in both styles too. So "Words" in "Section 1 — Words (Rules ...)"
        and "Rules" after "(" are treated as phrase-initial, not as
        title-case evidence.
      * An all-caps acronym ("API") is capitalized under either style.
      * A lowercase function word ("with", "to", "the") is lowercase
        under either style, so it carries no signal; a *capitalized*
        function word ("With", "The") is abnormal and does count.

    Title case is declared only when at least two such words survive and
    every one of them is capitalized. A single trailing proper noun
    ("Working with Docker", "Deploy to Kubernetes", "Install Postgres")
    is one word, not two, so it never trips the check.
    """
    hits = 0
    for line in text.splitlines():
        m = re.match(r"^\s*(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        heading = re.sub(r"`[^`]*`", "", m.group(2).strip())
        content_words = []
        for segment in re.split(r"[—():]", heading):
            words = re.findall(r"[A-Za-z][A-Za-z'-]*", segment)
            for w in words[1:]:  # drop the phrase-initial word of each segment
                if w.isupper():
                    continue  # acronym: no signal
                if w.lower() in _LC_WORDS and not w[0].isupper():
                    continue  # lowercase function word: no signal
                content_words.append(w)
        if len(content_words) < 2:
            continue
        if all(w[0].isupper() for w in content_words):
            hits += 1
    return hits


_CONDITIONAL_STARTS = frozenset({"if", "when"})
# Placeholders `strip_code` leaves behind. They are not real words, so
# two rows whose first cell is inline code (both -> "CODESPAN") are not a
# genuine repeated opener.
_PLACEHOLDER_FIRST = frozenset({"codespan", "url"})


def _rule_consecutive_same_start(text):
    """Flag when 2+ adjacent sentences in a paragraph share a first token.

    Conditional openers ("If X. If Y.") are excluded: back-to-back
    conditionals are a normal procedural-writing pattern (a list of cases),
    not the LLM tic ("This enables. This allows.") this rule targets.

    Each list item and table row is its own paragraph unit (see
    `paragraph_units`), so a first-word repeat is only counted within one
    item or row, never across the rows of a table.
    """
    hits = 0
    for para in paragraph_units(text):
        sents = sentences(para)
        prev_first = None
        for s in sents:
            words = re.findall(r"[A-Za-z']+", s)
            if not words or words[0].lower() in _PLACEHOLDER_FIRST:
                prev_first = None
                continue
            first = words[0].lower()
            if (
                prev_first is not None
                and first == prev_first
                and first not in _CONDITIONAL_STARTS
            ):
                hits += 1
            prev_first = first
    return hits


def _rule_transition_opener(text):
    """Flag the 2nd+ sentence-initial transition opener per paragraph."""
    hits = 0
    for para in re.split(r"\n\s*\n", text):
        matches = _TRANSITION_RE.findall(para)
        if len(matches) > 1:
            hits += len(matches) - 1
    return hits


def _rule_em_dash_cumulative(text):
    """Cumulative dash check (contradiction 3): fires only on a cluster.

    >=2 dash-as-punctuation instances in one sentence, OR >=3 in one
    paragraph. A lone dash anywhere produces zero violations.
    """
    hits = 0
    for para in paragraph_units(text):
        para_total = len(DASH.findall(para))
        if para_total >= 3:
            hits += para_total
            continue
        for sent in sentences(para):
            sent_count = len(DASH.findall(sent))
            if sent_count >= 2:
                hits += sent_count
    return hits


def _rule_emoji_decoration(text):
    """Flag an emoji only where the spec means "decoration": in a heading
    line, or in the leader position of a list item (the first token right
    after the `-`/`*`/`1.` marker). An emoji in the middle of a prose
    sentence is not flagged, and `text` here is already code-stripped, so
    an emoji inside a fenced code block never reaches this check.
    """
    hits = 0
    for line in text.splitlines():
        heading = re.match(r"^\s*#{1,6}\s+(.*)$", line)
        if heading:
            hits += len(EMOJI.findall(heading.group(1)))
            continue
        leader = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(\S+)", line)
        if leader:
            hits += len(EMOJI.findall(leader.group(1)))
    return hits


def lint(text, text_type):
    body = strip_code(text)
    sents = sentences(body)
    limit = LIMITS[text_type]
    counts = {}
    lengths = [len(s.split()) for s in sents]
    counts["sentence_over_limit"] = sum(1 for n in lengths if n > limit)
    counts["banned_modal"] = len(BANNED_MODALS.findall(body))
    counts["perfect_tense"] = len([m for m in PERFECT.finditer(body)])
    counts["ing_clause"] = len(ING_CLAUSE.findall(body))
    counts["semicolon"] = body.count(";")
    counts["em_dash"] = _rule_em_dash_cumulative(body)
    counts["latin_abbrev"] = len(LATIN.findall(body))
    counts["slop_word"] = len(SLOP.findall(body))

    def trailing_cond(s):
        m = TRAILING_COND.search(s)
        if not m:
            return False
        line_start = s.rfind("\n", 0, m.start()) + 1
        return m.start() - line_start >= 4 and not re.match(r"^(if|when)\b", s, re.I)

    counts["trailing_condition"] = sum(1 for s in sents if trailing_cond(s))
    rotation = 0
    for _, rx in ROTATION_SETS:
        stems = {m.group(1).lower().rstrip("s") for m in rx.finditer(body)}
        if len(stems) > 1:
            rotation += len(stems) - 1
    counts["synonym_rotation"] = rotation
    counts["curly_quote"] = len(CURLY_QUOTE.findall(body))
    counts["title_case_heading"] = _rule_title_case_heading(body)
    counts["transition_opener"] = _rule_transition_opener(body)
    counts["consecutive_same_start"] = _rule_consecutive_same_start(body)
    counts["bold_mini_heading"] = len(BOLD_MINI_HEADING.findall(body))
    counts["emoji_decoration"] = _rule_emoji_decoration(body)
    counts["filter_word"] = len(FILTER_WORDS.findall(body))

    words = max(1, len(body.split()))
    total = sum(counts.values())
    return {
        "type": text_type,
        "words": words,
        "sentences": len(sents),
        "mean_sentence_words": round(sum(lengths) / max(1, len(lengths)), 1),
        "longest_sentence_words": max(lengths, default=0),
        "violations": counts,
        "violations_total": total,
        "violations_per_100w": round(100.0 * total / words, 2),
    }


SLOP_FIXTURE = """Leveraging our robust retry mechanism, failed uploads are automatically
reattempted, ensuring data integrity is maintained throughout the entire process which has
been designed from the ground up to gracefully handle even the most challenging network
interruptions. You should verify your credentials; it's also worth checking the settings,
e.g. the timeout config. Contact support if the problem persists."""

CLEAN_FIXTURE = """The system retries a failed upload automatically. This process keeps the data correct.

If failures continue, make sure that your credentials are correct. If the problem continues, contact support."""

CONTRACTION_FIXTURE = """It's fine. The build didn't fail this time, and we're confident it won't happen again.
You'll see the fix in the next release."""

# A lone dash must not fire; a cluster must.
DASH_LONE_FIXTURE = """The deploy failed — the disk was full.

Do not use --force against production. The window is 5 - 10 minutes."""

DASH_CLUSTER_FIXTURE = """The deploy failed — the disk was full — and the retry — which ran twice — also failed.

The upload failed -- the token expired -- and nobody -- not even the on-call engineer -- noticed."""

TITLE_CASE_FIXTURE = """## Getting Started With The API

Some text under the heading."""

SENTENCE_CASE_FIXTURE = """## Getting started with the API

Some text under the heading."""

TRANSITION_FIXTURE = """The service retries automatically. Additionally, it logs every attempt. Furthermore, it alerts on the third failure. Moreover, the alert includes the request ID."""

CURLY_QUOTE_FIXTURE = """She said, “this works.” Then she left."""

BOLD_MINI_HEADING_FIXTURE = """- **User Experience:** improved significantly this quarter."""

EMOJI_FIXTURE = """## 🚀 Launch

We shipped the update today."""

# An emoji inside a fenced code block, and an emoji mid-sentence in prose,
# are both left alone; only a heading or a list-item leader is flagged.
EMOJI_CODE_FIXTURE = """We shipped the update today 🚀 and it went fine.

```
print('🚀 done')
```
"""

EMOJI_LEADER_FIXTURE = """- 🚀 Shipped the new pipeline.
- Cleaned up the old one."""

FILTER_WORD_FIXTURE = """The on-call engineer felt the rollback was too risky to attempt."""

# A non-conditional repeat must fire (contrast with CLEAN_FIXTURE's "If X. If Y."
# exemption, which must not).
REPEAT_START_FIXTURE = """The service logged the error. The service logged the retry."""

# Each table row / list item carries ONE lone, correct dash. That is never
# a cluster (contradiction 3), so em_dash must stay 0.
DASH_TABLE_FIXTURE = """| Field | Note |
|---|---|
| timeout | the client wait — in seconds |
| retries | attempts before failure — capped at five |
| backoff | delay between attempts — doubles each time |"""

DASH_LIST_FIXTURE = """1. Set the timeout — 30 seconds is typical.
2. Set the retry count — three is typical.
3. Enable backoff — exponential is the default.
4. Turn on logging — debug level for the first run."""

# Two-plus table rows whose first cell is inline code must not register as
# a repeated sentence opener.
CODE_ROW_FIXTURE = """| Command | Effect |
|---|---|
| `git add` | stages the change |
| `git commit` | records the snapshot |
| `git push` | uploads the commits |"""

# A wide Markdown table must not become a giant over-limit "sentence".
TABLE_LONG_ROW_FIXTURE = """| Setting | Explanation |
|---|---|
| timeout | The number of seconds the client waits for a response from the server before it gives up and reports a connection error to the caller and writes the failure to the log for the on-call engineer to review later. |"""

# Proper-noun and structured headings are sentence case already; the
# capitalized words are proper nouns or phrase-initial, not title case.
PROPER_NOUN_HEADING_FIXTURE = """## Working with Docker

Body.

## Deploy to Kubernetes

Body.

## Install Postgres

Body.

### Section 1 — Words (Rules 1.1-1.15)

Body."""

# "key" / "gate" match as exact words only: keyword, keyboard, gateway
# must not count.
SLOP_KEY_GATE_FIXTURE = """The API key is a keyword in the keyboard config."""

# A Markdown heading has no terminal punctuation. It must not merge with the
# first sentence of the section body. Each body sentence below is short and
# clean on its own; only the heading+body merge would push a unit over the
# limit or read as a trailing condition.
HEADING_MERGE_FIXTURE = """## How to roll out the change to every region

Apply the manifest to one region first and watch the error rate for ten minutes.

## Roll back the change if the error rate climbs

Delete the new manifest and re-apply the previous one from the archive folder."""

# A heading that itself contains "if" or "when" must not create a
# trailing_condition on the body sentence it would otherwise merge with.
HEADING_CONDITION_FIXTURE = """## What to do when the build fails

Read the last 50 lines of the log. Re-run the job once.

## Escalate if the second run also fails

Page the on-call engineer with the job URL and the error line."""


def self_test():
    # The self-test must not depend on a machine's learned.json.
    os.environ["AUTHENGENTIC_DISABLE_LEARN"] = "1"
    global SLOP
    SLOP = slop_pattern()
    slop = lint(SLOP_FIXTURE, "procedural")
    clean = lint(CLEAN_FIXTURE, "procedural")
    contractions = lint(CONTRACTION_FIXTURE, "descriptive")
    dash_lone = lint(DASH_LONE_FIXTURE, "descriptive")
    dash_cluster = lint(DASH_CLUSTER_FIXTURE, "descriptive")
    title_case = lint(TITLE_CASE_FIXTURE, "descriptive")
    sentence_case = lint(SENTENCE_CASE_FIXTURE, "descriptive")
    transitions = lint(TRANSITION_FIXTURE, "descriptive")
    curly = lint(CURLY_QUOTE_FIXTURE, "descriptive")
    bold_heading = lint(BOLD_MINI_HEADING_FIXTURE, "descriptive")
    emoji = lint(EMOJI_FIXTURE, "descriptive")
    emoji_code = lint(EMOJI_CODE_FIXTURE, "descriptive")
    emoji_leader = lint(EMOJI_LEADER_FIXTURE, "descriptive")
    filter_word = lint(FILTER_WORD_FIXTURE, "descriptive")
    repeat_start = lint(REPEAT_START_FIXTURE, "descriptive")
    dash_table = lint(DASH_TABLE_FIXTURE, "descriptive")
    dash_list = lint(DASH_LIST_FIXTURE, "descriptive")
    code_row = lint(CODE_ROW_FIXTURE, "descriptive")
    table_long_row = lint(TABLE_LONG_ROW_FIXTURE, "procedural")
    proper_noun_heading = lint(PROPER_NOUN_HEADING_FIXTURE, "descriptive")
    slop_key_gate = lint(SLOP_KEY_GATE_FIXTURE, "descriptive")
    heading_merge = lint(HEADING_MERGE_FIXTURE, "procedural")
    heading_condition = lint(HEADING_CONDITION_FIXTURE, "procedural")

    assert "contraction" not in slop["violations"], "contraction key must not exist (contradiction 1)"
    assert slop["violations"]["sentence_over_limit"] >= 1, slop
    assert slop["violations"]["banned_modal"] >= 1, slop
    assert slop["violations"]["perfect_tense"] >= 1, slop
    assert slop["violations"]["ing_clause"] >= 1, slop
    assert slop["violations"]["semicolon"] == 1, slop
    assert slop["violations"]["latin_abbrev"] >= 1, slop
    assert slop["violations"]["slop_word"] >= 2, slop
    assert slop["violations"]["trailing_condition"] >= 1, slop
    assert slop["violations"]["synonym_rotation"] >= 1, slop
    assert clean["violations_total"] == 0, clean

    assert contractions["violations_total"] == 0, (
        f"contractions must never be flagged (contradiction 1): {contractions}"
    )

    assert dash_lone["violations"]["em_dash"] == 0, (
        f"a lone dash per sentence must not fire (contradiction 3): {dash_lone}"
    )
    assert dash_cluster["violations"]["em_dash"] >= 4, (
        f"a dash cluster must fire (contradiction 3): {dash_cluster}"
    )

    assert title_case["violations"]["title_case_heading"] >= 1, (
        f"a title-case heading must be flagged (contradiction 2): {title_case}"
    )
    assert sentence_case["violations"]["title_case_heading"] == 0, (
        f"a sentence-case heading must not be flagged (contradiction 2): {sentence_case}"
    )

    assert transitions["violations"]["transition_opener"] >= 2, transitions

    assert curly["violations"]["curly_quote"] >= 1, curly
    assert bold_heading["violations"]["bold_mini_heading"] >= 1, bold_heading
    assert emoji["violations"]["emoji_decoration"] >= 1, emoji
    assert emoji_code["violations"]["emoji_decoration"] == 0, (
        f"an emoji in a code fence or mid-prose is not decoration: {emoji_code}"
    )
    assert emoji_leader["violations"]["emoji_decoration"] >= 1, (
        f"an emoji as a list-item leader is decoration: {emoji_leader}"
    )
    assert filter_word["violations"]["filter_word"] >= 1, filter_word
    assert repeat_start["violations"]["consecutive_same_start"] >= 1, (
        f"a genuine non-conditional repeat must fire: {repeat_start}"
    )
    assert clean["violations"]["consecutive_same_start"] == 0, (
        f"the 'If X. If Y.' conditional exemption must still hold: {clean}"
    )

    assert dash_table["violations"]["em_dash"] == 0, (
        f"one lone dash per table row is not a cluster (contradiction 3): {dash_table}"
    )
    assert dash_list["violations"]["em_dash"] == 0, (
        f"one lone dash per list item is not a cluster (contradiction 3): {dash_list}"
    )
    assert code_row["violations"]["consecutive_same_start"] == 0, (
        f"code-first table rows are not a repeated opener: {code_row}"
    )
    assert table_long_row["violations"]["sentence_over_limit"] == 0, (
        f"a wide table row is not an over-limit sentence: {table_long_row}"
    )
    assert proper_noun_heading["violations"]["title_case_heading"] == 0, (
        f"proper-noun and phrase-initial headings are sentence case: {proper_noun_heading}"
    )
    assert slop_key_gate["violations"]["slop_word"] == 1, (
        f"'key'/'gate' match exact words only, not keyword/keyboard/gateway: {slop_key_gate}"
    )

    assert heading_merge["violations"]["sentence_over_limit"] == 0, (
        f"a heading must not merge with the body sentence and inflate it: {heading_merge}"
    )
    assert heading_merge["violations"]["trailing_condition"] == 0, (
        f"an 'if' in a heading must not become a trailing condition: {heading_merge}"
    )
    assert heading_merge["violations_total"] == 0, heading_merge
    assert heading_condition["violations"]["trailing_condition"] == 0, (
        f"a 'when'/'if' heading must not flag the body it precedes: {heading_condition}"
    )
    assert heading_condition["violations_total"] == 0, heading_condition

    print(
        "self-test OK:", slop["violations_total"], "violations in slop fixture, 0 in clean, "
        "0 in contractions fixture, dash cumulative + title-case + transition checks pass, "
        "curly-quote + bold-mini-heading + emoji + filter-word + consecutive-same-start checks pass, "
        "heading lines do not merge with the section body",
    )


USAGE = "usage: authengentic_lint.py [--type procedural|descriptive] [--gate] (FILE|-) | --self-test"


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        self_test()
        return 0
    gate = "--gate" in args
    if gate:
        args.remove("--gate")
    text_type = "descriptive"
    if "--type" in args:
        i = args.index("--type")
        if i + 1 >= len(args):
            sys.exit("missing value after --type\n" + USAGE)
        text_type = args[i + 1]
        del args[i:i + 2]
    if text_type not in LIMITS:
        sys.exit("unknown --type %r (expected procedural or descriptive)\n%s" % (text_type, USAGE))
    if len(args) != 1:
        sys.exit(USAGE)
    src = args[0]
    if src == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(src, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as err:
            sys.exit(str(err))
    report = lint(text, text_type)
    print(json.dumps(report, indent=2))
    return 1 if gate and report["violations_total"] else 0


if __name__ == "__main__":
    sys.exit(main())
