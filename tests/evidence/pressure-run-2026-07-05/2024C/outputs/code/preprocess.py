"""preprocess.py — 解析附件 1/2/3 → 内部 dict, 写出 code/data/processed.json

输入: research/attachments_raw/fujian1.xlsx, fujian2.xlsx
输出: code/data/processed.json
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
import openpyxl

BASE = Path(__file__).resolve().parent
RAW = BASE.parent / "research" / "attachments_raw"
OUT = BASE / "data" / "processed.json"


def _strip(x):
    if x is None:
        return None
    if isinstance(x, str):
        return x.strip().replace(" ", "")
    return x


def parse_plots(fujian1_path: Path) -> list[dict]:
    """解析附件 1 / 乡村的现有耕地 → 54 块地的列表."""
    wb = openpyxl.load_workbook(fujian1_path, data_only=True)
    ws = wb["乡村的现有耕地"]
    plots = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        if not row or row[0] is None:
            continue
        name, ptype, area = row[0], _strip(row[1]), row[2]
        if name is None:
            continue
        # 普通大棚 / 智慧大棚每年两季; 水浇地两季(但也可只种一季水稻); 平旱地/梯田/山坡地单季
        if ptype in ("普通大棚", "智慧大棚"):
            seasons = 2
        elif ptype == "水浇地":
            seasons = 2  # 默认两季 (水稻 / 白菜萝卜)
        else:
            seasons = 1
        plots.append({
            "id": len(plots),
            "name": str(name).strip(),
            "type": str(ptype).strip(),
            "area": float(area),
            "seasons": seasons,
        })
    return plots


def parse_crops(fujian1_path: Path) -> list[dict]:
    """解析附件 1 / 乡村种植的农作物 → 41 种作物的列表."""
    wb = openpyxl.load_workbook(fujian1_path, data_only=True)
    ws = wb["乡村种植的农作物"]
    crops = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        cid = row[0]
        if not isinstance(cid, int):
            continue
        name, ctype, allowed = row[1], row[2], row[3]
        # 解析 allowed: 多行字符串, 每个非空行是允许的地块类型
        allowed_types = set()
        if isinstance(allowed, str):
            for line in allowed.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # 例如 "水浇地第一季" / "普通大棚第一季" / "智慧大棚第一季、第二季"
                m = re.match(r"^([^第]+?)(第[一二]季(?:、第[一二]季)?)?$", line)
                if m:
                    allowed_types.add(m.group(1).strip())
        is_legume = isinstance(ctype, str) and "豆类" in ctype
        # 季节标记
        first_season = True
        second_season = True
        if isinstance(allowed, str):
            s = allowed.replace("\n", " ")
            if "第一季" in s and "第二季" not in s:
                second_season = False
            if "第二季" in s and "第一季" not in s:
                first_season = False
        # 单季作物: 平旱地/梯田/山坡地/水浇地水稻 都按第一季
        if any(t in (allowed or "") for t in ["平旱地", "梯田", "山坡地"]):
            first_season = True
            second_season = False
        if "水浇地" in (allowed or "") and "水稻" in (name or ""):
            first_season = True
            second_season = False
        # 水浇地第二季专属
        if "水浇地第二季" in (allowed or ""):
            first_season = False
            second_season = True
        crops.append({
            "id": int(cid) - 1,  # 0-based
            "code": int(cid),
            "name": str(name).strip(),
            "type": str(ctype).strip(),
            "is_legume": is_legume,
            "first_season": first_season,
            "second_season": second_season,
            "allowed_types": sorted(list(allowed_types)),
        })
    return crops


def parse_stats(fujian2_path: Path) -> dict:
    """解析附件 2 / 2023 年统计的相关数据 → { (crop_code, plot_type, season): {yield, cost, price} }."""
    wb = openpyxl.load_workbook(fujian2_path, data_only=True)
    ws = wb["2023年统计的相关数据"]
    stats = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[1] is None:
            continue
        cid, name, ptype, season, yld, cost, price = row[1], row[2], _strip(row[3]), _strip(row[4]), row[5], row[6], row[7]
        if cid is None:
            continue
        # parse price range
        if isinstance(price, str) and "-" in price:
            lo, hi = price.split("-")
            try:
                p = (float(lo) + float(hi)) / 2
            except Exception:
                p = None
        else:
            try:
                p = float(price)
            except Exception:
                p = None
        stats[(int(cid), str(ptype).strip(), str(season).strip())] = {
            "yield": float(yld) if yld is not None else None,
            "cost": float(cost) if cost is not None else None,
            "price": p,
        }
    return stats


def parse_2023_planting(fujian2_path: Path) -> list[dict]:
    """解析附件 2 / 2023 年农作物种植情况 → [(plot_name, crop_code, area, season)]."""
    wb = openpyxl.load_workbook(fujian2_path, data_only=True)
    ws = wb["2023年的农作物种植情况"]
    rec = []
    cur_plot = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or all(c is None for c in row):
            continue
        plot, cid, name, _, area, season = row[0], row[1], row[2], row[3], row[4], row[5]
        if plot is not None:
            cur_plot = str(plot).strip()
        rec.append({
            "plot": cur_plot,
            "crop_code": int(cid) if cid is not None else None,
            "crop_name": str(name).strip() if name else None,
            "area": float(area) if area is not None else 0.0,
            "season": _strip(season) if season is not None else None,
        })
    return rec


def main():
    plots = parse_plots(RAW / "fujian1.xlsx")
    crops = parse_crops(RAW / "fujian1.xlsx")
    stats = parse_stats(RAW / "fujian2.xlsx")
    planting_2023 = parse_2023_planting(RAW / "fujian2.xlsx")
    # 转 stats key 为 str (JSON 不能有 tuple)
    stats_json = {
        f"{k[0]}|{k[1]}|{k[2]}": v for k, v in stats.items()
    }
    out = {
        "plots": plots,
        "crops": crops,
        "stats": stats_json,
        "planting_2023": planting_2023,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK plots={len(plots)} crops={len(crops)} stats={len(stats_json)} planting_2023={len(planting_2023)}")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()