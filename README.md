# authengentic

Write non-fiction English that a smart reader outside your field understands on one read, and that reads as though a person wrote it, not a language model.

authengentic merges four writing-rule projects into one non-fiction ruleset:

- [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) gives the ASD-STE100 Simplified Technical English base: short sentences, active voice, simple tenses, one word one meaning, condition before command, and the plugin, hook, and linter mechanism.
- [agent-style](https://github.com/yzhao062/agent-style) gives the RULE-01 through RULE-12 and RULE-A through RULE-I directives, plus the mechanical detectors for dash clusters, title-case headings, and repeated sentence openers.
- [humanizer](https://github.com/blader/humanizer) gives the Wikipedia "Signs of AI writing" pattern catalog and the voice-matching-from-a-sample mechanism.
- [sepia](https://github.com/Nanako0129/sepia) gives the professional-pass checklist, the per-domain rule files, the calibration principles, and the model-fingerprint tables.

None of their code is vendored. Their prose and detector logic is re-expressed here. Full attribution and licenses are in [SOURCES.md](SOURCES.md).

Scope is non-fiction: documentation, technical prose, and professional prose. It does not touch fiction or marketing copy, on purpose.

## Install

**Claude Code plugin** (skill, session hook, output style):

```bash
claude plugin marketplace add /Users/dj/Documents/Personal/Code/authengentic
claude plugin install authengentic@authengentic
```

The plugin also ships an [output style](https://code.claude.com/docs/en/output-styles), named `authengentic:authengentic`. The short name does not resolve. For one project, run `/config`, open **Output style**, and select it. For all projects, put `{"outputStyle": "authengentic:authengentic"}` in `~/.claude/settings.json` and start Claude Code again.

**Codex plugin** (skill, session hook):

```bash
codex plugin marketplace add /Users/dj/Documents/Personal/Code/authengentic
codex plugin add authengentic@authengentic
```

Then ask for any technical or professional writing, or say: *"rewrite this with authengentic"*.

## What's different from SimpleEnglish

authengentic overrules its parent on four points. Each is stated in full in [SKILL.md, "Where authengentic differs from its sources"](skills/authengentic/SKILL.md#where-authengentic-differs-from-its-sources).

1. **Contractions are restored, not banned.** SimpleEnglish's old Rule 4.2 and agent-style's RULE-I are both repealed. Grammar stays complete (articles, "that", no telegraph style), and you use contractions where a person would. A document with every sentence spelled out reads as machine-written. The modal ladder is untouched: `can`, `will`, and `must` stay, and a contracted banned modal such as "shouldn't" stays banned.
2. **Headings are sentence case, not title case.** This overrides agent-style's RULE-G, which asks for title case in academic and engineering venues. Rule 8.9 carries it, with no venue exception and no mode exception. Proper nouns and code identifiers inside a heading keep their own capitalization.
3. **Dashes are judged by cluster, not per instance.** A lone, correctly placed em-dash or en-dash is fine. Only a cluster triggers a fix: two or more dashes acting as punctuation in one sentence, or three or more in one paragraph. "Correcting" a single clean dash is itself a tell. A numeric range (`5-10`), a CLI flag (`--force`), and a list marker never count.
4. **Every other pattern is fix-on-first-hit.** The cluster carve-out applies to dashes and nothing else. A banned modal, a semicolon, a perfect tense, an `-ing` clause, a slop word, a filler phrase, a trailing condition, a title-case heading: fix each one on its first occurrence.

## See it

Left is real, unedited Claude output. Right is the same model with authengentic loaded. The right column keeps two contractions and one em-dash, and all three are correct, so authengentic leaves them alone (differences 1 and 3 above).

<table>
<tr>
<th width="50%">Without authengentic</th>
<th width="50%">With authengentic</th>
</tr>
<tr>
<td valign="top">

> Leveraging sqlpipe's robust architecture, users can seamlessly synchronize their Postgres tables to S3 with minimal configuration overhead. Before getting started, you should ensure that your AWS credentials have been properly configured — this is crucial for avoiding frustrating permission issues down the line.

</td>
<td valign="top">

> sqlpipe copies your Postgres tables to S3. It needs one configuration file, and you don't have to create the bucket first.
>
> Before you start, make sure that your AWS credentials are correct — the upload runs as your IAM user, not as sqlpipe. If they aren't, S3 rejects the write with a permission error.

</td>
</tr>
</table>

## The rules

53 numbered rules across sections 1 through 9, paraphrased with software examples in [`SKILL.md`](skills/authengentic/SKILL.md). Those sections are the ASD-STE100 Issue 9 catalog, extended in place with the merged material. A tenth section is authengentic's own: reader, parallelism, word order, end weight, evidence-matched claims, and the middle-of-document choke point.

Around the catalog:

- **The merged AI-tells catalog.** 38 numbered patterns from the Wikipedia "Signs of AI writing" list and the three source projects, each with a before and after, in [`references/ai-tells.md`](skills/authengentic/references/ai-tells.md).
- **Four operations.** `write` is new content. `review` diagnoses only and changes nothing. `refactor` is a minimal in-place revision that keeps the structure and voice. `recreate` is a full rewrite from an extracted fact list. Operations and modes are independent axes.
- **Two modes.** Plain (default) writes for a smart reader outside the field. Strict adds the STE dictionary discipline when you name STE, ASD-STE100, or compliance.
- **Domain files.** Release notes, dev replies, postmortems, tickets, technical articles, error messages, and API docs, in [`references/domains/`](skills/authengentic/references/domains).

## License

MIT for everything in this repo. Full text in [LICENSE](LICENSE).

authengentic re-expresses rule content from four upstream projects. [SOURCES.md](SOURCES.md) lists each one, its license, and what was used. agent-style's `RULES.md` rule text is CC-BY-4.0, so SOURCES.md is a required attribution wherever authengentic's rule text draws on it. The other three sources are MIT.
