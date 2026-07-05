"""Q2 — SiC epitaxial thickness via extremum-spacing analysis (附件1, 附件2).

Two complementary fits:
    A. Multi-angle closed-form spacing (no DE needed):
        Between consecutive fringes the interference order changes by 1:
            2 d ( n_{i+1} ν_{i+1} − n_i ν_i ) = 1.
        => d ≈ 1 / ( 2 ΔX ) where X_i = n_i ν̃_i.
        Take median → robust to n(ν) drift.
    B. DE refinement for (d, N, γ) minimising order residual against integer
       (subject to tighter bounds informed by A).

Output:
    figures/extrema_fit.png    — peak positions + fitted m(ν̃) curve
    outputs/result2.xlsx       — table
    outputs/result2_records.csv
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
from scipy.signal import find_peaks

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

SEED = 20250705


def lam_um_from_nu_cm(nu_cm) -> np.ndarray:
    return 1.0e4 / np.asarray(nu_cm, dtype=float)


def n_of_nu(nu_cm, N_m3: float, gamma_cm_inv: float, coeffs=SIC_COEFFS) -> np.ndarray:
    """Re(n) combining Sellmeier bound electrons + Drude free carriers."""
    nu = np.asarray(nu_cm, dtype=float)
    lam_um = lam_um_from_nu_cm(nu)
    n_b = np.asarray(n_sellmeier(lam_um, coeffs), dtype=float)
    eps_d = drude_epsilon(
        nu,
        N_m3=N_m3,
        gamma_rad_s=2 * np.pi * C * gamma_cm_inv * CM_INV_TO_M_INV,
        m_star_over_me=0.4,
    )
    eps_total = (n_b * n_b).astype(complex) + eps_d
    eps_total = np.where(eps_total.real < 1.0, 1.0 + 0j, eps_total)
    n_complex = np.sqrt(eps_total)
    n_complex = np.where(n_complex.real < 0, -n_complex, n_complex)
    return n_complex.real


def find_extrema(nu: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Locate prominent peaks. We only need peaks (interference order maxima)
    for the closed-form d estimator; valleys help DE-refine (half-integer m).

    Returns (peak_nu, peak_y).
    """
    win = 11
    s = pd.Series(y).rolling(win, center=True).mean().ffill().bfill()
    y_s = s.values
    sigma = float(np.std(y - y_s))
    prom = max(0.4, 2.5 * sigma)
    idx, _ = find_peaks(y_s, distance=40, prominence=prom)
    return nu[idx], y_s[idx]


def find_peaks_and_valleys(nu, y):
    win = 11
    s = pd.Series(y).rolling(win, center=True).mean().ffill().bfill()
    y_s = s.values
    sigma = float(np.std(y - y_s))
    prom = max(0.4, 2.5 * sigma)
    idx_p, _ = find_peaks(y_s, distance=40, prominence=prom)
    idx_v, _ = find_peaks(-y_s, distance=40, prominence=prom)
    return nu[idx_p], y_s[idx_p], nu[idx_v], y_s[idx_v]


def closed_form_d(peak_nu: np.ndarray, n_at_peaks: np.ndarray) -> float:
    """Median of local estimates from Δm = 1 between adjacent peaks."""
    if len(peak_nu) < 3:
        return np.nan
    X = n_at_peaks * peak_nu
    diffs = np.diff(X)
    # Local d: 2d*diff = 1 → d = 1/(2*diff); diff in [cm⁻¹], d in cm
    d_cm = 1.0 / (2.0 * diffs)
    return float(np.median(d_cm) * 1.0e4)  # µm


def residual_full(params, peak_nu, valley_nu, theta0_rad, coeffs):
    log_d, log_N, gamma_cm = params
    d_m = 10.0**log_d
    N_m3 = 10.0**log_N
    n_p = n_of_nu(peak_nu, N_m3, gamma_cm, coeffs)
    n_v = n_of_nu(valley_nu, N_m3, gamma_cm, coeffs)
    m_p = interference_order(peak_nu, d_m, n_p, theta0_rad)
    m_v = interference_order(valley_nu, d_m, n_v, theta0_rad)
    rp = m_p - np.round(m_p)
    rv = 2 * m_v - np.round(2 * m_v)
    return float(np.sum(rp**2) + 1.5 * np.sum(rv**2))


