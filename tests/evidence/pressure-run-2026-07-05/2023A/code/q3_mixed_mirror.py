"""Q3: 在 60 MW 额定功率约束下,定日镜尺寸与安装高度可异构,
优化单位面积年平均输出热功率最大化。

策略(在 Q2 基础上分区共用):
- 把镜场按径向分成 3 圈区(近 r∈[100,180)、中 r∈[180,260)、远 r∈[260,350])
- 每圈区共用一套 (w_class, h_class),w_class ∈ {2,3,4,5,6,7,8},h_class ∈ {2,3,4,5,6}
- 用离散编码的 DE 优化

编码(int 索引):
  z[0..2] = 三个圈区的镜面尺寸索引(0..6)
  z[3..5] = 三个圈区的安装高度索引(0..4)
  z[6]    = 是否在每圈增加密度的密度系数(0..3)
"""
from __future__ import annotations
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common.seeds import SEED
from common.astro import all_time_points, sun_position, sun_vector, dni as compute_dni
from common.field_layout import R_OUTER, R_INNER, MIN_GAP
from common.efficiency import RECV_CENTER_Z_M, TOWER_HEIGHT_M, RECV_HEIGHT_M, RECV_RADIUS_M, ETA_REF

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "outputs")
FIGDIR = os.path.join(REPO, "figures")

W_CLASSES = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
H_CLASSES = [2.0, 3.0, 4.0, 5.0, 6.0]
RING_BOUNDS = [(R_INNER, 180.0), (180.0, 260.0), (260.0, R_OUTER + 0.001)]
DENSITY_OPTIONS = [1.0, 1.05, 1.10, 1.15]  # 每圈镜数密度系数


def build_mixed_field(w_idx: np.ndarray, h_idx: np.ndarray,
                      density_idx: int, seed: int = 20230705) -> pd.DataFrame:
    """按圈区生成异构镜场。

    每圈区的镜宽 = W_CLASSES[w_idx[i]],安装高度 = H_CLASSES[h_idx[i]]。
    每圈镜数 ≈ density * 2πr / (w + MIN_GAP)。
    """
    rng = np.random.default_rng(seed)
    rows = []
    for ri, (r_lo, r_hi) in enumerate(RING_BOUNDS):
        w = W_CLASSES[int(w_idx[ri])]
        h = H_CLASSES[int(h_idx[ri])]
        density = DENSITY_OPTIONS[int(density_idx)]
        spacing = w + MIN_GAP
        r = r_lo + 0.5 * spacing
        ring_local = 0
        while r <= r_hi - 0.5 * spacing:
            n_ring = max(1, int(density * 2.0 * math.pi * r / spacing))
            offset = (math.pi / n_ring) if ring_local % 2 == 1 else 0.0
            for k in range(n_ring):
                theta = 2.0 * math.pi * k / n_ring + offset + rng.normal(0.0, 0.015)
                x = r * math.cos(theta); y = r * math.sin(theta)
                rows.append((x, y, h, w, w))
            r += spacing
            ring_local += 1
    return pd.DataFrame(rows, columns=["x", "y", "h", "width", "height"])


def _truncate_mc(mp, n, target, sun, N, rng, w, h):
    import math
    from common.efficiency import SUN_HALF_ANGLE
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


