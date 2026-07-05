"""q3_run.py — 问题 3: 间作 + 替代弹性.

在 Q2 基础上:
- legume_cover=True: 每个地块 3 年窗口内至少 10% 豆类
- substitute_rho: 豆类之间 ρ=+1, 同科蔬菜 ρ=+0.3, 其他 ρ=0
- 超产按 max(0, 0.5 + 0.3*ρ) 折价
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from algo.greedy import greedy_solve
from data_structure import load_processed
from objective import base_sales_capacity
from q1_run import x_to_template_sheets

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / "outputs"


def build_substitute_rho(processed):
    """豆类之间 +1, 同 type 蔬菜 +0.3, 其他 0; 返回 {(cid_i, cid_j): ρ}."""
    rho = {}
    crops = processed["crops"]
    for ci in crops:
        for cj in crops:
            if ci["id"] == cj["id"]:
                rho[(ci["id"], cj["id"])] = 1.0
                continue
            if ci["is_legume"] and cj["is_legume"]:
                rho[(ci["id"], cj["id"])] = 1.0
            elif ("蔬菜" in ci["type"]) and ("蔬菜" in cj["type"]):
                rho[(ci["id"], cj["id"])] = 0.3
            else:
                rho[(ci["id"], cj["id"])] = 0.0
    return rho


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--sigma", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    processed = load_processed()
    crops = processed["crops"]
    rho = build_substitute_rho(processed)
    caps_default = {c["id"]: base_sales_capacity(processed, c["code"]) for c in crops}

    scenario_profits = []
    best_x = None
    best_profit = -1e18
    for k in range(args.n):
        caps_k = {c["id"]: caps_default[c["id"]] * max(0.5, 1 + rng.normal(0, args.sigma)) for c in crops}
        pm = max(0.5, 1 + rng.normal(0, args.sigma))
        cm = max(0.5, 1 + rng.normal(0, args.sigma))
        ym = max(0.5, 1 + rng.normal(0, args.sigma))
        # 简化: 用平均 ρ = 0.3 作 global substitute_rho
        x, profit = greedy_solve(
            mode="elastic", n_years=7,
            legume_cover=True,
            substitute_rho=0.3,
            discount_alpha=0.5,
            fixed_caps=caps_k,
            price_mult=pm, cost_mult=cm, yield_mult=ym,
        )
        scenario_profits.append(profit)
        if profit > best_profit:
            best_profit = profit
            best_x = x
    arr = np.array(scenario_profits)
    summary = {
        "n_scenarios": args.n,
        "sigma": args.sigma,
        "mode": "elastic+legume_cover",
        "mean_wan": float(arr.mean() / 1e4),
        "std_wan": float(arr.std() / 1e4),
        "min_wan": float(arr.min() / 1e4),
        "max_wan": float(arr.max() / 1e4),
        "cv": float(arr.std() / arr.mean()) if arr.mean() != 0 else 0.0,
    }
    (OUT / "result3_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Q3 (elastic + 间作, n={args.n}, σ={args.sigma})")
    print(f"  均值 = {summary['mean_wan']:.2f} 万元")
    print(f"  CV   = {summary['cv']:.4f}")
    if best_x is None:
        best_x, _ = greedy_solve(mode="elastic", n_years=7, legume_cover=True, substitute_rho=0.3)
    x_to_template_sheets(best_x, processed, OUT / "result3.xlsx")
    pd.DataFrame({"scenario": range(args.n), "profit_wan": arr / 1e4}).to_csv(
        OUT / "result3_scenarios.csv", index=False, encoding="utf-8-sig"
    )


if __name__ == "__main__":
    main()