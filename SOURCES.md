# Sources

authengentic merges rule content from four upstream projects. None of their
code is vendored. Their prose and detector *logic* is adapted and re-expressed
here.

| Project | URL | License | What was used |
|---|---|---|---|
| SimpleEnglish | https://github.com/AminBlg/SimpleEnglish | MIT | Base rule catalog (ASD-STE100 derivative), plugin/hook mechanism, linter structure, output-style format |
| agent-style | https://github.com/yzhao062/agent-style | Code: MIT. `RULES.md` rule text: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) | RULE-01–12 and RULE-A–I directives and rationale (re-expressed, not copied verbatim except short quoted phrases), mechanical detector logic (dash, title-case, transition-opener, consecutive-same-start) |
| humanizer | https://github.com/blader/humanizer | MIT | Wikipedia "Signs of AI writing"-derived pattern catalog (its numbered pattern catalog, ~25–35 numbered entries depending on version), voice-matching-from-sample mechanism |
| sepia | https://github.com/Nanako0129/sepia | MIT | Professional-pass checklist, domain rule files (release notes, dev-replies, postmortems, tickets, tech-articles), calibration principles, model-fingerprint tables (non-fiction prose layer only) |

Because agent-style's `RULES.md` prose is licensed
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/), this attribution
file is required wherever authengentic's rule text draws on it.

**Modified:** agent-style's rule text was re-expressed and condensed, and in
four places (contractions restored, headings forced to sentence case, dashes
judged by cluster, every other pattern fixed on first hit) it was deliberately
overruled. See SKILL.md, "Where authengentic differs from its sources".

authengentic's own files are released under the MIT license in `LICENSE`. The
merged rule text adapted from agent-style's `RULES.md` remains under CC-BY-4.0.
