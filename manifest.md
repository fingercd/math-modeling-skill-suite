# manifest.md

Generated: 2026-07-04

## Deliverable

| Path | Type | Purpose |
| --- | --- | --- |
| `README.md` | guide | Explain how to use the suite |
| `LICENSE` | license | MIT open-source license |
| `manifest.md` | manifest | List files and validation notes |
| `math-modeling-suite/SKILL.md` | skill | Six-stage controller |
| `math-modeling-research/SKILL.md` | skill | Research workflow |
| `math-modeling-writer/SKILL.md` | skill | Paper and LaTeX workflow |
| `math-modeling-code/SKILL.md` | skill | Python/Excel code workflow |
| `math-modeling-review/SKILL.md` | skill | Independent review workflow |
| `*/agents/openai.yaml` | metadata | UI metadata and default prompt for each skill |
| `references/stage-gates.md` | reference | Six-stage rules and transition gates |
| `references/cumcm-2026-notes.md` | reference | CUMCM-style paper and compliance notes |
| `references/model-method-map.md` | reference | Modeling method selection map |
| `references/review-checklist.md` | reference | Independent reviewer checklist |
| `references/cross-device-collaboration.md` | reference | Lightweight cross-device usage tips |
| `references/code-tuning-guide.md` | reference | Lightweight model tuning guidance |
| `templates/first-response.md` | template | First response template for contest/problem-only requests |
| `templates/stage-files/*.md` | template | Stage record templates |
| `templates/cumcm/main.tex` | template | Editable CUMCM-style LaTeX skeleton |
| `templates/figures/flowchart-placeholder.md` | template | Flowchart placeholder and insertion guide |
| `templates/tables/result-table-template.md` | template | Result table placeholders |
| `templates/outputs/*.md` | template | Final delivery README, manifest, and AI-use statement templates |

## Source Basis

- User-approved implementation plan in current conversation.
- RIPER-5 phase gating idea: `NeekChaw/RIPER-5`.
- CUMCM/高教社杯 2026-style paper requirements from official format notes gathered during planning.
- Comparable math-modeling skill repositories and reviewer checklist references gathered during planning.

## Validation Commands

Run from the repository root:

```powershell
python C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/math-modeling-skill-suite/math-modeling-suite
python C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/math-modeling-skill-suite/math-modeling-research
python C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/math-modeling-skill-suite/math-modeling-writer
python C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/math-modeling-skill-suite/math-modeling-code
python C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/math-modeling-skill-suite/math-modeling-review
```

## Known Limits

- The suite is a handoff deliverable and is not installed into local Codex.
- `templates/cumcm/main.tex` is a practical skeleton, not an official class file.
- Official contest rules must be checked again before live submission.