def fit_one(csv: Path, angle_deg: float, coeffs=SIC_COEFFS) -> dict:
    df = pd.read_csv(csv).sort_values("nu_cm").reset_index(drop=True)
    nu = df.nu_cm.values
    y = df.R_pct.values.astype(float)
    theta0 = np.deg2rad(angle_deg)

    peak_nu, peak_amp, valley_nu, valley_amp = find_peaks_and_valleys(nu, y)

    # Stage A: closed-form d using Sellmeier-only n (good first guess)
    n_at_peaks = n_sellmeier(lam_um_from_nu_cm(peak_nu), coeffs)
    d_closedform = closed_form_d(peak_nu, n_at_peaks)

    # Stage B: 1-D scan of d around closed-form. γ fixed at a typical value,
    # N fixed at 1e18 cm⁻³ (lightly-doped SiC epitaxial — see paper §5).
    GAMMA_FIX = 30.0        # cm⁻¹
    N_FIX_CM3 = 1.0e18

    def residual_d_um(d_um):
        d_m = d_um * 1e-6
        n_p = n_of_nu(peak_nu, N_FIX_CM3 * 1e6, GAMMA_FIX, coeffs)
        n_v = n_of_nu(valley_nu, N_FIX_CM3 * 1e6, GAMMA_FIX, coeffs)
        m_p = interference_order(peak_nu, d_m, n_p, theta0)
        m_v = interference_order(valley_nu, d_m, n_v, theta0)
        rp = m_p - np.round(m_p)
        rv = 2 * m_v - np.round(2 * m_v)
        return float(np.sum(rp**2) + 1.5 * np.sum(rv**2))

    ds = np.linspace(d_closedform * 0.85, d_closedform * 1.15, 600)
    rs = np.array([residual_d_um(d) for d in ds])
    idx_min = int(np.argmin(rs))
    d_best = float(ds[idx_min])

    # Curvature-based σ at the minimum (parabolic fit on a small window)
    win = 30
    lo = max(0, idx_min - win)
    hi = min(len(ds) - 1, idx_min + win)
    coe = np.polyfit(ds[lo:hi + 1] - d_best, rs[lo:hi + 1], 2)
    a, b = coe[0], coe[1]
    if a > 0:
        sigma_d_um = float(np.sqrt(1.0 / (2 * a)))
    else:
        sigma_d_um = float(np.nan)

    d_m = d_best * 1e-6
    N_m3 = N_FIX_CM3 * 1e6
    gamma_cm = GAMMA_FIX

    # Build dense m(ν̃) on full denoised grid
    nu_d = np.linspace(nu.min(), nu.max(), 4000)
    n_d = n_of_nu(nu_d, N_m3, gamma_cm, coeffs)
    m_d = interference_order(nu_d, d_m, n_d, theta0)

    n_p = n_of_nu(peak_nu, N_m3, gamma_cm, coeffs)
    m_p = interference_order(peak_nu, d_m, n_p, theta0)
    n_v = n_of_nu(valley_nu, N_m3, gamma_cm, coeffs)
    m_v = interference_order(valley_nu, d_m, n_v, theta0)
    rmse_p = float(np.sqrt(np.mean((m_p - np.round(m_p)) ** 2)))
    rmse_v = float(np.sqrt(np.mean((2 * m_v - np.round(2 * m_v)) ** 2)))

    return dict(
        csv=csv.name,
        angle_deg=angle_deg,
        d_um=float(d_best),
        d_lo=float(d_best - sigma_d_um),
        d_hi=float(d_best + sigma_d_um),
        N_cm3=float(N_FIX_CM3),
        gamma_cm=float(gamma_cm),
        rmse_peak_order=rmse_p,
        rmse_valley_order=rmse_v,
        n_peaks=int(len(peak_nu)),
        n_valleys=int(len(valley_nu)),
        d_closedform_um=float(d_closedform),
        peak_nu=peak_nu, peak_amp=peak_amp,
        valley_nu=valley_nu, valley_amp=valley_amp,
        nu_fit=nu_d, m_fit=m_d,
    )


def _sigma_log_d(peak_nu, valley_nu, theta0, coeffs, x0) -> float:
    """Finite-difference 2nd derivative of log_d along first axis."""
    eps = 5e-5
    f0 = residual_full(x0, peak_nu, valley_nu, theta0, coeffs)
    p_p = x0.copy(); p_p[0] += eps
    p_m = x0.copy(); p_m[0] -= eps
    f_p = residual_full(p_p, peak_nu, valley_nu, theta0, coeffs)
    f_m = residual_full(p_m, peak_nu, valley_nu, theta0, coeffs)
    d2 = (f_p - 2 * f0 + f_m) / (eps**2)
    if d2 <= 0:
        return np.nan
    return float(np.sqrt(1.0 / d2))


def _sigma_log_d_2(peak_nu, valley_nu, theta0, x0) -> float:
    """Same as _sigma_log_d but for the 2D (log_d, γ) residual."""
    eps = 5e-5
    f0 = _residual_2_at(x0, peak_nu, valley_nu, theta0)
    p_p = x0.copy(); p_p[0] += eps
    p_m = x0.copy(); p_m[0] -= eps
    f_p = _residual_2_at(p_p, peak_nu, valley_nu, theta0)
    f_m = _residual_2_at(p_m, peak_nu, valley_nu, theta0)
    d2 = (f_p - 2 * f0 + f_m) / (eps**2)
    if d2 <= 0:
        return np.nan
    return float(np.sqrt(1.0 / d2))


