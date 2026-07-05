# Pressure Run Evidence 2026-07-05

This folder archives the 2023A / 2024C / 2025B pressure-run artifacts used to design Math Modeling Skill Suite 2.0.

These projects are regression evidence, not recommended answer samples. They intentionally preserve defects found during the 1.0 pressure test so the 2.0 validators can catch them consistently.

## Contents

- `2023A/`: heliostat field optimization pressure run.
- `2024C/`: crop planting strategy pressure run.
- `2025B/`: SiC epitaxial layer thickness pressure run.
- `AUDIT_PROMPT.md`: independent audit prompt used after the pressure run.
- `AUDIT_REPORT.md`: audit report that motivated the 2.0 changes.

## Archive Rules

The archive keeps:

- problem and prompt files
- stage records
- `paper/main.tex`
- `paper/review_report.md`
- key `main.log` files that prove compile errors
- final `outputs/README.md`, `outputs/manifest.md`, tables, figures, and SHA256 files when present
- `git-status-before-archive.txt`, `git-log-before-archive.txt`, and `git-ls-files-before-archive.txt`

The archive excludes:

- `__pycache__/`
- `.pyc`
- LaTeX aux/fdb/fls/out/toc files
- local caches and disposable build products

Run the regression check from the suite root:

```powershell
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/run_regression_checks.py --root .
```
