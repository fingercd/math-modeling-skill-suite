"""Optical-path helpers: phase difference, interference order, etc.

We work in the "wavenumber convention":
    ν̃ [cm⁻¹], wavelength λ [cm] = 1/ν̃.
    Optical path for thin film: Δ = 2 d n cos(θ_film) where θ_film by Snell.
    For oblique incidence from vacuum: cos(θ_film) = sqrt(1 - sin²θ/n²).
    Hence Δ = 2 d √(n² - sin²θ) .
"""
from __future__ import annotations

import numpy as np


def optical_path_delta(
    nu_cm: np.ndarray | float,
    d_m: float,
    n: np.ndarray | float,
    theta0_rad: float,
) -> np.ndarray | float:
    """Optical path difference Δ [cm] = 2 d √(n² − sin²θ)."""
    s = np.sin(theta0_rad)
    radicand = n * n - s * s
    radicand = np.maximum(radicand, 0.0)
    # Convert d from m to cm
    return 2.0 * (d_m * 100.0) * np.sqrt(radicand)


def interference_order(
    nu_cm: np.ndarray | float,
    d_m: float,
    n: np.ndarray | float,
    theta0_rad: float,
) -> np.ndarray | float:
    """m = Δ / λ  where λ = 1/ν̃ [cm]."""
    delta = optical_path_delta(nu_cm, d_m, n, theta0_rad)
    lam_cm = 1.0 / np.asarray(nu_cm)
    return delta / lam_cm


def lam_from_nu_cm(nu_cm: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / np.asarray(nu_cm)
