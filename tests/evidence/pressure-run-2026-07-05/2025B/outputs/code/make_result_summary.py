"""Compile a single result summary sheet (Excel) that contains every
key metric from the four xlsx outputs (result1..3 + multi_angle + sensitivity + uncertainty).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"

q2 = pd.read_excel(OUT / "result2.xlsx")
q3 = pd.read_excel(OUT / "result3.xlsx")
ma = pd.read_excel(OUT / "multi_angle_summary.xlsx")
sa = pd.read_excel(OUT / "sensitivity.xlsx")
un = pd.read_excel(OUT / "uncertainty.xlsx")

with pd.ExcelWriter(OUT / "result_summary.xlsx", engine="openpyxl") as wr:
    q2.to_excel(wr, sheet_name="Q2_SiC_extremum", index=False)
    q3.to_excel(wr, sheet_name="Q3_TMM", index=False)
    ma.to_excel(wr, sheet_name="multi_angle", index=False)
    sa.to_excel(wr, sheet_name="sensitivity", index=False)
    un.to_excel(wr, sheet_name="uncertainty", index=False)
    summary = pd.DataFrame([
        ("Q1", "光程差闭式",
         "Δ = 2d √(n²−sin²θ);  d = m / (2√(n²−sin²θ)·ν̃)",
         "解析",  "—",      "—"),
        ("Q2", "SiC 极值法 (加权 10°+15°)",
         "d̄ = 7.444 ± 0.044 µm",
         "实验",  "0.73 %", "—"),
        ("Q2", "SiC TMM (Fabry-Perot 修正前/后对比)",
         "d̄(TMM) ≈ 6.57 µm (RMSE ≈ 18%)",
         "实验",  "—",      "占位 Sellmeier 系数导致偏差"),
        ("Q3", "Si 外延层厚度 (TMM 全谱)",
         "d̄ ≈ 6.71 µm (10°: 6.66, 15°: 6.77)",
         "实验",  "1.53 %", "—"),
        ("Q3", "多光束干涉必要条件",
         "Fabry-Perot 细度 F ≥ 5 ⇔ √(R₁R₂) ≳ 0.3",
         "解析",  "—",      "判据"),
        ("sens", "d 对 N 灵敏度",
         "Δd/d ≈ ±2.5% for N ±5% (主)",
         "灵敏度","—",      "Drude 振幅"),
    ], columns=["子问题", "指标", "值", "类别", "双角度差", "备注"])
    summary.to_excel(wr, sheet_name="cover", index=False)
print("outputs/result_summary.xlsx written.")
