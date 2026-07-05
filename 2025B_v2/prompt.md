# v2 测试 prompt · 2025 高教社杯 B 题 · SiC 外延层厚度反演

> 第二轮 skill v2.0 压力测试。被测 agent 必须独立读完本 prompt，**不要再问任何中间问题**。

---

## 0. 你（被测 agent）现在要做什么

完整作答 **2025 年高教社杯 B 题"碳化硅外延层厚度反演"**，按本仓库 skill 套件 **`math-modeling-suite` v2.0**（`VERSION=2.0.0`）的六阶段状态机从阶段 1 走到阶段 6。

每阶段回复开头标注：`(全网广泛调研)` / `(建模思路与论文框架)` / `(论文撰写与代码开发)` / `(实验结果汇总确认)` / `(独立审查)` / `(最终交付归档)`。

完成后给一段简短交付清单 + `git log --oneline | head -30`。

---

## ⚠️ 红线提示（你正在被独立测试）

**你正在被独立测试，本 prompt 写得直接。**

1. **禁止搜这道原题的任何完整题解、最优论文、官方答案**——你被允许搜的方向只有：
   - 通用物理：单次反射/透射干涉、Fabry-Perot 多光束、Airy 函数
   - 通用光学模型：Sellmeier / Drude / TMM 传输矩阵、椭偏数据反演
   - 行业常识：Filmetrics / KLA-Tencor / SENTECH 商业厚度量测原理（只作背景）
   - 数值方法：小波去噪、差分进化、闭式间距 + 一维残差扫描

   **禁止搜的范围**（明确）：
   - `2025 高教社杯 B 题` `SiC 外延层 题解` `2025 CUMCM B solved` `2025B 论文`
   - GitHub 仓库 `Skyler-Luo/CUMCM2025-B` `caufande/cumcm-2025-b` `KaiDecker/CUMCM-2025-B` `Chang-Liu6/CUMCM2025`
   - 任何包含"碳化硅 TMM 7.44 µm"、"极值法 6.57 µm RMSE 18%" 等上轮特定数值的网页
   - 公开题解中报告的最终厚度数字

2. **附件下载**：你可以**下载附件**（附件不是题解）。下载成功后**必须在 `research/research.md` 的 `Data Provenance` 段写明**：URL、文件大小、SHA256、行数、波数范围；若下载失败，合成数据并写明合成方法。

3. **Sellmeier / Drude 系数**：
   - 你**禁止**复读 GitHub 上的 Skyler-Luo `SIC_COEFFS` 占位系数当作真值使用
   - 你**必须**在 `research/research.md` 的 `Data Provenance` 段写明：你的 Sellmeier 系数从哪来（教材 / Palik / 自由合成 / 占位）
   - 若是占位，论文 §9（局限）必须诚实承认
   - `outputs/result_contract.json` 必须记录系数取值

4. **Git 提交必须真做**——v2.0 的阶段门禁强制 stage commit。

5. **不允许模拟"用户回话"**——你无权说"用户已审批"。所有决策落地 MD。

6. **Q2 与 Q3 之间必须选一个作为最终答案**——上轮没给出选择判据是最大缺陷。本轮 v2.0 prompt 强制要求。

---

## 1. 必须用的文件与目录

skill 仓库根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/`

读：
- `VERSION` / `CHANGELOG.md`
- 5 个 `math-modeling-*/SKILL.md`
- `references/stage-gates.md`（含 2.0 检查点）
- `references/cumcm-2026-notes.md`、`references/review-checklist.md`、`references/model-method-map.md`
- `templates/cumcm/main.tex`（v2.0：XeLaTeX + SimSun + hidelinks + `\setstretch{1.25}` + 多路径图搜索）
- `templates/project/.gitignore`
- `templates/outputs/{README-template.md,manifest-template.md}`、`templates/stage-files/{research,writer,code,review}.md`
- `templates/contracts/{result_contract,constraint_checks,figure_manifest}.template.json`
- `scripts/validate_project_delivery.py` & `scripts/run_regression_checks.py`

项目根：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/2025B_v2/`

源/交付分层：`paper/main.tex` 写作源；`outputs/main.tex` 交付副本。

---

## 2. 六阶段硬要求

