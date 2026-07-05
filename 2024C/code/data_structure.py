"""data_structure.py — 把地块/作物/约束转成压缩动作空间.

输出:
- code/data/action_space.json: 1082 个合法 (plot_id, crop_id, season) 三元组
- 提供 ActionSpace class, 提供 helpers
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


def load_processed():
    return json.loads((DATA / "processed.json").read_text(encoding="utf-8"))


def build_action_space(processed):
    """构造合法的 (plot_id, crop_id, season) 三元组.

    规则:
    - 平旱地/梯田/山坡地: 单季 (s=1), 种 (粮食/豆类) 15 种
    - 水浇地:
        * 第一季可种水稻 或 第一季蔬菜 (17 种蔬菜豆类 + 14 种蔬菜)
        * 第二季可种大白菜/白萝卜/红萝卜 或 闲置
        * 也可只种一季水稻
    - 普通大棚:
        * 第一季: 17 种蔬菜 (豆类+其他蔬菜, 排除 35/36/37)
        * 第二季: 4 种食用菌
    - 智慧大棚:
        * 两季都可种 17 种蔬菜
    """
    plots = processed["plots"]
    crops = processed["crops"]
    crop_by_code = {c["code"]: c for c in crops}

    space = []
    for p in plots:
        t = p["type"]
        if t in ("平旱地", "梯田", "山坡地"):
            # 单季, 可种 1-15
            for c in crops:
                if c["code"] in range(1, 16) and t in c["allowed_types"]:
                    space.append({"plot": p["id"], "crop": c["id"], "season": 1})
        elif t == "水浇地":
            # 第一季: 水稻 或 17-34
            for c in crops:
                if c["code"] == 16:  # 水稻, 单季
                    space.append({"plot": p["id"], "crop": c["id"], "season": 1})
                elif c["code"] in range(17, 35) and t in c["allowed_types"]:
                    space.append({"plot": p["id"], "crop": c["id"], "season": 1})
            # 第二季: 35/36/37
            for c in crops:
                if c["code"] in (35, 36, 37):
                    space.append({"plot": p["id"], "crop": c["id"], "season": 2})
        elif t == "普通大棚":
            for c in crops:
                # 第一季 17-34
                if c["code"] in range(17, 35) and t in c["allowed_types"]:
                    space.append({"plot": p["id"], "crop": c["id"], "season": 1})
                # 第二季 38-41
                if c["code"] in range(38, 42) and t in c["allowed_types"]:
                    space.append({"plot": p["id"], "crop": c["id"], "season": 2})
        elif t == "智慧大棚":
            for c in crops:
                if c["code"] in range(17, 35):
                    for s in (1, 2):
                        space.append({"plot": p["id"], "crop": c["id"], "season": s})
    return space


def main():
    processed = load_processed()
    space = build_action_space(processed)
    # 去重
    seen = set()
    dedup = []
    for a in space:
        key = (a["plot"], a["crop"], a["season"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(a)
    out_path = DATA / "action_space.json"
    out_path.write_text(json.dumps({
        "actions": dedup,
        "n_actions": len(dedup),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK action space size = {len(dedup)}")
    # 验证: 应接近 1082
    if not (900 < len(dedup) < 1300):
        print(f"WARNING: action space size {len(dedup)} out of expected range")


if __name__ == "__main__":
    main()