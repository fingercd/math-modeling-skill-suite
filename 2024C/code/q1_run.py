"""q1_run.py — 问题 1 求解: 滞销 / 50% 折价 两种情形.

输出:
- outputs/result1_1.xlsx (waste)
- outputs/result1_2.xlsx (discount)
- stdout: 7 年累计净利润
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import openpyxl
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from algo.greedy import greedy_solve
from data_structure import load_processed

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / "outputs"
OUT.mkdir(exist_ok=True)


def x_to_long_table(x, processed):
    """x: {(pid,cid,s,y): 亩} → DataFrame (地块, 年, 季, 作物, 种植面积)."""
    plots = processed["plots"]
    crops = processed["crops"]
    plot_by_id = {p["id"]: p for p in plots}
    crop_by_id = {c["id"]: c for c in crops}
    rows = []
    for (pid, cid, s, y), area in x.items():
        if area <= 0:
            continue
        rows.append({
            "地块": plot_by_id[pid]["name"],
            "地块类型": plot_by_id[pid]["type"],
            "年": y,
            "季": "第一季" if s == 1 else "第二季",
            "作物编号": crop_by_id[cid]["code"],
            "作物名称": crop_by_id[cid]["name"],
            "种植面积(亩)": round(area, 2),
        })
    return pd.DataFrame(rows)


def x_to_template_sheets(x, processed, path):
    """把 x 写成附件 3 模板格式: 7 张 sheet, 行=(地块, 第一/第二季), 列=41 种作物."""
    plots = processed["plots"]
    crops = processed["crops"]
    crop_codes = [c["code"] for c in crops]
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for y in range(2024, 2031):
        ws = wb.create_sheet(str(y))
        # 模板: 行= (season, plot), 列=41 种作物
        headers = ["季次", "地块名"] + [crops[code-1]["name"] for code in crop_codes]
        ws.append(headers)
        for p in plots:
            for s in (1, 2):
                row = ["第一季" if s == 1 else "第二季", p["name"]]
                for cid in range(41):
                    area = x.get((p["id"], cid, s, y), 0.0)
                    row.append(round(area, 2) if area > 0 else None)
                ws.append(row)
    wb.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["waste", "discount", "both"], default="both")
    args = ap.parse_args()
    processed = load_processed()
    results = {}
    if args.mode in ("waste", "both"):
        x, profit = greedy_solve(mode="waste", n_years=7)
        x_to_template_sheets(x, processed, OUT / "result1_1.xlsx")
        df = x_to_long_table(x, processed)
        df.to_csv(OUT / "result1_1_long.csv", index=False, encoding="utf-8-sig")
        results["waste_profit_wan"] = round(profit / 1e4, 2)
        print(f"Q1 子问 1 (waste): 7 年累计 = {profit/1e4:.2f} 万元, 非零动作 = {sum(1 for v in x.values() if v>0)}")
    if args.mode in ("discount", "both"):
        x, profit = greedy_solve(mode="discount", n_years=7)
        x_to_template_sheets(x, processed, OUT / "result1_2.xlsx")
        df = x_to_long_table(x, processed)
        df.to_csv(OUT / "result1_2_long.csv", index=False, encoding="utf-8-sig")
        results["discount_profit_wan"] = round(profit / 1e4, 2)
        print(f"Q1 子问 2 (discount): 7 年累计 = {profit/1e4:.2f} 万元, 非零动作 = {sum(1 for v in x.values() if v>0)}")
    (OUT / "q1_summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()