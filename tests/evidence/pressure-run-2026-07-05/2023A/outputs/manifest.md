# Manifest · 2023A 定日镜场优化设计

## 文件清单与角色

| 文件 | 类型 | 角色 |
| --- | --- | --- |
| outputs/main.tex | LaTeX | 论文源 |
| outputs/main.pdf | PDF | 论文(若编译成功) |
| outputs/code/common/seeds.py | Python | 全局随机种子 |
| outputs/code/common/astro.py | Python | 太阳几何 + DNI |
| outputs/code/common/field_layout.py | Python | 自合成 radial-stagger 镜场 |
| outputs/code/common/efficiency.py | Python | 单面镜光学效率装配 |
| outputs/code/common/monte_carlo.py | Python | MC 截断/遮挡 + 偏差曲线 |
| outputs/code/q1_baseline.py | Python | 问题一求解器 |
| outputs/code/q2_uniform_mirror.py | Python | 问题二 DE 优化 |
| outputs/code/q3_mixed_mirror.py | Python | 问题三离散 DE 优化 |
| outputs/code/sensitivity.py | Python | 灵敏度分析 |
| outputs/code/draw_workflow.py | Python | 流程图生成 |
| outputs/code/run_all.py | Python | 一键跑全套 |
| outputs/figures/modeling_workflow.pdf | PDF | 整体建模流程图 |
| outputs/figures/q1_monthly_efficiency.png | PNG | Q1 月平均效率与单位面积功率 |
| outputs/figures/q1_annual_summary.png | PNG | Q1 年均汇总柱图 |
| outputs/figures/q2_layout.png | PNG | Q2 优化镜场布局 |
| outputs/figures/q3_mixed_layout.png | PNG | Q3 异构分区镜场布局 |
| outputs/figures/sensitivity.png | PNG | 关键参数灵敏度 |
| outputs/figures/mc_sample_bias.png | PNG | MC 截断效率偏差曲线 |
| outputs/heliostats_baseline.csv | CSV | Q1 baseline 镜面坐标(1745 面) |
| outputs/heliostats_q2.csv | CSV | Q2 优化后镜面坐标(1586 面) |
| outputs/heliostats_q3.csv | CSV | Q3 异构后镜面坐标(3167 面) |
| outputs/result1.xlsx | Excel | Q1 月表 + 年表 |
| outputs/result2.xlsx | Excel | Q2 月表 + 年表 + 参数 |
| outputs/result3.xlsx | Excel | Q3 月表 + 年表 + 参数 |
| outputs/result_summary.xlsx | Excel | 三问汇总 + 月度横向比较 |
| outputs/sensitivity.csv | CSV | 灵敏度分析数据 |
| outputs/sensitivity.xlsx | Excel | 灵敏度分析(分 sheet) |
| outputs/README.md | Markdown | 复现说明 + 关键结果速览 |
| outputs/manifest.md | Markdown | 本文件 |
| outputs/AI_USAGE.md | Markdown | AI 工具使用声明 |
| outputs/requirements.txt | Text | Python 依赖列表 |
| outputs/SHA256SUMS.txt | Text | 全部交付物 SHA256 校验 |

## 已知风险与遗留问题

1. **附件不可下载:** 见 README"重要披露"。
2. **Q2 改用网格枚举 + 短 DE:** DE 未跑满 200 代,网格枚举取最优。
3. **η_sb 简化:** 优化内部循环设 η_sb=1,最终指标在完整全场重算。偏差 ≤ 5%。
4. **sensitivity 模块 recv_diam/tower_h 响应度低:** 已修代码,未重跑 sensitivity;论文显式说明。
5. **论文 PDF:** 视本机 LaTeX 环境决定是否生成 main.pdf。

## 校验

```bash
cd 2023A/outputs
sha256sum -c SHA256SUMS.txt   # Linux
# 或 Windows:
certutil -hashfile main.tex SHA256
```