def eval_mixed(w_idx, h_idx, density_idx,
               n_mc: int = 80, seed: int = 20230705,
               max_mirrors: int = 10**6):
    rng = np.random.default_rng(seed)
    df = build_mixed_field(w_idx, h_idx, density_idx, seed=seed)
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
        return 0.0, 0.0, 0.0, df, monthly_power, monthly_count, 0.0

    # 邻镜(按最近圈区搜索半径 = max_w + MIN_GAP + 2)
    from scipy.spatial import cKDTree
    tree = cKDTree(df[["x", "y"]].to_numpy())
    pairs = np.array(list(tree.query_pairs(r=80.0)))

    mirror_pos = df[["x", "y", "h"]].to_numpy().astype(float)
    mirror_w = df["width"].to_numpy().astype(float)
    mirror_h = df["height"].to_numpy().astype(float)

    for ti, (month, st, doy) in enumerate(time_points):
        alpha_s, gamma_s = sun_position(doy, st)
        if alpha_s <= 0.0:
            continue
        sun = sun_vector(alpha_s, gamma_s)
        d = compute_dni(alpha_s)
        d_vec = target_pos[None, :] - mirror_pos
        d_unit = d_vec / np.linalg.norm(d_vec, axis=1, keepdims=True)
        n_vec = sun[None, :] + d_unit
        n_vec = n_vec / np.linalg.norm(n_vec, axis=1, keepdims=True)
        cos_eta = np.clip((n_vec * sun[None, :]).sum(axis=1), 0.0, 1.0)
        d_hr = np.linalg.norm(d_vec, axis=1)
        eta_at = 0.99321 - 0.0001176 * d_hr + 1.97e-8 * d_hr * d_hr
        eta_trunc = np.zeros(len(df))
        for i in range(len(df)):
            local_rng = np.random.default_rng(int(rng.integers(0, 2 ** 32 - 1)))
            eta_trunc[i] = _truncate_mc(mirror_pos[i], n_vec[i], target_pos,
                                         sun, n_mc, local_rng,
                                         mirror_w[i], mirror_h[i])
        eta = cos_eta * eta_at * ETA_REF * eta_trunc
        power_tp = d * float((mirror_w * mirror_h * eta).sum())
        m = month - 1
        monthly_power[m] += power_tp / 1e3
        monthly_count[m] += 1
        monthly_eta[m] += float(eta.mean())
        monthly_eta_cnt[m] += 1

    valid = monthly_count > 0
    annual_power = float(monthly_power[valid].mean()) if valid.any() else 0.0
    annual_eta = float(monthly_eta[valid].mean() / max(1, monthly_eta_cnt[valid].mean())) if valid.any() else 0.0
    annual_E_A = annual_power * 1e6 / total_area
    return annual_power, annual_E_A, annual_eta, df, monthly_power, monthly_count, total_area


def de_optimize(pop: int = 24, gen: int = 40, n_mc: int = 80,
                max_mirrors: int = 800, seed: int = 20230705):
    """离散编码 DE:每个个体是长度 7 的整数向量。"""
    rng = np.random.default_rng(seed)
    # 决策维度与上下界
    lo = np.array([0, 0, 0, 0, 0, 0, 0])
    hi = np.array([len(W_CLASSES) - 1, len(W_CLASSES) - 1, len(W_CLASSES) - 1,
                    len(H_CLASSES) - 1, len(H_CLASSES) - 1, len(H_CLASSES) - 1,
                    len(DENSITY_OPTIONS) - 1])
    dim = len(lo)

    def decode(ind):
        return (ind[:3].astype(int), ind[3:6].astype(int), int(ind[6]))

    def obj(ind):
        w_idx, h_idx, d_idx = decode(ind)
        P, EA, eta, df, mp, mc, A = eval_mixed(w_idx, h_idx, d_idx,
                                                n_mc=n_mc, seed=seed,
                                                max_mirrors=max_mirrors)
        if P < 60.0:
            return -1e6 * (60.0 - P) ** 2
        return EA

    # 初始化种群
    X = np.empty((pop, dim), dtype=int)
    for d in range(dim):
        X[:, d] = rng.integers(lo[d], hi[d] + 1, size=pop)
    fitness = np.full(pop, -np.inf)
    for i in range(pop):
        fitness[i] = obj(X[i])
    best_idx = int(np.argmax(fitness))
    best_f = float(fitness[best_idx])
    best_x = X[best_idx].copy()
    best_curve = [best_f]
    print(f"[Q3-DE] init best={best_f:.4f}")

    no_improve = 0
    for g in range(1, gen + 1):
        for i in range(pop):
            idxs = [k for k in range(pop) if k != i]
            r1, r2, r3 = rng.choice(idxs, 3, replace=False)
            v = X[r1] + np.round(0.7 * (X[r2] - X[r3])).astype(int)
            v = np.clip(v, lo, hi)
            # 二项交叉
            mask = rng.random(dim) < 0.9
            j_rand = rng.integers(0, dim)
            mask[j_rand] = True
            u = np.where(mask, v, X[i])
            u = np.clip(u, lo, hi)
            f_u = obj(u)
            if f_u > fitness[i]:
                X[i] = u; fitness[i] = f_u
                if f_u > best_f:
                    best_f = float(f_u); best_x = u.copy(); no_improve = 0
        best_curve.append(best_f)
        if (g % 5 == 0) or g == 1:
            print(f"[Q3-DE] gen={g:3d}  best_fit={best_f:.4f}")
        no_improve += 1
        if no_improve >= 15:
            print(f"[Q3-DE] early stop at gen={g}")
            break

    w_idx, h_idx, d_idx = decode(best_x)
    P, EA, eta, df, mp, mc, A = eval_mixed(w_idx, h_idx, d_idx, n_mc=n_mc,
                                            seed=seed, max_mirrors=10**6)
    return dict(w_idx=w_idx, h_idx=h_idx, d_idx=d_idx,
                annual_power_MW=P, annual_E_A_Wpm2=EA, annual_eta=eta,
                field=df, monthly_power=mp, monthly_count=mc, total_area=A,
                best_curve=np.array(best_curve), best_x=best_x)


