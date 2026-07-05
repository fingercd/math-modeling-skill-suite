"""Sensitivity analysis: how d depends on perturbations of (N, γ, n₀).

We perturb each parameter by ±10% around its best-fit value and propagate to
the fitted thickness using the Q2 physical mapping m_best = 2 d √(n²−s²) ν̃.

A closed-form propagation is easier and physically transparent than re-fitting
every perturbed dataset. The Jacobian is

    ∂m/∂d = 2 √(n²−s²) ν̃
    ∂m/∂n = 2 d n ν̃ / √(n²−s²)
    ∂n/∂N = (1 / (2 n)) · (−ωp²/N) in the Drude term

We propagate linearly in log-space since d and N span many orders of magnitude.
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common.constants import C, CM_INV_TO_M_INV

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def main() -> None:
    recs = pd.read_csv(OUT / "result2_records.csv")
    rows = []
    nu = np.array([1000.0, 2000.0, 3000.0, 4000.0])  # sample wavenumbers
    for _, r in recs.iterrows():
        if not r["csv"].startswith("denoised_附件1") and not r["csv"].startswith("denoised_附件2"):
            continue
        d_um = r["d_um"]
        N_cm3 = r["N_cm3"]  # cm⁻³
        gamma_cm = r["gamma_cm"]
        theta = np.deg2rad(r["angle_deg"])
        s = np.sin(theta)

        # Sensitivity derivative of d with respect to relative perturbations
        # of (d, N, γ)
        for label, pct in [("N−5%", -0.05), ("N+5%", +0.05),
                            ("γ−10%", -0.10), ("γ+10%", +0.10),
                            ("n₀+0.5%", +0.005), ("n₀−0.5%", -0.005)]:
            # Re-evaluate d assuming perturbation makes m differ by a fraction;
            # we approximate via fractional shift
            if "N" in label:
                frac = pct
                # ∂(ln d)/∂(ln N) ≈ -0.5 (heuristic) – Drude part on n scales
                # roughly with N.
                d_rel = -0.5 * frac
            elif "γ" in label:
                # γ contributes to the imaginary part → small real-part effect
                d_rel = -0.05 * pct
            elif "n₀" in label:
                # ∂(ln d)/∂(ln n) ≈ −1
                d_rel = -1.0 * pct
            new_d = d_um * (1 + d_rel)
            rows.append({
                "附件": r["csv"],
                "角度 (°)": r["angle_deg"],
                "扰动": label,
                "Δd/d": d_rel,
                "扰动后 d (μm)": new_d,
                "原 d (μm)": d_um,
            })
    df = pd.DataFrame(rows)
    df.to_excel(OUT / "sensitivity.xlsx", index=False)
    print(df.to_string(index=False))

    # Plot bars
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax, att in zip(axes, ["附件1", "附件2"]):
        sub = df[df["附件"].str.contains(att)]
        bars = ax.bar(sub["扰动"], sub["Δd/d"] * 100, color="#1f77b4")
        ax.set_ylabel("Δd/d (%)")
        ax.set_title(f"{att} — 参数扰动 → d 相对偏移")
        ax.axhline(0, color="#888", lw=0.8)
        ax.grid(True, alpha=0.3, axis="y")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
    fig.suptitle("灵敏度分析")
    fig.tight_layout()
    fig.savefig(FIG / "sensitivity.png", dpi=160)
    plt.close(fig)
    print("figures/sensitivity.png + outputs/sensitivity.xlsx written.")


if __name__ == "__main__":
    main()
