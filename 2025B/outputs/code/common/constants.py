"""Physical constants used by the project (SI)."""
from __future__ import annotations

# Speed of light [m/s]
C = 299_792_458.0

# Planck [J·s]
H = 6.626_070_15e-34

# Vacuum permittivity [F/m]
EPS0 = 8.854_187_8128e-12

# Elementary charge [C]
QE = 1.602_176_634e-19

# Electron rest mass [kg]
ME = 9.109_383_7015e-31

# 1 cm⁻¹ -> 1e2 m⁻¹ (波数 → 频率 [Hz] 转换: ν [cm^-1] * 100 = wavenumber [m^-1])
CM_INV_TO_M_INV = 100.0

# 1 cm⁻¹ -> 频率 [Hz] 的换算:f [Hz] = c * ν̃ [m^-1]
def cm_inv_to_hz(nu_tilde_cm: float | "np.ndarray") -> float | "np.ndarray":
    return C * nu_tilde_cm * CM_INV_TO_M_INV


def hz_to_cm_inv(freq_hz: float | "np.ndarray") -> float | "np.ndarray":
    return freq_hz / (C * CM_INV_TO_M_INV)
