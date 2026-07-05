"""End-to-end reproducibility runner.

Re-runs the full pipeline in canonical order, ensuring every figure and
Excel/CSV in `outputs/` is regenerated against the same seed and config.

Steps:
    1. data_preprocess.py          -> 4 denoised CSVs + raw_vs_denoised.png + denoised_spectra.png + raw_spectra.png
    2. q1_model.py                 -> q1_path.png + n_sellmeier_preview.png + result1.xlsx
    3. q2_extremum_fitter.py       -> extrema_fit.png + result2.xlsx + result2_records.csv
    4. q3_full_spectrum.py         -> multi_beam_condition.png + n_surface.png + tmm_fit.png + result3.xlsx + result3_records.csv
    5. multi_angle_compare.py      -> multi_angle_compare.png + multi_angle_summary.xlsx
    6. sensitivity.py              -> sensitivity.png + sensitivity.xlsx
    7. uncertainty.py              -> uncertainty.xlsx
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))

MODULES = [
    "data_preprocess",
    "q1_model",
    "q2_extremum_fitter",
    "q3_full_spectrum",
    "multi_angle_compare",
    "sensitivity",
    "uncertainty",
]


def main() -> int:
    for name in MODULES:
        mod = importlib.import_module(name)
        print(f"\n=== {name} ===")
        if hasattr(mod, "main"):
            mod.main()
        else:
            print(f"  (no main() in {name}; skipped)")
    print("\nAll done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
