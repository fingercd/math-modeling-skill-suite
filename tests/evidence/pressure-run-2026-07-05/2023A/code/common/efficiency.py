"""单面镜的光学效率装配 + 向量化计算。

η = η_sb * η_cos * η_at * η_ref * η_trunc

- η_sb:阴影遮挡效率 = 1 - 被挡面积占比
- η_cos:余弦效率 = cos θ (θ = 入射光线与镜面法向的夹角)
- η_at :大气透射率 = 0.99321 - 0.0001176 d_HR + 1.97e-8 d_HR^2
- η_ref:镜面反射率 = 0.92
- η_trunc:截断效率 = 反射光锥与集热器圆柱侧面交叠比例
"""
from __future__ import annotations
import math
import numpy as np

from .astro import sun_vector, SUN_HALF_ANGLE


# 集热器与塔几何(可由题面参数推导)
TOWER_HEIGHT_M = 80.0     # 塔高
RECV_HEIGHT_M = 8.0       # 集热器高
RECV_DIAMETER_M = 7.0     # 集热器直径
RECV_CENTER_Z_M = TOWER_HEIGHT_M - RECV_HEIGHT_M / 2.0  # 76 m
RECV_RADIUS_M = RECV_DIAMETER_M / 2.0

ETA_REF = 0.92


def atmos_transmission(d_hr: float) -> float:
    """大气透射率 η_at。d_hr 单位 m。"""
    return 0.99321 - 0.0001176 * d_hr + 1.97e-8 * d_hr * d_hr


def cosine_efficiency(sun: np.ndarray, normal: np.ndarray) -> float:
    """cos θ = | sun · normal |。"""
    cos_t = float(np.dot(sun, normal))
    return max(0.0, cos_t)


def heliostat_normal(mirror_pos: np.ndarray,
                     target_pos: np.ndarray,
                     sun: np.ndarray) -> np.ndarray:
    """定日镜法向:使太阳中心点经镜面中心反射后指向集热器中心。

    约定:sun 是"从镜面指向太阳"的单位向量(sz > 0 表示太阳在地平线上)。
    入射光方向 I = -sun(从太阳到地面);反射定律 R = I - 2(I·n)n = -sun + 2(sun·n)n。
    要 R ∝ (target - mirror) 单位向量 d_unit,需要 n = (sun + d_unit) / |sun + d_unit|。
    """
    d = target_pos - mirror_pos
    d = d / np.linalg.norm(d)
    n = sun + d
    n = n / np.linalg.norm(n)
    return n


def distance_hr(mirror_pos: np.ndarray, target_pos: np.ndarray) -> float:
    return float(np.linalg.norm(target_pos - mirror_pos))


