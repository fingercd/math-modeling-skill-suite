"""镜场坐标合成:在 R=350 m 圆形区域(100 m 内不放镜)生成 N 面镜面坐标。

布局策略:radial-stagger(参考张平等 2018 与 Sanchez 2014 思路)。
- 按径向圈布置镜面,每圈镜面数随半径近似线性增加;
- 相邻圈在角度上交错半个角间距;
- 邻镜中心距由"径向圈间距"与"角间距"共同保证 ≥ 镜宽 + 5 m。

输出列:x, y, h(安装高度), width, height(镜面宽/高)。所有单位 m。
"""
from __future__ import annotations
import math
import numpy as np
import pandas as pd

from .astro import LAT_DEG


R_OUTER = 350.0
R_INNER = 100.0
DEFAULT_W = 6.0
DEFAULT_H = 6.0
INSTALL_H = 4.0
MIN_GAP = 5.0  # 邻镜中心距 ≥ 镜宽 + 5 m


def radial_stagger(n_target: int,
                   w: float = DEFAULT_W,
                   h: float = DEFAULT_H,
                   install: float = INSTALL_H,
                   seed: int = 20230705) -> pd.DataFrame:
    """生成 n_target 面 radial-stagger 镜场,中心塔位于 (0, 0)。

    通过逐圈累加镜数逼近 n_target,允许 ±2% 浮动。
    """
    rng = np.random.default_rng(seed)
    spacing = w + MIN_GAP  # 中心距下限
    rows = []
    r = R_INNER + 0.5 * spacing
    ring_idx = 0
    while r <= R_OUTER - 0.5 * spacing and len(rows) < int(n_target * 1.02):
        # 每圈镜数:角间距 ≈ spacing → n_ring = int(2πr / spacing)
        n_ring = max(1, int(2.0 * math.pi * r / spacing))
        # 起始角扰动,使圈间交错
        offset = (math.pi / n_ring) if ring_idx % 2 == 1 else 0.0
        for k in range(n_ring):
            if len(rows) >= int(n_target * 1.02):
                break
            theta = 2.0 * math.pi * k / n_ring + offset + rng.normal(0.0, 0.02)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            rows.append((x, y, install, w, h))
        r += spacing
        ring_idx += 1
    # 若数量不足,直接抛错(用户应增大场地或减小镜面);通常 n_target=1745 远小于容量
    if len(rows) < n_target:
        raise RuntimeError(
            f"radial_stagger: 容量 {len(rows)} < 目标 {n_target};请检查 R_OUTER/spacing"
        )
    # 截断到 n_target
    rows = rows[:n_target]
    df = pd.DataFrame(rows, columns=["x", "y", "h", "width", "height"])
    return df


def baseline_field(n: int = 1745, seed: int = 20230705) -> pd.DataFrame:
    return radial_stagger(n_target=n, w=DEFAULT_W, h=DEFAULT_H,
                          install=INSTALL_H, seed=seed)


if __name__ == "__main__":
    df = baseline_field(1745)
    print(df.describe())
    print(f"#heliostats={len(df)}")
    print(f"x range=({df.x.min():.1f},{df.x.max():.1f})  y range=({df.y.min():.1f},{df.y.max():.1f})")