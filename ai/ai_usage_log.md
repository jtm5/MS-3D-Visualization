# AI Usage Log: MS-3D-Visualization

This log records every substantive AI-assisted session on the project "Meteor Scatter 3D Explorer".

Required by the HamSCI Generative AI Use Agreement, and by any institutional or funder policy
that applies to this project (see `.claude/rules/ai-governance.md`).

**This log is the source of truth for what AI did on this project.** A disclosure paragraph in a
manuscript, poster, or software release summarizes this log truthfully. Keep it current: an
entry written from memory weeks later is not a record.

## Entry format

```
## [YYYY-MM-DD HH:MM TZ]
- **Tool**: Claude (Anthropic), <exact-model-id>
- **Session Purpose**: What the session set out to accomplish
- **Sections/Files Affected**: Specific files, sections, or documents touched
- **Nature of Contribution**: Draft / Edit / Analysis / Code generation / Research / Scaffolding
- **Human Review Status**: Reviewed and verified / Partially reviewed / Pending review
- **Git Hash**: <filled in after committing>
```

The date and time come from the system clock via `date`, never from an estimate. The `/commit`
command produces this format and appends it in the right order.

---

<!-- Append new entries below this line, newest at the bottom. -->

## [2026-11-24 17:09 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Adopt the HamSCI `ai_project_template` (commit `a09f960`) into this
  existing repository, at N. A. Frissell's (W2NAF) request, for review by the repository owner.
- **Sections/Files Affected**: `CLAUDE.md` (new; project overview, goal and repository structure
  filled in from `README.md`; lead callsign, institution, funder, working group and period left
  for the lead), `.claude/` (new: `settings.json`, `template.json`, `commands/commit.md`,
  `commands/template-sync.md`, `hooks/template_check.sh`, `rules/ai-governance.md`,
  `rules/hamsci-data.md`, `rules/python-code.md`), `.github/ISSUE_TEMPLATE/` (new),
  `ai/ai_usage_log.md` (new), `docs/GETTING_STARTED.md` (new), `.gitignore` (new),
  `__pycache__/*.pyc` (untracked; now ignored)
- **Nature of Contribution**: Scaffolding
- **Human Review Status**: Pending review
- **Git Hash**: [fill in after committing]
