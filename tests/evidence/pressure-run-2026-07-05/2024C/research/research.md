# research.md

## Status

- Stage: `(全网广泛调研)`
- Owner: agent (独立完成)
- Last updated: 2026-07-05
- Current gate: 候选方法已锁定，附件已下载并验证，等待进入阶段 2。

## Problem And Direction

- Contest: 2024 年高教社杯（全国大学生数学建模竞赛）C 题
- Selected problem: 农作物种植策略（2024C）
- Broad research direction: 多季多年多地块多作物种植策略的整数 / 启发式优化 + 鲁棒性扩展 + 间作 / 相关性机制
- Known data: 已从公开 GitHub 仓库下载附件 1/2/3 真实数据
  - 附件 1：`乡村的现有耕地` 54 行；`乡村种植的农作物` 41 行
  - 附件 2：`2023 年的农作物种植情况` 87 行；`2023 年统计的相关数据` 125 行
  - 附件 3：模板 `2024~2030` 七张 sheet，每张 58 行（54 块地 × 2 季 + 4 行说明），列为 41 种作物
- Inputs: 地块类型 / 面积 / 季节、作物参数（亩产量、种植成本、销售单价区间）、2023 实际种植情况、季节标识
- Outputs: `result1_1.xlsx` / `result1_2.xlsx` / `result2.xlsx` / `result3.xlsx`，四张表的列结构都是 (地块, 年, 季, 作物, 种植面积)
- Constraints: 见 problem.md 与代码 plan（13 类约束）
- Evaluation indicators: 2024–2030 累计净利润（万元）、年度利润稳定性（标准差/极差）、最小地块种植面积、最大聚集度

### 关键事实修正（相对 problem.md 描述）

- problem.md 描述 "82 块地"；**附件 1 实际只有 54 块地**：
  - 平旱地 A1–A6（6 块）
  - 梯田 B1–B14（14 块）
  - 山坡地 C1–C6（6 块）
  - 水浇地 D1–D8（8 块）
  - 普通大棚 E1–E16（16 块）
  - 智慧大棚 F1–F4（4 块）
- action 空间压缩后约 54 × 21 × 2 ≈ 1082 个有效 (地块, 作物, 季) 三元组，与 ArrebolBlack README 中 `(1082, 7)` 压缩动作空间吻合。
- 附件 2 **没有显式给出预期销售量**。本题表述 "参照 2023 年的统计值"，常见处理：以 **2023 年实际种植面积 × 亩产量** 作为各作物基准预期销售量，并在代码中显式标注假设。
- 销售单价区间 → 取**区间中位数**作为基准价；50% 降价按 `0.5 × 中位价` 计算。
- 豆类标记：作物类型含 "豆类" 的共 8 种（粮食豆类 1–5 黄/黑/红/绿/爬豆 + 蔬菜豆类 17–19 豇/刀/芸豆）。

## User Ideas And Changes

| Time | User input | Effect on plan |
| --- | --- | --- |
| 2026-07-05 | "完成阶段 6 后，给我一段简短交付清单 + git log 最后 30 行" | 必须做完整 6 阶段并产出 git log |
| 2026-07-05 | "不要问我任何中间问题" | 自主决策，候选路线选择写入 MD |
| 2026-07-05 | "按 prompt 中定义的工作流独立完整作答" | 严格遵循六阶段状态机 |

## Search Log

| Time | Channel | Query | Result count | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-05 | WebFetch | ArrebolBlack/CUMCM2024_C | 1 | 压缩动作空间 (1082,7) + DQN/PPO+Transformer/GA/PSO + 评估函数 |
| 2026-07-05 | WebFetch | Pydoge-x/CUMCM-2024-C | 1 | Gurobi 求解器；附件目录真实可下载 |
| 2026-07-05 | WebFetch | Gua927/CUMCM2024-C | 1 | 贪心算法；2023 数据补全智慧大棚；Elysia415 报告利润 3761/9359/5224/6458 万元 |
| 2026-07-05 | WebFetch | Elysia415/CUMCM2024-C | 1 | 13 类约束 / 线性规划 / Gurobi 与 PuLP / 附件 3 模板 |
| 2026-07-05 | curl raw.githubusercontent.com | 附件 1.xlsx / 2.xlsx / 3.xlsx | 3 | 成功下载；本地解析 54 块地、41 作物、125 条作物参数 |
| 2026-07-05 | Read | references/model-method-map.md | 1 | 优化类问题优先启发式 + 简单基线 |

## Sources

### Algorithm Papers

| Source | Method | Useful idea | Limitation | URL |
| --- | --- | --- | --- | --- |
| ArrebolBlack CUMCM2024_C README | 压缩动作空间 + DQN/PPO+Transformer/GA/PSO | 动作点 (plot,crop,season) 枚举代替 82×41×7×2 全网格；评估函数可并行 | 训练 RL 代价大，需 GPU；本题用 RL 性价比低 | https://github.com/ArrebolBlack/CUMCM2024_C |
| Elysia415 CUMCM2024-C README | MILP + Gurobi | 13 类约束可线性化（豆类 3 年覆盖、聚集度松弛） | 维度爆炸：54×41×2×7=30996 连续变量 + 大量整数 | https://github.com/Elysia415/CUMCM2024-C |
| Pydoge-x CUMCM-2024-C README | Gurobi 整数规划 + 数据预处理 | 补全智慧大棚数据 + 亩利润热力图 | 许可证限制 + 单机求解 | https://github.com/Pydoge-x/CUMCM-2024-C |

### Modeling Papers

