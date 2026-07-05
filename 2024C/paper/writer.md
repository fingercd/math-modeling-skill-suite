# writer.md

## Status

- Stage: `(建模思路与论文框架)`
- Owner: agent (独立完成)
- Last updated: 2026-07-05
- Current gate: 论文大纲、占位图表、待结果标记已就位；阶段 3 之后填具体数字。

## Confirmed Paper Route

- Selected modeling route:
  - Q1：基于"动作点（地块-作物-季）枚举 + 桶排序贪心"的种植方案优化器，配合 **2023 实际产量**作为各作物基准预期销售量，对子问 1（滞销）与子问 2（50% 降价）分别评估。
  - Q2：在 Q1 基础上加 **蒙特卡洛 500 场景** 模拟 2025–2030 年价格 / 成本 / 产量 ±10% 扰动，取年均利润最大、波动最小方案。
  - Q3：在 Q2 基础上加入 **豆科强制间作 mask**（任意 3 年窗口中每地块至少一季豆类）与 **作物可替代性 / 互补性权重表**（合成假设），并对超产部分按价格弹性折扣计算。
- Sections already drafted: 摘要模板、问题重述、问题分析、模型假设、符号说明、数据处理、模型建立与求解（问题 1/2/3）、结果分析、灵敏度、模型评价、参考文献、附录 — 全部使用模板骨架，待阶段 3 写入具体内容。
- Sections waiting for results: 摘要、结果分析与检验、灵敏度、模型评价中的具体数字。
- Writing style notes: 严肃学术 + 公式 + 表格 + 图，禁用任何队伍 / 学校 / 姓名信息；遵循 CUMCM 2026 默认（无目录、摘要前置、≤30 页）。

## Paper Outline

| Section | Purpose | Current status | Dependencies |
| --- | --- | --- | --- |
| Abstract | methods, results, conclusion | template 待填具体数字 | code/result confirmation |
| 1 问题重述 | 用自己语言重述 | 已写 | problem.md |
| 2 问题分析 | 求解逻辑与模块关系 | 已写 | research.md |
| 3 模型假设 | 列出 5 条假设 + 合理性 | 已写 | model plan |
| 4 符号说明 | 符号表 | 已写 | model plan |
| 5 数据处理与探索 | 附件来源 + 解析 + 修正 | 已写 | code.md |
| 6 模型建立与求解 | 三问模型与算法 | 待代码完成 | code.md |
| 7 结果分析与检验 | 三问核心数字 | 等代码跑完 | code.md |
| 8 灵敏度、误差与稳健性 | Q2 多年波动 | 等代码跑完 | code.md |
| 9 模型评价、改进与推广 | 优缺点 | 待阶段 4 填 | results |
| 参考文献 | 引用公开仓库 | 已占位 | research.md |
| 附录 | 代码 / 附件清单 | 已写 | code.md |

## Figure Placeholders

| Label | Expected file | Caption draft | Source script | Status |
| --- | --- | --- | --- | --- |
| fig:workflow | figures/modeling_workflow.pdf | 整体建模流程图（六阶段状态机 → 数据 → 评估 → 求解 → 结果） | code/plot_workflow.py | placeholder |
| fig:profit_heatmap | figures/profit_heatmap.png | 41 种作物 × 6 类地块的"亩净利润"热力图（用于解释贪心优先级） | code/plot_profit_heatmap.py | placeholder |
| fig:q1_strategy | figures/q1_strategy.png | Q1 两种情形下 7 年累计种植结构对比（堆叠柱状图） | code/plot_q1.py | placeholder |
| fig:q2_robust_path | figures/q2_robust_path.png | Q2 蒙特卡洛 500 场景下年均利润箱线图 + 7 年利润路径 | code/plot_q2.py | placeholder |
| fig:q3_intercropping | figures/q3_intercropping.png | Q3 间作 / 替代机制下 7 年累计种植结构与豆类覆盖占比 | code/plot_q3.py | placeholder |
| fig:sensitivity | figures/sensitivity.png | 关键参数（价格扰动 σ、豆类覆盖阈值、替代弹性）灵敏度 | code/plot_sensitivity.py | placeholder |

## Table Placeholders

| Label | Purpose | Required columns | Source | Status |
| --- | --- | --- | --- | --- |
| tab:notation | 符号说明 | 符号 / 含义 / 单位 | model plan | placeholder |
| tab:data_overview | 数据概览 | 变量 / 单位 / 问题 / 处理 | code.md | placeholder |
| tab:result_summary | 核心结果汇总 | 子问题 / 指标 / 结果值 / 结论 | code.md | waiting |
| tab:constraint_check | 13 类约束执行结果 | 约束编号 / 描述 / 通过率 / 备注 | code.md | waiting |

## Claims Waiting For Confirmation

| Claim | Needed evidence | Owner | Status |
| --- | --- | --- | --- |
| Q1 子问 1 七年累计净利润 ≈ 待结果确认 | code/q1_run.py 输出 | code agent | waiting |
| Q1 子问 2 七年累计净利润 ≈ 待结果确认 | code/q1_run.py 输出 | code agent | waiting |
| Q2 蒙特卡洛 500 场景下年均 / 7 年累计净利润 | code/q2_run.py 输出 | code agent | waiting |
| Q3 间作 + 替代机制下累计净利润与提升幅度 | code/q3_run.py 输出 | code agent | waiting |
| 13 类约束在所有解上 100% 通过 | code/check_constraints.py 输出 | code agent | waiting |

## User Revisions

| Time | Request | Applied to |
| --- | --- | --- |
| 2026-07-05 | "完成阶段 6 后，给我一段简短交付清单 + git log 最后 30 行" | 阶段 6 必交付 |
| 2026-07-05 | "不要问我任何中间问题" | 自主决策写 MD |
| 2026-07-05 | "按 prompt 中定义的工作流独立完整作答" | 严格六阶段状态机 |

## Next Gate

- 进入阶段 3（论文撰写与代码开发）需要的确认：
  1. 论文大纲与占位图表是否符合 CUMCM 评审口味（已自审，OK）；
  2. 候选模型路线（Q1 贪心 / Q2 蒙特卡洛 + 贪心 / Q3 贪心 + 间作 + 替代）已在 research.md 锁定，OK；
  3. 代码模块清单（data_structure / objective / algo/greedy / algo/ga / q1/q2/q3_run / plot_*）已写入 code.md，OK。