# v2 测试 prompt · 2024 高教社杯 C 题 · 农作物的种植策略

> 第二轮 skill v2.0 压力测试。被测 agent 必须独立读完本 prompt，**不要再问任何中间问题**。

---

## 0. 你（被测 agent）现在要做什么

完整作答 **2024 年高教社杯 C 题"农作物的种植策略"**，按本仓库 skill 套件 **`math-modeling-suite` v2.0**（`VERSION=2.0.0`）的六阶段状态机从阶段 1 走到阶段 6。

每阶段回复开头标注：`(全网广泛调研)` / `(建模思路与论文框架)` / `(论文撰写与代码开发)` / `(实验结果汇总确认)` / `(独立审查)` / `(最终交付归档)`，中文圆括号。

完成后给一段简短交付清单 + `git log --oneline | head -30`。

---

## ⚠️ 红线提示（你正在被独立测试）

**你正在被独立测试，本 prompt 写得直接。**

1. **禁止搜这道原题的任何完整题解、最优论文、官方答案**——你被允许搜的方向只有：
   - 通用算法：MILP（pulp / gurobi）、贪心、GA、PSO、PPO、Transformer 序列生成
   - 通用优化：桶排序、动作空间压缩、约束规划
   - 行业常识：农业农村部种植推荐、运筹学教材案例
   - 通用公式：整数规划模型、随机扰动、蒙特卡洛

   **禁止搜的范围**（明确）：
   - `2024 高教社杯 C 题` `农作物种植策略 题解` `2024 CUMCM C solved` `2024C 优秀论文`
   - GitHub 仓库 `Pydoge-x/CUMCM-2024-C` `Gua927/CUMCM2024-C` `Elysia415/CUMCM2024-C` `ArrebolBlack/CUMCM2024_C`（这些是上轮已知公开题解）
   - 任何包含"农作物 1082 动作空间"、"贪心 GA 9359 万元"等上轮特定数值的网页
   - 公开题解中报告的实际利润数字（3761 / 9359 / 5224 / 6458 等）

2. **你可以下载官方附件**——附件不是题解，是真实数据。下载成功后**在 `research/research.md` 的 `Data Provenance` 段写明下载路径、文件大小、行数**；**禁止**把它当作"答案"。

3. **不允许编造利润数字**——所有数字必须来自 code 真实跑出。如果你只跑贪心，论文必须诚实写"贪心结果，未跑 GA/RL 对比"；如果你跑 GA 对比，必须在论文 §7 给出对比表与差距解释。**禁止凭直觉写 9359 万 / 1224 万这种对不齐证据的数字。**

4. **Git 提交必须真做**——v2.0 的阶段门禁强制 stage commit。

5. **不允许模拟"用户回话"**——你无权说"用户已审批"。所有决策落地 MD。

---

## 1. 必须用的文件与目录

skill 仓库根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/`

读：
- `VERSION` / `CHANGELOG.md`
- `math-modeling-suite/SKILL.md`、`math-modeling-research/-writer/-code/-review/SKILL.md`
- `references/stage-gates.md`（含 2.0 检查点）
- `references/cumcm-2026-notes.md`、`references/review-checklist.md`、`references/model-method-map.md`
- `templates/cumcm/main.tex`（v2.0：XeLaTeX + SimSun + hidelinks + `\setstretch{1.25}` + 多路径图搜索）
- `templates/project/.gitignore`（已复制到项目根 `.gitignore`）
- `templates/outputs/{README-template.md,manifest-template.md}`、`templates/stage-files/{research,writer,code,review}.md`
- `templates/contracts/{result_contract,constraint_checks,figure_manifest}.template.json`
- `scripts/validate_project_delivery.py` & `scripts/run_regression_checks.py`

项目根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/2024C_v2/`

源/交付分层：`paper/main.tex` 写作源；`outputs/main.tex` 交付副本。

---

## 2. 六阶段硬要求

### 阶段 1 · `(全网广泛调研)`
1. 读 `2024C_v2/problem.md` & `../2024C/problem.md`。
2. 必须下载（或诚实地说明下载失败并合成）附件 1/2/3。推荐从 arXiv / 中国知网镜像等一般渠道走。
3. `research/research.md` 字段：`Status / Problem And Direction / Data Provenance (含 82 vs 54 差异) / Search Log / Sources / Candidate Routes / Rejected Ideas / Next Gate`。
4. 跑至少 3 类检索、留真链接。
5. 退出前 `git status --short` 摘要 + `stage(1)` commit + 记录 SHA。
6. 严禁把禁止搜的范围用作证据来源。

