"""画整体建模流程图(modeling_workflow.pdf)。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "figures", "modeling_workflow.pdf")
OUT = os.path.normpath(OUT)

fig, ax = plt.subplots(figsize=(8.6, 9.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 14)
ax.axis("off")

nodes = [
    (5, 13, "题目输入:60 时点 + 几何/塔参数", "#cfe2ff"),
    (5, 11.5, "太阳几何:α_s, γ_s(罗盘) · DNI", "#fff3cd"),
    (5, 10, "单镜效率 5 项:η_sb · η_cos · η_at · η_ref · η_trunc", "#d1e7dd"),
    (2.7, 8.2, "Q1\n给定 1745 面\nradial-stagger", "#f8d7da"),
    (5.2, 8.2, "Q2\nDE/rand/1/bin\n(w, h_in, n_rings)", "#f8d7da"),
    (7.7, 8.2, "Q3\n离散混合 DE\n3 圈区 × (w,h,ρ)", "#f8d7da"),
    (5, 6.4, "全场 60 时点聚合 → 月表 / 年表", "#cfe2ff"),
    (5, 4.8, "Excel 输出 + figures/*.png", "#fff3cd"),
    (5, 3.4, "灵敏度分析(η_ref / 高度 / 直径 / 塔高)", "#d1e7dd"),
    (5, 1.8, "独立审查与最终交付", "#f8d7da"),
]
for (x, y, label, color) in nodes:
    box = FancyBboxPatch((x - 1.6, y - 0.55), 3.2, 1.1,
                          boxstyle="round,pad=0.06,rounding_size=0.18",
                          linewidth=1.2, edgecolor="#222", facecolor=color)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=9.5)

# 主箭头
def arrow(xy_from, xy_to, color="#0d6efd"):
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle="->",
                                  mutation_scale=18, lw=1.5, color=color))

arrow((5, 12.45), (5, 12.05))
arrow((5, 10.95), (5, 10.55))
arrow((5, 9.5), (5, 8.85))
arrow((2.7, 7.65), (2.7, 6.95))
arrow((5.2, 7.65), (5.2, 6.95))
arrow((7.7, 7.65), (7.7, 6.95))
arrow((5, 5.85), (5, 5.35))
arrow((5, 4.25), (5, 3.95))
arrow((5, 2.85), (5, 2.35))

ax.set_title("整体建模与求解流程", fontsize=13)
fig.tight_layout()
fig.savefig(OUT, format="pdf", bbox_inches="tight")
plt.close(fig)
print(f"saved -> {OUT}")