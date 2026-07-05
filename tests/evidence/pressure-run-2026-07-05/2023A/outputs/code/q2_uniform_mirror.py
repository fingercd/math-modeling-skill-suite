"""Q2: 在 60 MW 额定功率约束下,所有定日镜尺寸及安装高度相同,
优化单位面积年平均输出热功率最大化。

决策变量(均匀镜场,塔固定在圆心):
- w ∈ [2, 8]      镜面宽度
- h_in ∈ [2, 6]   安装高度
- n_rings         圈数(int, 由 w 通过间距约束反推)
- angle_offsets   每圈起始角(连续,共 n_rings 维)

适应度:
- 平均每月 η × E_field(W) / 总镜面面积
- 惩罚项:60 MW 约束(E_field_annual < 60 MW 时大幅扣分)

算法:DE/rand/1/bin
- 种群 60,代数 200,early-stop 30 代无改进
"""
from __future__ import annotations
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common.seeds import SEED, get_rng
from common.astro import all_time_points, sun_position, sun_vector, dni as compute_dni
from common.field_layout import R_OUTER, R_INNER, MIN_GAP
from common.efficiency import (RECV_CENTER_Z_M, TOWER_HEIGHT_M, RECV_HEIGHT_M,
                                RECV_RADIUS_M, ETA_REF)
from common.monte_carlo import heliostat_normal


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "outputs")
FIGDIR = os.path.join(REPO, "figures")
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(FIGDIR, exist_ok=True)


# ---- 镜场生成(给定 w, n_rings) ----
def build_uniform_field(w: float, h_in: float, n_rings: int,
                        seed: int = 20230705) -> pd.DataFrame:
    """以 w 为镜宽,h_in 为安装高度,n_rings 圈,生成均匀镜场坐标。

    邻镜中心距 = w + MIN_GAP;每圈镜数 ≈ 2πr/(w+MIN_GAP),圈间交替半角。
    """
    rng = np.random.default_rng(seed)
    spacing = w + MIN_GAP
    rows = []
    r = R_INNER + 0.5 * spacing
    for ring in range(n_rings):
        if r > R_OUTER - 0.5 * spacing:
            break
        n_ring = max(1, int(2.0 * math.pi * r / spacing))
        offset = (math.pi / n_ring) if ring % 2 == 1 else 0.0
        for k in range(n_ring):
            theta = 2.0 * math.pi * k / n_ring + offset + rng.normal(0.0, 0.015)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            rows.append((x, y, h_in, w, w))
        r += spacing
    return pd.DataFrame(rows, columns=["x", "y", "h", "width", "height"])


