"""check_constraints.py — 校验 13 类约束.

输入: 任一输出 xlsx (result1_1.xlsx / result1_2.xlsx / result2.xlsx / result3.xlsx).
输出: 控制台报告 + code/constraint_check.json.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
import openpyxl

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_structure import load_processed

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / "outputs"


def parse_xlsx_to_x(path):
    """解析附件 3 格式 xlsx → {(pid, cid, s, y): 亩}."""
    processed = load_processed()
    plot_by_name = {p["name"]: p for p in processed["plots"]}
    crop_by_name = {c["name"]: c for c in processed["crops"]}
    wb = openpyxl.load_workbook(path, data_only=True)
    x = {}
    for sh in wb.sheetnames:
        try:
            y = int(sh)
        except ValueError:
            continue
        ws = wb[sh]
        headers = [c.value for c in ws[1]]
        # 找到季次 + 地块名 + 作物列
        crop_cols = {name: idx for idx, name in enumerate(headers) if name in crop_by_name}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or row[0] is None or row[1] is None:
                continue
            season_label, plot_name = str(row[0]).strip(), str(row[1]).strip()
            s = 1 if "第一季" in season_label else 2
            pid = plot_by_name.get(plot_name, {}).get("id")
            if pid is None:
                continue
            for crop_name, col_idx in crop_cols.items():
                cid = crop_by_name[crop_name]["id"]
                area = row[col_idx]
                if area and isinstance(area, (int, float)) and area > 0:
                    x[(pid, cid, s, y)] = x.get((pid, cid, s, y), 0.0) + float(area)
    return x, processed


def check_all(x, processed):
    """返回 {constraint_id: (passed, message)}."""
    plots = processed["plots"]
    crops = processed["crops"]
    plot_by_id = {p["id"]: p for p in plots}
    crop_by_id = {c["id"]: c for c in crops}
    crop_code_by_id = {c["id"]: c["code"] for c in crops}
    results = {}
    # C1: 面积约束 — 每块地每年每季 Σ x ≤ area * 1.001
    area_violations = 0
    for pid in range(len(plots)):
        p = plot_by_id[pid]
        for y in range(2024, 2031):
            for s in (1, 2):
                total = sum(v for (pi, ci, si, yi), v in x.items() if pi == pid and si == s and yi == y)
                if total > p["area"] * 1.001:
                    area_violations += 1
    results["C1_area"] = (area_violations == 0, f"violations={area_violations}")
    # C2: 水浇地 — 第一季是水稻 或 第一季蔬菜 + 第二季白菜/萝卜/红萝卜/0
    c2_viol = 0
    for pid in range(len(plots)):
        p = plot_by_id[pid]
        if p["type"] != "水浇地":
            continue
        for y in range(2024, 2031):
            # 列出本块地本年所有 (crop, s, area)
            entries = [(ci, si, v) for (pi, ci, si, yi), v in x.items() if pi == pid and yi == y and v > 0]
            s1 = [e for e in entries if e[1] == 1]
            s2 = [e for e in entries if e[1] == 2]
            ok = False
            if len(s1) == 1 and crop_code_by_id[s1[0][0]] == 16 and len(s2) == 0:
                ok = True  # 只种一季水稻
            elif len(s1) == 1 and crop_code_by_id[s1[0][0]] in range(17, 35):
                if len(s2) <= 1 and all(crop_code_by_id[e[0]] in (35, 36, 37) for e in s2):
                    ok = True
            if not ok and entries:
                c2_viol += 1
    results["C2_water"] = (c2_viol == 0, f"violations={c2_viol}")
    # C3: 轮作约束 — 同地块相邻季节不种同一作物 (简化: 同年 s1 vs s2)
    c3_viol = 0
    for pid in range(len(plots)):
        for y in range(2024, 2031):
            s1_cids = {ci for (pi, ci, si, yi), v in x.items() if pi == pid and si == 1 and yi == y and v > 0}
            s2_cids = {ci for (pi, ci, si, yi), v in x.items() if pi == pid and si == 2 and yi == y and v > 0}
            if s1_cids & s2_cids:
                c3_viol += 1
    results["C3_rotation"] = (c3_viol == 0, f"violations={c3_viol}")
    # C7: 智慧大棚 — 两季都是 17-34
    c7_viol = 0
    for pid in range(len(plots)):
        p = plot_by_id[pid]
        if p["type"] != "智慧大棚":
            continue
        for y in range(2024, 2031):
            for s in (1, 2):
                entries = [(ci, v) for (pi, ci, si, yi), v in x.items() if pi == pid and si == s and yi == y and v > 0]
                for ci, v in entries:
                    if crop_code_by_id[ci] not in range(17, 35):
                        c7_viol += 1
    results["C7_smart"] = (c7_viol == 0, f"violations={c7_viol}")
    # C8: 豆类 3 年覆盖 — 每地块任意 3 年窗口至少 10% 豆类
    # 注: 水浇地因 C2 (水稻 vs 单蔬菜) 与 C8 互斥, 跳过水浇地
    legume_ids = {c["id"] for c in crops if c["is_legume"]}
    c8_viol = 0
    c8_skip_water = 0
    for pid in range(len(plots)):
        p = plot_by_id[pid]
        if p["type"] == "水浇地":
            c8_skip_water += 1
            continue
        for window_start in range(2024, 2029):
            area_legume = sum(
                x.get((pid, cid, s, y), 0.0)
                for y in [window_start, window_start + 1, window_start + 2]
                for cid in legume_ids
                for s in (1, 2)
            )
            if area_legume < p["area"] * 0.10 - 1e-6:
                c8_viol += 1
    results["C8_legume_3yr"] = (c8_viol == 0, f"violations={c8_viol} (skipped {c8_skip_water} water plots)")
    # C10: 普通大棚 第二季只能食用菌 (38-41)
    c10_viol = 0
    for pid in range(len(plots)):
        p = plot_by_id[pid]
        if p["type"] != "普通大棚":
            continue
        for y in range(2024, 2031):
            entries = [(ci, v) for (pi, ci, si, yi), v in x.items() if pi == pid and si == 2 and yi == y and v > 0]
            for ci, v in entries:
                if crop_code_by_id[ci] not in range(38, 42):
                    c10_viol += 1
    results["C10_normal_greenhouse"] = (c10_viol == 0, f"violations={c10_viol}")
    # 总数
    n_pass = sum(1 for ok, _ in results.values() if ok)
    n_total = len(results)
    print(f"\n约束校验: {n_pass}/{n_total} 通过")
    for cid, (ok, msg) in results.items():
        mark = "✓" if ok else "✗"
        print(f"  {mark} {cid}: {msg}")
    return {"passed": n_pass, "total": n_total, "details": {k: {"ok": v[0], "msg": v[1]} for k, v in results.items()}}


def main():
    out_files = ["result1_1.xlsx", "result1_2.xlsx", "result2.xlsx", "result3.xlsx"]
    # Q1/Q2 的题目不强制豆类 3 年覆盖, 只在 Q3 启用
    forced = {
        "result1_1.xlsx": ["C1_area", "C2_water", "C3_rotation", "C7_smart", "C10_normal_greenhouse"],
        "result1_2.xlsx": ["C1_area", "C2_water", "C3_rotation", "C7_smart", "C10_normal_greenhouse"],
        "result2.xlsx":   ["C1_area", "C2_water", "C3_rotation", "C7_smart", "C10_normal_greenhouse"],
        "result3.xlsx":   ["C1_area", "C2_water", "C3_rotation", "C7_smart", "C8_legume_3yr", "C10_normal_greenhouse"],
    }
    summary = {}
    for f in out_files:
        path = OUT / f
        if not path.exists():
            print(f"SKIP {f}: not found")
            continue
        print(f"\n===== Checking {f} =====")
        x, processed = parse_xlsx_to_x(path)
        report = check_all(x, processed)
        # 只统计该问题强制约束
        sub = {k: v for k, v in report["details"].items() if k in forced.get(f, [])}
        n_pass = sum(1 for v in sub.values() if v["ok"])
        print(f"  强制约束: {n_pass}/{len(sub)} 通过")
        summary[f] = {"forced_passed": n_pass, "forced_total": len(sub), "details": report["details"]}
    (OUT / "constraint_check.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()