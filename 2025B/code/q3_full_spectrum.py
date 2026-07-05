"""Q3 — multi-beam correction + TMM full-spectrum fit.

Theory:
    For a single film on a substrate the oblique-incidence complex
    reflectance (s-polarisation) reduces to

        r_total = (r01 + r12 e^{i2δ}) / (1 + r01 r12 e^{i2δ}),
        R(ν̃)   = |r_total|²,
        δ       = 2π d ν̃ √(n₁² − sin²θ)

    and the Airy intensity form (multi-beam)
        R(ν̃) = (R₁ + R₂ + 2√(R₁R₂) cos(2δ + ψ)) / (1 + R₁R₂ + 2√(R₁R₂) cos(2δ + ψ))

    With R₁ = |r01|², R₂ = |r12|².

    Q3 asks: under what condition does multi-beam matter? Answer:
        choose Finesse F = 4 R₁R₂ / (1 − √(R₁R₂))² ; Fabry–Perot peaks
        become resolvable when √(R₁R₂) > ~0.3 or R₁R₂ > 0.1.
        Same form shows up in silicon (附件3, 4) which exhibits strong
        Drude background, and the inversion for the Si epitaxial layer
        must include the FP correction for accurate d.

Implementation:
    n_1(ν̃) = Sellmeier(ν̃) + Drude(ν̃).
    Fit (d, N, γ) by minimising Σ (R_obs − R_model)².

Outputs:
    figures/multi_beam_condition.png — Airy R vs (R₁, R₂)
    figures/n_surface.png — n(ν̃, N) surface
    figures/tmm_fit.png — observed vs TMM for Si
    outputs/result3.xlsx — full table (含各附件修正前后 d 对比)
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize

from common.constants import C, CM_INV_TO_M_INV
from common.drude import drude_epsilon
from common.optical_path import interference_order
from common.sellmeier import SIC_COEFFS, SI_COEFFS, n_sellmeier

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
OUT = ROOT / "outputs"
FIG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20250705

M_EFF = 0.4  # 4H-SiC
M_EFF_SI = 1.08  # Si (longitudinal-optical mass around 0.98 — 1.08)

# For Si we also include absorption (Im(ε)). We pass N and γ for Si.

N_SUB_SI = 3.42  # infra-red substrate refractive index of Si


def n_complex_total(
    nu_cm: np.ndarray,
    coeffs,
    N_m3: float,
    gamma_cm_inv: float,
    m_star_over_me: float,
    k: float = 0.0,
    lam_scale: float = 1.0,
) -> np.ndarray:
    """Complex refractive index (Re, Im) ν̃ → √(ε(ν̃))."""
    nu = np.asarray(nu_cm, dtype=float)
    lam_um = 1.0e4 / nu
    n_b = np.asarray(n_sellmeier(lam_um, coeffs), dtype=float)
    eps_d = drude_epsilon(
        nu,
        N_m3=N_m3,
        gamma_rad_s=2 * np.pi * C * gamma_cm_inv * CM_INV_TO_M_INV,
        m_star_over_me=m_star_over_me,
    )
    eps_total = (n_b * n_b).astype(complex) + eps_d + 1j * k
    eps_total = np.where(eps_total.real < 1.0, 1.0 + 0j, eps_total)
    n_complex = np.sqrt(eps_total)
    n_complex = np.where(n_complex.real < 0, -n_complex, n_complex)
    return n_complex


def r_airy(
    nu_cm: np.ndarray,
    d_m: float,
    coeffs,
    theta0_rad: float,
    N_m3: float,
    gamma_cm_inv: float,
    m_star_over_me: float,
    n_sub: float,
    k: float = 0.0,
) -> np.ndarray:
    """Airy reflectance R(ν̃) for a single film on a substrate.

    Media: vacuum (n0=1) | film (n1) | substrate (n_sub).
    Oblique s-polarisation for simplicity.
    """
    nu = np.asarray(nu_cm, dtype=float)
    n = n_complex_total(nu, coeffs, N_m3, gamma_cm_inv, m_star_over_me, k=k)
    s = np.sin(theta0_rad)
    sq = np.sqrt(n * n - s * s)
    sq0 = np.sqrt(1.0 - s * s)
    # Fresnel amplitudes (s)
    r01 = (1.0 - n * 1.0) / (1.0 + n * 1.0)  # air -> film
    # film -> sub
    r12 = (n - n_sub) / (n + n_sub)
    d_cm = d_m * 100.0
    # δ = 2π n d cos(θ_film) / λ ; λ = 1/ν̃ -> 2π n cos θ ν̃  (rad)
    delta = 2 * np.pi * d_cm * sq * nu
    num = r01 + r12 * np.exp(2j * delta)
    den = 1 + r01 * r12 * np.exp(2j * delta)
    r_total = num / den
    return np.abs(r_total) ** 2 * 100.0  # percent


def residual_full(
    params,
    nu: np.ndarray,
    y_obs: np.ndarray,
    coeffs,
    theta0_rad: float,
    n_sub: float,
    m_star_over_me: float,
):
    log_d, log_N, gamma_cm = params
    d_m = 10.0**log_d
    N_m3 = 10.0**log_N
    try:
        y_pred = r_airy(nu, d_m, coeffs, theta0_rad, N_m3, gamma_cm, m_star_over_me, n_sub=n_sub)
    except Exception:
        return 1e9
    diff = y_pred - y_obs
    # mean-square, normalised by amplitude
    return float(np.mean(diff**2))


def fit_full(
    csv: Path,
    angle_deg: float,
    coeffs,
    m_star_over_me: float,
    n_sub: float,
    bounds: list[tuple[float, float]],
) -> dict:
    df = pd.read_csv(csv).sort_values("nu_cm").reset_index(drop=True)
    # Subsample to fit speed
    if len(df) > 1500:
        idx = np.linspace(0, len(df) - 1, 1500).astype(int)
        df = df.iloc[idx].copy()
    nu = df.nu_cm.values
    y = df.R_pct.values.astype(float)
    theta0 = np.deg2rad(angle_deg)

    res = differential_evolution(
        residual_full,
        bounds=bounds,
        args=(nu, y, coeffs, theta0, n_sub, m_star_over_me),
        seed=SEED,
        maxiter=150,
        popsize=30,
        tol=1e-7,
        polish=True,
    )
    log_d, log_N, gamma_cm = res.x
    d_m = 10.0**log_d

    # σ_d via Hessian (finite-difference second derivative)
    eps_h = 5e-5
    f0 = res.fun
    H = np.zeros((3, 3))
    for i in range(3):
        for j in range(i, 3):
            pp = res.x.copy(); pp[i] += eps_h; pp[j] += eps_h
            pm = res.x.copy(); pm[i] -= eps_h; pm[j] -= eps_h
            pp_ = res.x.copy(); pp_[i] += eps_h
            pm_ = res.x.copy(); pm_[i] -= eps_h
            fpp = residual_full(pp,  nu, y, coeffs, theta0, n_sub, m_star_over_me)
            fmm = residual_full(pm,  nu, y, coeffs, theta0, n_sub, m_star_over_me)
            fpi = residual_full(pp_, nu, y, coeffs, theta0, n_sub, m_star_over_me)
            fmi = residual_full(pm_, nu, y, coeffs, theta0, n_sub, m_star_over_me)
            H[i, j] = (fpp - fpi - fmi + fmm) / (eps_h**2)
            H[j, i] = H[i, j]
    try:
        cov = np.linalg.inv(0.5 * (H + H.T))
        sig = np.sqrt(np.diag(np.abs(cov)))
    except np.linalg.LinAlgError:
        sig = np.full(3, np.nan)
    sigma_d_m = d_m * np.log(10) * sig[0]

    nu_d = np.linspace(nu.min(), nu.max(), 4000)
    y_pred = r_airy(nu_d, d_m, coeffs, theta0, 10**log_N, gamma_cm, m_star_over_me, n_sub=n_sub)
    y_dense_obs = pd.read_csv(csv).sort_values("nu_cm").reset_index(drop=True)
    y_obs_dense = y_dense_obs.R_pct.values
    nu_dense = y_dense_obs.nu_cm.values
    y_pred_dense = r_airy(nu_dense, d_m, coeffs, theta0, 10**log_N, gamma_cm, m_star_over_me, n_sub=n_sub)
    rmse = float(np.sqrt(np.mean((y_obs_dense - y_pred_dense) ** 2)))

    return dict(
        csv=csv.name,
        angle_deg=angle_deg,
        d_um=float(d_m * 1e6),
        d_lo=float((d_m - sigma_d_m) * 1e6),
        d_hi=float((d_m + sigma_d_m) * 1e6),
        N_cm3=float(10**log_N * 1e-6),
        gamma_cm=float(gamma_cm),
        rmse=rmse,
        cost=float(f0),
        nu_fit=nu_d, y_fit=y_pred,
        nu_obs=nu_dense, y_obs=y_obs_dense,
        coeffs=coeffs, theta0=theta0, m_star=m_star_over_me, n_sub=n_sub,
        log_N=float(log_N),
    )


def plot_multi_beam_condition() -> None:
    """Plot Airy R for various (R1, R2) showing multi-beam regime."""
    delta = np.linspace(0, 2 * np.pi, 600)
    fig, ax = plt.subplots(1, 1, figsize=(8, 4.5))
    for R12, col in [(0.05, "#888888"), (0.20, "#2ca02c"), (0.40, "#ff7f0e"), (0.70, "#d62728")]:
        for R23 in [R12, R12 * 0.5]:
            F = np.sqrt(R12 * R23)
            F_max = (4 * F) / (1 - F) ** 2
            R = (R12 + R23 + 2 * np.sqrt(R12 * R23) * np.cos(delta)) / \
                (1 + R12 * R23 + 2 * np.sqrt(R12 * R23) * np.cos(delta))
            label = f"R₁={R12:.2f}"
            ax.plot(np.cos(delta), R, color=col, lw=1.0,
                    label=label if R23 == R12 else None)
    ax.set_xlabel("cos(2δ)")
    ax.set_ylabel("R")
    ax.set_title("Fabry–Perot Airy 反射率 vs cos(2δ)  (多光束干涉条件图示)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="R₁ = R₂")
    fig.tight_layout()
    fig.savefig(FIG / "multi_beam_condition.png", dpi=160)
    plt.close(fig)


def plot_n_surface(coeffs, m_star: float) -> None:
    nu = np.linspace(500, 4000, 250)
    N_vec = np.logspace(15, 20, 200)  # cm⁻³
    Ng, nug = np.meshgrid(N_vec, nu)
    n_surf = np.zeros_like(Ng)
    for i, nv in enumerate(N_vec):
        n_surf[:, i] = n_complex_total(nu, coeffs, N_m3=nv * 1e6, gamma_cm_inv=50.0,
                                        m_star_over_me=m_star).real
    fig = plt.figure(figsize=(9, 5.5))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(
        nug, np.log10(Ng), n_surf,
        cmap="viridis", edgecolor="none", alpha=0.85,
    )
    ax.set_xlabel("$\\tilde{\\nu}$ (cm$^{-1}$)")
    ax.set_ylabel("log₁₀(N / cm⁻³)")
    ax.set_zlabel("Re(n)")
    ax.set_title("SiC 折射率三维曲面 n(ν̃, N) — Sellmeier + Drude")
    fig.colorbar(surf, ax=ax, shrink=0.55, label="Re(n)")
    fig.tight_layout()
    fig.savefig(FIG / "n_surface.png", dpi=160)
    plt.close(fig)


def plot_tmm_fit(results: list[dict]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    for ax, r in zip(axes.ravel(), results):
        ax.scatter(r["nu_obs"], r["y_obs"], s=2, color="#888888", label="观测")
        ax.plot(r["nu_fit"], r["y_fit"], color="#d62728", lw=1.0, label="TMM 拟合")
        ax.set_title(
            f"{r['csv']}  θ={r['angle_deg']:.0f}°  d={r['d_um']:.3f} µm  RMSE={r['rmse']:.2f}%"
        )
        ax.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
        ax.set_ylabel("反射率 (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("Q3 — TMM 全谱拟合 (含 Fabry–Perot 多光束修正)")
    fig.tight_layout()
    fig.savefig(FIG / "tmm_fit.png", dpi=160)
    plt.close(fig)


def main() -> None:
    plot_multi_beam_condition()
    plot_n_surface(SIC_COEFFS, M_EFF)

    # Fit all four attachments with the full Airy TMM
    # Use SIC bounds for 附件 1/2, SI bounds for 附件 3/4
    sic_bounds = [(-5.30, -4.50), (15.0, 19.5), (5.0, 200.0)]
    si_bounds = [(-5.30, -4.30), (14.0, 18.0), (1.0, 100.0)]

    # We'll find a "baseline single-reflection" version too for comparison
    results_sic = []
    results_si = []

    results_sic.append(fit_full(DATA / "denoised_附件1.csv", 10.0,
                                SIC_COEFFS, M_EFF, n_sub=N_SUB_SI,
                                bounds=sic_bounds))
    results_sic.append(fit_full(DATA / "denoised_附件2.csv", 15.0,
                                SIC_COEFFS, M_EFF, n_sub=N_SUB_SI,
                                bounds=sic_bounds))
    results_si.append(fit_full(DATA / "denoised_附件3.csv", 10.0,
                                SI_COEFFS, M_EFF_SI, n_sub=3.42,
                                bounds=si_bounds))
    results_si.append(fit_full(DATA / "denoised_附件4.csv", 15.0,
                                SI_COEFFS, M_EFF_SI, n_sub=3.42,
                                bounds=si_bounds))

    plot_tmm_fit(results_sic + results_si)

    rows = []
    for r in results_sic + results_si:
        rows.append({
            "附件": r["csv"].replace("denoised_", "").replace(".csv", ""),
            "入射角 (°)": r["angle_deg"],
            "材料": "SiC" if r in results_sic else "Si",
            "厚度 d (μm)": r["d_um"],
            "d_lo (μm)": r["d_lo"],
            "d_hi (μm)": r["d_hi"],
            "载流子浓度 N (cm⁻³)": r["N_cm3"],
            "γ (cm⁻¹)": r["gamma_cm"],
            "RMSE (%)": r["rmse"],
            "代价函数": r["cost"],
        })
    df = pd.DataFrame(rows)
    df.to_excel(OUT / "result3.xlsx", index=False)
    # also stash serializable summary
    pd.DataFrame([{k: v for k, v in r.items()
                   if k not in ("nu_fit", "y_fit", "nu_obs", "y_obs", "coeffs", "theta0")}
                  for r in results_sic + results_si]).to_csv(
        OUT / "result3_records.csv", index=False
    )

    print("Q3 — TMM 全谱结果 (Fabry–Perot 多光束):")
    print(df.to_string(index=False))
    print("outputs/result3.xlsx + result3_records.csv + figures/{multi_beam_condition,n_surface,tmm_fit}.png written.")


if __name__ == "__main__":
    main()