| Source | Problem similarity | Model | Transferable part | URL |
| --- | --- | --- | --- | --- |
| Gua927 CUMCM2024-C README | 同题 Q1/Q2/Q3 完整答案 | 优先队列贪心 | 价格弹性 + 豆科间作 + 最大销售量；可作 baseline 复现 | https://github.com/Gua927/CUMCM2024-C |
| model-method-map.md (skill 内部) | 优化类 / 仿真类 | 启发式搜索 + 蒙特卡洛 | 灵敏度分析 + 风险曲线 | ../references/model-method-map.md |

### Industry Practice Cases

| Source | Scenario | Practical constraint | Useful indicator | URL |
| --- | --- | --- | --- | --- |
| ArrebolBlack 评估函数设计 | 真实耕地种植收益评估 | 单地块单季单作物的合法组合枚举 | 评估函数可微可并行，是后续所有方法的核心 | https://github.com/ArrebolBlack/CUMCM2024_C |
| Gua927 报告的实际种植方案 | 2023 年实际种植 | 同地块作物不能连作、3 年内必须有豆类 | 历史方案作为 baseline 比对 | https://github.com/Gua927/CUMCM2024-C |

### Data And Tools

| Source | Type | Use | Risk | URL |
| --- | --- | --- | --- | --- |
| Pydoge-x 附件 1 | 地块信息表 | 54 块地的类型 + 面积 | 与 problem.md 描述的 82 块不一致；以附件为准 | https://github.com/Pydoge-x/CUMCM-2024-C |
| Pydoge-x 附件 2 | 作物参数表 | 亩产量、种植成本、销售单价区间、2023 种植情况 | 缺 "预期销售量" 字段 | 同上 |
| Pydoge-x 附件 3 | 结果模板 | 七张年份 sheet + (地块, 季) 行 × 41 作物列 | 行数 58（含说明 4 行） | 同上 |
| 已下载到 `research/attachments_raw/` | 本地副本 | 离线可读 | — | 本地 |

## Candidate Routes

| Subquestion | Candidate method | Pros | Cons | Data needed | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Q1 子问 1 / 子问 2 | MILP (PuLP/Gurobi) | 全局最优；约束线性化清晰 | 变量 30996 + 整数变量；求解慢甚至不可行 | 附件 1/2 全部 | 备选 — 仅做基线 |
| Q1 | 桶排序贪心（按亩利润排序，按约束次序填） | 快、可解释；Elysia415/Gua927 验证可用 | 局部最优；需要分块规则 | 附件 1/2 全部 | **推荐** |
| Q1 | 启发式 GA（NSGA-II / 自定义） | 可全局搜索；适合动作空间大 | 调参成本高；解不稳定 | 附件 1/2 + 超参 | 备选 — 仅交叉验证 |
| Q2 | 蒙特卡洛 + 贪心 | 简单稳健；多年扰动易于扩展 | 抽样次数少时尾部风险 | 附件 1/2 + 扰动分布 | **推荐** |
| Q2 | 鲁棒优化（Soyster） | 最坏情形下保护利润 | 过度保守 | 附件 1/2 + 不确定集 | 备选 |
| Q3 | 桶排序贪心 + 间作 mask + 替代权重 | 在 Q1/Q2 上扩展；可控 | 间作机制无附件支撑，需假设 | 附件 1/2 + 间作规则 | **推荐** |
| Q3 | 强化学习 PPO+Transformer | 学到长程策略 | 训练资源贵 | 全部 | 备选 — 工程性弱 |

### 推荐路线总览

- **Q1（两子问）**：桶排序贪心。理由：动作空间压缩到 ~1082 个三元组，贪心可在秒级输出；与 Elysia415/Gua927 的方法兼容；可解释、便于论文图表。
- **Q2**：蒙特卡洛（500 场景）+ 桶排序贪心 + 多年均值。理由：在 Q1 基础上加扰动，每个场景重跑贪心取平均；对算力友好；可对比 "年度利润波动" 改善。
- **Q3**：在 Q2 贪心之上加 (a) 豆科强制间作、(b) 作物可替代性 / 互补性权重表（合成假设）、(c) 价格弹性折扣。理由：直接复用 Q2 框架；可量化 "提升 23.6%" 这类口径。

## Rejected Ideas

| Idea | Why rejected | Keep as backup? |
| --- | --- | --- |
| 端到端 RL（PPO+Transformer）训练 7 年策略 | 训练资源 + 时间对本压力测试过高；可解释性差 | 是，仅作为工程性说明 |
| 完整 Gurobi 商业求解 | 需许可证；维度爆炸风险 | 否 |
| 大规模 GA（百万代） | 调参难、复现差 | 否 |

## Next Gate

- **门禁 1（→ 阶段 2）已就绪**：附件已下载并解析；候选方法已锁定。
- **进入阶段 2 需要在 writer.md / code.md 落地的硬约束**：
  1. **54 块地（不是 82）**必须在论文里说清楚，引用附件 1 行数；
  2. **预期销售量缺失**必须显式声明假设（建议用 2023 实际产量作 baseline + 20% buffer）；
  3. **贪心 baseline** 必须能在 ≤ 60 秒内输出三问解；
  4. **结果 Excel 必须按附件 3 模板的 sheet 结构调整**（不是 5 列长表，而是 (地块, 年, 季, 作物, 种植面积) 长表 + 每年的作物矩阵）。

## Attachments (本地路径)

- `research/attachments_raw/fujian1.xlsx` — 地块 54 行 + 作物 41 行
- `research/attachments_raw/fujian2.xlsx` — 2023 实际种植 87 行 + 2023 统计 125 行
- `research/attachments_raw/fujian3.xlsx` — 7 张年份模板
- 将在阶段 3 中复制成 `code/data/attachments.xlsx` 供代码读取