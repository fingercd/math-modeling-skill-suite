# Changelog

## v2.0.0 - 2026-07-05

### Added

- Stage checkpoint gate requiring stage MD updates, `git status --short`, stage commits, and explicit risk records.
- Outputs-only delivery contract with `paper/main.tex` as source and `outputs/main.tex` as final copy.
- Machine-readable contracts:
  - `outputs/result_contract.json`
  - `outputs/constraint_checks.json`
  - `outputs/figure_manifest.json`
- Read-only validators:
  - `scripts/validate_skill_suite.py`
  - `scripts/validate_project_delivery.py`
  - `scripts/run_regression_checks.py`
- Pressure-run evidence archive for 2023A / 2024C / 2025B under `tests/evidence/pressure-run-2026-07-05/`.
- Regression expected-failure list in `tests/evidence/expected_failures.json`.

### Changed

- Updated all five skills with 2.0 gates, data provenance disclosure, output contracts, and review blocking rules.
- Updated CUMCM LaTeX template for Windows/XeLaTeX stability, no default table of contents, `hidelinks`, line spacing, and outputs-priority figure paths.
- Expanded stage MD templates and final delivery templates with git, hash, PDF, contract, and unresolved-risk fields.

### Fixed

- 1.0 allowed final delivery despite unclosed review findings; 2.0 blocks Stage 6 when `CRITICAL` or `MAJOR` remains open unless manifest records an explicit user waiver.
- 1.0 lacked a machine-readable trace from paper numbers and figures back to code outputs; 2.0 requires result, constraint, and figure contracts.
- 1.0 pressure-run artifacts mixed final and temporary files; 2.0 adds project `.gitignore` and validators for generated noise.