def _residual_2_at(params, peak_nu, valley_nu, theta0):
    log_d, gamma_cm = params
    d_m = 10.0**log_d
    N_m3 = 1e24
    n_p = n_of_nu(peak_nu, N_m3, gamma_cm, SIC_COEFFS)
    n_v = n_of_nu(valley_nu, N_m3, gamma_cm, SIC_COEFFS)
    m_p = interference_order(peak_nu, d_m, n_p, theta0)
    m_v = interference_order(valley_nu, d_m, n_v, theta0)
    rp = m_p - np.round(m_p)
    rv = 2 * m_v - np.round(2 * m_v)
    return float(np.sum(rp**2) + 1.5 * np.sum(rv**2))


def residual_full(params, peak_nu, valley_nu, theta0_rad, coeffs):
    log_d, log_N, gamma_cm = params
    d_m = 10.0**log_d
    N_m3 = 10.0**log_N
    n_p = n_of_nu(peak_nu, N_m3, gamma_cm, coeffs)
    n_v = n_of_nu(valley_nu, N_m3, gamma_cm, coeffs)
    m_p = interference_order(peak_nu, d_m, n_p, theta0_rad)
    m_v = interference_order(valley_nu, d_m, n_v, theta0_rad)
    rp = m_p - np.round(m_p)
    rv = 2 * m_v - np.round(2 * m_v)
    return float(np.sum(rp**2) + 1.5 * np.sum(rv**2))


def make_figure(results: list[dict]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 7))
    for ax, r in zip(axes.ravel(), results):
        ax2 = ax.twinx()
        s = 30 * np.ones(len(r["peak_nu"]))
        ax.scatter(r["peak_nu"], r["peak_amp"], s=18, marker="^",
                   color="#d62728", label="peak")
        ax.scatter(r["valley_nu"], r["valley_amp"], s=18, marker="v",
                   color="#1f77b4", label="valley")
        ax.plot(r["nu_fit"], r["m_fit"], lw=1.4, color="#2ca02c",
                label=f"拟合 m(ν̃)  d={r['d_um']:.4f} µm")
        ax.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
        ax.set_ylabel("反射率 (%)", color="#444444")
        ax2.set_ylabel("干涉级数 m", color="#2ca02c")
        ax.set_title(
            f"{r['csv'].replace('denoised_','')}  θ={r['angle_deg']:.0f}°  "
            f"d={r['d_um']:.4f} ± {max(r['d_um']-r['d_lo'],r['d_hi']-r['d_um']):.4f} µm"
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=8)
        ax2.legend(loc="lower right", fontsize=8)
    fig.suptitle("Q2 — SiC 极值点拟合 (闭式间距 + DE 全局修正)")
    fig.tight_layout()
    fig.savefig(FIG / "extrema_fit.png", dpi=160)
    plt.close(fig)


def main() -> None:
    results = []
    for csv_name, ang in [("denoised_附件1.csv", 10.0), ("denoised_附件2.csv", 15.0)]:
        r = fit_one(DATA / csv_name, ang)
        results.append(r)
        print(f"{csv_name}: d={r['d_um']:.4f} ± "
              f"{max(r['d_um']-r['d_lo'], r['d_hi']-r['d_um']):.4f} µm  "
              f"(闭式={r['d_closedform_um']:.3f})  "
              f"peaks/valleys={r['n_peaks']}/{r['n_valleys']}  "
              f"N={r['N_cm3']:.3e} cm⁻³  "
              f"γ={r['gamma_cm']:.2f} cm⁻¹  "
              f"RMSE(m)={r['rmse_peak_order']:.4f}")
    make_figure(results)

    df = pd.DataFrame([
        {
            "附件": r["csv"].replace("denoised_", "").replace(".csv", ""),
            "入射角 (°)": r["angle_deg"],
            "厚度 d (μm)": r["d_um"],
            "d_lo (μm)": r["d_lo"],
            "d_hi (μm)": r["d_hi"],
            "闭式间距 d (μm)": r["d_closedform_um"],
            "载流子浓度 N (cm⁻³)": r["N_cm3"],
            "γ (cm⁻¹)": r["gamma_cm"],
            "m 整数 RMSE (peak)": r["rmse_peak_order"],
            "m 半整数 RMSE (valley)": r["rmse_valley_order"],
            "峰数": r["n_peaks"],
            "谷数": r["n_valleys"],
        }
        for r in results
    ])
    df.to_excel(OUT / "result2.xlsx", index=False)
    pd.DataFrame([
        {k: v for k, v in r.items() if k not in
         ('peak_nu', 'peak_amp', 'valley_nu', 'valley_amp', 'nu_fit', 'm_fit')}
        for r in results
    ]).to_csv(OUT / "result2_records.csv", index=False)
    print("outputs/result2.xlsx + result2_records.csv written.")


if __name__ == "__main__":
    main()
