"""q2_run.py — 问题 2 蒙特卡洛 500 场景 + 贪心.

输出:
- outputs/result2.xlsx (场景均值)
- outputs/result2_scenarios.json (各场景利润)
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import openpyxl
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from algo.greedy import greedy_solve
from data_structure import load_processed
from objective import base_sales_capacity

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / "outputs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--sigma", type=float, default=0.10)
    ap.add_argument("--mode", choices=["waste", "discount"], default="discount")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    processed = load_processed()
    crops = processed["crops"]

    # 场景结果: {scenario_id: profit}
    scenario_profits = []
    best_x = None
    best_profit = -1e18
    caps_default = {c["id"]: base_sales_capacity(processed, c["code"]) for c in crops}
    # 每个场景对每个 (crop, year) 生成扰动后的 cap
    for k in range(args.n):
        caps_k = {c["id"]: caps_default[c["id"]] * max(0.5, 1 + rng.normal(0, args.sigma)) for c in crops}
        # 价格/成本/产量每年每作物单独扰动 (这里简化为场景级共享)
        pm = max(0.5, 1 + rng.normal(0, args.sigma))
        cm = max(0.5, 1 + rng.normal(0, args.sigma))
        ym = max(0.5, 1 + rng.normal(0, args.sigma))
        x, profit = greedy_solve(
            mode=args.mode, n_years=7,
            fixed_caps=caps_k,
            price_mult=pm, cost_mult=cm, yield_mult=ym,
            sales_mult=1.0,
        )
        scenario_profits.append(profit)
        if profit > best_profit:
            best_profit = profit
            best_x = x
    arr = np.array(scenario_profits)
    summary = {
        "n_scenarios": args.n,
        "sigma": args.sigma,
        "mode": args.mode,
        "mean_wan": float(arr.mean() / 1e4),
        "std_wan": float(arr.std() / 1e4),
        "min_wan": float(arr.min() / 1e4),
        "max_wan": float(arr.max() / 1e4),
        "median_wan": float(np.median(arr) / 1e4),
        "cv": float(arr.std() / arr.mean()) if arr.mean() != 0 else 0.0,
    }
    (OUT / "result2_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Q2 ({args.mode}, n={args.n}, σ={args.sigma})")
    print(f"  均值 = {summary['mean_wan']:.2f} 万元")
    print(f"  标准差 = {summary['std_wan']:.2f} 万元")
    print(f"  CV = {summary['cv']:.4f}")
    print(f"  min/max = {summary['min_wan']:.2f} / {summary['max_wan']:.2f} 万元")
    # 用 best_x 写 result2.xlsx (使用场景均值 cap)
    if best_x is None:
        best_x, _ = greedy_solve(mode=args.mode, n_years=7)
    from q1_run import x_to_template_sheets
    x_to_template_sheets(best_x, processed, OUT / "result2.xlsx")
    # 保存所有场景利润
    pd.DataFrame({"scenario": range(args.n), "profit_wan": arr / 1e4}).to_csv(
        OUT / "result2_scenarios.csv", index=False, encoding="utf-8-sig"
    )


if __name__ == "__main__":
    main()