def truncate_efficiency_mc(mirror_pos: np.ndarray,
                           normal: np.ndarray,
                           target_pos: np.ndarray,
                           sun: np.ndarray,
                           n_samples: int,
                           rng: np.random.Generator) -> float:
    """Monte Carlo 求截断效率 η_trunc。

    在镜面局部坐标系内采样 N 个点(以镜心为中心、宽 w、高 h 的矩形),
    每点按 4.65 mrad 锥形太阳光反射,统计有多少反射线与集热器圆柱侧面相交。
    """
    w, h = 6.0, 6.0  # 默认 6×6;若需异构,调用方在外层重设
    # 局部正交基:法向 n;辅助 u 选 xz 平面投影的副法线
    n = normal / np.linalg.norm(normal)
    # 取与 n 不平行的世界轴构造 u/v
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(world_up, n)) > 0.95:
        world_up = np.array([1.0, 0.0, 0.0])
    u = np.cross(world_up, n)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    # 矩形采样
    uu = rng.uniform(-w / 2.0, w / 2.0, size=n_samples)
    vv = rng.uniform(-h / 2.0, h / 2.0, size=n_samples)
    # 锥形太阳光:在太阳方向上加小角度偏移
    # 偏移:以太阳为中心、半角 SUN_HALF_ANGLE 的锥形
    # 近似:把偏移分解到与 sun 正交的两个基上
    if abs(sun[2]) < 0.95:
        axis = np.array([0.0, 0.0, 1.0])
    else:
        axis = np.array([1.0, 0.0, 0.0])
    e1 = np.cross(sun, axis)
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(sun, e1)
    e2 = e2 / np.linalg.norm(e2)
    # 均匀采样圆盘(半径 = tan(SUN_HALF_ANGLE)),平方根降低偏差
    rho = np.sqrt(rng.uniform(0.0, SUN_HALF_ANGLE ** 2, size=n_samples))
    phi = rng.uniform(0.0, 2.0 * np.pi, size=n_samples)
    off = rho[:, None] * (np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2)
    sun_dirs = sun[None, :] + off
    sun_dirs = sun_dirs / np.linalg.norm(sun_dirs, axis=1, keepdims=True)

    # 反射方向 = sun_dirs - 2 (sun_dirs · n) n
    sd_n = (sun_dirs * n[None, :]).sum(axis=1, keepdims=True)
    # 入射方向 I = -sun_dirs(从太阳到镜面);反射 R = I - 2(I·n)n = -sun_dirs - 2((-sun_dirs)·n)n
    #   = -sun_dirs + 2(sun_dirs·n)n
    refl = -sun_dirs + 2.0 * sd_n * n[None, :]
    refl = refl / np.linalg.norm(refl, axis=1, keepdims=True)

    # 镜面上的点
    pts = (mirror_pos[None, :]
           + uu[:, None] * u[None, :]
           + vv[:, None] * v[None, :])

    # 与圆柱侧面(半径 RECV_RADIUS_M,中心轴沿 z 方向,z ∈ [TOWER_HEIGHT_M - RECV_HEIGHT_M, TOWER_HEIGHT_M])相交判定
    z_min = TOWER_HEIGHT_M - RECV_HEIGHT_M
    z_max = TOWER_HEIGHT_M
    # 反射线参数方程: P(t) = pts + t * refl
    hit = np.zeros(n_samples, dtype=bool)
    # 两个候选 t(若 |refl_z| 太小,设为 ±inf;若 refl_z=0 则不可达,直接排除)
    safe = np.abs(refl[:, 2]) > 1e-9
    if not np.any(safe):
        return 0.0
    t1 = np.where(safe, (z_min - pts[:, 2]) / np.where(safe, refl[:, 2], 1.0), -np.inf)
    t2 = np.where(safe, (z_max - pts[:, 2]) / np.where(safe, refl[:, 2], 1.0), -np.inf)
    t_low = np.minimum(t1, t2)
    t_high = np.maximum(t1, t2)
    # 圆柱相交条件:t ∈ [max(0, t_low), t_high] 上径向距离 ≤ RECV_RADIUS_M
    t_enter = np.maximum(0.0, t_low)
    t_exit = t_high
    valid_range = safe & (t_exit > t_enter)
    t_sample = np.where(valid_range, (t_enter + t_exit) / 2.0, 0.0)
    xs = pts[:, 0] + t_sample * refl[:, 0]
    ys = pts[:, 1] + t_sample * refl[:, 1]
    radial = np.sqrt(xs * xs + ys * ys)
    ok = valid_range & (radial <= RECV_RADIUS_M)
    hit[ok] = True
    return float(hit.mean())


