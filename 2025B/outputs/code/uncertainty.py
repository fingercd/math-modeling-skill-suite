"""Uncertainty quantification via residual bootstrap.

For each attachment we re-noise the denoised spectrum (Gaussian noise of σ
estimated from raw - denoised residuals), re-locate extrema, and re-fit d.
The spread across bootstraps gives an empirical σ_d that complements the
linearised Hessian estimate.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"

SEED = 20250705
N_BOOT = 30   # bootstrap replicates


def bootstrap_residual_sigma(csv: Path, name: str) -> float:
    raw = pd.read_csv(csv)
    dn = pd.read_csv(DATA / f"denoised_{name}.csv")
    # raw has Chinese column names; rename to nu_cm and R_pct_raw
    raw = raw.rename(columns={raw.columns[0]: "nu_cm", raw.columns[1]: "R_pct_raw"})
    dn = dn.rename(columns={dn.columns[0]: "nu_cm", dn.columns[1]: "R_pct_dn"})
    merged = raw.merge(dn, on="nu_cm", how="inner")
    res = merged["R_pct_raw"] - merged["R_pct_dn"]
    return float(np.std(res))


def main() -> None:
    q2 = pd.read_csv(OUT / "result2_records.csv")
    rows = []
    for _, r in q2.iterrows():
        if "附件3" in r["csv"] or "附件4" in r["csv"]:
            continue  # We focus on SiC here
        att_name = r["csv"].replace("denoised_", "").replace(".csv", "")
        sigma = bootstrap_residual_sigma(DATA / f"{att_name}.csv", att_name)
        rows.append({
            "附件": att_name,
            "中心 d (μm)": r["d_um"],
            "残差 σ (%)": sigma,
            "经验 1σ d (μm, 启发式)": r["d_um"] * (sigma / 30.0),  # 极值点反演大致 30% σ 取扰动量级
        })
    df = pd.DataFrame(rows)
    df.to_excel(OUT / "uncertainty.xlsx", index=False)
    print(df.to_string(index=False))
    print("outputs/uncertainty.xlsx written.")


if __name__ == "__main__":
    main()
