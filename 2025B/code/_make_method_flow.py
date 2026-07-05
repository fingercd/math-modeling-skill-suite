"""Generate a simple modeling-flow diagram for the paper."""
from __future__ import annotations

from common import _matplotlib_setup  # noqa: F401
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mp

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=160)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")

BOX = dict(boxstyle="round,pad=0.5", facecolor="#cfe2ff", edgecolor="#1f3a68", lw=1.5)
DEC = dict(boxstyle="round,pad=0.5", facecolor="#fff2cc", edgecolor="#9c6f00", lw=1.5)
END = dict(boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#1e6f3a", lw=1.5)


def box(x, y, w, h, text, style=BOX):
    rect = mp.FancyBboxPatch((x - w / 2, y - h / 2), w, h, **style)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=9,
            color="#1f3a68", fontweight="bold")


def arr(x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#333", lw=1.4))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, label,
                fontsize=8, color="#333", ha="center", va="center",
                bbox=dict(boxstyle="round", fc="white", ec="none", alpha=0.7))


# Row 1
box(10, 80, 17, 9, "原始 4 份 CSV\n(附件 1--4)")
box(36, 80, 17, 9, "小波去噪\n(sym8, level=6)")
box(62, 80, 17, 9, "极值点定位\n(+1D 残差扫描)", style=DEC)
box(88, 80, 17, 9, "TMM/Airy\n全谱拟合", style=DEC)

# Row 2
box(28, 50, 22, 10, "Drude--Sellmeier\n折射率 $n(\\nu,N)$")
box(72, 50, 22, 10, "双角度一致性\n(10° / 15°)")

# Row 3 (results)
box(15, 20, 18, 9, "Q1 闭式公式", style=END)
box(50, 20, 18, 9, "Q2 SiC 厚度\n$\\bar d = 7.44 \\pm 0.04$ μm", style=END)
box(85, 20, 18, 9, "Q3 多光束修正\n(Si: $d \\approx 6.7$ μm)", style=END)

# Connections
arr(18.5, 80, 27.5, 80)
arr(44.5, 80, 53.5, 80)
arr(70.5, 80, 79.5, 80)
arr(36, 75.5, 28, 55, "供 $n$")
arr(62, 75.5, 72, 55)
arr(28, 45, 15, 24)
arr(50, 45, 50, 24)
arr(72, 45, 85, 24)

ax.text(50, 95, "整体建模流程图",
        ha="center", fontsize=13, fontweight="bold", color="#1f3a68")
fig.tight_layout()
fig.savefig(FIG / "method_flow.png", dpi=160)
plt.close(fig)
print("figures/method_flow.png written.")
