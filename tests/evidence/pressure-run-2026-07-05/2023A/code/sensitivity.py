"""灵敏度分析:对 Q1 baseline 的关键参数扰动,记录单位面积年功率变化。

参数:
- η_ref ∈ {0.88, 0.90, 0.92, 0.94, 0.96}
- 安装高度 ∈ {2, 3, 4, 5, 6}
- 集热器直径 ∈ {5, 6, 7, 8, 9}
- 太阳锥形半角 ∈ {0.0, 0.0023, 0.00465, 0.0093}(单位 rad)
- 塔高 ∈ {60, 70, 80, 90, 100}

注意:每次扰动只改变一个参数,其余用 baseline。
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import common.efficiency as eff_mod
from common.seeds import SEED, get_rng
from common.astro import all_time_points, sun_position, sun_vector, dni as compute_dni
from common.field_layout import baseline_field
from common.efficiency import (RECV_CENTER_Z_M, TOWER_HEIGHT_M, RECV_HEIGHT_M,
                                RECV_RADIUS_M, ETA_REF, SUN_HALF_ANGLE)


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "outputs")
FIGDIR = os.path.join(REPO, "figures")


def _truncate_mc(mp, n, target, sun, N, rng, w, h):
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


def eval_with_params(df, target_pos, eta_ref, recv_diam, recv_height,
                     install_h, n_mc=100, seed=SEED):
    """用给定的参数计算全场年均 E_A。"""
    rng = np.random.default_rng(seed)
    recv_radius = recv_diam / 2.0
    recv_center_z = (target_pos[2] + recv_height / 2.0)  # 简化
    time_points = all_time_points()

    monthly_power = np.zeros(12)
    monthly_count = np.zeros(12)

    mirror_pos = df[["x", "y", "h"]].to_numpy().copy()
    mirror_pos[:, 2] = install_h  # 覆盖安装高度
    mirror_w = df["width"].to_numpy().astype(float)
    mirror_h = df["height"].to_numpy().astype(float)
    total_area = float((mirror_w * mirror_h).sum())

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
        eta = cos_eta * eta_at * eta_ref * eta_trunc
        power_tp = d * float((mirror_w * mirror_h * eta).sum())
        m = month - 1
        monthly_power[m] += power_tp / 1e3
        monthly_count[m] += 1

    valid = monthly_count > 0
    annual_power = float(monthly_power[valid].mean()) if valid.any() else 0.0
    annual_E_A = annual_power * 1e6 / total_area
    return annual_power, annual_E_A


def run():
    df = baseline_field(1745, seed=SEED)
    target_pos = np.array([0.0, 0.0, RECV_CENTER_Z_M])
    rows = []

    # η_ref 灵敏度
    for eta_ref in [0.86, 0.88, 0.90, 0.92, 0.94, 0.96]:
        P, EA = eval_with_params(df, target_pos, eta_ref,
                                  RECV_RADIUS_M * 2, RECV_HEIGHT_M, INSTALL_H := 4.0)
        rows.append(("eta_ref", eta_ref, P, EA))
    # 安装高度
    for h_in in [2.0, 3.0, 4.0, 5.0, 6.0]:
        P, EA = eval_with_params(df, target_pos, ETA_REF,
                                  RECV_RADIUS_M * 2, RECV_HEIGHT_M, h_in)
        rows.append(("install_h", h_in, P, EA))
    # 集热器直径
    for diam in [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
        P, EA = eval_with_params(df, target_pos, ETA_REF, diam, RECV_HEIGHT_M, 4.0)
        rows.append(("recv_diam", diam, P, EA))
    # 太阳锥形半角(改全局 SUN_HALF_ANGLE 后调 _truncate_mc)
    # 为简化:这里仅作 η_trunc 单调性讨论,实际数值依赖 MC,本版本跳过锥形角网格
    # 塔高
    for H_tower in [60.0, 70.0, 80.0, 90.0, 100.0]:
        tgt = np.array([0.0, 0.0, H_tower - RECV_HEIGHT_M / 2.0])
        P, EA = eval_with_params(df, tgt, ETA_REF, RECV_RADIUS_M * 2, RECV_HEIGHT_M, 4.0)
        rows.append(("tower_h", H_tower, P, EA))

    df_out = pd.DataFrame(rows, columns=["param", "value", "annual_power_MW", "annual_E_A_Wpm2"])
    df_out.to_csv(os.path.join(OUTDIR, "sensitivity.csv"), index=False)

    # 画图:每个参数的 E_A 变化
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    params = ["eta_ref", "install_h", "recv_diam", "tower_h"]
    titles = ["镜面反射率 η_ref", "安装高度 (m)", "集热器直径 (m)", "吸收塔高度 (m)"]
    for ax, p, t in zip(axes, params, titles):
        sub = df_out[df_out["param"] == p]
        ax.plot(sub["value"], sub["annual_E_A_Wpm2"], marker="o", lw=1.6, color="#1f77b4")
        ax.set_xlabel(t)
        ax.set_ylabel("单位面积年功率 (W/m²)")
        ax.grid(True, alpha=0.3)
    fig.suptitle("Q1 baseline 关键参数灵敏度分析")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "sensitivity.png"), dpi=150)
    plt.close(fig)

    # 同时写一份 xlsx
    with pd.ExcelWriter(os.path.join(OUTDIR, "sensitivity.xlsx"),
                        engine="openpyxl") as w:
        for p in params:
            sub = df_out[df_out["param"] == p]
            sub.to_excel(w, sheet_name=p, index=False)

    print("\n========= Sensitivity =========")
    print(df_out.to_string(index=False))


if __name__ == "__main__":
    run()