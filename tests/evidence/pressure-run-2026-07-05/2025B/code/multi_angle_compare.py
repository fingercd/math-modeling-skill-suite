"""Multi-angle cross-validation: weighted mean of {d_10°, d_15°} with propagated σ.

Uses outputs/result2_records.csv (extremum-fit stage) which always has both
attachments fitted. Also reports the TMM-FP results when Q3 has run.
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

OUT.mkdir(parents=True, exist_ok=True)


def weighted_mean(d_a: float, sig_a: float, d_b: float, sig_b: float) -> tuple[float, float]:
    w_a = 1.0 / max(sig_a**2, 1e-12)
    w_b = 1.0 / max(sig_b**2, 1e-12)
    mu = (w_a * d_a + w_b * d_b) / (w_a + w_b)
    sigma = 1.0 / np.sqrt(w_a + w_b)
    return mu, sigma


def main() -> None:
    recs_p = pd.read_csv(OUT / "result2_records.csv")
    recs_t = pd.read_csv(OUT / "result3_records.csv") if (OUT / "result3_records.csv").exists() else None

    # Extract by attachment & angle (CSV columns: csv, angle_deg, d_um, d_lo, d_hi, …)
    def by_att(recs, att):
        sub = recs[recs["csv"].str.contains(att)]
        if len(sub) == 0:
            return None
        return sub.iloc[0]

    def sigma(row):
        return max(row.d_um - row.d_lo, row.d_hi - row.d_um)

    rows = []

    # SiC: Q2 has both angles, Q3 also has both
    sic_a = by_att(recs_p, "附件1")
    sic_b = by_att(recs_p, "附件2")
    if sic_a is not None and sic_b is not None:
        sa, sb = sigma(sic_a), sigma(sic_b)
        d_w, sd_w = weighted_mean(sic_a.d_um, sa, sic_b.d_um, sb)
        rel_diff = abs(sic_a.d_um - sic_b.d_um) / ((sic_a.d_um + sic_b.d_um) / 2) * 100.0
        rows.append({
            "材料": "SiC",
            "d_10° (μm)": sic_a.d_um, "σ_10° (μm)": sa,
            "d_15° (μm)": sic_b.d_um, "σ_15° (μm)": sb,
            "加权均值 d (μm)": d_w,
            "加权 σ (μm)": sd_w,
            "相对差 (10° vs 15°) (%)": rel_diff,
            "极值法 d (μm)": d_w,
        })

    # Si: Q3 only; report per-angle TMM values and weighted mean
    if recs_t is not None:
        si_a = by_att(recs_t, "附件3")
        si_b = by_att(recs_t, "附件4")
        if si_a is not None and si_b is not None:
            sa, sb = sigma(si_a), sigma(si_b)
            d_w, sd_w = weighted_mean(si_a.d_um, sa, si_b.d_um, sb)
            rel_diff = abs(si_a.d_um - si_b.d_um) / ((si_a.d_um + si_b.d_um) / 2) * 100.0
            rows.append({
                "材料": "Si",
                "d_10° (μm)": si_a.d_um, "σ_10° (μm)": sa,
                "d_15° (μm)": si_b.d_um, "σ_15° (μm)": sb,
                "加权均值 d (μm)": d_w,
                "加权 σ (μm)": sd_w,
                "相对差 (10° vs 15°) (%)": rel_diff,
                "极值法 d (μm)": np.nan,
            })

    # Optionally annotate with TMM for SiC
    if recs_t is not None:
        t1 = by_att(recs_t, "附件1")
        t2 = by_att(recs_t, "附件2")
        for r in rows:
            if r["材料"] == "SiC" and t1 is not None:
                r.setdefault("TMM d_10° (μm)", t1.d_um)
                r.setdefault("TMM σ_10° (μm)", sigma(t1))
                r.setdefault("TMM RMSE_10° (%)", t1.rmse)
            if r["材料"] == "SiC" and t2 is not None:
                r.setdefault("TMM d_15° (μm)", t2.d_um)
                r.setdefault("TMM σ_15° (μm)", sigma(t2))
                r.setdefault("TMM RMSE_15° (%)", t2.rmse)
            if r["材料"] == "Si" and t1 is not None and r["d_10° (μm)"] == t1.d_um:
                r.setdefault("TMM RMSE_10° (%)", t1.rmse)
            if r["材料"] == "Si" and t2 is not None and r["d_15° (μm)"] == t2.d_um:
                r.setdefault("TMM RMSE_15° (%)", t2.rmse)

    df = pd.DataFrame(rows)
    df.to_excel(OUT / "multi_angle_summary.xlsx", index=False)
    print(df.to_string(index=False))

    # Plot — only if both material rows present
    n_axes = len(df)
    fig, axes = plt.subplots(1, n_axes, figsize=(6 * n_axes, 4.0))
    if n_axes == 1:
        axes = [axes]
    for ax, (_, rr) in zip(axes, df.iterrows()):
        x = [0, 1]
        y = [rr["d_10° (μm)"], rr["d_15° (μm)"]]
        yerr = [rr["σ_10° (μm)"], rr["σ_15° (μm)"]]
        ax.errorbar(x, y, yerr=yerr, fmt="o", color="#1f77b4", capsize=6, lw=2)
        ax.axhline(rr["加权均值 d (μm)"], color="#d62728", ls="--",
                   label=f"加权 d={rr['加权均值 d (μm)']:.3f} µm")
        ax.set_xticks(x)
        ax.set_xticklabels(["θ = 10°", "θ = 15°"])
        ax.set_ylabel("厚度 d (μm)")
        ax.set_title(f"{rr['材料']}: 多角度反演厚度一致性")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("多角度交叉验证")
    fig.tight_layout()
    fig.savefig(FIG / "multi_angle_compare.png", dpi=160)
    plt.close(fig)
    print("figures/multi_angle_compare.png + outputs/multi_angle_summary.xlsx written.")


if __name__ == "__main__":
    main()