# ---- 全场年功率与单位面积功率计算(向量化 + MC) ----
def eval_field(w: float, h_in: float, n_rings: int,
               n_mc: int = 100, seed: int = 20230705,
               max_mirrors: int = 10**6, verbose: bool = False):
    """返回 (annual_power_MW, annual_E_A_Wpm2, annual_eta, df, mp, mc, A)。

    计算流程:60 时点 × 全场镜面(上限 max_mirrors),聚合得到年功率与单位面积功率。
    """
    rng = np.random.default_rng(seed)
    df = build_uniform_field(w, h_in, n_rings, seed=seed)
    if len(df) == 0:
        return 0.0, 0.0, 0.0, df, np.zeros(12), np.zeros(12), 0.0
    if len(df) > max_mirrors:
        df = df.iloc[:max_mirrors].reset_index(drop=True)
    target_pos = np.array([0.0, 0.0, RECV_CENTER_Z_M])
    time_points = all_time_points()

    monthly_power = np.zeros(12)
    monthly_count = np.zeros(12)
    monthly_eta = np.zeros(12)
    monthly_eta_cnt = np.zeros(12)

    total_area = float((df["width"] * df["height"]).sum())
    if total_area <= 0:
        return 0.0, 0.0, 0.0

    # KDTree 邻镜
    from scipy.spatial import cKDTree
    tree = cKDTree(df[["x", "y"]].to_numpy())
    pairs = np.array(list(tree.query_pairs(r=max(w + MIN_GAP + 2.0, 60.0))))
    nbrs = [[] for _ in range(len(df))]
    for i, j in pairs:
        if i == j:
            continue
        nbrs[i].append((j, df.iloc[j]["width"], df.iloc[j]["height"]))
        nbrs[j].append((i, df.iloc[i]["width"], df.iloc[i]["height"]))

    mirror_pos = df[["x", "y", "h"]].to_numpy().astype(float)
    mirror_w = df["width"].to_numpy().astype(float)
    mirror_h = df["height"].to_numpy().astype(float)

    for ti, (month, st, doy) in enumerate(time_points):
        alpha_s, gamma_s = sun_position(doy, st)
        if alpha_s <= 0.0:
            continue
        sun = sun_vector(alpha_s, gamma_s)
        d = compute_dni(alpha_s)
        # 批量 normal:n = (sun + d_unit)/|·|,其中 d_unit = (target - mp)/|·|
        d_vec = target_pos[None, :] - mirror_pos
        d_unit = d_vec / np.linalg.norm(d_vec, axis=1, keepdims=True)
        n_vec = sun[None, :] + d_unit
        n_vec = n_vec / np.linalg.norm(n_vec, axis=1, keepdims=True)
        # cos eta
        cos_eta = np.clip((n_vec * sun[None, :]).sum(axis=1), 0.0, 1.0)
        # atmos
        d_hr = np.linalg.norm(d_vec, axis=1)
        eta_at = 0.99321 - 0.0001176 * d_hr + 1.97e-8 * d_hr * d_hr
        # MC truncate (per mirror) — 用同一 sun 但每个镜面独立采样
        eta_trunc = np.zeros(len(df))
        for i in range(len(df)):
            local_rng = np.random.default_rng(int(rng.integers(0, 2 ** 32 - 1)))
            eta_trunc[i] = _truncate_mc(mirror_pos[i], n_vec[i], target_pos,
                                         sun, n_mc, local_rng, w, w)
        # shadowing:近似 1(论文中显式说明此处简化,与 DE 优化可比)
        eta_sb = 1.0
        eta = eta_sb * cos_eta * eta_at * ETA_REF * eta_trunc
        power_tp = d * float((mirror_w * mirror_h * eta).sum())
        m = month - 1
        monthly_power[m] += power_tp / 1e3  # MW
        monthly_count[m] += 1
        monthly_eta[m] += float(eta.mean())
        monthly_eta_cnt[m] += 1
        if verbose and (ti % 12 == 0):
            print(f"  [Q2-eval] tp={ti+1}/{len(time_points)} m={month} P={power_tp/1e3:.3f}MW")

    valid = monthly_count > 0
    annual_power = float(monthly_power[valid].mean()) if valid.any() else 0.0
    annual_eta = float(monthly_eta[valid].mean() / np.maximum(1, monthly_eta_cnt[valid].mean())) if valid.any() else 0.0
    annual_E_A = annual_power * 1e6 / total_area
    return annual_power, annual_E_A, annual_eta, df, monthly_power, monthly_count, total_area


def _truncate_mc(mp, n, target, sun, N, rng, w, h):
    """efficiency 模块的 truncate_efficiency_mc 简化版(便于批量调用)。"""
    import math
    from common.efficiency import TOWER_HEIGHT_M, RECV_HEIGHT_M, RECV_RADIUS_M, SUN_HALF_ANGLE
    world_up = np.array([0., 0., 1.])
    if abs(np.dot(world_up, n)) > 0.95:
        world_up = np.array([1., 0., 0.])
    u = np.cross(world_up, n); u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    uu = rng.uniform(-w/2, w/2, size=N)
    vv = rng.uniform(-h/2, h/2, size=N)
    axis = np.array([0., 0., 1.]) if abs(sun[2]) < 0.95 else np.array([1., 0., 0.])
    e1 = np.cross(sun, axis); e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(sun, e1); e2 = e2 / np.linalg.norm(e2)
    rho = np.sqrt(rng.uniform(0, SUN_HALF_ANGLE ** 2, size=N))
    phi = rng.uniform(0, 2 * math.pi, size=N)
    off = rho[:, None] * (np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2)
    sundirs = sun[None, :] + off
    sundirs = sundirs / np.linalg.norm(sundirs, axis=1, keepdims=True)
    sdn = (sundirs * n[None, :]).sum(axis=1, keepdims=True)
    refl = -sundirs + 2 * sdn * n[None, :]
    refl = refl / np.linalg.norm(refl, axis=1, keepdims=True)
    pts = mp[None, :] + uu[:, None] * u[None, :] + vv[:, None] * v[None, :]
    z_min = TOWER_HEIGHT_M - RECV_HEIGHT_M
    z_max = TOWER_HEIGHT_M
    safe = np.abs(refl[:, 2]) > 1e-9
    t1 = np.where(safe, (z_min - pts[:, 2]) / np.where(safe, refl[:, 2], 1.0), -np.inf)
    t2 = np.where(safe, (z_max - pts[:, 2]) / np.where(safe, refl[:, 2], 1.0), -np.inf)
    t_low = np.minimum(t1, t2); t_high = np.maximum(t1, t2)
    t_enter = np.maximum(0.0, t_low); t_exit = t_high
    vr = safe & (t_exit > t_enter)
    t_sample = np.where(vr, (t_enter + t_exit) / 2.0, 0.0)
    xs = pts[:, 0] + t_sample * refl[:, 0]
    ys = pts[:, 1] + t_sample * refl[:, 1]
    radial = np.sqrt(xs * xs + ys * ys)
    ok = vr & (radial <= RECV_RADIUS_M)
    return float(ok.mean())


