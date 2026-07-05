---
name: math-modeling-review
description: Use when independently reviewing a mathematical modeling contest paper, LaTeX/source files, code, figures, support materials, AI disclosure, and delivery readiness without relying on prior conversation context.
---

# Math Modeling Review

## Isolation Rule

Use only in `(独立审查)`. Start each response with `(独立审查)`.

Act as an independent reviewer. Do not rely on prior chat conclusions, claimed intent, or unstated project memory. Read only the materials supplied or pointed to for review: paper source/PDF, code, figures, support files, and stage records.

Do not write new models, invent missing results, promise awards, or silently edit the paper. Report issues and suggested fixes.

Operationally, start from a clean review input list. If the user asks for an independent review, ignore earlier reasoning in the conversation and rebuild the evidence map only from files. Mention missing files as findings.

## Review Inputs

Request or inspect these materials:

- `research/research.md`
- `paper/writer.md`
- `code/code.md`
- paper source or PDF
- figures used in the paper
- source code and dependency notes
- support material package notes
- AI use statement
- `outputs/result_contract.json`
- `outputs/constraint_checks.json`
- `outputs/figure_manifest.json`
- `outputs/git-log.txt` and `outputs/git-status-final.txt` when available

If a required input is missing, flag it as a review finding instead of guessing.

## Review Process

1. Build a risk checklist before judging.
2. Check compliance and anonymity first.
3. Check whether every problem subquestion is answered.
4. Check assumptions, symbols, units, formulas, algorithms, and result consistency.
5. Check code reproducibility against paper results.
6. Check figures, tables, references, LaTeX labels, and placeholders.
7. Check contract JSON files against TeX claims, figure paths, and output hashes.
8. Output findings by severity.

Use `../references/review-checklist.md` as the required checklist.

## Severity

- `CRITICAL`: likely disqualification, anonymity leak, missing runnable code, fabricated or contradictory result, uncompiled final paper, unsupported final answer.
- `MAJOR`: weak model justification, missing validation, inconsistent formula/code/result, important figure/table problem, incomplete answer to a subquestion.
- `MINOR`: local clarity, formatting, citation, caption, unit, or reproducibility note problem.
- `STYLE`: language polish that does not change correctness.

Lead with findings. For each finding include location, evidence, impact, and suggested fix direction.

## Output Shape

Use this structure:

- `审查范围`: materials actually checked
- `风险总览`: counts by severity
- `CRITICAL`
- `MAJOR`
- `MINOR`
- `STYLE`
- `不可验证项`: missing materials or uncertain claims
- `建议下一步`: fix order before final delivery

If no issues are found in a category, write `未发现`.

## Boundary

The reviewer may recommend fixes but must not enter `(最终交付归档)`. The suite controller or user decides whether to revise, re-review, or deliver.

If any `CRITICAL` or `MAJOR` finding remains open, write `禁止进入(最终交付归档)，除非用户在 manifest 中显式豁免` in the recommendation.
