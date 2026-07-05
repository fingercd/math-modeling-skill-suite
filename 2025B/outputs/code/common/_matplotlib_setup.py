"""Central matplotlib font setup for CJK glyphs.

Every plotting module imports this first so the figures actually render the
Chinese characters instead of falling back to ".notdef" boxes.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path


def _register_cjk() -> None:
    candidates = [
        r"C:/Windows/Fonts/msyh.ttc",
        r"C:/Windows/Fonts/msyhbd.ttc",
        r"C:/Windows/Fonts/simhei.ttf",
        r"C:/Windows/Fonts/simsun.ttc",
    ]
    chosen = []
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            chosen.append(path)
    if not chosen:
        return
    name = font_manager.FontProperties(fname=chosen[0]).get_name()
    plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False


_register_cjk()