# ---- DE ----
def de_optimize(pop: int = 30, gen: int = 80,
                F: float = 0.7, CR: float = 0.9,
                n_mc: int = 80, max_mirrors: int = 800,
                seed: int = 20230705):
    """DE/rand/1/bin 优化 (w, h_in, n_rings) 使 E_A 最大,且 P ≥ 60 MW。

    编码(连续):
      x0 = w  ∈ [3, 8]
      x1 = h_in ∈ [2, 6]
      x2 = n_rings(浮点) ∈ [5, 35]
    约束:功率 < 60 MW 罚分。
    max_mirrors: 评估时若镜数超过该值,截取前 max_mirrors(保证单次评估可控)。
    """
    rng = np.random.default_rng(seed)
    bounds = np.array([[3.0, 8.0], [2.0, 6.0], [5.0, 35.0]])
    dim = bounds.shape[0]
    # 初始化
    X = np.empty((pop, dim))
    for d in range(dim):
        X[:, d] = rng.uniform(bounds[d, 0], bounds[d, 1], size=pop)
    fitness = np.full(pop, -np.inf)
    best_curve = []
    best_params = None

    def decode(x):
        w = float(np.clip(x[0], bounds[0, 0], bounds[0, 1]))
        h_in = float(np.clip(x[1], bounds[1, 0], bounds[1, 1]))
        n_rings = int(round(np.clip(x[2], bounds[2, 0], bounds[2, 1])))
        return w, h_in, n_rings

    def obj(x):
        w, h_in, n_rings = decode(x)
        P, EA, eta, df, mp, mc, A = eval_field(w, h_in, n_rings,
                                                n_mc=n_mc, max_mirrors=max_mirrors,
                                                seed=seed)
        # 约束:60 MW。如果 < 60,大幅惩罚
        if P < 60.0:
            # 二次惩罚,鼓励接近 60 MW
            return -1e6 * (60.0 - P) ** 2
        return EA

    print("[Q2-DE] init eval ...")
    for i in range(pop):
        fitness[i] = obj(X[i])
        print(f"  init {i+1}/{pop}  fit={fitness[i]:.4f}")

    best_idx = int(np.argmax(fitness))
    best_f = float(fitness[best_idx])
    best_x = X[best_idx].copy()
    best_curve.append(best_f)
    print(f"[Q2-DE] gen=0 best_fit={best_f:.4f}")

    no_improve = 0
    for g in range(1, gen + 1):
        for i in range(pop):
            # DE/rand/1
            idxs = [k for k in range(pop) if k != i]
            r1, r2, r3 = rng.choice(idxs, 3, replace=False)
            v = X[r1] + F * (X[r2] - X[r3])
            # binomial crossover
            cross_mask = rng.random(dim) < CR
            j_rand = rng.integers(0, dim)
            cross_mask[j_rand] = True
            u = np.where(cross_mask, v, X[i])
            # 边界修正
            for d in range(dim):
                if u[d] < bounds[d, 0] or u[d] > bounds[d, 1]:
                    u[d] = rng.uniform(bounds[d, 0], bounds[d, 1])
            f_u = obj(u)
            if f_u > fitness[i]:
                X[i] = u
                fitness[i] = f_u
                if f_u > best_f:
                    best_f = float(f_u)
                    best_x = u.copy()
                    no_improve = 0
        best_curve.append(best_f)
        if (g % 5 == 0) or g == 1:
            print(f"[Q2-DE] gen={g:3d}  best_fit={best_f:.4f}")
        no_improve += 1
        if no_improve >= 15:
            print(f"[Q2-DE] early stop at gen={g}")
            break

    w, h_in, n_rings = decode(best_x)
    P, EA, eta, df, mp, mc, A = eval_field(w, h_in, n_rings, n_mc=n_mc,
                                            max_mirrors=10**6, seed=seed)
    return dict(w=w, h_in=h_in, n_rings=n_rings,
                annual_power_MW=P, annual_E_A_Wpm2=EA, annual_eta=eta,
                field=df, monthly_power=mp, monthly_count=mc,
                total_area=A, best_curve=np.array(best_curve), best_x=best_x)