### 阶段 1 · `(全网广泛调研)`
1. 读 `2025B_v2/problem.md` & `../2025B/problem.md`。
2. 下载（或合成）4 份附件。下载必须真实，合成必须写明方法。
3. `research/research.md` 字段：`Status / Problem And Direction / Data Provenance (含 Sellmeier 系数来源) / Search Log / Sources / Candidate Routes / Rejected Ideas / Next Gate`。
4. 跑至少 3 类检索 + 真链接 + 失败记录。
5. 退出前 `git status --short` 摘要 + `stage(1)` commit + 记录 SHA。
6. 严禁把禁止搜的范围用作证据来源。

### 阶段 2 · `(建模思路与论文框架)`
1. `paper/main.tex` 用 v2.0 模板，按 CUMCM 框架。
2. 占位图固定：`figures/{raw_spectra,denoised_spectra,raw_vs_denoised,extrema_fit,n_surface,multi_beam_condition,multi_angle_compare,sensitivity,sensitivity_N,tmm_fit,q1_path,method_flow}.{png,pdf}`
3. `code/code.md` 列脚本计划：Q1 公式推导 + 数值验证 / Q2 极值法 + DE 全局 / Q3 TMM 全谱 + 多光束判据 / 多角度比较 / 灵敏度 N 扫描 / 不确定度。
4. stage(2) commit。

### 阶段 3 · `(论文撰写与代码开发)`
1. Python 脚本：`code/common/{constants,sellmeier,drude,optical_path,_matplotlib_setup}.py` + `code/{download_attachments,data_preprocess,q1_model,q2_extremum_fitter,q3_full_spectrum,multi_angle_compare,sensitivity,sensitivity_N,uncertainty,make_result_summary,run_all}.py`。
2. 全局 `SEED=20250705`。
3. matplotlib 中文：`plt.rcParams['font.sans-serif']=['SimHei','Microsoft YaHei',...]`。
4. 小波去噪：wavelet=db4, level=5, threshold=universal。论文 §5 引用。
5. 论文 §7 / §9 必须写"模型选择判据"段，**选 Q2 极值法 或 Q3 TMM 之一作为主推荐**，给出判据与 RMSE / 残差偏度对比。
6. stage(3) commit。

### 阶段 4 · `(实验结果汇总确认)`
1. 跑全套两次验证可复现。
2. `outputs/result_summary.xlsx`、`result_contract.json`、`figure_manifest.json`、`constraint_checks.json`。
3. **N 灵敏度扫描**：N ∈ [1e16, 1e19]（10 个 log 等距点），结果写入 `outputs/sensitivity_N.xlsx` + `figures/sensitivity_N.png`。
4. 多角度一致性：相对差 < 5% 才合格（写在论文 §灵敏度）。
5. tag `stage4-results`。
6. stage(4) commit。

### 阶段 5 · `(独立审查)`
1. **独立**宣言。`references/review-checklist.md` + `scripts/run_regression_checks.py` + `scripts/validate_project_delivery.py --project 2025B_v2`。
2. 评级 CRITICAL / MAJOR / MINOR / STYLE，含 file:line。
3. CRITICAL/MAJOR 不关闭禁 stage 6。
4. `paper/review_report.md` 落地。
5. stage(5) commit。

### 阶段 6 · `(最终交付归档)`
1. `outputs/` 内必备：`main.tex`、`main.pdf`（缺失要显眼披露）、`README.md`、`manifest.md`、`AI_USAGE.md`、`git-log.txt`、`git-status-final.txt`、`SHA256SUMS.txt`、三份 contract、4 张 result*.xlsx + `result_summary.xlsx` + `multi_angle_summary.xlsx` + `sensitivity_N.xlsx` + `uncertainty.xlsx`。
2. 编译：`cd 2025B_v2/outputs && xelatex -interaction=nonstopmode main.tex`。
3. `manifest.md` 写：`paper/main.tex` SHA、`outputs/main.tex` SHA、PDF 页数、Sellmeier/Drude 系数版本与来源、若豁免了什么 CRITICAL/MAJOR 写明原因。
4. stage(6) commit。

---

## 3. v2.0 阶段 MD 必含字段

```
- 阶段 MD 已更新
- git status --short 摘要
- stage commit SHA
- 数据来源（含系数） + AI 披露状态
- CRITICAL/MAJOR 关闭状态
```

## 4. 合规与硬底线

- 论文 / 代码 / 表格 / 压缩包**不出现** 学校、姓名、队号、赛区、邮箱、队伍编号
- `AI_USAGE.md` 诚实声明
- 论文正文 ≤ 30 页
- 摘要 = 模型 + 方法 + 关键结果 + 结论

---

读到这里，请用 5 行内回我"开始阶段 1"再继续执行。
