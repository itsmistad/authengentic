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


def slop_pattern():
    """Union of the measured core list and evals/slop.tsv (term, source, swap).

    Falls back to the core list when the file is absent. Comment lines
    (leading '#') and blank lines are skipped.
    """
    terms = []
    if SLOP_TSV.exists():
        for line in SLOP_TSV.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            term = line.split("\t")[0].strip().lower()
            if term:
                terms.append(re.escape(term).replace(r"\ ", r"\s+") + r"\w*")
    if not terms:
        return SLOP_CORE
    return re.compile(SLOP_CORE.pattern[:-len(r")\b")] + "|" + "|".join(terms) + r")\b", re.I)


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


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", " CODESPAN ", text)  # one word per SE Rule 8.6
    text = re.sub(r"https?://\S+", " URL ", text)
    return text


def strip_code_keep_headings(text):
    """Like strip_code, but leaves ATX headings (#...) intact for the
    heading-case and consecutive-same-start passes, which need them."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", " CODESPAN ", text)
    text = re.sub(r"https?://\S+", " URL ", text)
    return text


def sentences(text):
    text = re.sub(r"^\s*([-*]|\d+\.)\s+", "", text, flags=re.M)  # list markers
    parts = re.split(r"(?<=[.!?:])\s+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def _rule_title_case_heading(text):
    """Flag a Markdown heading that IS title case (sentence case wanted).

    Signal comes only from non-first "content" words (skipping the first
    word, which is capitalized in both styles, and skipping function
    words like "with"/"the", which stay lowercase in both styles). An
    all-caps acronym (e.g. "API") is also excluded from the signal: it is
    capitalized under either style, so it cannot tell title case from
    sentence case — counting it as generic evidence of capitalization is
    what makes a sentence-case heading ending in an acronym look like
    title case. Title case is declared only when every remaining content
    word is capitalized, and at least one such word exists.
    """
    hits = 0
    for line in text.splitlines():
        m = re.match(r"^\s*(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        heading = m.group(2).strip()
        heading = re.sub(r"`[^`]*`", "", heading)
        words = re.findall(r"[A-Za-z][A-Za-z'-]*", heading)
        if len(words) < 2:
            continue
        content_words = [
            w for w in words[1:]
            if w.lower() not in _LC_WORDS and not w.isupper()
        ]
        if not content_words:
            continue
        capitalized_content = sum(1 for w in content_words if w[0].isupper())
        if capitalized_content == len(content_words):
            hits += 1
    return hits


_CONDITIONAL_STARTS = frozenset({"if", "when"})


def _rule_consecutive_same_start(text):
    """Flag when 2+ adjacent sentences in a paragraph share a first token.

    Conditional openers ("If X. If Y.") are excluded: back-to-back
    conditionals are a normal procedural-writing pattern (a list of cases),
    not the LLM tic ("This enables. This allows.") this rule targets.
    """
    hits = 0
    for para in re.split(r"\n\s*\n", text):
        sents = sentences(para)
        prev_first = None
        for s in sents:
            words = re.findall(r"[A-Za-z']+", s)
            if not words:
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
    for para in re.split(r"\n\s*\n", text):
        para_total = len(DASH.findall(para))
        if para_total >= 3:
            hits += para_total
            continue
        for sent in sentences(para):
            sent_count = len(DASH.findall(sent))
            if sent_count >= 2:
                hits += sent_count
    return hits


def lint(text, text_type):
    body = strip_code(text)
    heading_body = strip_code_keep_headings(text)
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
    counts["title_case_heading"] = _rule_title_case_heading(heading_body)
    counts["transition_opener"] = _rule_transition_opener(body)
    counts["consecutive_same_start"] = _rule_consecutive_same_start(body)
    counts["bold_mini_heading"] = len(BOLD_MINI_HEADING.findall(text))
    counts["emoji_decoration"] = len(EMOJI.findall(text))
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

FILTER_WORD_FIXTURE = """She felt nervous as the deadline approached."""

# A non-conditional repeat must fire (contrast with CLEAN_FIXTURE's "If X. If Y."
# exemption, which must not).
REPEAT_START_FIXTURE = """She noted the door. She noted the lock."""


def self_test():
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
    filter_word = lint(FILTER_WORD_FIXTURE, "descriptive")
    repeat_start = lint(REPEAT_START_FIXTURE, "descriptive")

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
    assert filter_word["violations"]["filter_word"] >= 1, filter_word
    assert repeat_start["violations"]["consecutive_same_start"] >= 1, (
        f"a genuine non-conditional repeat must fire: {repeat_start}"
    )
    assert clean["violations"]["consecutive_same_start"] == 0, (
        f"the 'If X. If Y.' conditional exemption must still hold: {clean}"
    )

    print(
        "self-test OK:", slop["violations_total"], "violations in slop fixture, 0 in clean, "
        "0 in contractions fixture, dash cumulative + title-case + transition checks pass, "
        "curly-quote + bold-mini-heading + emoji + filter-word + consecutive-same-start checks pass",
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
