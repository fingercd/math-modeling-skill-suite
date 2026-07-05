#!/usr/bin/env python3
"""Read-only static checks for Math Modeling Skill Suite 2.0."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_SKILLS = [
    "math-modeling-suite",
    "math-modeling-research",
    "math-modeling-writer",
    "math-modeling-code",
    "math-modeling-review",
]

REQUIRED_REFERENCES = [
    "references/stage-gates.md",
    "references/cumcm-2026-notes.md",
    "references/model-method-map.md",
    "references/review-checklist.md",
    "references/cross-device-collaboration.md",
    "references/code-tuning-guide.md",
]

REQUIRED_TEMPLATES = [
    "templates/first-response.md",
    "templates/stage-files/research.md",
    "templates/stage-files/writer.md",
    "templates/stage-files/code.md",
    "templates/stage-files/review.md",
    "templates/cumcm/main.tex",
    "templates/figures/flowchart-placeholder.md",
    "templates/tables/result-table-template.md",
    "templates/outputs/README-template.md",
    "templates/outputs/manifest-template.md",
    "templates/outputs/ai-use-statement-template.md",
    "templates/contracts/result_contract.template.json",
    "templates/contracts/constraint_checks.template.json",
    "templates/contracts/figure_manifest.template.json",
    "templates/project/.gitignore",
]

REQUIRED_SCRIPTS = [
    "scripts/validate_skill_suite.py",
    "scripts/validate_project_delivery.py",
    "scripts/run_regression_checks.py",
]


@dataclass
class Issue:
    severity: str
    code: str
    path: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def add(issues: list[Issue], severity: str, code: str, path: Path, message: str) -> None:
    issues.append(Issue(severity, code, str(path).replace("\\", "/"), message))


def check_required_paths(root: Path, issues: list[Issue]) -> None:
    for rel in REQUIRED_REFERENCES + REQUIRED_TEMPLATES + REQUIRED_SCRIPTS:
        path = root / rel
        if not path.exists():
            add(issues, "MAJOR", "required_path_missing", path, f"Missing required path: {rel}")


def check_skills(root: Path, issues: list[Issue]) -> None:
    for skill in REQUIRED_SKILLS:
        skill_dir = root / skill
        skill_md = skill_dir / "SKILL.md"
        agent_yaml = skill_dir / "agents" / "openai.yaml"
        if not skill_md.exists():
            add(issues, "CRITICAL", "skill_missing", skill_md, f"Missing {skill}/SKILL.md")
            continue
        text = read_text(skill_md)
        frontmatter = parse_frontmatter(text)
        if frontmatter.get("name") != skill:
            add(issues, "CRITICAL", "skill_frontmatter_name", skill_md, f"Expected name {skill}")
        if not frontmatter.get("description"):
            add(issues, "MAJOR", "skill_frontmatter_description", skill_md, "Missing description")
        if not agent_yaml.exists():
            add(issues, "MAJOR", "agent_yaml_missing", agent_yaml, "Missing agents/openai.yaml")
        else:
            agent_text = read_text(agent_yaml)
            if skill not in agent_text:
                add(issues, "MAJOR", "agent_yaml_skill_name", agent_yaml, f"Agent metadata does not mention {skill}")


def check_tex_template(root: Path, issues: list[Issue]) -> None:
    tex_path = root / "templates" / "cumcm" / "main.tex"
    if not tex_path.exists():
        return
    tex = read_text(tex_path)
    checks = {
        "tex_uses_ctexart": r"\\documentclass\[.*ctexart",
        "tex_line_spacing": r"\\setstretch",
        "tex_hidelinks": r"hidelinks",
        "tex_pdfborder": r"pdfborder=\{0 0 0\}",
        "tex_outputs_graphicspath": r"\.\./outputs/figures/",
        "tex_result_contract_note": r"result\\_contract\.json|result_contract\.json",
    }
    for code, pattern in checks.items():
        if not re.search(pattern, tex, flags=re.DOTALL):
            add(issues, "MAJOR", code, tex_path, f"TeX template missing pattern: {pattern}")
    if r"\tableofcontents" in tex:
        add(issues, "CRITICAL", "tex_table_of_contents_enabled", tex_path, "CUMCM template must not include a table of contents by default")


def check_contract_language(root: Path, issues: list[Issue]) -> None:
    required_terms = {
        root / "math-modeling-suite" / "SKILL.md": [
            "git status --short",
            "outputs/result_contract.json",
            "outputs/constraint_checks.json",
            "outputs/figure_manifest.json",
            "outputs/git-log.txt",
            "CRITICAL",
            "MAJOR",
        ],
        root / "references" / "stage-gates.md": [
            "阶段检查点",
            "git status --short",
            "result_contract.json",
            "constraint_checks.json",
            "figure_manifest.json",
            "outputs/",
        ],
        root / "math-modeling-review" / "SKILL.md": [
            "Operationally",
            "outputs/result_contract.json",
            "禁止进入",
        ],
    }
    for path, terms in required_terms.items():
        if not path.exists():
            continue
        text = read_text(path)
        for term in terms:
            if term not in text:
                add(issues, "MAJOR", "contract_language_missing", path, f"Missing required 2.0 term: {term}")


def check_json_templates(root: Path, issues: list[Issue]) -> None:
    for rel in [
        "templates/contracts/result_contract.template.json",
        "templates/contracts/constraint_checks.template.json",
        "templates/contracts/figure_manifest.template.json",
    ]:
        path = root / rel
        if not path.exists():
            continue
        try:
            data = json.loads(read_text(path).lstrip("\ufeff"))
        except json.JSONDecodeError as exc:
            add(issues, "CRITICAL", "json_template_invalid", path, f"Invalid JSON: {exc}")
            continue
        if data.get("schema_version") != "2.0.0":
            add(issues, "MAJOR", "json_template_schema_version", path, "Expected schema_version 2.0.0")


def check_generated_noise(root: Path, issues: list[Issue]) -> None:
    noisy_suffixes = {".pyc", ".aux", ".fdb_latexmk", ".fls", ".out", ".toc"}
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name == "__pycache__":
            add(issues, "MINOR", "generated_noise_present", path, "Generated __pycache__ directory should not be committed")
        elif path.is_file() and path.suffix in noisy_suffixes:
            add(issues, "MINOR", "generated_noise_present", path, f"Generated file should not be committed: {path.name}")


def validate(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    check_required_paths(root, issues)
    check_skills(root, issues)
    check_tex_template(root, issues)
    check_contract_language(root, issues)
    check_json_templates(root, issues)
    check_generated_noise(root, issues)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Math Modeling Skill Suite 2.0.")
    parser.add_argument("--root", default=".", help="Suite repository root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.root)
    issues = validate(root)
    payload = {
        "root": str(root.resolve()).replace("\\", "/"),
        "ok": not any(issue.severity in {"CRITICAL", "MAJOR"} for issue in issues),
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"root: {payload['root']}")
        print(f"ok: {payload['ok']}")
        for issue in issues:
            print(f"[{issue.severity}] {issue.code} {issue.path}: {issue.message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
