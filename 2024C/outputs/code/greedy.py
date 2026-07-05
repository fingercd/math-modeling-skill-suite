"""algo/greedy.py — 桶排序贪心 v3, 动态跟踪销售量, 按实时边际利润贪心.

核心思路:
- 每个动作点 (plot, crop, season) 在被填入时, 先看当年该作物的销售量是否还剩.
  * 剩余 > 0: 单位利润 = yield * price - cost
  * 剩余 <= 0: 单位利润 = yield * price * discount_factor - cost  (discount_factor: 0=waste, 0.5=Q1子问2, 弹性=Q3)
- 按"动态边际利润"从高到低, 一次性填满所有 7 年.
"""
from __future__ import annotations
import json
import random
from collections import defaultdict
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from objective import evaluate_solution, base_sales_capacity, crop_unit_profit
from data_structure import load_processed

DATA = Path(__file__).resolve().parent.parent / "data"


def _load_all():
    processed = load_processed()
    actions = json.loads((DATA / "action_space.json").read_text(encoding="utf-8"))["actions"]
    return processed, actions


def _discount_factor(mode, rho=None, alpha=0.5):
    if mode == "waste":
        return 0.0
    if mode == "discount":
        return 0.5
    if mode == "elastic" and rho is not None:
        return max(0.0, alpha + 0.3 * rho)
    return 0.5


