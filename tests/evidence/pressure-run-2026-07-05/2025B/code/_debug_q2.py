"""Diagnostic for Q2: inspect extracted extrema + interference orders."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from common.sellmeier import SIC_COEFFS, n_sellmeier
from common.optical_path import interference_order

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def main() -> None:
    for csv in ["denoised_附件1.csv", "denoised_附件2.csv"]:
        df = pd.read_csv(DATA / csv)
        nu = df.nu_cm.values
        y = df.R_pct.values.astype(float)
        ang = 10 if "附件1" in csv else 15
        print(f"--- {csv} (θ={ang}°) ---")
        print(f"  nu range: {nu.min():.2f}–{nu.max():.2f} cm⁻¹,  points={len(nu)}")

        # very simple peak finder
        from scipy.signal import find_peaks
        sigma = float(np.std(np.diff(y)))
        prom = max(0.3, 3 * sigma)
        ip, _ = find_peaks(y, distance=40, prominence=prom)
        iv, _ = find_peaks(-y, distance=40, prominence=prom)
        print(f"  peaks: {len(ip)}, valleys: {len(iv)}, prominence={prom:.3f}")

        lam_um = 1.0e4 / nu
        n = n_sellmeier(lam_um, SIC_COEFFS)
        theta = np.deg2rad(ang)
        for d_um in [5, 6, 7, 7.5, 7.7, 8, 10, 12, 15]:
            m_p = interference_order(nu[ip], d_um * 1e-6, n[ip], theta)
            m_v = interference_order(nu[iv], d_um * 1e-6, n[iv], theta)
            rp = np.std(m_p - np.round(m_p))
            rv = np.std(2 * m_v - np.round(2 * m_v))
            print(f"  d={d_um:.2f} µm: m peak mean={np.mean(m_p):.2f}±{np.std(m_p):.2f}, "
                  f"σ(m-peak to int)={rp:.4f}, "
                  f"σ(2m-valley to int)={rv:.4f}")
        print()


if __name__ == "__main__":
    main()
