#!/usr/bin/env python3
"""Run expected-failure regression checks against archived pressure evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_expected(root: Path) -> dict:
    path = root / "tests" / "evidence" / "expected_failures.json"
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(root: Path, project: Path) -> dict:
    script = root / "scripts" / "validate_project_delivery.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--project", str(project), "--json"],
        cwd=str(root),
        check=False,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    if proc.returncode not in {0, 1}:
        raise RuntimeError(f"validator failed for {project}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 2.0 regression checks over archived pressure evidence.")
    parser.add_argument("--root", default=".", help="Suite repository root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    expected = load_expected(root)
    case_results = []
    all_ok = True

    for case in expected["cases"]:
        project = root / case["project"]
        payload = run_validator(root, project)
        actual_codes = {issue["code"] for issue in payload["issues"]}
        expected_codes = set(case["expected_issue_codes"])
        missing = sorted(expected_codes - actual_codes)
        unexpected_pass = payload["ok"]
        ok = not missing and not unexpected_pass
        all_ok = all_ok and ok
        case_results.append(
            {
                "project": case["project"],
                "ok": ok,
                "validator_ok": payload["ok"],
                "expected_issue_codes": sorted(expected_codes),
                "actual_issue_codes": sorted(actual_codes),
                "missing_expected_issue_codes": missing,
                "notes": case.get("notes", ""),
            }
        )

    result = {
        "suite": expected.get("suite", ""),
        "ok": all_ok,
        "case_count": len(case_results),
        "cases": case_results,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"suite: {result['suite']}")
        print(f"ok: {result['ok']}")
        for case in case_results:
            print(f"- {case['project']}: ok={case['ok']}")
            if case["missing_expected_issue_codes"]:
                print(f"  missing: {', '.join(case['missing_expected_issue_codes'])}")
            print(f"  actual: {', '.join(case['actual_issue_codes'])}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
