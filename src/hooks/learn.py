#!/usr/bin/env python3
"""Automatic learning for the authengentic hooks.

The Stop and PostToolUse hooks call `record()` after they print a
violation summary. `record()` writes three files under the bucket
`${CLAUDE_CONFIG_DIR:-~/.claude}/authengentic/` and never touches the
plugin folder, which is a cache that Claude Code can wipe.

Files in the bucket:

- `observations.jsonl` — one line per rule per event, capped at
  OBSERVATION_CAP lines.
- `profile.json` — a decayed score per rule. The score halves every 30
  days, so the digest tracks recent habits, not the whole history.
- `digest.md` — regenerated on every call. It ranks the rules you break
  most, and lists the terms the `/authengentic-learn` command promoted.
  `src/hooks/authengentic-activate.js` injects it at session start.

`learned.json` also lives in the bucket. The `/authengentic-learn`
command writes it. The linter and the hook read it through
`load_learned()` to extend their term lists. This module only reads it.

Every function swallows its own errors. Learning must never break a hook.
"""
import json
import os
import pathlib
import time

OBSERVATION_CAP = 2000
HALF_LIFE_SECONDS = 30 * 24 * 60 * 60
DIGEST_RULES = 8
DROP_BELOW = 1.0

# The rule key -> a short line for the digest. A reader outside the
# project must understand each one.
RULE_GUIDANCE = {
    "sentence_over_limit": "Split the sentence. 20 words for a step, 25 for a description.",
    "banned_modal": "Use can, will, or must. Drop should, would, may, might, could.",
    "semicolon": "Write two sentences.",
    "perfect_tense": "Use the simple past. \"has done\" becomes \"did\".",
    "ing_clause": "No \"-ing\" verb right after a comma. Start a new sentence.",
    "slop_word": "Delete the empty word.",
    "curly_quote": "Use straight quotes.",
    "latin_abbrev": "Write \"for example\" and \"that is\".",
    "em_dash": "A lone dash is fine. Break a cluster with a word or a full stop.",
    "filter_word": "State the thing. Drop felt, seemed, noticed, realized.",
    "trailing_condition": "Put the condition first, with a comma.",
    "synonym_rotation": "Pick one term and keep it for the whole document.",
    "consecutive_same_start": "Vary the first word of consecutive sentences.",
    "transition_opener": "Do not open with Additionally, Furthermore, Moreover.",
    "title_case_heading": "Write headings in sentence case.",
    "bold_mini_heading": "Use a real heading, not a bold run-in.",
    "emoji_decoration": "No emoji as structure.",
}

# The linter and the hook read these categories from learned.json.
LEARNED_CATEGORIES = ("slop", "openers", "closers")


def bucket():
    """The directory for generated files. Honors AUTHENGENTIC_CONFIG_DIR
    first (tests set it), then CLAUDE_CONFIG_DIR, then ~/.claude."""
    override = os.environ.get("AUTHENGENTIC_CONFIG_DIR")
    if override:
        base = pathlib.Path(override)
    else:
        cfg = os.environ.get("CLAUDE_CONFIG_DIR")
        base = pathlib.Path(cfg) if cfg else pathlib.Path.home() / ".claude"
    return base / "authengentic"


def _path(name):
    return bucket() / name


