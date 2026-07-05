# v2 测试 prompt · 2023 高教社杯 A 题 · 定日镜场优化设计

> 第二轮 skill v2.0 压力测试。被测 agent 必须独立读完本 prompt，**不要再问任何中间问题**。

---

## 0. 你（被测 agent）现在要做什么

完整作答 **2023 年高教社杯 A 题"定日镜场的优化设计"**，按本仓库 skill 套件 **`math-modeling-suite` v2.0**（`VERSION=2.0.0`）的六阶段状态机从阶段 1 走到阶段 6。

每阶段回复**开头必须标注**：`(全网广泛调研)` / `(建模思路与论文框架)` / `(论文撰写与代码开发)` / `(实验结果汇总确认)` / `(独立审查)` / `(最终交付归档)`，中文圆括号。

完成阶段 6 后给一段简短交付清单 + `git log --oneline | head -30`。

---

## ⚠️ 红线提示（你正在被独立测试）

**你正在被独立测试，本 prompt 写得直接。**

1. **禁止搜这道原题的任何完整题解、最优论文、官方答案**——你被允许搜的方向只有：
   - 通用算法：DE / NSGA-II / 蒙特卡洛 / 并行光线追迹
   - 通用物理：太阳高度角、DNI 模型、大气透射率（题目附录已给公式）
   - 行业常识：青海德令哈 / SolarPaces / NREL CSP（只作背景描述，不引用具体数字）

   **禁止搜的范围**（明确）：
   - `2023 高教社杯 A 题` `定日镜场 参考答案` `定日镜场 高教社 优秀论文` `CUMCM 2023 A solved` `2023A 题解`
   - GitHub 仓库 `boa-z/CUMCM-2023-A` 等本轮已知公开题解
   - 任何包含"定日镜场 60 MW 最优解"、"2023A 答辩 PPT"等字样的网页
   - 中文/英文"2023 math contest heliostat field solution"等

2. **不允许模拟"用户回话"**——你无权说"用户已审批"。所有决策落地 MD。

3. **不允许编造"已下载官方附件"**——若 attach 下载失败，按 `research.md` 的 `Data Provenance` 段显式记录"合成数据 + 合成脚本路径"，并在论文致谢/局限性里坦白。

4. **Git 提交必须真做**——v2.0 的阶段门禁强制 stage commit；上轮 2023A 完全没做这步是这次最大失败。

---

## 1. 必须用的文件与目录

skill 仓库根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/`

读：
- `VERSION` / `CHANGELOG.md`（v2.0 改动摘要）
- `math-modeling-suite/SKILL.md`、`math-modeling-research/-writer/-code/-review/SKILL.md`（5 个 skill）
- `references/stage-gates.md`（含 **2.0 阶段检查点**）
- `references/cumcm-2026-notes.md`、`references/review-checklist.md`、`references/model-method-map.md`
- `templates/cumcm/main.tex`（v2.0：XeLaTeX + 字体声明 + `\setstretch{1.25}` + hidelinks + 多路径图搜索）
- `templates/project/.gitignore`（已复制到你项目根 `.gitignore`）
- `templates/outputs/{README-template.md,manifest-template.md}`、`templates/stage-files/{research,writer,code,review}.md`
- `templates/contracts/{result_contract,constraint_checks,figure_manifest}.template.json`
- `scripts/validate_project_delivery.py`（验证交付）& `scripts/run_regression_checks.py`（回归检查）

你的项目根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/2023A_v2/`

目录契约（强制）：
```
research/ paper/ code/ figures/ outputs/ tests/evidence/
```
源/交付分层：`paper/main.tex` 是写作源，`outputs/main.tex` 是交付副本。

---

## 2. 六阶段硬要求（每阶段退出前跑 2.0 阶段检查点）

### 阶段 1 · `(全网广泛调研)`
1. 读 `2023A_v2/problem.md` & `../2023A/problem.md`。
2. `research/research.md` 写：题目拆解、约束清单（≥/≤/=），允许的检索通道、禁止的检索通道、附件/数据 Provenance（自合成 or 下载）、候选方法（含理由）。
3. **必须做至少 3 类检索 + 真链接**（不能全部失败）。失败如实写。
4. 字段：`Status / Problem And Direction / Search Log / Sources / Data Provenance / Candidate Routes / Rejected Ideas / Next Gate`。
5. 退出前 `git status --short` 摘要写进 MD，做 `git add -A && git commit -m "stage(1): research baseline + data provenance + candidate routes"`，记录 SHA。
6. 必须无 CUMCM 同题 GitHub 痕迹。如发现，禁止采纳为证据来源。

