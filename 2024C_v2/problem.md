# 2024 年高教社杯全国大学生数学建模竞赛 C 题 · v2 复跑版

> 第二轮 skill v2.0 压力测试。本目录在题面层面与 `../2024C/problem.md` 等价；本轮新增约束以 prompt.md 为准。

## v2 本轮特别提醒（来自上轮现场复审）

1. **附件真实性**：题面与 `problem.md` 都描述"82 块地块"。**实际官方附件仅 54 块**——本轮 v2.0 要求在 `research/research.md` 的 `Data Provenance` 段写清楚"以附件为准、题面与附件差异"。**禁止修改题面以迁就附件**；强制提醒：在 `outputs/manifest.md` 与论文摘要显眼标注差异。
2. **数值目标档次**：上轮跑出 1106 / 940 / 953 / 1224 万元（4 个数字），**比公开优秀论文低一个数量级**。本轮 v2.0 prompt 强制要求：(a) 至少跑两种算法对比（贪心 + 启发式/RL），(b) `outputs/result_contract.json` 写两种算法的结果差距并解释，(c) 论文 §7 必须有"算法选择判据"。
3. **中文字体**：v2.0 模板自带 `\setCJKmainfont{SimSun}` + XeLaTeX；论文/figures 全部按 XeLaTeX 编译。
4. **结果追溯**：每张 result*.xlsx + 论文表格的数字必须在 `outputs/result_contract.json` 里追溯到 code 路径 + 随机种子 + 参数。

## 题面核心要点（与上轮一致）

乡村 82 块地块（官方附件 54 行）/ 41 种农作物 / 2024-2030 七年规划。

三种处理：
- 销售量、价格、成本、产量参照 2023 年稳定
- 每季总产量超销售：超过部分 (a) 滞销浪费 或 (b) 按 50% 降价
- Q1：两种处理分别给七年最优方案 → `result1_1.xlsx` / `result1_2.xlsx`
- Q2：引入 ± 10% 随机扰动，求鲁棒七年方案 → `result2.xlsx`
- Q3：加豆科强制间作 + 价格弹性 + 替代/互补权重 → `result3.xlsx`

13 类约束见 `../2024C/problem.md`（与本目录等价）。

## 提交物（v2.0 Directory Contract + 5 个 contract JSON）

```
2024C_v2/outputs/
  main.tex + main.pdf
  README.md
  manifest.md
  AI_USAGE.md
  git-log.txt
  git-status-final.txt
  SHA256SUMS.txt
  result_contract.json      # 必备：每数字追溯
  constraint_checks.json    # 必备：13 类约束校验
  figure_manifest.json      # 必备：图引用
  result1_1.xlsx
  result1_2.xlsx
  result2.xlsx
  result3.xlsx
  result_summary.xlsx
  code/
  figures/
```

## v2.0 强约束

- 每阶段 commit；CRITICAL/MAJOR 不关闭禁 stage 6
- `outputs/main.pdf` 缺失必须显眼披露
- 论文正文 ≤ 30 页；匿名；AI_USAGE.md
- 中文字体用模板自带 SimSun + XeLaTeX
