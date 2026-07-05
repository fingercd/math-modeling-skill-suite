"""Drude free-carrier contribution to the dielectric function.

ε_Drude(ω) = −ωp² / (ω² + iγω)
with ωp² = N e² / (ε₀ m*) .

Inputs use wavenumber ν̃ [cm⁻¹] (matches the experimental axes).
"""
from __future__ import annotations

import numpy as np

from .constants import CM_INV_TO_M_INV, C, EPS0, ME, QE


def plasma_omega_sq(
    N_m3: float,
    m_star_over_me: float = 1.0,
) -> float:
    """ωp² [rad/s]² for carrier density N [m⁻³] and effective mass m*.

    Default m* = m_e (free electron mass) is a reasonable proxy for lightly
    doped SiC; for heavily doped SiC substrates use m_star_over_me ~ 0.4
    (4H-SiC). The function returns the angular-frequency squared form so the
    caller multiplies by the conversion to circular frequency.
    """
    m_star = m_star_over_me * ME
    return N_m3 * QE**2 / (EPS0 * m_star)


def drude_epsilon(
    nu_cm: np.ndarray | float,
    N_m3: float,
    gamma_rad_s: float,
    m_star_over_me: float = 1.0,
) -> np.ndarray | float:
    """Complex Drude dielectric function ε_Drude(ν̃).

    angular frequency ω = 2π c ν̃ · 100 .
    γ is given in angular frequency units (rad/s).
    """
    arr = np.asarray(nu_cm, dtype=float)
    omega = 2 * np.pi * C * arr * CM_INV_TO_M_INV
    wp2 = plasma_omega_sq(N_m3, m_star_over_me)
    denom = omega * omega + 1j * gamma_rad_s * omega
    eps_d = -wp2 / denom
    return eps_d


def drude_n_absorption(
    nu_cm: np.ndarray | float,
    N_m3: float,
    gamma_rad_s: float,
    m_star_over_me: float = 1.0,
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Return Re(n) and Im(α) where n² = ε_Drude.

    Returns complex refractive index with convention
        n_complex = sqrt(ε)  (Re > 0).
    """
    eps = drude_epsilon(nu_cm, N_m3, gamma_rad_s, m_star_over_me)
    eps = eps + 0j
    n_complex = np.sqrt(eps)
    # Branch: Re(n) > 0
    n_complex = np.where(n_complex.real < 0, -n_complex, n_complex)
    return n_complex.real, n_complex.imag
