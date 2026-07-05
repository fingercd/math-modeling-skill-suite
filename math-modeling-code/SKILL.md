---
name: math-modeling-code
description: Use when implementing lightweight Python and Excel-supported mathematical modeling contest experiments, including data cleaning, classification, clustering, optimization, visualization, and code/code.md records.
---

# Math Modeling Code

## Stage Labels

Use in `(论文撰写与代码开发)` and `(实验结果汇总确认)`. Start each response with the active stage label.

## Tool Boundary

Python is the core computation tool. Excel is only for data records, manual result tables, and lightweight inspection. Do not require MATLAB, R, Lingo, SPSS, or heavyweight training unless the user explicitly asks.

Supported work:

- data cleaning and feature engineering
- descriptive statistics and exploratory plots
- classification and regression with lightweight traditional ML
- supervised or unsupervised clustering
- optimization, simulation, scoring, and evaluation models
- paper-ready figures and result tables

Unsupported by default:

- long deep-learning training
- large model fine-tuning
- GPU-heavy experiments
- unbounded hyperparameter searches

For heavy training, produce scripts and instructions, tell the user to train/tune, and record the limitation in `code/code.md`.

## Autotuning Rule

Use simple, bounded tuning for lightweight models:

- fixed random seed
- train/validation split or cross-validation when data allows
- small parameter grid
- metric aligned with the paper's objective
- saved best parameters and score

If basic tuning is weak or unstable, stop escalating compute. Give the user a short tuning tutorial for the chosen model and record what was tried.

## code.md Contract

Maintain `code/code.md` after every user turn. Use `../templates/stage-files/code.md`.

Record:

- scripts created or modified
- input data files and expected schema
- output figures and tables
- parameters, seeds, metrics, and environment
- successful runs and failed attempts
- results exported for `paper/writer.md`
- open problems requiring user training, tuning, or data fixes
- latest `git status --short`, stage commit SHA, and unresolved code risks before a stage transition

Every paper-facing result must include script name, input, output file, parameter summary, and reproducibility note.

## Figure/Table Contract

Write outputs to `figures/` for paper images and `outputs/` only for final exports. Use stable filenames agreed with the writer, for example:

- `figures/q1_data_overview.png`
- `figures/q2_cluster_result.png`
- `figures/q3_sensitivity.png`
- `outputs/result_summary.xlsx`

Do not silently change a filename that `paper/writer.md` already references; update both records if a name changes.

## Machine-Readable Contracts

Generate or maintain these final delivery files when results are ready:

- `outputs/result_contract.json`: one entry per paper-facing number, with subquestion, metric, value, unit, script, output file, parameters, and confirmation status.
- `outputs/constraint_checks.json`: one entry per constraint or consistency check, with expected relation, observed value, pass/fail, severity, and source script.
- `outputs/figure_manifest.json`: one entry per TeX figure, with label, TeX path, real file path, source script, SHA256, caption, and missing status.

If a number, constraint, or figure cannot be verified, mark it unconfirmed instead of smoothing over the gap.

## Result Confirmation

In `(实验结果汇总确认)`, summarize:

- key numerical answers per subquestion
- generated figures and tables
- model performance metrics
- sensitivity/robustness results
- known limitations

Ask the user to confirm which results enter the final paper before `math-modeling-writer` writes final conclusions.