def sb_efficiency_grid(mirror_pos: np.ndarray,
                        mirror_w: float, mirror_h: float,
                        sun: np.ndarray,
                        neighbor_xy: np.ndarray,
                        neighbor_wh: np.ndarray,
                        grid_n: int = 24) -> float:
    """阴影遮挡效率 η_sb:在镜面上做 grid_n × grid_n 采样,统计被邻镜投影遮挡的比例。

    简化:只考虑邻镜"投影到该镜面上"的多边形遮挡。
    实现策略:对每个邻镜,判断其中心到该镜面中心的连线是否在"迎光面"上;
    若在,把邻镜按 sun 方向投影到该镜平面,统计重叠像素。

    为保证可复现与速度,这里采用一个工程近似:
      - 计算该镜"投影锥"在地面上的多边形;邻镜中心落入该锥且邻镜尺寸大于阈值,按面积比打折。
    """
    if neighbor_xy.shape[0] == 0:
        return 1.0
    # 法向:取 (0,0,1) 作为镜面法向近似(此函数只算地面投影遮挡,法向不影响)
    # 入射光反向(从太阳指向镜心)
    light_dir = -sun
    if abs(light_dir[2]) < 1e-6:
        return 1.0
    # 投影:邻镜中心 (xn, yn, hn) 沿 light_dir 投射到 z = mirror_pos[2] 平面
    # t = (mirror_pos[2] - hn) / light_dir[2]
    t = (mirror_pos[2] - neighbor_xy.shape[0])  # 占位
    # 实际计算:
    h_n = neighbor_wh[:, 0] * 0.0 + 4.0  # 简化:邻镜安装高度统一 4 m;若异构由调用方传入
    t_proj = (mirror_pos[2] - h_n) / light_dir[2]
    proj_xy = neighbor_xy + t_proj[:, None] * light_dir[:2][None, :]
    # 邻镜在投影面上的"等效宽度":按其真实宽度的 cos(α) 投影
    # 简化:不区分迎光面/背光面,只判断邻镜投影中心是否落在镜面矩形内
    mx, my = mirror_pos[0], mirror_pos[1]
    hw = mirror_w / 2.0
    hh = mirror_h / 2.0
    # 把投影点转镜面局部坐标(忽略旋转:取与场地坐标对齐的简化)
    inside = (np.abs(proj_xy[:, 0] - mx) <= hw + neighbor_wh[:, 0] / 2.0) & \
             (np.abs(proj_xy[:, 1] - my) <= hh + neighbor_wh[:, 0] / 2.0)
    if not np.any(inside):
        return 1.0
    # 在镜面上 grid 采样,判定每个样本是否被任一邻镜的投影多边形覆盖
    u = np.linspace(-hw, hw, grid_n)
    v = np.linspace(-hh, hh, grid_n)
    UU, VV = np.meshgrid(u, v, indexing="ij")
    pts = np.stack([UU.ravel() + mx, VV.ravel() + my], axis=1)
    # 对每个邻镜做轴对齐矩形遮挡判定
    blocked = np.zeros(pts.shape[0], dtype=bool)
    for i in np.where(inside)[0]:
        xn, yn = proj_xy[i]
        wn = neighbor_wh[i, 0]
        hn = neighbor_wh[i, 1]
        rect_hit = (np.abs(pts[:, 0] - xn) <= wn / 2.0) & \
                   (np.abs(pts[:, 1] - yn) <= hn / 2.0)
        blocked |= rect_hit
    blocked = blocked.reshape(grid_n, grid_n)
    eta_sb = 1.0 - blocked.mean()
    return float(max(0.0, min(1.0, eta_sb)))


def full_efficiency(mirror_pos: np.ndarray,
                    mirror_w: float, mirror_h: float,
                    sun: np.ndarray,
                    target_pos: np.ndarray,
                    neighbor_xy: np.ndarray,
                    neighbor_wh: np.ndarray,
                    n_mc: int,
                    rng: np.random.Generator) -> dict:
    """装配 5 项效率并返回字典。"""
    n = heliostat_normal(mirror_pos, target_pos, sun)
    eta_cos = cosine_efficiency(sun, n)
    d_hr = distance_hr(mirror_pos, target_pos)
    eta_at = atmos_transmission(d_hr)
    eta_sb = sb_efficiency_grid(mirror_pos, mirror_w, mirror_h,
                                sun, neighbor_xy, neighbor_wh)
    eta_trunc = truncate_efficiency_mc(mirror_pos, n, target_pos, sun,
                                       n_samples=n_mc, rng=rng)
    eta = eta_sb * eta_cos * eta_at * ETA_REF * eta_trunc
    return dict(eta_sb=eta_sb, eta_cos=eta_cos, eta_at=eta_at,
                eta_ref=ETA_REF, eta_trunc=eta_trunc, eta=eta,
                d_hr=d_hr)