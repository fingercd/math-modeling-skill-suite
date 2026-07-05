---
name: math-modeling-writer
description: Use when drafting CUMCM-style mathematical modeling paper frameworks, LaTeX skeletons, flowchart/table/figure placeholders, writer.md records, and final paper prose after results are confirmed.
---

# Math Modeling Writer

## Stage Labels

Use in `(建模思路与论文框架)`, `(论文撰写与代码开发)`, `(实验结果汇总确认)`, and `(最终交付归档)`. Start each response with the active stage label.

## CUMCM Paper Framework

Default to the CUMCM/高教社杯 paper shape:

- title, abstract, keywords
- problem restatement
- problem analysis
- model assumptions
- notation table
- data preprocessing and exploratory analysis
- model establishment and solution by subquestion
- result analysis and validation
- sensitivity, error, or robustness analysis
- model evaluation, improvement, and extension
- references
- appendix

Do not add a table of contents by default. Keep the main body within the contest page limit. Put long code and large intermediate results in appendix or support files.

## LaTeX and Placeholder Rules

Use `../templates/cumcm/main.tex` as the editable starting point.

Pre-place:

- a standard modeling-flow figure slot
- algorithm-flow figure slots
- core result table skeletons
- experiment/result figure slots
- conclusion/result placeholders that wait for user-confirmed numbers

For flowcharts, use `../templates/figures/flowchart-placeholder.md`. The paper should require only filename changes when real figures are ready.

For tables, use `../templates/tables/result-table-template.md` and include cell-level guidance on what the user should fill.

Keep `paper/main.tex` as the writing source. During `(最终交付归档)`, copy the approved source to `outputs/main.tex` and validate the copy from `outputs/`, not from scattered project files.

## writer.md Contract

Maintain `paper/writer.md` after every user turn. Use `../templates/stage-files/writer.md`.

Record:

- current paper outline and section status
- model route chosen by the user
- figure/table placeholder names
- claims that require code results
- user wording preferences and revisions
- references and citation notes
- final result statements waiting for confirmation
- exact output file expected for each figure and table
- contract status for `outputs/result_contract.json`, `outputs/constraint_checks.json`, and `outputs/figure_manifest.json`
- latest `git status --short`, stage commit SHA, and open writing risks before a stage transition

Never invent numerical conclusions. Write model background, assumptions, derivations, algorithm explanations, and generic result interpretation; fill final values only after the user or code stage confirms them.

## Parallel Work

During `(论文撰写与代码开发)`, coordinate with `math-modeling-code` through filenames and result contracts:

- every figure placeholder must name the expected file, such as `figures/q1_trend.png`
- every result table must list required columns and units
- every paper claim must reference the code output or mark `待结果确认`
- every paper number must have a matching `result_contract` entry before final writing
- every figure in TeX must have a matching `figure_manifest` entry before final delivery

## Final Paper Rule

Before final writing, check `code/code.md`, `outputs/result_contract.json`, `outputs/constraint_checks.json`, and `outputs/figure_manifest.json`. If results are missing, write placeholders and ask for the missing values instead of fabricating them. If `main.pdf` cannot be produced, the final README and manifest must say so plainly.
