# writer.md

## Status

- Stage:
- Owner:
- Last updated:
- Current gate:
- Latest git status:
- Stage commit SHA:
- User waiver:

## Confirmed Paper Route

- Selected modeling route:
- Sections already drafted:
- Sections waiting for results:
- Writing style notes:

## Paper Outline

| Section | Purpose | Current status | Dependencies |
| --- | --- | --- | --- |
| Abstract | methods, results, conclusion | waiting for final results | code/result confirmation |
| Problem Restatement | restate tasks |  |  |
| Problem Analysis | explain solution logic |  | research.md |
| Assumptions | list and justify assumptions |  | model plan |
| Notation | define variables and units |  | model plan |
| Data Processing | data source and cleaning |  | code.md |
| Model And Solution | formulas and algorithms |  | model route |
| Results | confirmed numbers and figures | waiting | code.md |
| Sensitivity/Robustness | reliability | waiting | code.md |
| Evaluation | strengths and limits | waiting | results |
| References | citations |  | research.md |
| Appendix | code/support notes |  | code.md |

## Figure Placeholders

| Label | Expected file | Caption draft | Source script | Status |
| --- | --- | --- | --- | --- |
| fig:workflow | figures/modeling_workflow.pdf | Overall modeling workflow | manual/template | placeholder |
| fig:q1 | figures/q1_result.png | Q1 result figure |  | waiting |
| fig:q2 | figures/q2_result.png | Q2 result figure |  | waiting |
| fig:sensitivity | figures/sensitivity.png | Sensitivity analysis |  | waiting |

## Table Placeholders

| Label | Purpose | Required columns | Source | Status |
| --- | --- | --- | --- | --- |
| tab:notation | notation | symbol, meaning, unit | model plan | placeholder |
| tab:data | data overview | variable, unit, missing, handling | code.md | waiting |
| tab:results | result summary | subquestion, metric, value, conclusion | code.md | waiting |

## Claims Waiting For Confirmation

| Claim | Needed evidence | Owner | Status |
| --- | --- | --- | --- |
|  |  |  |  |

## Contract Links

| Contract | Expected path | Writer responsibility | Status |
| --- | --- | --- | --- |
| result contract | outputs/result_contract.json | every paper number has an entry | waiting |
| constraint checks | outputs/constraint_checks.json | claims respect checked constraints | waiting |
| figure manifest | outputs/figure_manifest.json | every TeX figure has a real file | waiting |

## User Revisions

| Time | Request | Applied to |
| --- | --- | --- |
|  |  |  |

## Next Gate

- What must be confirmed before final paper writing:

## Stage Checkpoint Evidence

- `git status --short` output:
- Commit command:
- Commit SHA:
- `paper/main.tex` source updated: no
- `outputs/main.tex` final copy status:
- Open `CRITICAL/MAJOR` review findings:
- Open risks:
