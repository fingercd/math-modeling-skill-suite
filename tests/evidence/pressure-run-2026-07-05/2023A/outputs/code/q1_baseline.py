"""Q1: 给定 1745 面 6×6 镜面、4 m 安装高度、中心塔,计算 60 个时点的
光学效率与单位面积输出热功率,输出月表与年表。

约定:
- 塔坐标 (0, 0)
- 镜面坐标由 common.field_layout.baseline_field() 合成(自合成策略)
- 时点 60 个:12 月 × 5 时点(每月 21 日 9:00/10:30/12:00/13:30/15:00)
- 每时点功率按"该时点瞬时 DNI × Σ(A_i η_i)"计算
- 年均 = 12 个月均值,每月均值 = 该月 5 时点均值
- 输出热功率单位:kW(乘 1e-3 转 MW)
"""
from __future__ import annotations
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common.seeds import SEED, get_rng
from common.astro import (all_time_points, sun_position, sun_vector,
                          dni as compute_dni)
from common.field_layout import baseline_field
from common.efficiency import (heliostat_normal, atmos_transmission,
                                cosine_efficiency, truncate_efficiency_mc,
                                sb_efficiency_grid, ETA_REF,
                                TOWER_HEIGHT_M, RECV_CENTER_Z_M)
from common.monte_carlo import heliostat_normal as hn_mc  # 别名避免循环导入


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "outputs")
FIGDIR = os.path.join(REPO, "figures")
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(FIGDIR, exist_ok=True)


# ---- 邻镜搜索:对每面镜选 r < 80 m 的邻镜集合 ----
def build_neighbor_lists(df: pd.DataFrame, search_radius: float = 80.0):
    """KDTree 不依赖 sklearn,使用 scipy。"""
    from scipy.spatial import cKDTree
    xy = df[["x", "y"]].to_numpy()
    tree = cKDTree(xy)
    pairs = tree.query_pairs(r=search_radius)
    pairs = np.array(list(pairs))
    # 构造 neighbors[i] = list of (j, w_j, h_j)
    nbrs = [[] for _ in range(len(df))]
    for i, j in pairs:
        if i == j:
            continue
        nbrs[i].append((j, df.iloc[j]["width"], df.iloc[j]["height"]))
    return nbrs


# ---- 单镜在单时点的全套效率 ----
def mirror_eta_one_tp(mirror_pos, mirror_w, mirror_h, sun, target_pos,
                      nbr_xy_arr, nbr_wh_arr, n_mc, rng) -> dict:
    n = hn_mc(mirror_pos, target_pos, sun)
    cos_v = cosine_efficiency(sun, n)
    d_hr = float(np.linalg.norm(target_pos - mirror_pos))
    eta_at = atmos_transmission(d_hr)
    eta_sb = sb_efficiency_grid(mirror_pos, mirror_w, mirror_h,
                                sun, nbr_xy_arr, nbr_wh_arr)
    eta_trunc = truncate_efficiency_mc(mirror_pos, n, target_pos, sun,
                                       n_samples=n_mc, rng=rng)
    eta = eta_sb * cos_v * eta_at * ETA_REF * eta_trunc
    return dict(eta=eta, eta_sb=eta_sb, eta_cos=cos_v,
                eta_at=eta_at, eta_trunc=eta_trunc)


def run(n_mc: int = 200, n_helio: int = 1745, verbose: bool = True):
    t0 = time.time()
    rng = get_rng()
    df = baseline_field(n_helio, seed=SEED)
    df.to_csv(os.path.join(OUTDIR, "heliostats_baseline.csv"), index=False)
    if verbose:
        print(f"[Q1] field built: {len(df)} mirrors, t={time.time()-t0:.1f}s")

    nbrs = build_neighbor_lists(df, search_radius=80.0)
    if verbose:
        avg_n = np.mean([len(x) for x in nbrs])
        print(f"[Q1] avg neighbors per mirror = {avg_n:.1f}")

    target_pos = np.array([0.0, 0.0, RECV_CENTER_Z_M])
    time_points = all_time_points()  # [(month, st, doy), ...]
    n_tp = len(time_points)

    # 每月聚合容器
    monthly_eta_sum = np.zeros(12)
    monthly_eta_cnt = np.zeros(12)
    monthly_power_sum = np.zeros(12)  # kW 时点瞬时(不是能量)
    monthly_area = 0.0

    total_area = (df["width"] * df["height"]).sum()

    # 主循环:对每时点遍历每面镜
    for ti, (month, st, doy) in enumerate(time_points):
        alpha_s, gamma_s = sun_position(doy, st)
        if alpha_s <= 0.0:
            continue
        sun = sun_vector(alpha_s, gamma_s)
        d = compute_dni(alpha_s)  # kW/m^2
        power_tp = 0.0
        eta_sum_tp = 0.0
        cnt_tp = 0
        # 镜面逐面循环(向量化阴影遮挡与 MC 较复杂,此处保留单镜循环)
        # 为加速,采用每镜共用 rng 但预分配
        for i in range(len(df)):
            row = df.iloc[i]
            mp = np.array([row.x, row.y, row.h], dtype=float)
            # 邻镜
            if len(nbrs[i]) > 0:
                nbr_arr = np.array([(df.iloc[j]["x"], df.iloc[j]["y"])
                                    for j, _, _ in nbrs[i]])
                wh_arr = np.array([(w, h) for _, w, h in nbrs[i]])
            else:
                nbr_arr = np.zeros((0, 2))
                wh_arr = np.zeros((0, 2))
            res = mirror_eta_one_tp(mp, row.width, row.height, sun, target_pos,
                                     nbr_arr, wh_arr, n_mc, rng)
            eta_i = res["eta"]
            area_i = row.width * row.height
            power_tp += d * area_i * eta_i  # kW
            eta_sum_tp += eta_i
            cnt_tp += 1
        # 写入月聚合
        m = month - 1
        monthly_eta_sum[m] += eta_sum_tp / max(1, cnt_tp)
        monthly_eta_cnt[m] += 1
        monthly_power_sum[m] += power_tp / 1e3  # MW
        if verbose and (ti % 10 == 0):
            print(f"[Q1] tp={ti+1:3d}/{n_tp}  m={month:02d} st={st:5.2f}  "
                  f"power={power_tp/1e3:7.3f}MW  mean_eta={eta_sum_tp/max(1,cnt_tp):.4f}  "
                  f"t={time.time()-t0:.1f}s")

    # 月均:平均 η(时点间)与平均功率(时点间)
    monthly_mean_eta = np.where(monthly_eta_cnt > 0,
                                 monthly_eta_sum / np.maximum(1, monthly_eta_cnt),
                                 0.0)
    monthly_mean_power = np.where(monthly_eta_cnt > 0,
                                   monthly_power_sum / np.maximum(1, monthly_eta_cnt),
                                   0.0)
    monthly_E_A = monthly_mean_power * 1e6 / total_area  # W/m^2

    # 年均
    valid = monthly_eta_cnt > 0
    annual_eta = float(monthly_mean_eta[valid].mean())
    annual_power = float(monthly_mean_power[valid].mean())
    annual_E_A = float(monthly_E_A[valid].mean())

    # 写出月表
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_df = pd.DataFrame({
        "month": list(range(1, 13)),
        "month_name": month_names,
        "valid_tp": monthly_eta_cnt.astype(int),
        "mean_optical_efficiency": np.round(monthly_mean_eta, 6),
        "mean_thermal_power_MW": np.round(monthly_mean_power, 6),
        "mean_thermal_power_per_area_Wpm2": np.round(monthly_E_A, 4),
    })
    annual_df = pd.DataFrame({
        "annual_optical_efficiency": [round(annual_eta, 6)],
        "annual_thermal_power_MW": [round(annual_power, 6)],
        "annual_thermal_power_per_area_Wpm2": [round(annual_E_A, 4)],
        "total_mirror_area_m2": [round(total_area, 2)],
        "n_mirrors": [int(len(df))],
        "n_mc_samples": [n_mc],
        "seed": [SEED],
    })

    # Excel
    with pd.ExcelWriter(os.path.join(OUTDIR, "result1.xlsx"),
                        engine="openpyxl") as w:
        monthly_df.to_excel(w, sheet_name="Monthly", index=False)
        annual_df.to_excel(w, sheet_name="Annual", index=False)

    # Figure: monthly
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].bar(monthly_df["month_name"], monthly_df["mean_optical_efficiency"],
                color="#1f77b4", alpha=0.85)
    axes[0].set_ylabel("月平均光学效率 η")
    axes[0].set_title("Q1 月平均光学效率")
    axes[0].grid(True, alpha=0.3, axis="y")
    axes[1].bar(monthly_df["month_name"], monthly_df["mean_thermal_power_per_area_Wpm2"],
                color="#d62728", alpha=0.85)
    axes[1].set_ylabel("单位面积输出热功率 (W/m²)")
    axes[1].set_title("Q1 月平均单位面积输出热功率")
    axes[1].grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q1_monthly_efficiency.png"), dpi=150)
    plt.close(fig)

    # Figure: annual summary
    fig, ax = plt.subplots(figsize=(7, 4))
    metrics = ["年均光学效率 η", "年均输出热功率(MW)", "单位面积年功率(W/m²)"]
    values = [annual_eta, annual_power, annual_E_A]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    bars = ax.bar(metrics, values, color=colors, alpha=0.85)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.4f}",
                ha="center", va="bottom", fontsize=10)
    ax.set_title("Q1 年均汇总")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q1_annual_summary.png"), dpi=150)
    plt.close(fig)

    if verbose:
        print("\n========= Q1 Annual Summary =========")
        print(f"年平均光学效率        : {annual_eta:.4f}")
        print(f"年平均输出热功率(MW)  : {annual_power:.4f}")
        print(f"单位面积年功率(W/m²) : {annual_E_A:.4f}")
        print(f"总镜面积(m²)          : {total_area:.1f}")
        print(f"耗时(s)               : {time.time()-t0:.1f}")

    return dict(annual_eta=annual_eta, annual_power=annual_power,
                annual_E_A=annual_E_A, total_area=float(total_area),
                monthly=monthly_df)


if __name__ == "__main__":
    # 为加快压力测试,默认 n_mc=200;完整版本可调到 400
    run(n_mc=200, n_helio=1745)