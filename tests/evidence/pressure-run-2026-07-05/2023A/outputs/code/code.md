# code.md

## Status

- Stage: `(建模思路与论文框架)` → `(论文撰写与代码开发)`
- Owner: agent
- Last updated: 2026-07-05
- Current gate: 已列脚本清单与契约;等待阶段 3 实现并落地真实数字

## Environment

- Python version: 3.12.12
- Main packages: numpy, pandas, openpyxl, matplotlib, scipy(均为常见科学计算栈;无 GPU)
- Random seed: 全局 `SEED = 20230705`,在 `common/seeds.py` 中集中管理
- Excel files used for records: outputs/result1.xlsx / result2.xlsx / result3.xlsx / result_summary.xlsx

## Data Inventory

| File | Description | Columns/schema | Issues | Handling |
| --- | --- | --- | --- | --- |
| outputs/heliostats_baseline.csv | 自合成 1745 面 6×6 / 4 m 安装高度的镜面坐标 | x, y, h, width, height | 无真实附件 | radial-stagger 自合成 |
| outputs/heliostats_q2.csv | Q2 优化后镜面坐标 | 同上 | DE 输出 | DE 输出 |
| outputs/heliostats_q3.csv | Q3 异构后镜面坐标 | x, y, h, width, height, mirror_class | DE 输出 | DE 输出 |
| outputs/result1.xlsx | Q1 月表 + 年表 | month, eta, E_field_MW, E_A_Wpm2 | 待跑 | pandas.to_excel |
| outputs/result2.xlsx | Q2 参数 + 月表 + 年表 | 同上 + tower_x/tower_y/mirror_size/height/N | 待跑 | pandas.to_excel |
| outputs/result3.xlsx | Q3 参数 + 月表 + 年表 | 同上 + mirror_class | 待跑 | pandas.to_excel |
| outputs/result_summary.xlsx | 三问 + 灵敏度汇总 | subq, metric, value, source | 待跑 | pandas.to_excel |

## Scripts

| Script | Purpose | Inputs | Outputs | Status |
| --- | --- | --- | --- | --- |
| code/common/seeds.py | 全局随机种子 | — | — | planned |
| code/common/astro.py | 太阳高度/方位/时角/赤纬/DNI | φ, λ, H, month, day, hour | α_s, γ_s, DNI | planned |
| code/common/monte_carlo.py | 单面镜 MC 反射 → η_trunc;邻镜投影遮挡 → η_sb | mirror, sun, target, neighbors | eta_trunc, eta_sb | planned |
| code/common/field_layout.py | 自合成 radial-stagger 镜场 + KDTree | R=350, d_min=镜宽+5 | heliostats_baseline.csv | planned |
| code/common/efficiency.py | 单面镜光学效率 η 全链路装配 | mirror, sun, tower, target | eta dict | planned |
| code/q1_baseline.py | Q1 60 时点 × 1745 面镜场年均指标 | heliostats_baseline.csv, 60 时点 | result1.xlsx, q1_monthly_efficiency.png, q1_annual_summary.png | planned |
| code/q2_uniform_mirror.py | DE 优化均匀镜场到 60 MW | 60 时点,DE 参数 | result2.xlsx, q2_layout.png, q2_convergence.png | planned |
| code/q3_mixed_mirror.py | 离散混合编码 DE 优化异构镜场 | 60 时点,离散集合 | result3.xlsx, q3_mixed_layout.png, q3_convergence.png | planned |
| code/sensitivity.py | 关键参数扰动(η_ref / 安装高度 / 集热器直径 / 锥形角) | DE 输出 | sensitivity.png, sensitivity.xlsx | planned |
| code/mc_bias_check.py | 截断/阴影 MC 采样数 N 偏差曲线 | N ∈ {50,100,200,400,800,1600} | mc_sample_bias.png | planned |
| code/run_all.py | 一键跑全套 + 校验 | — | 全部 outputs | planned |

## Experiments

| ID | Script | Parameters | Metric | Result | Output files | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| E000 | code/mc_bias_check.py | SEED=20230705, N=400 | MC 偏差 | — | figures/mc_sample_bias.png | 验证 MC 收敛 |
| E001 | code/q1_baseline.py | DEFAULTS | η, E_field, E_A | — | result1.xlsx, q1_*.png | Q1 |
| E002 | code/q2_uniform_mirror.py | pop=60, gen=200, SEED | E_A (max) | — | result2.xlsx, q2_layout.png, q2_convergence.png | Q2 |
| E003 | code/q3_mixed_mirror.py | pop=80, gen=200, SEED | E_A (max) | — | result3.xlsx, q3_mixed_layout.png, q3_convergence.png | Q3 |
| E004 | code/sensitivity.py | 5 维网格 | ΔE_A | — | sensitivity.png | 灵敏度 |

## Autotuning Record

| Model | Parameter grid | Best params | Best metric | Decision |
| --- | --- | --- | --- | --- |
| DE | pop∈{40,60,80,100}, F∈{0.5,0.7,0.9}, CR∈{0.7,0.9} | 待跑 | E_A | 暂用 pop=60/80, F=0.7, CR=0.9 起步 |

## Paper-Facing Results

| Subquestion | Result | Figure/table | Reproducibility note | Confirmed? |
| --- | --- | --- | --- | --- |
| Q1 | — | tab:q1-monthly / tab:q1-annual / fig:q1-* | code/q1_baseline.py | no |
| Q2 | — | tab:q2-* / fig:q2-* | code/q2_uniform_mirror.py | no |
| Q3 | — | tab:q3-* / fig:q3-* | code/q3_mixed_mirror.py | no |
| 灵敏度 | — | tab:sensitivity / fig:sensitivity | code/sensitivity.py | no |

## Failed Attempts

| Time | Attempt | Failure | Lesson |
| --- | --- | --- | --- |
| 2026-07-05 | curl 直连 GitHub 拉附件 | HTTP 451 | 改用自合成 |
| 2026-07-05 | WebSearch 默认通道 | API 400 | 改用 WebFetch 抓 arXiv |

## Next Gate(进入阶段 3 自评)

- ✅ 脚本清单与契约完整
- ✅ 数据契约(列名/文件路径)与 paper/writer.md 占位符一致
- ✅ 随机种子策略统一
- ✅ 阶段 3 开始实现代码,阶段 4 出真实数字

进入阶段 3。