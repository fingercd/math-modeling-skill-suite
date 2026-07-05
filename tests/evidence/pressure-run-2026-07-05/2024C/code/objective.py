"""objective.py — 评估函数.

约定: 输入为 (plot, crop, season) 三元组的种植面积 x_ijts (亩), 输出净利润 (元).
支持两种超产处理: 'waste' 滞销 / 'discount' 50% 折价.

外部依赖: code/data/processed.json, code/data/action_space.json.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


def _load():
    processed = json.loads((DATA / "processed.json").read_text(encoding="utf-8"))
    action_space = json.loads((DATA / "action_space.json").read_text(encoding="utf-8"))
    return processed, action_space


def _stats_key(processed, crop_code, plot_type, season):
    """把 (作物, 地块类型, 季) 映射到 stats 字典 key."""
    if season == 1:
        season_label = "第一季"
    elif season == 2:
        season_label = "第二季"
    else:
        season_label = "单季"
    if plot_type in ("普通大棚",):
        season_label = "第一季" if season == 1 else "第二季"
    if plot_type in ("智慧大棚",):
        season_label = "第一季" if season == 1 else "第二季"
    if plot_type in ("平旱地", "梯田", "山坡地"):
        season_label = "单季"
    if plot_type == "水浇地" and crop_code == 16:
        season_label = "单季"
    return f"{crop_code}|{plot_type}|{season_label}"


def base_sales_capacity(processed, crop_code, baseline_buffer=1.0):
    """用 2023 实际产量 × buffer 作 baseline 预期销售量 (斤/季)."""
    total = 0.0
    for rec in processed["planting_2023"]:
        if rec["crop_code"] == crop_code and rec["area"]:
            # 用对应地块类型的亩产量
            plot_name = rec["plot"]
            # 找到地块类型
            ptype = None
            for p in processed["plots"]:
                if p["name"] == plot_name:
                    ptype = p["type"]
                    break
            if ptype is None:
                continue
            season_label = rec["season"] or "单季"
            key = f"{crop_code}|{ptype}|{season_label}"
            st = processed["stats"].get(key)
            if st and st["yield"]:
                total += st["yield"] * rec["area"]
    return total * baseline_buffer


def crop_unit_profit(processed, crop_code, plot_type, season, mode="discount",
                     rho=None, alpha=0.5):
    """返回 (yield, cost, price, unit_profit).

    unit_profit = yield * price - cost (正常销售); 超产部分按 mode 处理.
    mode: 'waste' | 'discount' | 'elastic'
    """
    season_label_map = {1: "第一季", 2: "第二季"}
    if plot_type in ("平旱地", "梯田", "山坡地"):
        season_label = "单季"
    elif plot_type == "水浇地" and crop_code == 16:
        season_label = "单季"
    else:
        season_label = season_label_map[season]
    key = f"{crop_code}|{plot_type}|{season_label}"
    st = processed["stats"].get(key)
    if not st:
        return None
    yld = st["yield"] or 0
    cost = st["cost"] or 0
    price = st["price"] or 0
    unit_profit_normal = yld * price - cost
    if mode == "waste":
        unit_profit_over = 0.0  # 超产部分不算收入也不扣成本 (成本已扣)
    elif mode == "discount":
        unit_profit_over = yld * price * 0.5 - cost
    elif mode == "elastic":
        df = max(0.0, alpha + 0.3 * (rho or 0.0))
        unit_profit_over = yld * price * df - cost
    else:
        raise ValueError(mode)
    return {
        "yield": yld,
        "cost": cost,
        "price": price,
        "unit_profit_normal": unit_profit_normal,
        "unit_profit_over": unit_profit_over,
    }


def evaluate_solution(processed, action_space, x_dict, mode="discount", n_years=7,
                      price_mult=None, cost_mult=None, yield_mult=None, sales_mult=None,
                      substitute_rho=None, discount_alpha=0.5):
    """评估一组解的总利润 (元).

    x_dict: {(plot, crop, season, year): 亩数}
    """
    plots = processed["plots"]
    crops = processed["crops"]
    stats = processed["stats"]
    plot_by_id = {p["id"]: p for p in plots}
    crop_by_id = {c["id"]: c for c in crops}
    crop_code_by_id = {c["id"]: c["code"] for c in crops}

    # 聚合每年每季每作物的总产量
    production = defaultdict(float)  # (year, season, crop_id) -> 斤
    cost_total = 0.0
    # 第一遍: 计算成本 + 总产量
    for (pid, cid, s, y), area in x_dict.items():
        if area <= 0:
            continue
        p = plot_by_id[pid]
        c = crop_by_id[cid]
        ccode = crop_code_by_id[cid]
        st = crop_unit_profit(processed, ccode, p["type"], s, mode=mode)
        if not st:
            continue
        yld = st["yield"] * (yield_mult or 1.0)
        cost = st["cost"] * (cost_mult or 1.0)
        cost_total += cost * area
        production[(y, s, cid)] += yld * area
    # 第二遍: 计算销售收入
    revenue = 0.0
    for (y, s, cid), produced in production.items():
        c = crop_by_id[cid]
        ccode = crop_code_by_id[cid]
        # 用基准价 + price_mult
        st = crop_unit_profit(processed, ccode, "平旱地", 1, mode=mode)
        if not st:
            continue
        price_base = st["price"] * (price_mult or 1.0)
        # 销售量上限
        baseline = base_sales_capacity(processed, ccode) * (sales_mult or 1.0)
        if produced <= baseline:
            revenue += produced * price_base
        else:
            normal = baseline * price_base
            over = produced - baseline
            if mode == "waste":
                over_rev = 0.0
            elif mode == "discount":
                # Q1: 50% 折价
                over_rev = over * price_base * 0.5
            else:
                # Q3: 弹性折扣: max(0, 0.5 + 0.3*rho) * price
                rho = 0.0
                if substitute_rho:
                    # 简单用 0 表示无替代
                    rho = substitute_rho
                over_rev = over * price_base * max(0.0, discount_alpha + 0.3 * rho)
            revenue += normal + over_rev
    return revenue - cost_total


def main():
    processed, action_space = _load()
    # sanity check: 一个空解
    print("Empty:", evaluate_solution(processed, action_space, {}, mode="discount"))
    # 一个示例解: 在 A1 平旱地 第一季 种 黄豆 80 亩
    p = next(p for p in processed["plots"] if p["name"] == "A1")
    c = next(c for c in processed["crops"] if c["code"] == 1)  # 黄豆
    a = next(a for a in action_space["actions"] if a["plot"] == p["id"] and a["crop"] == c["id"])
    x = {(p["id"], c["id"], 1, 2024): 80.0}
    print("A1 黄豆 80 亩 (year=2024):", evaluate_solution(processed, action_space, x, mode="discount"))


if __name__ == "__main__":
    main()