### 阶段 2 · `(建模思路与论文框架)`
1. `paper/main.tex` 用 v2.0 模板，按 CUMCM 框架：
   - 摘要 / 问题重述 / 问题分析 / 模型假设（至少 6 条 H，**含 H6 "C2 vs C8 互斥"**）/ 符号说明 / 数据处理 / 模型建立与求解 / 结果分析 / 灵敏度 / 评价与推广 / 参考文献 / 附录
2. 占位图：命名固定 `figures/{modeling_workflow,profit_heatmap,q1_strategy,q2_robust_path,q3_intercropping,sensitivity,basebuffer_sensitivity}.{png,pdf}`
3. `paper/writer.md` + `code/code.md` 写代码任务清单 + 数据契约 + 输入输出 schema。
4. `code/code.md` 必须含 2 种算法对比计划（如贪心 vs GA）。
5. stage(2) commit。

### 阶段 3 · `(论文撰写与代码开发)`
1. Python 脚本至少：`code/{preprocess,data_structure,objective,check_constraints}.py` + `code/algo/{greedy,ga}.py` + `code/{q1_run,q2_run,q3_run,plot_results,run_all}.py`。
2. 至少实现两种算法（如桶排序贪心 + GA / PSO），并在 `outputs/result_contract.json` 写两种结果与差距百分比。
3. 全局 `SEED=20240905`。
4. matplotlib 中文：`plt.rcParams['font.sans-serif']=['SimHei','Microsoft YaHei',...]`。
5. **Q3 必须诚实**：(a) 豆类强制间作；(b) 价格弹性折扣；(c) 在论文 §7 写出对 Q2 的提升幅度 + 解释机制。
6. Q1 子问 1 子问 2 数值结果必须在论文摘要显眼位置；论文里"问题分析"段必须坦白附件 54 行 vs 题面 82 块地差异。
7. stage(3) commit。

### 阶段 4 · `(实验结果汇总确认)`
1. 跑全套（`run_all.py`）两次以确认可复现。
2. `outputs/result_summary.xlsx`、`result_contract.json`、`figure_manifest.json`、`constraint_checks.json` 全部生成。
3. `constraint_checks.json` 必须校验 13 类约束（至少 C1 面积 / C2 水浇地 / C3 轮作 / C7 智慧大棚 / C10 普通大棚），无违反才通过。
4. baseline buffer 灵敏度扫描（buffer ∈ {0.5, 0.8, 1.0, 1.2, 1.5, 2.0}）：在论文 §灵敏度分析 写。
5. tag `stage4-results`。
6. stage(4) commit。

### 阶段 5 · `(独立审查)`
1. **独立**宣言。读 `references/review-checklist.md` + 跑 `scripts/run_regression_checks.py` + 跑 `scripts/validate_project_delivery.py --project 2024C_v2`。
2. 评级 CRITICAL / MAJOR / MINOR / STYLE，含 file:line。
3. CRITICAL/MAJOR 不关闭禁 stage 6。
4. `paper/review_report.md` 落地。
5. stage(5) commit。

### 阶段 6 · `(最终交付归档)`
1. `outputs/` 内必备：`main.tex`、`main.pdf`（缺失要显眼披露）、`README.md`、`manifest.md`、`AI_USAGE.md`、`git-log.txt`、`git-status-final.txt`、`SHA256SUMS.txt`、三份 contract、4 张 result*.xlsx + `result_summary.xlsx`。
2. 编译：`cd 2024C_v2/outputs && xelatex -interaction=nonstopmode main.tex`。
3. `manifest.md` 写：`paper/main.tex` SHA、`outputs/main.tex` SHA、PDF 页数、若豁免了什么 CRITICAL/MAJOR 写明原因。
4. stage(6) commit。

---

## 3. v2.0 阶段 MD 必含字段

```
- 阶段 MD 已更新
- git status --short 摘要
- stage commit SHA
- 数据来源 + AI 披露状态
- CRITICAL/MAJOR 关闭状态
```

## 4. 合规与硬底线

- 论文 / 代码 / 表格 / 压缩包**不出现** 学校、姓名、队号、赛区、邮箱、队伍编号
- `AI_USAGE.md` 诚实声明
- 论文正文 ≤ 30 页
- 摘要 = 模型 + 方法 + 关键结果 + 结论

---

读到这里，请用 5 行内回我"开始阶段 1"再继续执行。