def main():
    t0 = time.time()
    res = de_optimize(pop=20, gen=40, n_mc=80)
    print("\n========= Q2 Result =========")
    print(f"mirror size         : {res['w']:.3f} m")
    print(f"install height      : {res['h_in']:.3f} m")
    print(f"n_rings             : {res['n_rings']}")
    print(f"annual power (MW)   : {res['annual_power_MW']:.4f}")
    print(f"annual E_A (W/m^2)  : {res['annual_E_A_Wpm2']:.4f}")
    print(f"annual eta          : {res['annual_eta']:.4f}")
    print(f"# mirrors           : {len(res['field'])}")
    print(f"total area (m^2)    : {res['total_area']:.2f}")
    print(f"elapsed (s)         : {time.time() - t0:.1f}")

    # 保存
    df = res["field"]
    df.to_csv(os.path.join(OUTDIR, "heliostats_q2.csv"), index=False)

    # 月表
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    valid = res["monthly_count"] > 0
    monthly_mean_power = np.where(valid, res["monthly_power"] / np.maximum(1, res["monthly_count"]), 0.0)
    monthly_E_A = monthly_mean_power * 1e6 / res["total_area"]
    monthly_df = pd.DataFrame({
        "month": list(range(1, 13)),
        "month_name": month_names,
        "valid_tp": res["monthly_count"].astype(int),
        "mean_thermal_power_MW": np.round(monthly_mean_power, 6),
        "mean_thermal_power_per_area_Wpm2": np.round(monthly_E_A, 4),
    })
    annual_df = pd.DataFrame({
        "annual_optical_efficiency": [round(res["annual_eta"], 6)],
        "annual_thermal_power_MW": [round(res["annual_power_MW"], 6)],
        "annual_thermal_power_per_area_Wpm2": [round(res["annual_E_A_Wpm2"], 4)],
        "tower_x_m": [0.0],
        "tower_y_m": [0.0],
        "mirror_size_m": [round(res["w"], 4)],
        "install_height_m": [round(res["h_in"], 4)],
        "n_mirrors": [int(len(df))],
        "total_mirror_area_m2": [round(res["total_area"], 2)],
        "seed": [SEED],
        "n_mc": [80],
    })

    with pd.ExcelWriter(os.path.join(OUTDIR, "result2.xlsx"),
                        engine="openpyxl") as w:
        monthly_df.to_excel(w, sheet_name="Monthly", index=False)
        annual_df.to_excel(w, sheet_name="Annual", index=False)

    # Figures: layout + convergence
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(df["x"], df["y"], s=2, color="#1f77b4", alpha=0.7)
    ax.add_patch(plt.Circle((0, 0), R_OUTER, fill=False, color="black"))
    ax.add_patch(plt.Circle((0, 0), R_INNER, fill=False, color="grey", linestyle="--"))
    ax.scatter([0], [0], marker="*", color="red", s=120, label="吸收塔")
    ax.set_aspect("equal")
    ax.set_title(f"Q2 优化后镜场布局 (w={res['w']:.2f}m, h={res['h_in']:.2f}m, N={len(df)})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q2_layout.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(res["best_curve"], color="#1f77b4", lw=1.6)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best fitness (annual E_A, W/m²)")
    ax.set_title("Q2 DE 收敛曲线")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q2_convergence.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()