"""Wavelet denoising + spectrum cropping for the 4 attachments.

Pipeline:
    raw CSV -> drop leading-zero segment -> wavelet denoise (universal thr)
              -> write denoised CSV -> plot raw vs denoised.
"""
from __future__ import annotations

from pathlib import Path

from common import _matplotlib_setup  # noqa: F401  (registers fonts first)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

WAVELET = "sym8"
LEVEL = 6
NU_MIN = 400.0
NU_MAX = 4000.0


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = ["nu_cm", "R_pct"]
    return df


def crop_band(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df.nu_cm >= NU_MIN) & (df.nu_cm <= NU_MAX)].copy()
    df = df.sort_values("nu_cm").reset_index(drop=True)
    return df


def wavelet_denoise(y: np.ndarray, wavelet: str = WAVELET, level: int = LEVEL) -> np.ndarray:
    coeffs = pywt.wavedec(y, wavelet=wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    thr = sigma * np.sqrt(2 * np.log(len(y)))
    coeffs[1:] = [pywt.threshold(c, thr, mode="soft") for c in coeffs[1:]]
    return pywt.waverec(coeffs, wavelet=wavelet)[: len(y)]


def process_one(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    raw = load_csv(path)
    crop = crop_band(raw)
    y = crop.R_pct.values.astype(float)
    y_dn = wavelet_denoise(y)
    df_dn = crop.copy()
    df_dn["R_pct"] = y_dn
    res = y - y_dn
    return raw, df_dn, res


def plot_all(results: dict[str, tuple[pd.DataFrame, pd.DataFrame, np.ndarray]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for ax, (name, (raw, dn, _)) in zip(axes.ravel(), results.items()):
        ax.plot(raw.nu_cm, raw.R_pct, color="#888888", lw=0.6, label="原始")
        ax.plot(dn.nu_cm, dn.R_pct, color="#1f77b4", lw=1.0, label="去噪")
        ax.set_title(name)
        ax.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
        ax.set_ylabel("反射率 (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("四份附件原始/去噪反射率对比")
    fig.tight_layout()
    fig.savefig(FIG / "raw_vs_denoised.png", dpi=160)
    plt.close(fig)

    # Combined overlay
    fig2, ax2 = plt.subplots(1, 1, figsize=(11, 5))
    colours = {"附件1": "#d62728", "附件2": "#1f77b4", "附件3": "#2ca02c", "附件4": "#9467bd"}
    labels = {"附件1": "SiC 10°", "附件2": "SiC 15°", "附件3": "Si 10°", "Si 15°": "附件4"}
    # fix label mapping
    labels = {"附件1": "SiC 10°", "附件2": "SiC 15°", "附件3": "Si 10°", "附件4": "Si 15°"}
    for name, (_, dn, _) in results.items():
        ax2.plot(dn.nu_cm, dn.R_pct, color=colours[name], lw=1.1, label=labels[name])
    ax2.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
    ax2.set_ylabel("反射率 (%)")
    ax2.set_title("四份附件去噪后光谱对比")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")
    fig2.tight_layout()
    fig2.savefig(FIG / "denoised_spectra.png", dpi=160)
    plt.close(fig2)

    # raw_spectra (no denoise)
    fig3, ax3 = plt.subplots(1, 1, figsize=(11, 5))
    for name, (raw, _, _) in results.items():
        ax3.plot(raw.nu_cm, raw.R_pct, color=colours[name], lw=0.6, label=labels[name])
    ax3.set_xlabel("波数 $\\tilde{\\nu}$ (cm$^{-1}$)")
    ax3.set_ylabel("反射率 (%)")
    ax3.set_title("四份附件原始光谱")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="best")
    fig3.tight_layout()
    fig3.savefig(FIG / "raw_spectra.png", dpi=160)
    plt.close(fig3)


def main() -> None:
    results: dict[str, tuple[pd.DataFrame, pd.DataFrame, np.ndarray]] = {}
    summary = []
    for name in ["附件1", "附件2", "附件3", "附件4"]:
        path = DATA / f"{name}.csv"
        raw, dn, res = process_one(path)
        dn.to_csv(DATA / f"denoised_{name}.csv", index=False)
        rmse = float(np.sqrt(np.mean(res**2)))
        summary.append((name, len(dn), float(rmse)))
        results[name] = (raw, dn, res)
    plot_all(results)
    print("| 附件 | 行数 (去噪) | 去噪残差 RMSE (%) |")
    print("| --- | --- | --- |")
    for name, n, r in summary:
        print(f"| {name} | {n} | {r:.4f} |")
    print("figures: figures/raw_spectra.png, denoised_spectra.png, raw_vs_denoised.png")


if __name__ == "__main__":
    main()