def _read_json(name, default):
    try:
        return json.loads(_path(name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(name, data):
    target = _path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _decay(score, last, now):
    if not last or now <= last:
        return score
    return score * (0.5 ** ((now - last) / HALF_LIFE_SECONDS))


def load_learned():
    """Return {category: [term, ...]} for the categories the linter and
    the hook extend. Missing file or bad shape returns empty lists."""
    raw = _read_json("learned.json", {})
    out = {cat: [] for cat in LEARNED_CATEGORIES}
    if isinstance(raw, dict):
        for cat in LEARNED_CATEGORIES:
            value = raw.get(cat)
            if isinstance(value, list):
                out[cat] = [str(v) for v in value if isinstance(v, str)]
    return out


def _extras_for(rule, report_extras):
    return report_extras.get(rule, []) if report_extras else []


TOKENS_PER_RULE = 12


def _merge_tokens(existing, new):
    """A small frequency map, token -> count, capped at TOKENS_PER_RULE
    by dropping the least frequent."""
    counts = dict(existing) if isinstance(existing, dict) else {}
    for token in new:
        key = str(token).strip().lower()
        if key:
            counts[key] = counts.get(key, 0) + 1
    if len(counts) > TOKENS_PER_RULE:
        keep = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:TOKENS_PER_RULE]
        counts = dict(keep)
    return counts


def _append_observations(rows):
    target = _path("observations.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    _trim_observations(target)


def _trim_observations(target):
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if len(lines) > OBSERVATION_CAP:
        target.write_text("\n".join(lines[-OBSERVATION_CAP:]) + "\n", encoding="utf-8")


def record(source, lint, text, session, report_extras=None):
    """Score `text` with the descriptive linter and fold every non-zero
    violation into the profile. Then regenerate the digest. `source` is
    "stop" or "post_tool_use". `report_extras` optionally maps a rule to
    the offending tokens, for the observation log."""
    try:
        if lint is None or not (text or "").strip():
            return
        counts = {
            key: value
            for key, value in lint.lint(text, "descriptive")["violations"].items()
            if value
        }
        if not counts:
            return
        now = time.time()
        profile = _read_json("profile.json", {})
        rules = profile.get("rules", {}) if isinstance(profile, dict) else {}
        rows = []
        for key, count in counts.items():
            entry = rules.get(key, {"score": 0.0, "last": 0, "tokens": {}})
            entry["score"] = _decay(entry.get("score", 0.0), entry.get("last", 0), now) + count
            entry["last"] = now
            tokens = _extras_for(key, report_extras)
            entry["tokens"] = _merge_tokens(entry.get("tokens", {}), tokens)
            rules[key] = entry
            rows.append({
                "ts": round(now, 3),
                "session": session or "unknown",
                "source": source,
                "rule": key,
                "count": count,
                "tokens": tokens,
            })
        _write_json("profile.json", {"rules": rules, "updated": now})
        _append_observations(rows)
        regenerate_digest()
    except Exception:  # noqa: BLE001
        return


def _ranked_rules(now):
    profile = _read_json("profile.json", {})
    rules = profile.get("rules", {}) if isinstance(profile, dict) else {}
    scored = []
    for key, entry in rules.items():
        value = _decay(entry.get("score", 0.0), entry.get("last", 0), now)
        if value >= DROP_BELOW:
            scored.append((key, value, entry.get("tokens", {})))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:DIGEST_RULES]


def _top_tokens(tokens, limit=4):
    if not isinstance(tokens, dict) or not tokens:
        return ""
    ranked = sorted(tokens.items(), key=lambda item: item[1], reverse=True)
    return ", ".join(term for term, _ in ranked[:limit])


def regenerate_digest():
    """Rewrite digest.md from profile.json and learned.json. Remove it
    when there is nothing to say."""
    try:
        now = time.time()
        ranked = _ranked_rules(now)
        learned = load_learned()
        learned_lines = [
            f"- {cat}: {', '.join(terms)}"
            for cat, terms in learned.items()
            if terms
        ]
        if not ranked and not learned_lines:
            _path("digest.md").unlink(missing_ok=True)
            return
        lines = [
            "AUTHENGENTIC — YOUR RECURRING MISTAKES HERE",
            "",
            "This list comes from your own violations in this environment, ranked "
            "by a decayed count. Check the top items before you send.",
            "",
        ]
        for index, (key, value, tokens) in enumerate(ranked, start=1):
            label = key.replace("_", " ")
            guide = RULE_GUIDANCE.get(key, "")
            seen = _top_tokens(tokens)
            tail = f" You keep writing: {seen}." if seen else ""
            lines.append(f"{index}. {label} ({round(value)}). {guide}{tail}".rstrip())
        if learned_lines:
            lines.append("")
            lines.append("Terms the linter learned here. These now flag like the built-in lists.")
            lines.append("")
            lines.extend(learned_lines)
        _write_json_text("digest.md", "\n".join(lines) + "\n")
    except Exception:  # noqa: BLE001
        return


def _write_json_text(name, text):
    target = _path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def read_digest():
    """The digest text for the SessionStart hook, or an empty string."""
    try:
        return _path("digest.md").read_text(encoding="utf-8")
    except OSError:
        return ""


if __name__ == "__main__":
    # Manual regeneration: python3 learn.py
    regenerate_digest()
    print(str(_path("digest.md")))
