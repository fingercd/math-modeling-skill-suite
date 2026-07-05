---
name: math-modeling-suite
description: Use when coordinating a multi-skill mathematical modeling contest workflow for CUMCM/高教社杯 style projects, especially when the user needs phased research, modeling plans, paper/code parallel work, independent review, and final outputs-only delivery.
---

# Math Modeling Suite

## Core Rule

Run the project as a six-stage state machine. Start every response with the current stage label:

1. `(全网广泛调研)`
2. `(建模思路与论文框架)`
3. `(论文撰写与代码开发)`
4. `(实验结果汇总确认)`
5. `(独立审查)`
6. `(最终交付归档)`

Advance only when the user expresses approval or intent to continue, including phrases like `继续`, `进入下一阶段`, `方案批准`, `推进`, or equivalent wording. No fixed approval phrase is required.

Before leaving any stage, run the 2.0 checkpoint gate in `../references/stage-gates.md`. The gate requires the active stage MD to be updated, `git status --short` to be recorded, a stage commit to be created when the workspace is a git repository, and unresolved risks to be written into the next gate. If git is unavailable, record the reason and ask the user whether to continue without a stage commit.

## Directory Contract

Create and use exactly these project directories:

- `research/` for research material and `research.md`
- `paper/` for TeX, writing notes, and `writer.md`
- `code/` for Python scripts, Excel records, and `code.md`
- `figures/` for flowcharts, experimental plots, and result figures
- `outputs/` for final deliverables only

Do not automatically search scattered files when packaging delivery. The final package is assembled from `outputs/`.

Use this source/output contract:

- `paper/main.tex` is the editable writing source.
- `outputs/main.tex` is the final delivery copy.
- `figures/` stores working figures; `outputs/figures/` stores final referenced figures.
- `outputs/result_contract.json` records every paper-facing number.
- `outputs/constraint_checks.json` records feasibility, constraint, and consistency checks.
- `outputs/figure_manifest.json` records every TeX figure reference and real file.

## Routing

- Use `math-modeling-research` in `(全网广泛调研)`.
- Use `math-modeling-writer` in `(建模思路与论文框架)` and the paper side of `(论文撰写与代码开发)`.
- Use `math-modeling-code` in the code side of `(论文撰写与代码开发)` and result generation.
- Use `math-modeling-review` only in `(独立审查)`.

If multiple roles work in parallel, keep the user-facing stage label as `(论文撰写与代码开发)` and record which role changed which file.

## Required Stage Records

After every user turn, update the current stage record:

- research work and user ideas -> `research/research.md`
- paper structure, wording, and figure/table placeholders -> `paper/writer.md`
- code, data, experiment, and plotting work -> `code/code.md`

The record must let an outside teammate reconstruct the work without reading chat history. Include current status, decisions, user changes, actions taken, files touched, unresolved questions, and next gate.

Each stage record must also include:

- latest `git status --short` summary
- stage commit SHA or explicit reason no commit was made
- result, constraint, and figure contract status when applicable
- data provenance and AI-use disclosure status
- whether any `CRITICAL` or `MAJOR` review issue is still open

## CUMCM Defaults

Use CUMCM/高教社杯 2026-style assumptions unless the user chooses another contest:

- no table of contents in the paper body
- abstract page first, with page numbering starting there
- main body not over 30 pages
- AI use disclosure and anonymity checks are part of every stage
- source code and support files must be runnable and consistent with paper results
- all final numbers and figures must be traceable through the contract JSON files

Read `../references/stage-gates.md`, `../references/cumcm-2026-notes.md`, and `../references/cross-device-collaboration.md` when starting a new project.

If the first user request only names a contest or problem number, use `../templates/first-response.md` to avoid skipping the intake and research setup.

## Final Delivery

In `(最终交付归档)`, copy or generate final materials under project `outputs/` only:

- final PDF and editable TeX/source
- code and reproducibility notes
- figures and tables used in the paper
- support material package notes
- AI use statement
- `README.md`
- `manifest.md`
- `outputs/git-log.txt`
- `outputs/git-status-final.txt`
- `outputs/SHA256SUMS.txt`
- `result_contract.json`
- `constraint_checks.json`
- `figure_manifest.json`

Before claiming delivery is complete, verify from inside `outputs/` that `main.tex`, all figure paths, contract JSON files, manifest, README, and SHA256 records are present. If `main.pdf` is missing or failed to compile, state that visibly in both `outputs/README.md` and `outputs/manifest.md`.

Stage 5 blocks Stage 6 when any `CRITICAL` or `MAJOR` review finding remains open. The only exception is an explicit user waiver recorded in `outputs/manifest.md` with the finding IDs, reason, date, and remaining risk.