def greedy_solve(mode="discount", n_years=7, legume_cover=False,
                 substitute_rho=None, discount_alpha=0.5, seed=42,
                 plot_alloc_ratio=1.0, sales_buffer=1.0,
                 fixed_caps=None, price_mult=None, cost_mult=None,
                 yield_mult=None, sales_mult=None):
    """单次贪心.

    fixed_caps: 覆盖默认 sales cap (用于 Q2/Q3 场景).
    """
    random.seed(seed)
    np.random.seed(seed)
    processed, actions = _load_all()
    plots = processed["plots"]
    crops = processed["crops"]
    plot_by_id = {p["id"]: p for p in plots}
    crop_by_id = {c["id"]: c for c in crops}
    crop_code_by_id = {c["id"]: c["code"] for c in crops}
    df = _discount_factor(mode, substitute_rho, discount_alpha)

    # 静态 (plot, crop, season) 元组列表
    bases = []
    for a in actions:
        p = plot_by_id[a["plot"]]
        ccode = crop_code_by_id[a["crop"]]
        st = crop_unit_profit(processed, ccode, p["type"], a["season"], mode=mode,
                              rho=substitute_rho, alpha=discount_alpha)
        if not st:
            continue
        bases.append({
            "plot": a["plot"], "crop": a["crop"], "season": a["season"],
            "yield": st["yield"], "cost": st["cost"], "price": st["price"],
            "up_normal": st["unit_profit_normal"],
            "up_over": st["unit_profit_over"],
        })
    # 排序: 按 up_normal 降序
    bases.sort(key=lambda x: -x["up_normal"])

    # 销售量上限
    if fixed_caps:
        sales_cap = fixed_caps
    else:
        sales_cap = {c["id"]: base_sales_capacity(processed, c["code"], baseline_buffer=sales_buffer) for c in crops}
    pm = price_mult or 1.0
    cm = cost_mult or 1.0
    ym = yield_mult or 1.0
    sm = sales_mult or 1.0
    sales_cap = {cid: cap * sm for cid, cap in sales_cap.items()}

    x = {}
    last_year_planted = defaultdict(set)
    years = list(range(2024, 2024 + n_years))

    for y in years:
        plot_used_year = defaultdict(float)  # (plot, year) -> 已分配亩数
        plot_used_season = defaultdict(float)  # (plot, season, year) -> 已分配亩数
        used_sales = defaultdict(float)  # cid -> 斤
        crops_in_year = defaultdict(set)  # pid -> set(cid) 本年所有季已种作物
        for b in bases:
            p = plot_by_id[b["plot"]]
            if p["type"] in ("平旱地", "梯田", "山坡地") and b["season"] != 1:
                continue
            if p["type"] == "水浇地" and crop_code_by_id[b["crop"]] == 16 and b["season"] != 1:
                continue
            # 间作约束下禁用水稻 (否则水浇地无法补豆类)
            if legume_cover and p["type"] == "水浇地" and crop_code_by_id[b["crop"]] == 16:
                continue
            if (b["crop"], b["season"]) in last_year_planted[b["plot"]]:
                continue
            # C3 轮作: 同地块同年不能同时种 s=1 与 s=2 的同种作物
            if b["crop"] in crops_in_year[b["plot"]]:
                continue
            # 面积约束: 既看本年总量, 也看本季已分配 (单季地块只看年总量)
            cap_year = p["area"] * plot_alloc_ratio - plot_used_year[b["plot"]]
            cap_season = p["area"] * plot_alloc_ratio - plot_used_season[(b["plot"], b["season"])]
            cap_area = min(cap_year, cap_season)
            if cap_area <= 0:
                continue
            # 动态单位利润
            cap_total = sales_cap[b["crop"]]
            used = used_sales[b["crop"]]
            yld = b["yield"] * ym
            cost = b["cost"] * cm
            price = b["price"] * pm
            remaining = cap_total - used
            if remaining <= 0:
                # 全超产
                up = yld * price * df - cost
                if up <= 0:
                    continue  # 不值得种
                area = cap_area  # 全填
            else:
                max_area_normal = remaining / yld if yld > 0 else 0
                if max_area_normal >= cap_area:
                    up = yld * price - cost
                    if up <= 0:
                        continue
                    area = cap_area
                else:
                    # 部分正常 + 部分超产, 混合单位利润
                    rev_normal = max_area_normal * (yld * price - cost)
                    rev_over = (cap_area - max_area_normal) * (yld * price * df - cost)
                    avg_up = (rev_normal + rev_over) / cap_area
                    if avg_up <= 0:
                        continue
                    area = cap_area
            area = round(area, 2)
            if area <= 0:
                continue
            x[(b["plot"], b["crop"], b["season"], y)] = x.get((b["plot"], b["crop"], b["season"], y), 0.0) + area
            plot_used_year[b["plot"]] += area
            plot_used_season[(b["plot"], b["season"])] += area
            used_sales[b["crop"]] += yld * area
            crops_in_year[b["plot"]].add(b["crop"])
        last_year_planted.clear()
        for (pid, cid, s, yi), area in x.items():
            if area > 0 and yi == y:
                last_year_planted[pid].add((cid, s))

    # 间作约束 (Q3) — 简化为"每年至少 10% 豆类", 自动满足 3 年窗口约束
    if legume_cover:
        legume_ids = {c["id"] for c in crops if c["is_legume"]}
        for pid in range(len(plots)):
            p = plot_by_id[pid]
            min_area = p["area"] * 0.10
            for y in years:
                # 算本年豆类覆盖
                area_legume = sum(
                    x.get((pid, cid, s, y), 0.0)
                    for cid in legume_ids
                    for s in (1, 2)
                )
                if area_legume >= min_area:
                    continue
                needed = min_area - area_legume
                # 选最优豆类 (本年本块地允许)
                best_id = None
                best_margin = -1e18
                for cid in legume_ids:
                    for s in (1, 2):
                        st = crop_unit_profit(processed, crop_code_by_id[cid], p["type"], s, mode=mode)
                        if st and st["unit_profit_normal"] > best_margin:
                            best_margin = st["unit_profit_normal"]
                            best_id = (cid, s)
                if not best_id:
                    continue
                cid, s = best_id
                # 检查水浇地规则: s=1 已有水稻 (id=15) 时, 不能在 s=1 加豆类
                if p["type"] == "水浇地":
                    s1_entries = [(ci, si) for (pi, ci, si, yi), v in x.items()
                                  if pi == pid and si == 1 and yi == y and v > 0]
                    if any(crop_code_by_id[ci] == 16 for ci, _ in s1_entries):
                        continue  # 已是水稻单季, 不在 s=1 加豆类
                    # 蔬菜模式: 把已有 s=1 蔬菜条目里需要的部分直接替换为豆类 (而非新增)
                    if s == 1 and s1_entries:
                        existing_ci = s1_entries[0][0]
                        existing_v = x.get((pid, existing_ci, 1, y), 0.0)
                        if existing_v >= needed:
                            x[(pid, existing_ci, 1, y)] = round(existing_v - needed, 2)
                            x[(pid, cid, 1, y)] = x.get((pid, cid, 1, y), 0.0) + needed
                            continue
                        # existing_v < needed: 整条转豆类 + 在 s=2 (radish 区间) 加足
                        s2_entries = [(ci, si) for (pi, ci, si, yi), v in x.items()
                                      if pi == pid and si == 2 and yi == y and v > 0]
                        if s2_entries:
                            # 把 s=1 整条转豆类, 把剩余 needed 在 s=2 上加
                            x[(pid, existing_ci, 1, y)] = 0.0
                            x[(pid, cid, 1, y)] = existing_v
                            rem = needed - existing_v
                            if rem > 0:
                                ex2_ci = s2_entries[0][0]
                                ex2_v = x.get((pid, ex2_ci, 2, y), 0.0)
                                if ex2_v >= rem:
                                    x[(pid, ex2_ci, 2, y)] = round(ex2_v - rem, 2)
                                    x[(pid, cid, 2, y)] = x.get((pid, cid, 2, y), 0.0) + rem
                                else:
                                    # 水浇地 s=2 只能种 35/36/37, 不允许豆类; 只能尽量覆盖
                                    x[(pid, ex2_ci, 2, y)] = 0.0
                                    x[(pid, cid, 2, y)] = x.get((pid, cid, 2, y), 0.0) + ex2_v
                            continue
                        # s=1 + s=2 都空, 直接在 s=1 加 needed (假设第一季腾空)
                        x[(pid, cid, 1, y)] = needed
                        continue
                # 普通情况: 缩 20% 非豆类腾位置 + 加豆类
                shrink_factor = 0.20
                for si in (1, 2):
                    for ci in range(len(crops)):
                        if ci in legume_ids:
                            continue
                        v = x.get((pid, ci, si, y), 0.0)
                        if v > 0:
                            reduce = v * shrink_factor
                            x[(pid, ci, si, y)] = round(v - reduce, 2)
                cur_year_used = sum(
                    x.get((pid, ci, si, y), 0.0)
                    for ci in range(len(crops))
                    for si in (1, 2)
                )
                avail = p["area"] * plot_alloc_ratio - cur_year_used
                actual = min(needed, max(0.0, avail))
                if actual > 0:
                    x[(pid, cid, s, y)] = x.get((pid, cid, s, y), 0.0) + actual

    profit = evaluate_solution(
        processed, {"actions": actions}, x,
        mode=mode, n_years=n_years,
        price_mult=pm, cost_mult=cm, yield_mult=ym, sales_mult=sm,
        substitute_rho=substitute_rho, discount_alpha=discount_alpha,
    )
    return x, profit


if __name__ == "__main__":
    x_d, p_d = greedy_solve(mode="discount", n_years=7)
    x_w, p_w = greedy_solve(mode="waste", n_years=7)
    print(f"Q1 子问 2 (discount) 7 年累计 = {p_d/1e4:.1f} 万元, 动作数={sum(1 for v in x_d.values() if v>0)}")
    print(f"Q1 子问 1 (waste)    7 年累计 = {p_w/1e4:.1f} 万元, 动作数={sum(1 for v in x_w.values() if v>0)}")
    print(f"差 (discount - waste) = {(p_d - p_w)/1e4:.1f} 万元 (折扣挽回的超产损失)")