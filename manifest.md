# manifest.md

Generated: 2026-07-05
Version: 2.0.0

## Deliverable

| Path | Type | Purpose |
| --- | --- | --- |
| `README.md` | guide | Explain how to use the suite |
| `LICENSE` | license | MIT open-source license |
| `VERSION` | release marker | Current suite version |
| `CHANGELOG.md` | release notes | v2.0.0 changes |
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
| `templates/contracts/*.json` | template | Result, constraint, and figure machine-readable contracts |
| `templates/project/.gitignore` | template | Recommended project-level ignore rules |
| `scripts/validate_skill_suite.py` | validator | Read-only suite static validation |
| `scripts/validate_project_delivery.py` | validator | Read-only project delivery validation |
| `scripts/run_regression_checks.py` | validator | Evidence regression checks |
| `tests/evidence/pressure-run-2026-07-05/` | evidence | 2023A / 2024C / 2025B pressure-run archive |
| `tests/evidence/expected_failures.json` | evidence config | Expected validator findings for pressure-run archive |
| `AUDIT_PROMPT.md` | audit prompt | Independent audit prompt for the pressure run |
| `AUDIT_REPORT.md` | audit report | Independent audit report that motivated v2.0.0 |

## Source Basis

- User-approved implementation plan in current conversation.
- RIPER-5 phase gating idea: `NeekChaw/RIPER-5`.
- CUMCM/高教社杯 2026-style paper requirements from official format notes gathered during planning.
- Comparable math-modeling skill repositories and reviewer checklist references gathered during planning.

## Validation Commands

Run from the repository root:

```powershell
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/validate_skill_suite.py --root .
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/run_regression_checks.py --root .
```

## Known Limits

- The suite is a handoff deliverable and is not installed into local Codex.
- `templates/cumcm/main.tex` is a practical skeleton, not an official class file.
- Official contest rules must be checked again before live submission.
- Validators are read-only and do not auto-fix project files.
- Pressure-run evidence intentionally contains known failures for regression testing.
