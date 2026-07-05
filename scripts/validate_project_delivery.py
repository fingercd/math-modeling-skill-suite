#!/usr/bin/env python3
"""Read-only delivery validator for one math-modeling project."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_DIRS = ["research", "paper", "code", "figures", "outputs"]
REQUIRED_STAGE_FILES = ["research/research.md", "paper/writer.md", "code/code.md"]
CONTRACTS = {
    "outputs/result_contract.json": "missing_result_contract",
    "outputs/constraint_checks.json": "missing_constraint_checks",
    "outputs/figure_manifest.json": "missing_figure_manifest",
}
GENERATED_SUFFIXES = {".pyc", ".aux", ".fdb_latexmk", ".fls", ".out", ".toc"}
LATEX_ERROR_PATTERNS = [
    "! LaTeX Error",
    "Emergency stop",
    "Fatal error",
    "Undefined control sequence",
]
REVIEW_OPEN_PATTERNS = [
    "不进入 stage 6",
    "禁止进入",
    "未 re-run",
    "未重跑",
    "部分修补",
    "需要再跑",
    "MAJOR: 4",
    "MAJOR    | 3",
]


@dataclass
class Issue:
    severity: str
    code: str
    path: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def add(issues: list[Issue], severity: str, code: str, path: Path, message: str) -> None:
    issues.append(Issue(severity, code, str(path).replace("\\", "/"), message))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_project_shape(project: Path, issues: list[Issue]) -> None:
    for rel in REQUIRED_DIRS:
        path = project / rel
        if not path.is_dir():
            add(issues, "CRITICAL", "required_directory_missing", path, f"Missing required directory {rel}/")
    for rel in REQUIRED_STAGE_FILES:
        path = project / rel
        if not path.exists():
            add(issues, "MAJOR", "stage_md_missing", path, f"Missing stage record {rel}")
    review = project / "paper" / "review_report.md"
    if not review.exists():
        add(issues, "MAJOR", "review_report_missing", review, "Independent review report is missing")


def check_outputs(project: Path, issues: list[Issue]) -> None:
    outputs = project / "outputs"
    readme = outputs / "README.md"
    manifest = outputs / "manifest.md"
    if not readme.exists():
        add(issues, "MAJOR", "outputs_readme_missing", readme, "outputs/README.md is missing")
    if not manifest.exists():
        add(issues, "MAJOR", "outputs_manifest_missing", manifest, "outputs/manifest.md is missing")
    if not (outputs / "main.tex").exists():
        add(issues, "CRITICAL", "outputs_tex_missing", outputs / "main.tex", "outputs/main.tex is missing")
    if not (outputs / "main.pdf").exists():
        add(issues, "CRITICAL", "outputs_pdf_missing", outputs / "main.pdf", "outputs/main.pdf is missing")
    for rel, code in CONTRACTS.items():
        path = project / rel
        if not path.exists():
            add(issues, "MAJOR", code, path, f"{rel} is missing")
        else:
            try:
                json.loads(read_text(path).lstrip("\ufeff"))
            except json.JSONDecodeError as exc:
                add(issues, "CRITICAL", "contract_json_invalid", path, f"Invalid JSON: {exc}")


def extract_figures(tex: str) -> list[str]:
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return [match.group(1).strip() for match in pattern.finditer(tex)]


def figure_candidates(project: Path, ref: str) -> list[Path]:
    ref_path = Path(ref)
    name = ref_path.name
    return [
        project / "outputs" / ref_path,
        project / "outputs" / "figures" / name,
        project / "figures" / ref_path,
        project / "figures" / name,
        project / "paper" / ref_path,
    ]


def check_figures(project: Path, issues: list[Issue]) -> None:
    tex_path = project / "outputs" / "main.tex"
    if not tex_path.exists():
        return
    tex = read_text(tex_path)
    for ref in extract_figures(tex):
        if not any(path.exists() for path in figure_candidates(project, ref)):
            add(issues, "MAJOR", "figure_file_missing", tex_path, f"TeX figure reference has no file: {ref}")


def check_latex_logs(project: Path, issues: list[Issue]) -> None:
    for log_path in [project / "outputs" / "main.log", project / "paper" / "main.log"]:
        if not log_path.exists():
            continue
        text = read_text(log_path)
        for pattern in LATEX_ERROR_PATTERNS:
            if pattern in text:
                add(issues, "CRITICAL", "latex_log_error", log_path, f"LaTeX log contains: {pattern}")
                break


def check_generated_noise(project: Path, issues: list[Issue]) -> None:
    for path in project.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name == "__pycache__":
            add(issues, "MINOR", "python_cache_present", path, "__pycache__ should not be in delivery")
        elif path.is_file() and path.suffix in GENERATED_SUFFIXES:
            add(issues, "MINOR", "generated_file_present", path, "Generated temporary file should not be in delivery")


def check_source_output_contract(project: Path, issues: list[Issue]) -> None:
    source = project / "paper" / "main.tex"
    delivery = project / "outputs" / "main.tex"
    if not source.exists():
        add(issues, "MAJOR", "paper_source_tex_missing", source, "paper/main.tex is missing")
        return
    if not delivery.exists():
        return
    if sha256(source) == sha256(delivery):
        manifest = project / "outputs" / "manifest.md"
        manifest_text = read_text(manifest) if manifest.exists() else ""
        has_copy_evidence = all(term in manifest_text for term in ["Source TeX", "Delivery TeX", "SHA256"])
        if not has_copy_evidence:
            add(
                issues,
                "MAJOR",
                "paper_outputs_tex_identical",
                delivery,
                "paper/main.tex and outputs/main.tex have identical hashes but manifest lacks source/delivery/hash evidence",
            )


def check_review_closure(project: Path, issues: list[Issue]) -> None:
    review = project / "paper" / "review_report.md"
    if not review.exists():
        return
    text = read_text(review)
    for pattern in REVIEW_OPEN_PATTERNS:
        if pattern in text:
            add(issues, "MAJOR", "review_fix_not_closed", review, f"Review report suggests unresolved work: {pattern}")
            return


def check_stage_commit_evidence(project: Path, issues: list[Issue]) -> None:
    status_path = project / "git-status-before-archive.txt"
    log_path = project / "git-log-before-archive.txt"
    if status_path.exists():
        status = read_text(status_path)
        if "\n?? " in "\n" + status:
            add(issues, "MAJOR", "stage_commits_missing", status_path, "Archived status shows untracked stage files")
            return
    if log_path.exists():
        log = read_text(log_path)
        if "stage(" not in log:
            add(issues, "MAJOR", "stage_commits_missing", log_path, "Archived git log has no stage commits")


def validate(project: Path) -> list[Issue]:
    project = project.resolve()
    issues: list[Issue] = []
    check_project_shape(project, issues)
    check_outputs(project, issues)
    check_figures(project, issues)
    check_latex_logs(project, issues)
    check_generated_noise(project, issues)
    check_source_output_contract(project, issues)
    check_review_closure(project, issues)
    check_stage_commit_evidence(project, issues)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one math-modeling project delivery.")
    parser.add_argument("--project", required=True, help="Project directory to validate")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project)
    issues = validate(project)
    payload = {
        "project": str(project.resolve()).replace("\\", "/"),
        "ok": not any(issue.severity in {"CRITICAL", "MAJOR"} for issue in issues),
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"project: {payload['project']}")
        print(f"ok: {payload['ok']}")
        for issue in issues:
            print(f"[{issue.severity}] {issue.code} {issue.path}: {issue.message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
