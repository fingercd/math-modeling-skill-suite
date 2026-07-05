"""plot_results.py — 生成论文全部图表.

输出: figures/*.png + modeling_workflow.pdf
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
# 中文字体配置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
import pandas as pd
import openpyxl

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_structure import load_processed
from objective import crop_unit_profit, base_sales_capacity

BASE = Path(__file__).resolve().parent
FIG = BASE.parent / "figures"
FIG.mkdir(exist_ok=True)
OUT = BASE.parent / "outputs"


def plot_profit_heatmap(processed, path):
    """41 种作物 × 6 类地块的亩净利润热力图."""
    crops = processed["crops"]
    plot_types = ["平旱地", "梯田", "山坡地", "水浇地", "普通大棚", "智慧大棚"]
    M = np.zeros((len(crops), len(plot_types)))
    for i, c in enumerate(crops):
        for j, pt in enumerate(plot_types):
            s = 1 if pt in ("平旱地", "梯田", "山坡地") else 1
            st = crop_unit_profit(processed, c["code"], pt, s, mode="discount")
            if st:
                M[i, j] = st["unit_profit_normal"]
            else:
                M[i, j] = np.nan
    fig, ax = plt.subplots(figsize=(10, 14))
    im = ax.imshow(M, aspect="auto", cmap="RdYlGn")
    ax.set_xticks(range(len(plot_types)))
    ax.set_xticklabels(plot_types, rotation=30)
    ax.set_yticks(range(len(crops)))
    ax.set_yticklabels([f"{c['code']}-{c['name']}" for c in crops], fontsize=8)
    ax.set_title("亩净利润热力图 (元/亩, 正常销售)")
    plt.colorbar(im, ax=ax, label="元/亩")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_workflow(path):
    """六阶段流程图 (matplotlib)."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    boxes = [
        ("附件解析\n(fujian1-3)", 1, 2, "#7fb3d5"),
        ("动作空间压缩\n(1062 三元组)", 3.5, 2, "#76c7a7"),
        ("评估函数\n(收入-成本-超产)", 6, 2, "#f7c873"),
        ("桶排序贪心\n+ 蒙特卡洛\n+ 间作", 8.5, 2, "#ec7063"),
        ("13 类约束\n校验", 11, 2, "#af7ac5"),
        ("Excel + 图", 13, 2, "#5dade2"),
    ]
    for label, x, y, color in boxes:
        ax.add_patch(mpatches.FancyBboxPatch((x-0.8, y-0.7), 1.6, 1.4,
                                             boxstyle="round,pad=0.05",
                                             facecolor=color, edgecolor="black"))
        ax.text(x, y, label, ha="center", va="center", fontsize=9)
    for i in range(5):
        x1 = boxes[i][1] + 0.8
        x2 = boxes[i+1][1] - 0.8
        ax.annotate("", xy=(x2, 2), xytext=(x1, 2),
                    arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.set_title("CUMCM 2024C 整体建模流程图", fontsize=12)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_q1_compare(processed, x_waste, x_discount, path):
    """Q1 两种情形 7 年累计种植结构对比 (按作物类型聚合)."""
    crops = processed["crops"]
    type_map = {}
    for c in crops:
        # 粗聚合
        if "豆类" in c["type"]:
            type_map[c["id"]] = "豆类"
        elif c["type"] == "粮食":
            type_map[c["id"]] = "粮食"
        elif c["type"] == "粮食（豆类）":
            type_map[c["id"]] = "豆类"
        elif c["type"] == "水稻" or c["code"] == 16:
            type_map[c["id"]] = "水稻"
        elif c["type"].startswith("蔬菜"):
            type_map[c["id"]] = "蔬菜"
        elif c["type"] == "食用菌":
            type_map[c["id"]] = "食用菌"
        else:
            type_map[c["id"]] = c["type"]
    cats = ["豆类", "粮食", "水稻", "蔬菜", "食用菌"]
    waste_sum = {k: 0.0 for k in cats}
    disc_sum = {k: 0.0 for k in cats}
    for (pid, cid, s, y), v in x_waste.items():
        cat = type_map.get(cid, "其他")
        if cat in waste_sum:
            waste_sum[cat] += v
    for (pid, cid, s, y), v in x_discount.items():
        cat = type_map.get(cid, "其他")
        if cat in disc_sum:
            disc_sum[cat] += v
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.35
    x_pos = np.arange(len(cats))
    ax.bar(x_pos - width/2, [waste_sum[c] for c in cats], width, label="子问 1 (waste)", color="#ec7063")
    ax.bar(x_pos + width/2, [disc_sum[c] for c in cats], width, label="子问 2 (discount)", color="#5dade2")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cats)
    ax.set_ylabel("7 年累计种植面积 (亩)")
    ax.set_title("Q1 两种情形下 7 年累计种植结构对比")
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_q2_scenarios(path, scenarios_csv):
    """Q2 蒙特卡洛场景利润分布 + 7 年累计."""
    df = pd.read_csv(scenarios_csv)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(df["profit_wan"], bins=40, color="#76c7a7", edgecolor="black")
    axes[0].axvline(df["profit_wan"].mean(), color="red", linestyle="--", label=f"均值={df['profit_wan'].mean():.1f}")
    axes[0].set_xlabel("7 年累计净利润 (万元)")
    axes[0].set_ylabel("场景数")
    axes[0].set_title("Q2 蒙特卡洛场景利润分布")
    axes[0].legend()
    # 第二张: 排序后看尾部
    sorted_p = df["profit_wan"].sort_values().reset_index(drop=True)
    axes[1].plot(sorted_p, color="#5dade2")
    axes[1].fill_between(range(len(sorted_p)), 0, sorted_p, alpha=0.3)
    axes[1].set_xlabel("场景序号 (按利润升序)")
    axes[1].set_ylabel("7 年累计净利润 (万元)")
    axes[1].set_title("Q2 场景利润升序排列")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_q3_intercrop(processed, x_q3, path):
    """Q3 间作 + 替代机制 — 豆类覆盖占比."""
    crops = processed["crops"]
    legume_ids = {c["id"] for c in crops if c["is_legume"]}
    plots = processed["plots"]
    plot_by_id = {p["id"]: p for p in plots}
    yearly_legume = {y: 0.0 for y in range(2024, 2031)}
    yearly_total = {y: 0.0 for y in range(2024, 2031)}
    for (pid, cid, s, y), v in x_q3.items():
        if v <= 0:
            continue
        yearly_total[y] += v
        if cid in legume_ids:
            yearly_legume[y] += v
    ratio = [yearly_legume[y] / yearly_total[y] * 100 if yearly_total[y] > 0 else 0 for y in range(2024, 2031)]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(2024, 2031), ratio, color="#76c7a7", edgecolor="black")
    ax.set_xlabel("年份")
    ax.set_ylabel("豆类占当年种植面积比例 (%)")
    ax.set_title("Q3 间作机制下豆类覆盖占比")
    for i, r in enumerate(ratio):
        ax.text(2024 + i, r + 0.5, f"{r:.1f}%", ha="center")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_sensitivity(processed, path):
    """σ 灵敏度: 跑 7 个 σ 值, 看 Q2 均值与 CV."""
    from algo.greedy import greedy_solve
    from objective import base_sales_capacity
    sigmas = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    means, cvs = [], []
    for s in sigmas:
        rng = np.random.default_rng(42)
        profits = []
        crops = processed["crops"]
        caps_default = {c["id"]: base_sales_capacity(processed, c["code"]) for c in crops}
        for k in range(80):
            caps_k = {c["id"]: caps_default[c["id"]] * max(0.5, 1 + rng.normal(0, s)) for c in crops}
            pm = max(0.5, 1 + rng.normal(0, s))
            cm = max(0.5, 1 + rng.normal(0, s))
            ym = max(0.5, 1 + rng.normal(0, s))
            x, p = greedy_solve(mode="discount", n_years=7, fixed_caps=caps_k,
                                price_mult=pm, cost_mult=cm, yield_mult=ym)
            profits.append(p)
        arr = np.array(profits)
        means.append(arr.mean() / 1e4)
        cvs.append(arr.std() / arr.mean() if arr.mean() else 0)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    color1 = "#5dade2"
    ax1.bar([str(s) for s in sigmas], means, color=color1, alpha=0.7, label="均值 (万元)")
    ax1.set_xlabel("扰动 σ")
    ax1.set_ylabel("Q2 均值 (万元)", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax2 = ax1.twinx()
    color2 = "#ec7063"
    ax2.plot([str(s) for s in sigmas], cvs, color=color2, marker="o", label="CV")
    ax2.set_ylabel("波动 CV", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    plt.title("Q2 σ 灵敏度 (均值与波动)")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    processed = load_processed()
    print("plot_workflow ...")
    plot_workflow(FIG / "modeling_workflow.pdf")
    print("plot_profit_heatmap ...")
    plot_profit_heatmap(processed, FIG / "profit_heatmap.png")
    # 重新跑 Q1 拿 x
    from algo.greedy import greedy_solve
    x_w, _ = greedy_solve(mode="waste", n_years=7)
    x_d, _ = greedy_solve(mode="discount", n_years=7)
    print("plot_q1 ...")
    plot_q1_compare(processed, x_w, x_d, FIG / "q1_strategy.png")
    if (OUT / "result2_scenarios.csv").exists():
        print("plot_q2 ...")
        plot_q2_scenarios(FIG / "q2_robust_path.png", OUT / "result2_scenarios.csv")
    if (OUT / "result3_scenarios.csv").exists():
        from algo.greedy import greedy_solve
        x3, _ = greedy_solve(mode="elastic", n_years=7, legume_cover=True, substitute_rho=0.3)
        print("plot_q3 ...")
        plot_q3_intercrop(processed, x3, FIG / "q3_intercropping.png")
    print("plot_sensitivity ...")
    plot_sensitivity(processed, FIG / "sensitivity.png")
    print("Done.")


if __name__ == "__main__":
    main()