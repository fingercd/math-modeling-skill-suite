"""N-scan sensitivity: vary carrier concentration across [1e15, 1e20] cm⁻³,
re-run Q2 extremum fit at each N, plot d-bar vs log N.

Demonstrates that Q2 d depends only weakly on N at N > 1e17 cm⁻³.
"""
from __future__ import annotations

from common import _matplotlib_setup  # noqa: F401
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common.constants import C, CM_INV_TO_M_INV
from common.drude import drude_epsilon
from common.optical_path import interference_order
from common.sellmeier import SIC_COEFFS, n_sellmeier

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
OUT = ROOT / "outputs"
FIG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def lam_um_from_nu_cm(nu_cm):
    return 1.0e4 / np.asarray(nu_cm, dtype=float)


def n_of_nu(nu_cm, N_m3, gamma_cm_inv):
    nu = np.asarray(nu_cm, dtype=float)
    lam_um = lam_um_from_nu_cm(nu)
    n_b = n_sellmeier(lam_um, SIC_COEFFS)
    eps_d = drude_epsilon(
        nu, N_m3=N_m3,
        gamma_rad_s=2 * np.pi * C * gamma_cm_inv * CM_INV_TO_M_INV,
        m_star_over_me=0.4,
    )
    eps_total = (n_b * n_b).astype(complex) + eps_d
    eps_total = np.where(eps_total.real < 1.0, 1.0 + 0j, eps_total)
    n_complex = np.sqrt(eps_total)
    n_complex = np.where(n_complex.real < 0, -n_complex, n_complex)
    return n_complex.real


def fit_d_at_N(csv, angle_deg, N_cm3, gamma_cm):
    df = pd.read_csv(csv).sort_values("nu_cm").reset_index(drop=True)
    nu = df.nu_cm.values
    y = df.R_pct.values.astype(float)
    theta0 = np.deg2rad(angle_deg)
    from scipy.signal import find_peaks
    win = 11
    s = pd.Series(y).rolling(win, center=True).mean().ffill().bfill()
    y_s = s.values
    sigma = float(np.std(y - y_s))
    prom = max(0.4, 2.5 * sigma)
    ip, _ = find_peaks(y_s, distance=40, prominence=prom)
    peak_nu = nu[ip]
    if len(peak_nu) < 4:
        return np.nan

    def R(d_um):
        d_m = d_um * 1e-6
        n_p = n_of_nu(peak_nu, N_cm3 * 1e6, gamma_cm)
        m_p = interference_order(peak_nu, d_m, n_p, theta0)
        return np.sum((m_p - np.round(m_p)) ** 2)

    # closed-form initial
    n_at = n_sellmeier(lam_um_from_nu_cm(peak_nu), SIC_COEFFS)
    X = n_at * peak_nu
    diffs = np.diff(X)
    d_close = float(np.median(1.0 / (2.0 * diffs))) * 1e4

    ds = np.linspace(d_close * 0.85, d_close * 1.15, 200)
    rs = np.array([R(d) for d in ds])
    return float(ds[int(np.argmin(rs))])

    # closed-form initial
    n_at = n_sellmeier(lam_um_from_nu_cm(peak_nu), coeffs)
    X = n_at * peak_nu
    diffs = np.diff(X)
    d_close = float(np.median(1.0 / (2.0 * diffs))) * 1e4

    ds = np.linspace(d_close * 0.85, d_close * 1.15, 200)
    rs = np.array([R(d) for d in ds])
    return float(ds[int(np.argmin(rs))])


def main():
    N_grid = np.logspace(15, 20, 25)  # cm⁻³
    gamma = 30.0
    rows = []
    for ang, csv in [(10.0, "denoised_附件1.csv"), (15.0, "denoised_附件2.csv")]:
        for N in N_grid:
            d = fit_d_at_N(DATA / csv, ang, N, gamma)
            rows.append((csv, ang, N, d))
    df = pd.DataFrame(rows, columns=["csv", "angle", "N_cm3", "d_um"])
    df.to_excel(OUT / "sensitivity_N.xlsx", index=False)

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for ang, col in [(10.0, "#1f77b4"), (15.0, "#d62728")]:
        sub = df[df["angle"] == ang]
        sub = sub.sort_values("N_cm3")
        ax.plot(np.log10(sub.N_cm3), sub.d_um, "o-", color=col,
                label=f"附件 {2 if ang>10 else 1} (θ={int(ang)}°)")
    ax.set_xlabel("log₁₀(N / cm⁻³)")
    ax.set_ylabel("拟合 $d$ (µm)")
    ax.set_title("Q2 厚度对载流子浓度 $N$ 的灵敏度 (γ 固定为 30 cm⁻¹)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "sensitivity_N.png", dpi=160)
    plt.close(fig)
    print("figures/sensitivity_N.png + outputs/sensitivity_N.xlsx written.")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
