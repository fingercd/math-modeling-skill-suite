"""Monte Carlo 截断/遮挡偏差曲线:在不同 N 下验证 MC 估计的稳定性。"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common.seeds import get_rng
from common.astro import sun_vector, sun_position, all_time_points
from common.efficiency import (truncate_efficiency_mc, sb_efficiency_grid,
                                full_efficiency, RECV_CENTER_Z_M, TOWER_HEIGHT_M)


def bias_curve(mirror_pos, mirror_w, mirror_h, sun, target_pos,
               neighbor_xy, neighbor_wh,
               Ns=(50, 100, 200, 400, 800, 1600),
               repeats: int = 8,
               seed: int = 20230705) -> dict:
    """对每个 N 重复 repeats 次,记录 η_trunc 的均值与标准差。"""
    rng_master = np.random.default_rng(seed)
    means = []
    stds = []
    for N in Ns:
        vals = []
        for _ in range(repeats):
            rng = np.random.default_rng(rng_master.integers(0, 2 ** 32 - 1))
            vals.append(truncate_efficiency_mc(mirror_pos,
                                                heliostat_normal(mirror_pos, target_pos, sun),
                                                target_pos, sun, n_samples=N, rng=rng))
        means.append(np.mean(vals))
        stds.append(np.std(vals))
    return {"N": list(Ns), "mean": means, "std": stds}


def heliostat_normal(p, t, s):
    """与 common.efficiency.heliostat_normal 一致:约定 s 为指向太阳的单位向量。"""
    d = t - p
    d = d / np.linalg.norm(d)
    n = s + d
    return n / np.linalg.norm(n)


def plot_bias(curve: dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.errorbar(curve["N"], curve["mean"], yerr=curve["std"], marker="o",
                capsize=4, lw=1.6, color="#1f77b4")
    ax.set_xscale("log")
    ax.set_xlabel("MC sample size N")
    ax.set_ylabel("η_trunc (mean ± std)")
    ax.set_title("Monte Carlo 截断效率偏差曲线(单镜单时点)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    # 选取一个代表性场景:中圈 200 m 镜面 + 6×6 + 安装 4 m + 12 时点
    mirror_pos = np.array([200.0, 0.0, 4.0])
    target_pos = np.array([0.0, 0.0, RECV_CENTER_Z_M])
    pts = all_time_points()
    month, st, doy = pts[30]  # 约 7 月 12:00
    a, g = sun_position(doy, st)
    sun = sun_vector(a, g)
    curve = bias_curve(mirror_pos, 6.0, 6.0, sun, target_pos,
                       np.zeros((0, 2)), np.zeros((0, 2)))
    print(curve)
    out = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "mc_sample_bias.png")
    out = os.path.normpath(out)
    plot_bias(curve, out)
    print(f"saved -> {out}")