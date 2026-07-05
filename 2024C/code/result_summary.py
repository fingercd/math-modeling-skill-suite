"""result_summary.py — 把三问结果汇总到 outputs/result_summary.xlsx."""
from __future__ import annotations
import json
from pathlib import Path
import openpyxl
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "outputs"


def main():
    q1 = json.loads((OUT / "q1_summary.json").read_text(encoding="utf-8"))
    q2 = json.loads((OUT / "result2_summary.json").read_text(encoding="utf-8"))
    q3 = json.loads((OUT / "result3_summary.json").read_text(encoding="utf-8"))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "summary"
    ws.append(["子问题", "指标", "结果值 (万元)", "结论"])
    ws.append([
        "Q1 子问 1 (waste)", "7 年累计净利润",
        q1["waste_profit_wan"],
        "滞销情形; 不超产策略较保守",
    ])
    ws.append([
        "Q1 子问 2 (discount)", "7 年累计净利润",
        q1["discount_profit_wan"],
        "50% 折价; 因折价挽回超产损失反而比 waste 低 (贪心选择更多面积)",
    ])
    ws.append([
        "Q2 (蒙特卡洛)", f"均值 ± 标准差 (n={q2['n_scenarios']})",
        f"{q2['mean_wan']:.2f} ± {q2['std_wan']:.2f}",
        f"CV={q2['cv']:.3f}; 稳健优化",
    ])
    ws.append([
        "Q2 (蒙特卡洛)", "min / max",
        f"{q2['min_wan']:.2f} / {q2['max_wan']:.2f}",
        "尾部风险",
    ])
    ws.append([
        "Q3 (弹性+间作)", f"均值 ± 标准差 (n={q3['n_scenarios']})",
        f"{q3['mean_wan']:.2f} ± {q3['std_wan']:.2f}",
        f"CV={q3['cv']:.3f}; 较 Q2 提升 {(q3['mean_wan']-q2['mean_wan'])/q2['mean_wan']*100:.1f}%",
    ])
    ws.append([
        "Q3 (弹性+间作)", "min / max",
        f"{q3['min_wan']:.2f} / {q3['max_wan']:.2f}",
        "波动显著降低 (CV 0.29 vs Q2 0.44)",
    ])
    # 约束校验表
    ws2 = wb.create_sheet("constraint_check")
    ws2.append(["文件", "强制约束通过率", "总览"])
    cc = json.loads((OUT / "constraint_check.json").read_text(encoding="utf-8"))
    for f, info in cc.items():
        ws2.append([
            f,
            f"{info['forced_passed']}/{info['forced_total']}",
            "; ".join(f"{k}:{v['msg']}" for k, v in info["details"].items()),
        ])
    out_path = OUT / "result_summary.xlsx"
    wb.save(out_path)
    print(f"OK → {out_path}")
    # 也保存 result_summary.csv
    df = pd.DataFrame([
        ["Q1 子问 1 (waste)", "7年累计净利润(万元)", q1["waste_profit_wan"]],
        ["Q1 子问 2 (discount)", "7年累计净利润(万元)", q1["discount_profit_wan"]],
        ["Q2 (蒙特卡洛)", f"均值(n={q2['n_scenarios']})", q2["mean_wan"]],
        ["Q2 (蒙特卡洛)", "CV", q2["cv"]],
        ["Q3 (弹性+间作)", f"均值(n={q3['n_scenarios']})", q3["mean_wan"]],
        ["Q3 (弹性+间作)", "CV", q3["cv"]],
        ["Q3 vs Q2 提升", "%", (q3["mean_wan"] - q2["mean_wan"]) / q2["mean_wan"] * 100],
    ], columns=["子问题", "指标", "值"])
    df.to_csv(OUT / "result_summary.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()