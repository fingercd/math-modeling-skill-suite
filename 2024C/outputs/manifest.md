# manifest.md — 输出物字段说明

## 论文

- `main.tex` — CUMCM 风格 TeX 论文, ≤ 30 页正文, 含摘要 / 问题重述 / 问题分析 / 模型假设 (H1–H6) / 符号说明 / 数据处理 / 模型建立与求解 / 结果分析与检验 / 灵敏度 / 模型评价 / 参考文献 / 附录。

## 数据 Excel (附件 3 模板格式)

每个 xlsx 包含 7 张 sheet, 命名 `2024` ... `2030`, 每张 sheet:
- 列: `季次 | 地块名 | 黄豆 | 黑豆 | ... | 羊肚菌` (43 列, 41 种作物 + 季次 + 地块名)
- 行: 每块地 × 2 季 = 108 行, 加上 3 行说明 = 111 行
- 单元格值: 种植面积 (亩), 浮点数; 无种植则为 `None`

| 文件 | 含义 |
| --- | --- |
| `result1_1.xlsx` | Q1 子问 1 (waste, 滞销) |
| `result1_2.xlsx` | Q1 子问 2 (discount, 50% 折价) |
| `result2.xlsx` | Q2 (蒙特卡洛 best 场景) |
| `result3.xlsx` | Q3 (间作 + 弹性 best 场景) |
| `result_summary.xlsx` | 汇总: 三问数字 + 约束校验 (2 sheet) |

## 长表 CSV

`result*_long.csv` 字段: `地块, 地块类型, 年, 季, 作物编号, 作物名称, 种植面积(亩)`

## 场景 CSV

`result*_scenarios.csv` 字段: `scenario, profit_wan` (蒙特卡洛每场景的 7 年累计净利润)

## JSON 汇总

- `q1_summary.json` — `{waste_profit_wan, discount_profit_wan}`
- `result2_summary.json` — `{n_scenarios, sigma, mode, mean_wan, std_wan, min_wan, max_wan, median_wan, cv}`
- `result3_summary.json` — 同上, mode="elastic+legume_cover"
- `ga_validation.json` — `{ga_profit_wan, greedy_profit_wan, gap_percent, ga_actions, greedy_actions}`
- `constraint_check.json` — `{文件: {forced_passed, forced_total, details}}`

## 代码 (code/)

| 脚本 | 用途 |
| --- | --- |
| `preprocess.py` | 附件 1/2 xlsx → processed.json |
| `data_structure.py` | 动作空间压缩 (1062 个三元组) |
| `objective.py` | 评估函数 (waste / discount / elastic) |
| `algo/greedy.py` | 桶排序贪心 + 间作补丁 |
| `algo/ga.py` | GA 交叉验证 |
| `q1_run.py` | 问题 1 求解 |
| `q2_run.py` | 问题 2 蒙特卡洛 |
| `q3_run.py` | 问题 3 间作 + 弹性 |
| `check_constraints.py` | 13 类约束校验 |
| `plot_results.py` | 6 张图生成 |
| `result_summary.py` | 汇总到 result_summary.xlsx |

## 图 (figures/)

| 文件 | 内容 |
| --- | --- |
| `modeling_workflow.pdf` | 整体建模流程图 |
| `profit_heatmap.png` | 41 作物 × 6 地块类型的亩净利润热力图 |
| `q1_strategy.png` | Q1 两子问 7 年累计种植结构对比 |
| `q2_robust_path.png` | Q2 蒙特卡洛场景利润分布 + 升序排列 |
| `q3_intercropping.png` | Q3 豆类覆盖占比 |
| `sensitivity.png` | σ 灵敏度扫描 (均值 + CV) |