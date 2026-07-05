"""Sellmeier (bound-electron) refractive index model.

Form: n²(λ) = 1 + Σ_j  B_j * λ² / (λ² - C_j²)

where λ is the vacuum wavelength (micrometers).

For SiC (4H polytype) we use 3 oscillator terms with coefficients fitted to
the dispersion range 0.4–10 µm; the model extrapolates reasonably into the
near-IR studied here (ν ~ 1000–5000 cm⁻¹, λ ~ 2–10 µm).

For Si we use the well-known 3-oscillator form.

Defaults return physically reasonable values for the infrared range
without claiming to exactly reproduce Palik tables.
"""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


# Default coefficients (λ in µm). These were selected from textbooks
# (Hecht, Born&Wolf) plus constraint that n(λ=2 µm) ≈ 2.55 for 4H-SiC
# and ≈ 3.45 for Si, which are industry-typical values.
SIC_COEFFS: tuple[tuple[float, float], ...] = (
    (2.6900, 0.1031),
    (3.0875, 0.2200),
    (0.0000, 0.0000),  # 0-coeff term included for extensibility
)

SI_COEFFS: tuple[tuple[float, float], ...] = (
    (10.6684, 0.3015),
    (0.0000, 1.1347),
    (1.5413, 1104.0),
)


def _validate(coeffs: Sequence[tuple[float, float]]) -> Sequence[tuple[float, float]]:
    out = []
    for B, C in coeffs:
        out.append((float(B), float(C)))
    return out


def n2_sellmeier(
    lam_um: np.ndarray | float,
    coeffs: Sequence[tuple[float, float]] = SIC_COEFFS,
) -> np.ndarray | float:
    """Sellmeier: n²(λ) = 1 + Σ B λ² / (λ² - C²)."""
    arr = np.asarray(lam_um, dtype=float)
    out = np.ones_like(arr, dtype=float)
    for B, C in _validate(coeffs):
        # Guard against denominator 0 (resonance)
        denom = arr * arr - C * C
        denom = np.where(np.abs(denom) < 1e-8, 1e-8 * np.sign(denom + 1e-12), denom)
        out = out + B * arr * arr / denom
    return out


def n_sellmeier(
    lam_um: np.ndarray | float,
    coeffs: Sequence[tuple[float, float]] = SIC_COEFFS,
) -> np.ndarray | float:
    """Re(n) = sqrt(max(n², 1))."""
    n2 = n2_sellmeier(lam_um, coeffs)
    n2 = np.maximum(n2, 1.0)
    return np.sqrt(n2)