def main():
    t0 = time.time()
    res = de_optimize(pop=18, gen=30, n_mc=80)
    print("\n========= Q3 Result =========")
    print(f"w_idx (近/中/远)   : {res['w_idx'].tolist()}")
    print(f"h_idx (近/中/远)   : {res['h_idx'].tolist()}")
    print(f"density_idx        : {res['d_idx']}")
    w_classes = [W_CLASSES[i] for i in res['w_idx']]
    h_classes = [H_CLASSES[i] for i in res['h_idx']]
    print(f"w_classes (近/中/远): {w_classes}")
    print(f"h_classes (近/中/远): {h_classes}")
    print(f"annual power (MW)  : {res['annual_power_MW']:.4f}")
    print(f"annual E_A (W/m^2) : {res['annual_E_A_Wpm2']:.4f}")
    print(f"annual eta         : {res['annual_eta']:.4f}")
    print(f"# mirrors          : {len(res['field'])}")
    print(f"total area (m^2)   : {res['total_area']:.2f}")
    print(f"elapsed (s)        : {time.time() - t0:.1f}")

    df = res["field"]
    df.to_csv(os.path.join(OUTDIR, "heliostats_q3.csv"), index=False)

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
        "mirror_class_near": [f"w={W_CLASSES[res['w_idx'][0]]}m_h={H_CLASSES[res['h_idx'][0]]}m"],
        "mirror_class_mid": [f"w={W_CLASSES[res['w_idx'][1]]}m_h={H_CLASSES[res['h_idx'][1]]}m"],
        "mirror_class_far": [f"w={W_CLASSES[res['w_idx'][2]]}m_h={H_CLASSES[res['h_idx'][2]]}m"],
        "density_idx": [int(res['d_idx'])],
        "n_mirrors": [int(len(df))],
        "total_mirror_area_m2": [round(res["total_area"], 2)],
        "seed": [SEED],
        "n_mc": [80],
    })

    with pd.ExcelWriter(os.path.join(OUTDIR, "result3.xlsx"),
                        engine="openpyxl") as w:
        monthly_df.to_excel(w, sheet_name="Monthly", index=False)
        annual_df.to_excel(w, sheet_name="Annual", index=False)

    # Figures: layout (color by class) + convergence
    fig, ax = plt.subplots(figsize=(7, 7))
    cmap = plt.cm.viridis
    classes = np.zeros(len(df), dtype=int)
    rs = np.sqrt(df["x"] ** 2 + df["y"] ** 2)
    classes[(rs >= R_INNER) & (rs < 180.0)] = 0
    classes[(rs >= 180.0) & (rs < 260.0)] = 1
    classes[(rs >= 260.0)] = 2
    for c in range(3):
        sub = df[classes == c]
        ax.scatter(sub["x"], sub["y"], s=2, color=cmap(c / 2), alpha=0.8,
                   label=f"近/中/远={w_classes[c]}m".replace("近", str(w_classes[c])).replace("中", str(w_classes[c])).replace("远", str(w_classes[c])))
    ax.add_patch(plt.Circle((0, 0), R_OUTER, fill=False, color="black"))
    ax.add_patch(plt.Circle((0, 0), R_INNER, fill=False, color="grey", linestyle="--"))
    ax.scatter([0], [0], marker="*", color="red", s=120, label="吸收塔")
    # 重新画图例以反映类别
    for c in range(3):
        ax.scatter([], [], s=20, color=cmap(c / 2), label=f"圈区{c+1} w={w_classes[c]}m h={h_classes[c]}m")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_aspect("equal")
    ax.set_title(f"Q3 异构镜场布局 (N={len(df)})")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q3_mixed_layout.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(res["best_curve"], color="#1f77b4", lw=1.6)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best fitness (annual E_A, W/m²)")
    ax.set_title("Q3 DE 收敛曲线")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "q3_convergence.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()