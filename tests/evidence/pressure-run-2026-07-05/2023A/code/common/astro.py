"""太阳几何与 DNI 计算。

依据 problem.md 附录公式(已与公开论文核对):
- 太阳高度角 α_s、方位角 γ_s、太阳时角 ω、赤纬角 δ
- 法向直接辐射辐照度 DNI(H=3 km)

所有角度单位:弧度。
方位角约定:罗盘方位(从正北起算顺时针),取值范围 (-π, π]。
  - γ_s = 0   表示正北
  - γ_s = +π/2 表示正东
  - γ_s = ±π 表示正南
  - γ_s = -π/2 表示正西
这样 12:00(太阳在正南)γ_s = ±π,下午 γ_s 在 (-π, -π/2](西),上午 γ_s ∈ [π/2, π)(东)。
"""
from __future__ import annotations
import math
import numpy as np


# 题目场址参数
LAT_DEG = 39.4          # 北纬,度
LON_DEG = 98.5          # 东经,度
ALT_KM = 3.0            # 海拔 km
SUN_HALF_ANGLE = 0.00465  # 太阳锥形半角,rad(4.65 mrad)


def deg2rad(x: float) -> float:
    return x * math.pi / 180.0


def declination(doy: int) -> float:
    """赤纬角 δ。doy 从春分起算的天数 D。

    公式:sin δ = sin(2πD/365) * sin(2π/360 * 23.45)
    """
    return math.asin(math.sin(2.0 * math.pi * doy / 365.0)
                     * math.sin(2.0 * math.pi * 23.45 / 360.0))


def hour_angle(st_hour: float) -> float:
    """太阳时角 ω = π/12 * (ST - 12)。"""
    return math.pi / 12.0 * (st_hour - 12.0)


def sun_position(doy: int, st_hour: float,
                 lat_deg: float = LAT_DEG) -> tuple[float, float]:
    """返回 (α_s, γ_s) 弧度。α_s > 0 表示太阳在地平线以上。

    γ_s:罗盘方位,从正北起算顺时针,范围 (-π, π]。
    当 α_s <= 0 时返回 (-1, 0),调用方应跳过该时点。
    """
    phi = deg2rad(lat_deg)
    delta = declination(doy)
    omega = hour_angle(st_hour)
    sin_alpha = math.cos(phi) * math.cos(delta) * math.cos(omega) + math.sin(phi) * math.sin(delta)
    sin_alpha = max(-1.0, min(1.0, sin_alpha))
    alpha = math.asin(sin_alpha)
    if alpha <= 0.0:
        return -1.0, 0.0
    cos_gamma = (math.sin(delta) - math.sin(alpha) * math.sin(phi)) / (math.cos(alpha) * math.cos(phi))
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    gamma = math.acos(cos_gamma)
    # 公式给出的 γ_s 默认 0→π/2(对应上午东向),需要根据时角判断东西:
    # 上午(omega < 0)太阳在东,罗盘方位 ∈ [π/2, π):γ_s = π - γ_s
    # 下午(omega > 0)太阳在西,罗盘方位 ∈ (-π, -π/2]:γ_s = -π + γ_s
    # 中午(omega=0)γ_s=±π(正南)
    if omega < 0.0:
        gamma = math.pi - gamma
    elif omega > 0.0:
        gamma = -math.pi + gamma
    else:
        gamma = math.pi
    return alpha, gamma


def dni(alpha_s: float, alt_km: float = ALT_KM) -> float:
    """法向直接辐射辐照度 DNI(单位 kW/m²)。α_s 必须 > 0。

    G0=1.366,a/b/c 由 H(km) 给出:
      a = 0.4237 - 0.00821(6-H)^2
      b = 0.5055 + 0.00595(6.5-H)^2
      c = 0.2711 + 0.01858(2.5-H)^2
      DNI = G0 [a + b * exp(-c/sin α_s)]
    """
    if alpha_s <= 0.0:
        return 0.0
    H = alt_km
    a = 0.4237 - 0.00821 * (6.0 - H) ** 2
    b = 0.5055 + 0.00595 * (6.5 - H) ** 2
    c = 0.2711 + 0.01858 * (2.5 - H) ** 2
    s = math.sin(alpha_s)
    return 1.366 * (a + b * math.exp(-c / s))


def monthly_doys() -> list[tuple[int, int]]:
    """返回 12 个月每月 21 日对应的 doy(从春分起算)。

    春分约在 3 月 21 日(当年 doy≈80);此处按非闰年近似,逐月+30。
    """
    spring_doy = 80  # 春分 3/21
    out = []
    for m in range(12):
        day = 21
        # 每月 21 日对应的 doy(从 1/1 起算)
        month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        doy_jan1 = month_starts[m] + (day - 1)
        out.append((m + 1, doy_jan1 - spring_doy))
    return out


def all_time_points() -> list[tuple[int, float]]:
    """生成 60 个时点:12 月 × 5 时点(9:00/10:30/12:00/13:30/15:00)。"""
    times = [9.0, 10.5, 12.0, 13.5, 15.0]
    pts = []
    for month, doy in monthly_doys():
        for t in times:
            pts.append((month, t, doy))
    return pts


def sun_vector(alpha_s: float, gamma_s: float) -> np.ndarray:
    """把 (α_s, γ_s) 转 3D 单位向量,指向太阳。约定 x=东, y=北, z=上。

    返回向量 (sx, sy, sz),sz=sin α_s。
    γ_s 是罗盘方位(从正北起算顺时针)。
    """
    sa = math.sin(alpha_s)
    ca = math.cos(alpha_s)
    sg = math.sin(gamma_s)
    cg = math.cos(gamma_s)
    sx = sg * ca   # 东分量
    sy = cg * ca   # 北分量
    sz = sa
    return np.array([sx, sy, sz], dtype=float)


if __name__ == "__main__":
    # 自检:几个时点的 α_s / γ_s / DNI
    pts = all_time_points()
    print(f"#timepoints={len(pts)}")
    for month, st, doy in pts[:6]:
        a, g = sun_position(doy, st)
        d = dni(a)
        print(f"  m={month:02d} st={st:5.2f} doy={doy:+4d}  alpha={math.degrees(a):6.2f}deg  gamma={math.degrees(g):+7.2f}deg  DNI={d:6.3f}kW/m^2")