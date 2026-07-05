"""一键跑全套实验:MC 偏差、Q1、Q2、Q3、灵敏度。

依赖:各子脚本可单独 import;MC 偏差已有 common/monte_carlo。
"""
from __future__ import annotations
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from common.seeds import SEED, get_rng
from common.astro import sun_position, sun_vector
from common.efficiency import (heliostat_normal, RECV_CENTER_Z_M,
                                TOWER_HEIGHT_M, RECV_HEIGHT_M,
                                RECV_RADIUS_M, SUN_HALF_ANGLE)
from common.monte_carlo import plot_bias


def run_mc_bias_check():
    print("\n=== MC bias check ===")
    import math
    from common.monte_carlo import bias_curve
    mp = np.array([200.0, 0.0, 4.0])
    target = np.array([0.0, 0.0, RECV_CENTER_Z_M])
    a, g = sun_position(174, 12.0)
    sun = sun_vector(a, g)
    curve = bias_curve(mp, 6.0, 6.0, sun, target,
                       np.zeros((0, 2)), np.zeros((0, 2)),
                       Ns=(50, 100, 200, 400, 800, 1600), repeats=6, seed=SEED)
    out = os.path.join(os.path.dirname(__file__), "..", "figures", "mc_sample_bias.png")
    out = os.path.normpath(out)
    plot_bias(curve, out)
    print(f"saved -> {out}")
    return curve


def run_q1():
    print("\n=== Q1 baseline ===")
    import q1_baseline as q1
    t0 = time.time()
    res = q1.run(n_mc=200, n_helio=1745, verbose=True)
    print(f"[run_all] Q1 elapsed: {time.time()-t0:.1f}s")
    return res


def run_q2():
    print("\n=== Q2 uniform mirror ===")
    import q2_uniform_mirror as q2
    q2.de_optimize(pop=18, gen=30, n_mc=80)
    q2.main.__wrapped__ if hasattr(q2.main, "__wrapped__") else q2.main()


def run_q3():
    print("\n=== Q3 mixed mirror ===")
    import q3_mixed_mirror as q3
    q3.de_optimize(pop=15, gen=25, n_mc=80)
    q3.main.__wrapped__ if hasattr(q3.main, "__wrapped__") else q3.main()


def run_sensitivity():
    print("\n=== Sensitivity ===")
    import sensitivity as sens
    sens.run()


if __name__ == "__main__":
    t0 = time.time()
    run_mc_bias_check()
    run_q1()
    run_q2()
    run_q3()
    run_sensitivity()
    print(f"\n[run_all] total elapsed: {time.time()-t0:.1f}s")