### 阶段 2 · `(建模思路与论文框架)`
1. 在 `paper/main.tex` 用 v2.0 模板（XeLaTeX）落论文大纲 + 公式 + 图表占位（命名固定：`figures/{q1_monthly_efficiency,q1_annual_summary,q2_layout,q3_mixed_layout,sensitivity,method_flow}.{png,pdf}`）。
2. `paper/writer.md` 写章节状态 + 占位符表 + 待代码确认数字。
3. `code/code.md` 写代码任务清单 + 数据契约 + 输入输出 schema + Reproducibility note。
4. stage(2) commit。

### 阶段 3 · `(论文撰写与代码开发)`
1. Python 脚本至少：`code/common/{astro,monte_carlo,efficiency,field_layout,seeds}.py` + `code/{q1_baseline,q2_uniform_mirror,q3_mixed_mirror,sensitivity,run_all}.py`。
2. 全局 SEED = `20230705`，集中管理。
3. matplotlib 中文：模板已具备，但每个 `.py` 开头仍 `plt.rcParams['font.sans-serif']=['SimHei','Microsoft YaHei',...]` 防兼容。
4. 数值结果**仅来自 code 真实输出**，禁止手填。
5. **Q3 必须满足 ≥60 MW 上限**（v2.0 `constraint_checks.json` 会校）。最佳答案贴近 60 MW。
6. 每问题结束后 `paper/main.tex` 同步，引用 code 数字时写到 `outputs/result_contract.json`。
7. stage(3) commit。

### 阶段 4 · `(实验结果汇总确认)`
1. 重跑全套（`code/run_all.py` + 三个 q 脚本），所有 figures 与 Excel 输出。
2. `outputs/result_summary.xlsx` + `outputs/result_contract.json` 校验每张表里数字与 TeX 一致。
3. `outputs/figure_manifest.json` 校验每个 `\includegraphics{...}` 都对应真实文件。
4. `outputs/constraint_checks.json` 校验每条题面约束。
5. **Q3 必须 ≤ 100 MW（≥60 且接近 60）** + 在论文里"灵敏度分析"段写明 DE 收敛曲线 / 候选淘汰表。
6. 打 tag `stage4-results`。
7. stage(4) commit。

### 阶段 5 · `(独立审查)`
1. **独立**：必须新开会话或显式声明"进入独立审查，不再持有阶段 1-4 思维"。
2. 用 `references/review-checklist.md` + `scripts/run_regression_checks.py` + `scripts/validate_project_delivery.py --project 2023A_v2` 三重核对。
3. 输出分 CRITICAL / MAJOR / MINOR / STYLE，**含 file:line 引用**。
4. CRITICAL/MAJOR 未关闭**禁止**进 stage 6。
5. `paper/review_report.md` 至少修一遍，附 `code-review` 链接/讨论行。
6. stage(5) commit。

### 阶段 6 · `(最终交付归档)`
1. 必须从 `outputs/` 内部验证：`main.tex`、`main.pdf`（缺失必须显眼披露）、`README.md`、`manifest.md`、`git-log.txt`、`git-status-final.txt`、`SHA256SUMS.txt`、`result_contract.json`、`constraint_checks.json`、`figure_manifest.json`、4 张 result*.xlsx + `result_summary.xlsx`、`AI_USAGE.md`、`code/`、`figures/`。
2. `outputs/main.tex` 必须能独立编译成功（用 XeLaTeX）。图搜索路径顺序已对 paper/outputs 都生效。
3. `paper/main.tex` 字节可与 `outputs/main.tex` 不同——paper 是源，outputs 是副本。
4. `manifest.md` 写：`paper/main.tex` SHA、`outputs/main.tex` SHA、`main.pdf` 是否已编译、PDF 页数、若豁免了什么 CRITICAL/MAJOR 写明原因。
5. stage(6) commit，结束。

---

## 3. v2.0 阶段 MD 必含字段（每阶段退出前自查）

```
- 当前阶段 MD 已更新
- git status --short 摘要
- stage commit SHA（或"未提交 + 原因"）
- 数据来源 + AI 披露状态
- CRITICAL/MAJOR 关闭状态
```

---

## 4. 合规与硬底线

- 论文 / 代码 / 表格 / 压缩包**不出现** 学校、姓名、队号、赛区、邮箱、队伍编号
- `AI_USAGE.md` 诚实声明用了 Claude / Code / Claude Code 等工具
- 论文正文 ≤ 30 页
- 摘要 = 模型 + 方法 + 关键结果 + 结论，不是背景

---

## 5. 编译命令提示

```
cd 2023A_v2/paper && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
cd 2023A_v2/outputs && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```

模板 `\setCJKmainfont{SimSun}` 在 TeXLive 2024 自带。

---

读到这里，请用 5 行内回我"开始阶段 1"再继续执行。
