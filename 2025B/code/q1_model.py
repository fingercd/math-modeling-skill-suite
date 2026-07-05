"""Q1 — single-reflection interference math model.

We verify the closed-form expression:
    Δ = 2 d √(n² − sin²θ)  ;  m λ = Δ  ⇒  d = m / (2 ν̃ √(n² − sin²θ))

Outputs:
    figures/q1_path.png  — R vs ν schema
    figures/q1_demo.png  — synthetic R(ν) computed using the formula
    outputs/result1.xlsx — Q1 derivation summary table
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common.constants import C, CM_INV_TO_M_INV
from common.drude import drude_epsilon
from common.sellmeier import SIC_COEFFS, SI_COEFFS, n_sellmeier
from common.optical_path import interference_order

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "outputs"
FIG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def reflectivity_2beam(
    nu_cm: np.ndarray,
    d_m: float,
    theta0_rad: float,
    coeffs,
    N: float = 1.0e18,
    gamma_rad_s: float | None = None,
    m_star_over_me: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute two-beam interference reflectance R(ν̃).

    Modelled as:
        R(ν̃) = (r12² + r23² + 2 r12 r23 cos φ) / (1 + r12² r23² + 2 r12 r23 cos φ)
        φ = 4π d ν̃ √(n² − sin²θ)        [rad]
        r12 ~ (n − 1) / (n + 1)              air → film
        r23 ~ (n_s − n) / (n_s + n)         film → substrate (≈0 假设 n_s ≈ n ⇒ 弱衬底)
    For the pure two-beam limit we drop the denominator cosine term and use
        R ~ r12² + r23² + 2 r12 r23 cos φ
    which is the limiting "Fabry-Perot with low finesse" form. We treat
    this as a *pedagogical* single-reflection waveform and report the
    actual fitted multi-beam model inside `q3_full_spectrum.py`.

    Returns: R(ν̃), n(ν̃), m(ν̃) (half-integer at extrema).
    """
    nu = np.asarray(nu_cm, dtype=float)
    lam_um = 1.0e4 / nu  # cm⁻¹ -> µm
    n = np.asarray(n_sellmeier(lam_um, coeffs), dtype=float)
    s = np.sin(theta0_rad)
    sq = np.sqrt(np.maximum(n * n - s * s, 0.0))
    r12 = (n - 1.0) / (n + 1.0)
    # For SiC-on-Si: Si substrate refractive index much higher; the
    # substrate reflection term is non-negligible but bounded by (n_s - n)/(n_s + n).
    # We pick n_s ≈ 3.42 for Si in the IR (a typical value).
    n_sub = 3.42
    r23 = (n_sub - n) / (n_sub + n)
    # Phase φ [rad] = 4π d √(n² − sin²θ) ν̃ · 100
    d_cm = d_m * 100.0
    phi = 4.0 * np.pi * d_cm * nu * sq  # nu [cm⁻¹]
    # Two-beam reflectance (small-reflectivity approximation → formula)
    R = (r12**2) + (r23**2) + 2 * r12 * r23 * np.cos(phi)
    R = np.clip(R, 0.0, 1.0)
    m = interference_order(nu, d_m, n, theta0_rad)
    return R, n, m


def main() -> None:
    # Plot the interference diagram (single reflection)
    fig, ax = plt.subplots(1, 1, figsize=(10, 4.5))
    nu = np.linspace(500, 4000, 4000)
    for theta, col in zip([np.deg2rad(10.0), np.deg2rad(15.0)], ["#1f77b4", "#d62728"]):
        R, n, m = reflectivity_2beam(nu, d_m=7.7e-6, theta0_rad=theta, coeffs=SIC_COEFFS)
        # Convert to %
        ax.plot(nu, R * 100, color=col, lw=1.0,
                label=f"θ={np.rad2deg(theta):.0f}° 演示 R(ν̃)")
    ax.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
    ax.set_ylabel("反射率 (%)")
    ax.set_title("Q1 两光束干涉示意 (d = 7.7 µm, SiC)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "q1_path.png", dpi=160)
    plt.close(fig)

    # Also a "n-surface" or "n-vs-ν" preview for Q1
    fig2, ax2 = plt.subplots(1, 1, figsize=(10, 4.0))
    lam_um = 1.0e4 / nu
    n_sic = n_sellmeier(lam_um, SIC_COEFFS)
    n_si = n_sellmeier(lam_um, SI_COEFFS)
    ax2.plot(nu, n_sic, color="#d62728", lw=1.4, label="SiC Re(n) (Sellmeier)")
    ax2.plot(nu, n_si, color="#1f77b4", lw=1.4, label="Si Re(n) (Sellmeier)")
    ax2.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
    ax2.set_ylabel("Re(n)")
    ax2.set_title("Sellmeier 模型折射率 (λ → ν̃)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")
    fig2.tight_layout()
    fig2.savefig(FIG / "n_sellmeier_preview.png", dpi=160)
    plt.close(fig2)

    # result1.xlsx
    table = pd.DataFrame([
        ("Δ (optical path difference)", "2 d √(n²−sin²θ)", "cm", "Δ between the two reflected beams"),
        ("m λ = Δ", "m / (2 √(n²−sin²θ) ν̃)", "—", "interference condition (m ∈ ℤ)"),
        ("d =", "m / (2 √(n²−sin²θ) ν̃)", "cm", "thickness from order m and parameters"),
        ("n² Sellmeier", "1 + Σ B_j λ²/(λ²−C_j²)", "—", "bound-electron dispersion"),
        ("ε_Drude", "−ωp²/(ω²+iγω)", "—", "free-carrier term, ωp² = N e²/(ε₀m*)"),
        ("θ", "10° or 15° (题面)", "rad", "external incidence angle"),
    ], columns=["符号/量", "公式", "单位", "物理含义"])
    table.to_excel(OUT / "result1.xlsx", index=False)
    print("Q1: figures/q1_path.png + n_sellmeier_preview.png + outputs/result1.xlsx written.")


if __name__ == "__main__":
    main()
