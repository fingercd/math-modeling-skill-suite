# code.md

## Status

- Stage: `(建模思路与论文框架)`
- Owner: agent (独立完成)
- Last updated: 2026-07-05
- Current gate: 代码模块清单已就位；阶段 3 落实具体脚本。

## Environment

- Python version: 3.12.12 (C:/Users/lenovo/anaconda3/envs/pytorch/python.exe)
- Main packages: openpyxl, pandas, numpy, matplotlib, pulp (备用)
- Random seed: 42（蒙特卡洛场景生成）
- Excel files used for records:
  - `research/attachments_raw/fujian1.xlsx` — 地块 54 行 + 作物 41 行
  - `research/attachments_raw/fujian2.xlsx` — 2023 实际种植 + 统计 125 行
  - `research/attachments_raw/fujian3.xlsx` — 7 张年份模板
  - 阶段 6 之前会复制到 `code/data/attachments.xlsx`（合并 3 个 sheet），代码只读这个文件

## Data Inventory

| File | Description | Columns/schema | Issues | Handling |
| --- | --- | --- | --- | --- |
| fujian1.xlsx / 乡村的现有耕地 | 54 块地 | 地块名称 / 地块类型 / 地块面积 | problem.md 描述 "82" 是错的；以附件为准（54） | 直接用 |
| fujian1.xlsx / 乡村种植的农作物 | 41 种作物 | 作物编号 / 名称 / 类型 / 种植耕地 | 种植耕地是含换行的字符串 | 解析为 allowed_plots set |
| fujian2.xlsx / 2023 实际种植 | 87 行 | 地块 / 编号 / 名称 / 类型 / 亩数 / 季次 | 部分地块只种一季 | 用于 baseline 对比与历史产量基线 |
| fujian2.xlsx / 2023 统计 | 125 行 | 编号 / 名称 / 类型 / 地块类型 / 季 / 亩产量 / 成本 / 单价区间 | **缺预期销售量** | 用 2023 实际产量作 baseline + 20% buffer 作 max |
| fujian3.xlsx | 7 张年份模板 | 行=地块+季 / 列=41 种作物 | 行=地块+季 混排 | 我们改输出长表 (地块,年,季,作物,亩数) |

## Scripts

| Script | Purpose | Inputs | Outputs | Status |
| --- | --- | --- | --- | --- |
| code/preprocess.py | 解析 3 个 xlsx → 内部 dict | research/attachments_raw/*.xlsx | code/data/processed.json | planned |
| code/data_structure.py | 压缩动作空间：(地块,作物,季) 三元组 | code/data/processed.json | code/data/action_space.json | planned |
| code/objective.py | 评估函数：净利润 = 收入 - 成本，处理超产 / 50% 降价 | action_space + 价格 + 成本 + 销售量上限 | 单 (地块,作物,季) 的边际利润 | planned |
| code/algo/greedy.py | 桶排序贪心：按"剩余预期销售量"扣减，按边际利润填 | action_space + 2023 baseline 销售量 | dict[(i,j,s,t)] = 亩数 | planned |
| code/algo/ga.py | 遗传算法交叉验证（种群 50，代数 100） | 同上 | 同上 | planned |
| code/q1_run.py | Q1 两个子问 | processed.json + objective + greedy | outputs/result1_1.xlsx, result1_2.xlsx + 利润数字 | planned |
| code/q2_run.py | Q2 蒙特卡洛 500 场景 + 贪心 | 同上 + 扰动 | outputs/result2.xlsx + 7 年累计 + 波动 | planned |
| code/q3_run.py | Q3 间作 + 替代弹性 | 同上 + 合成替代矩阵 | outputs/result3.xlsx + 提升幅度 | planned |
| code/check_constraints.py | 13 类约束校验 | 任一输出 xlsx | 控制台通过率报告 | planned |
| code/plot_workflow.py | 流程图 | 无 | figures/modeling_workflow.pdf | planned |
| code/plot_profit_heatmap.py | 亩利润热力图 | objective | figures/profit_heatmap.png | planned |
| code/plot_q1.py | Q1 堆叠柱状图 | result1_*.xlsx | figures/q1_strategy.png | planned |
| code/plot_q2.py | Q2 箱线图 + 路径 | result2.xlsx + 场景结果 | figures/q2_robust_path.png | planned |
| code/plot_q3.py | Q3 间作覆盖 | result3.xlsx | figures/q3_intercropping.png | planned |
| code/plot_sensitivity.py | 灵敏度 | q1/q2/q3 输出 | figures/sensitivity.png | planned |

## Experiments

| ID | Script | Parameters | Metric | Result | Output files | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| E001 | q1_run.py | 子问 1 滞销 | 7 年累计净利润 | 待结果确认 | result1_1.xlsx | greedy baseline |
| E002 | q1_run.py | 子问 2 50% 降价 | 7 年累计净利润 | 待结果确认 | result1_2.xlsx | greedy baseline |
| E003 | q2_run.py | 500 场景 σ=0.10 | 年均 / 累计 / 波动 | 待结果确认 | result2.xlsx | 蒙特卡洛 |
| E004 | q3_run.py | 豆类 3 年覆盖 + 替代矩阵 | 7 年累计净利润 + 提升 % | 待结果确认 | result3.xlsx | 间作机制 |
| E005 | check_constraints.py | 13 类 | 通过率 | 待结果确认 | 控制台 | 校验 |
| E006 | plot_*.py | — | — | — | 6 张图 | 阶段 4 锁定 |

## Autotuning Record

| Model | Parameter grid | Best params | Best metric | Decision |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

## Paper-Facing Results

| Subquestion | Result | Figure/table | Reproducibility note | Confirmed? |
| --- | --- | --- | --- | --- |
| Q1 子问 1 | 待结果确认 | fig:q1_strategy, tab:result_summary | `python q1_run.py --mode waste` | no |
| Q1 子问 2 | 待结果确认 | 同上 | `python q1_run.py --mode discount` | no |
| Q2 | 待结果确认 | fig:q2_robust_path | `python q2_run.py --n 500 --sigma 0.10` | no |
| Q3 | 待结果确认 | fig:q3_intercropping | `python q3_run.py` | no |

## Failed Attempts

| Time | Attempt | Failure | Lesson |
| --- | --- | --- | --- |
| 2026-07-05 | 用 82 块地的描述跑规划 | 与附件 54 行不符 | 以附件为唯一真源 |

## Next Gate

- 阶段 3 落地时必须保证：
  1. 所有脚本能用 `python q1_run.py` 等命令独立运行；
  2. 数值结果可复现（固定种子 42）；
  3. 输出 xlsx 必须能填进 fujian3 模板对应的 7 张 sheet 结构；
  4. 所有图表文件名与 writer.md / main.tex 引用一致。