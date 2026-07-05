# 复审报告 · 2026-07-05 · 三题 + skill

## A. 现场复盘表

| # | 问题 | 你的判定 | 证据 |
|---|------|---------|------|
| 1 | 2023A 是否真没做 stage(1..6) commit | 成立 | `git -C ... log --oneline -- 2023A` 仅返回 `11dd8a7 test(2023A): scaffold ...`；`git -C ... status --short -- 2023A` 显示 `research/research.md`、`paper/main.tex`、`code/*.py`、`outputs/*` 全为 `??` 未跟踪。 |
| 2 | 三道题 `paper/main.tex` 与 `outputs/main.tex` 字节是否真相同 | 成立 | `sha256sum`：2023A 两份均为 `4c770586...77c03`；2024C 两份均为 `7eaad466...44bb`；2025B 两份均为 `1620fde0...301`。这证明 outputs 不是独立可复现构建结果，而是字节级复制。 |
| 3 | 2025B 是否真没有 `outputs/main.pdf` | 成立 | PowerShell 文件检查：`2025B\outputs\main.pdf Exists=False`，但 `2025B\paper\main.pdf Exists=True Length=2341702`。`2025B/outputs/README.md:74-76` 还让用户在 outputs 内运行 XeLaTeX，但交付目录没有 PDF。 |
| 4 | 2023A Q3=124 MW 是否真违反 60 MW 约束 | 部分成立 | `2023A/paper/main.tex:22`、`:276`、`:304`、`:319` 均出现 Q3 `124.04 MW`，`2023A/research/research.md:23-24` 把 Q2/Q3 写成 `60 MW 约束`，`:143` 又写年均功率 `>= 60 MW`。若按“至少 60 MW”解释，124 MW 不算数学上违反；若按“60 MW 额定设计”解释，124 MW 严重过建。当前论文没有解释为何允许远超额定，且 Q3 `E_A=988.32` 低于 Q2 `2423.08`，却仍作为 Q3 优化方案，属于目标函数/约束口径未闭合。 |
| 5 | 2024C 利润是否真比公开论文低 | 成立，归因需更精确 | `2024C/outputs/result_summary.xlsx` 首表显示 Q1 waste `1106.79`、discount `940.05`、Q2 `953.84 ± 354.40`、Q3 `1224.01 ± 369.7` 万元；同值见 `2024C/outputs/result_summary.csv:2-5`、`2024C/paper/main.tex:190-194`。公开对比数在 `2024C/research/research.md:52` 写为 `Elysia415 报告利润 3761/9359/5224/6458 万元`，并非完全是 Gua927 直接报告；但“本地结果比公开优秀/复杂方案低一个数量级或至少显著偏低”成立。 |
| 6 | 2025B Q2/Q3 厚度差 12% 是否真实且论文是否给出选哪个 | 厚度差成立；“论文没给判据”在最终稿不成立 | `2025B/paper/review_report.md:41` 明确 `6.57 µm` 与 `7.44 µm` 有约 `12%` 偏差；`2025B/paper/main.tex:298-300` 列 Q2 `7.444`、Q2 TMM `6.57`、Q3 Si `6.71`。但最终 `2025B/paper/main.tex:348-356` 已新增“模型选择判据”，明确 `Q2 极值法 —— 主推荐`、`Q3 TMM-FP —— 辅参考`。 |
| 7 | matplotlib 中文字体是否真在 figures 里变成了方框 | 成立，证据来自审查自承 | 未重新渲染图片；静态证据是 `2024C/paper/review_report.md:54-59` 自承 `[MINOR-1] 图表中文显示为方框`，原因是 matplotlib 默认 DejaVu Sans 不含中文字形，并给出 SimHei/Microsoft YaHei 修复建议。 |
| 8 | hyperref 蓝色框是否真在论文最后一页出现 | 部分成立 | 三份 TeX 均只有 `\usepackage{hyperref}` 而无 `\hypersetup`，见 `2023A/paper/main.tex:5`、`2024C/paper/main.tex:5`、`2025B/paper/main.tex:5`；日志显示 `Package hyperref Info: Link coloring OFF`，如 `2023A/paper/main.log:731`、`2024C/paper/main.log:486`。这通常意味着默认链接边框风险存在。未通过视觉渲染确认“最后一页蓝框”，但模板缺省确实没有禁止边框。 |
| 9 | 2024C/2025B `__pycache__` 是否真入库 | 不成立；存在但被忽略 | `Get-ChildItem` 显示 `2024C/code/__pycache__`、`2024C/code/algo/__pycache__`、`2025B/code/__pycache__` 存在；但 `git ls-files` 无输出，`git status --ignored --short` 显示 `!!`，且根 `.gitignore:1-3` 已忽略 `__pycache__/` 和 `*.pyc`。不过 `2023A/.gitignore:1-57` 是 agent 自创且重复规则，这个“分题自创 .gitignore”问题成立。 |
| 10 | review 自报修补是否真完成 | 成立 | `2023A/paper/review_report.md:60-61` 写“代码已改,但未重跑 sensitivity”，`:93-94` 又建议进入 stage 6；`2024C/paper/review_report.md:98-114` 列“阶段 6 前修补”后直接说可进入交付；`2025B/paper/review_report.md:129-139` 明确“不进入 stage 6”，但 `git log --all --oneline` 随后有 `1922df2 stage(6): final delivery...`。审查与修补闭环没有被门禁强制。 |

补充现场发现：

- 2023A 和 2024C 均有非干净 LaTeX 编译日志：`2023A/paper/main.log:1168`、`:1222` 是 `LaTeX Error`；`2024C/paper/main.log:874` 是 `Something's wrong--perhaps a missing \item`，`:948-955` 仍要求 rerun。Skill 目前只要求“最终 PDF”，没有要求编译日志无错误/关键 warning。
- 2024C 对 54/82 的差异在摘要中已显眼说明，见 `2024C/paper/main.tex:22-23`、`:47`、`:80`；原“public summary 没显眼说明”对最终论文不成立，但它说明 skill 仍需要“附件差异必须进入摘要/README/manifest”的硬规则。

## B. Skill 缺陷归纳

### B.1 `math-modeling-suite/SKILL.md`

- 问题1：阶段机只说用户许可切换，未把每阶段 git checkpoint 写入门禁。位置：`math-modeling-suite/SKILL.md:19`、`:42-50`；现场证据：2023A 只有脚手架 commit。
- 修复1：

```diff
diff --git a/math-modeling-suite/SKILL.md b/math-modeling-suite/SKILL.md
@@
 Advance only when the user expresses approval or intent to continue...
+
+## Stage Checkpoint Gate
+
+Before leaving any stage:
+- Run `git status --short` and record it in the current stage MD.
+- Commit all required stage artifacts, unless the user explicitly disables git.
+- The commit message must start with the stage label, for example `(全网广泛调研) ...`.
+- If required artifacts remain untracked or modified, do not enter the next stage; report the blocking file list.
+- Stage 6 must export `outputs/git-log.txt` and `outputs/git-status-final.txt`.
```

- 问题2：outputs 契约只说“从 outputs 组装”，未说明 source-of-truth 和可编译关系。位置：`math-modeling-suite/SKILL.md:21-31`、`:66-78`；现场证据：三题 `paper/main.tex` 与 `outputs/main.tex` hash 相同，2025B 缺 `outputs/main.pdf`。
- 修复2：

```diff
diff --git a/math-modeling-suite/SKILL.md b/math-modeling-suite/SKILL.md
@@
 Do not automatically search scattered files when packaging delivery...
+
+## Source And Delivery Contract
+
+`paper/main.tex` is the editable source of truth before final delivery.
+In `(最终交付归档)`, copy the final source to `outputs/main.tex`, copy all referenced figures to `outputs/figures/`, then compile or verify `outputs/main.tex` from inside `outputs/`.
+The delivery is not complete unless either `outputs/main.pdf` exists and matches the final TeX, or `outputs/README.md` states why PDF compilation is unavailable.
+Never leave `paper/` and `outputs/` as two silent competing truths; record the copy time, source commit, and SHA256 in `outputs/manifest.md`.
```

### B.2 `references/stage-gates.md`

- 问题：阶段产物表没有“git 状态、验证命令、失败即阻断”的列。位置：`references/stage-gates.md:32-37`、`:39-50`。
- 修复：

```diff
diff --git a/references/stage-gates.md b/references/stage-gates.md
@@
 ## 阶段产物
 
 | 阶段 | 必交付内容 | 记录文件 | 不允许提前做 |
@@
 | 最终交付归档 | `outputs/README.md`, `outputs/manifest.md`, 最终文件 | `outputs/manifest.md` | 从散落文件自动搜集未确认材料 |
+
+## 阶段退出校验
+
+每阶段退出前必须完成：
+1. `git status --short` 无本阶段必交付文件的未跟踪/未提交变化。
+2. 当前阶段 MD 写明本阶段产物、验证命令和遗留风险。
+3. 有阶段 commit，commit message 以阶段标签开头。
+4. 若阶段 5 发现 CRITICAL/MAJOR 且未修复，必须回到阶段 3/4；不得直接进入阶段 6。
+5. 阶段 6 必须在 `outputs/` 下完成 TeX 编译验证、文件引用验证、SHA256 清单和 final git status 记录。
```

### B.3 `math-modeling-writer/SKILL.md`

- 问题：虽然声明“不默认目录”，但缺少生成后 lint；2023A/2025B 实际生成了 `\tableofcontents`。位置：`math-modeling-writer/SKILL.md:29`、`templates/cumcm/main.tex:5-9`。
- 修复：

```diff
diff --git a/math-modeling-writer/SKILL.md b/math-modeling-writer/SKILL.md
@@
 Do not add a table of contents by default...
+
+Before any paper is marked ready, grep `paper/main.tex` for forbidden unresolved template artifacts:
+- `\\tableofcontents`
+- `待填写`, `待确认`, `TODO`, `placeholder`
+- figure filenames that do not exist under `figures/`
+Record the grep result in `paper/writer.md`.
```

- 问题：缺少编译日志质量门禁。现场证据：2023A/2024C PDF 存在但 log 有 `LaTeX Error`。位置：`math-modeling-writer/SKILL.md:71-73`。
- 修复：

```diff
diff --git a/math-modeling-writer/SKILL.md b/math-modeling-writer/SKILL.md
@@
 Before final writing, check `code/code.md`...
+
+Final paper readiness also requires a clean LaTeX check:
+- compile from `paper/` during drafting and from `outputs/` during delivery;
+- fail the gate on `! LaTeX Error`, missing figures, undefined citations/labels after the final rerun, or absent final PDF;
+- save the compile command and log summary in `paper/writer.md` and `outputs/manifest.md`.
```

### B.4 `templates/cumcm/main.tex`

- 问题：模板缺字体/行距/链接边框处理，且 `\graphicspath{{../figures/}{figures/}}` 在 outputs 内优先找错目录。位置：`templates/cumcm/main.tex:1-9`。
- 修复：

```diff
diff --git a/templates/cumcm/main.tex b/templates/cumcm/main.tex
@@
-\documentclass[UTF8,a4paper,12pt]{ctexart}
+\documentclass[UTF8,a4paper,12pt,fontset=windows]{ctexart}
 \usepackage{geometry}
 \usepackage{amsmath,amssymb,booktabs,graphicx,float}
 \usepackage{caption,subcaption}
 \usepackage{hyperref}
 \usepackage{enumitem}
 \usepackage{longtable}
+\usepackage{setspace}
 \geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}
-\graphicspath{{../figures/}{figures/}}
+\graphicspath{{figures/}{../figures/}}
+\setstretch{1.25}
+\hypersetup{
+  hidelinks,
+  pdfborder={0 0 0}
+}
@@
 \begin{document}
 \maketitle
 \thispagestyle{plain}
```

说明：当前模板本身没有 `\tableofcontents`，原“模板默认带目录”对当前文件不成立；问题是 agent 生成的三题 TeX 偏离模板，因此需要 writer lint。

### B.5 `math-modeling-code/SKILL.md`

- 问题：只要求每个论文结果记录脚本和复现说明，缺少机器可核对的 result contract / constraint contract。位置：`math-modeling-code/SKILL.md:46-60`、`:73-83`；现场证据：2023A Q3 124 MW、2024C 贪心低结果、2025B 6.57/7.44 分歧都依赖人工发现。
- 修复：

```diff
diff --git a/math-modeling-code/SKILL.md b/math-modeling-code/SKILL.md
@@
 Every paper-facing result must include script name...
+
+Additionally write machine-readable contracts:
+- `outputs/result_contract.json`: each paper-facing number, unit, source script, source output file, parameters, and timestamp.
+- `outputs/constraint_checks.json`: each problem constraint, expected relation, observed value, pass/fail, and source script.
+- `outputs/figure_manifest.json`: every figure used by TeX, generating script, SHA256, and caption.
+Stage 4 cannot pass if any core result lacks a contract or any hard constraint is `fail`/`unknown`.
```

- 问题：没有强制统一 `.gitignore` 与缓存清理。现场证据：2024C/2025B pycache 未入库但存在；2023A 自创重复 `.gitignore`。
- 修复：

```diff
diff --git a/math-modeling-code/SKILL.md b/math-modeling-code/SKILL.md
@@
 Write outputs to `figures/`...
+
+At project creation, create one project-level `.gitignore` from the suite template.
+Do not create per-problem ad hoc duplicate `.gitignore` files unless the user asks.
+Before each commit, remove or ignore `__pycache__/`, `*.pyc`, LaTeX aux/log files, virtual environments, and local scratch files.
```

### B.6 `math-modeling-review/SKILL.md`

- 问题：审查独立性是文字要求，不是操作门禁；agent 自审后继续修补/交付。位置：`math-modeling-review/SKILL.md:8-14`、`:69`。
- 修复：

```diff
diff --git a/math-modeling-review/SKILL.md b/math-modeling-review/SKILL.md
@@
 Act as an independent reviewer...
+
+Operational isolation requirements:
+- Prefer a fresh Codex thread/window or a separately spawned reviewer with no prior task messages.
+- The reviewer prompt must include only paths to materials, not the prior solution rationale.
+- The reviewer must not edit files. Any fix returns control to the suite controller in stage 3/4.
+- After fixes, run a second review pass; do not let the same message both fix and approve.
+- The review report must include `审查者上下文来源` and `未读取材料`.
@@
 The reviewer may recommend fixes...
+If CRITICAL or MAJOR findings remain open, the suite controller must not enter `(最终交付归档)` unless the user explicitly waives them in writing and the waiver is copied into `outputs/manifest.md`.
```

### B.7 `references/review-checklist.md`

- 问题：清单覆盖通用风险，但没有要求审查 git、hash、PDF 是否来自 outputs、编译日志、result contract。位置：`references/review-checklist.md:5-31`。
- 修复：

```diff
diff --git a/references/review-checklist.md b/references/review-checklist.md
@@
 ## CRITICAL
 
+- 阶段必交付文件未提交，或最终 `git status --short` 仍有必交付文件未跟踪。
+- `outputs/main.pdf` 缺失，或 `outputs/main.tex` 不能在 `outputs/` 内编译。
+- LaTeX 日志含 `! LaTeX Error`，或最终 rerun 后仍有关键 undefined reference/citation。
 - 论文、代码、图表或压缩包出现学校、姓名、赛区、队员等匿名信息。
@@
 ## MAJOR
 
+- `outputs/result_contract.json` / `constraint_checks.json` 缺失，或论文核心结果无法追溯到脚本输出。
+- `paper/main.tex` 与 `outputs/main.tex` 分裂且 manifest 未说明 source commit / copy time / SHA256。
 - 假设没有理由，或正文没有使用关键假设。
@@
 ## MINOR
 
+- `__pycache__`、LaTeX aux/log 或临时文件留在交付目录。
 - 图表 caption 不完整。
```

### B.8 `math-modeling-research/SKILL.md` 与 `templates/stage-files/research.md`

- 问题：附件获取失败、镜像数据、合成数据的透明度只靠研究记录，未要求传递到摘要/README/manifest。位置：`math-modeling-research/SKILL.md:26-39`、`templates/stage-files/research.md:13-16`、`:53-56`；现场证据：2024C 54/82 差异虽在最终稿说明，但这是 agent 自觉，不是 skill 强制。
- 修复：

```diff
diff --git a/math-modeling-research/SKILL.md b/math-modeling-research/SKILL.md
@@
 Each update must include:
@@
 - next gate question for the user
+
+If official attachments cannot be obtained, or if public mirrors/synthetic data are used:
+- mark the data status as `official / mirrored / reconstructed / synthetic / mixed`;
+- record source URL, retrieval command, SHA256, row/column counts, and known differences;
+- require the writer to disclose the data status in abstract or data section, and require outputs README/manifest to repeat it.
```

```diff
diff --git a/templates/stage-files/research.md b/templates/stage-files/research.md
@@
 - Known data:
+- Data status: official / mirrored / reconstructed / synthetic / mixed
+- Attachment provenance: source URL, retrieval command, SHA256, row/column count
+- Differences from problem statement:
```

### B.9 `templates/outputs/manifest-template.md` 与 `README-template.md`

- 问题：manifest 没有强制列 git commit、hash、编译命令结果、缺失文件；README 让用户比对但不是交付门禁。位置：`templates/outputs/manifest-template.md:1-34`、`templates/outputs/README-template.md:15-26`。
- 修复：

```diff
diff --git a/templates/outputs/manifest-template.md b/templates/outputs/manifest-template.md
@@
 Generated at:
+Source commit:
+Stage commits:
+Final git status:
@@
 ## Files
 
-| Path | Type | Purpose | Source |
-| --- | --- | --- | --- |
-|  |  |  |  |
+| Path | Type | Purpose | Source | SHA256 | Required? | Exists? |
+| --- | --- | --- | --- | --- | --- | --- |
+| main.tex | paper-source | final editable paper | paper/main.tex |  | yes |  |
+| main.pdf | paper-pdf | final readable paper | compiled from outputs/main.tex |  | yes or waived |  |
@@
 ## Key Commands
@@
 # Fill in commands used to reproduce code results and compile the paper.
 ```
+
+## Delivery Checks
+
+| Check | Command | Result |
+| --- | --- | --- |
+| TeX compiles from outputs | `xelatex -interaction=nonstopmode main.tex` |  |
+| No LaTeX errors | grep log for `! LaTeX Error` |  |
+| TeX figure references exist | list `\\includegraphics` vs `outputs/figures` |  |
+| Paper/code result consistency | compare `result_contract.json` with TeX |  |
+| Final git clean/known | `git status --short` |  |
```

```diff
diff --git a/templates/outputs/README-template.md b/templates/outputs/README-template.md
@@
 ## 已知风险
 
 - 待填写
+
+## 必须显眼披露
+
+- 数据来源状态：official / mirrored / reconstructed / synthetic / mixed
+- 未修复 CRITICAL/MAJOR 审查项：
+- 不能复现或不能编译的文件：
+- 与公开优秀方案差距较大的指标：
```

### B.10 `templates/stage-files/code.md` 与 `writer.md`

- 问题：模板有 `Confirmed?`，但没有强制“confirmed by whom/what command”。位置：`templates/stage-files/code.md:45-49`、`templates/stage-files/writer.md:51-56`。
- 修复：

```diff
diff --git a/templates/stage-files/code.md b/templates/stage-files/code.md
@@
-| Subquestion | Result | Figure/table | Reproducibility note | Confirmed? |
+| Subquestion | Result | Unit | Source command | Output file | Constraint check | Confirmed by | Confirmed? |
```

```diff
diff --git a/templates/stage-files/writer.md b/templates/stage-files/writer.md
@@
 ## Claims Waiting For Confirmation
 
-| Claim | Needed evidence | Owner | Status |
+| Claim | Needed evidence | Source script/output | Constraint affected | Owner | Status |
```

## C. 三类问题严重度分级

- CRITICAL：
  - 2023A 阶段 1-6 产物未提交，只有脚手架 commit；这会让复盘、交接、回滚和最终归档失效。
  - 2025B 缺 `outputs/main.pdf`，但 README 指示用户在 outputs 内编译；最终交付不完整。
  - 2023A/2024C LaTeX 日志含 `! LaTeX Error`，PDF 存在但构建不干净，可能导致最终稿不可信。

- MAJOR：
  - outputs 与 paper 字节级复制，source-of-truth 不清，且未验证 outputs 内 TeX 可独立编译。
  - 审查不是操作上独立，review 后修补/交付门禁失效。
  - 代码结果缺少机器可读 result/constraint contract，导致 2023A 124 MW、2025B 6.57/7.44 这类口径只能人工发现。
  - 2024C 采用简化贪心，结果显著低于公开复杂方案；论文有局限说明，但 skill 没强制公开 benchmark 差距进入风险表。
  - TeX 模板和 writer skill 未强制禁止目录、未处理 hyperref 边框、未规定字体/行距。

- MINOR：
  - 2024C 图表中文字体方框自承未闭环。
  - 2023A 自创重复 `.gitignore`，虽然 pycache 未入库，但项目卫生差。
  - 输出模板缺少“数据状态/镜像/合成”的显眼披露字段。

## D. 改进 PR 拆分建议

### PR-1 流程门禁（commit 强制 + 阶段门禁脚本）

- 改动文件：
  - `math-modeling-suite/SKILL.md`
  - `references/stage-gates.md`
  - `templates/outputs/manifest-template.md`
  - 新增 `templates/project/.gitignore`（可选）
- commit 顺序：
  1. `docs(gates): require stage commit and clean required artifacts before transition`
  2. `docs(outputs): require git log/status and source commit in manifest`
  3. `templates(gitignore): add shared project hygiene ignore rules`
- 工作量：小到中。主要是文档与模板；后续若加脚本再拆一个实现 PR。

### PR-2 论文骨架 + 目录契约（CUMCM TeX + paper/outputs 同步）

- 改动文件：
  - `templates/cumcm/main.tex`
  - `math-modeling-writer/SKILL.md`
  - `templates/outputs/README-template.md`
  - `templates/outputs/manifest-template.md`
- commit 顺序：
  1. `templates(tex): add CUMCM font, line spacing, hidelinks and outputs-first graphic path`
  2. `docs(writer): add no-toc/template-artifact lint and clean compile gate`
  3. `docs(outputs): define paper source-of-truth and outputs compile verification`
- 工作量：中。需要用三个小样例验证 `paper/` 和 `outputs/` 都能找到图。

### PR-3 一致性检测 + 审稿（code vs paper vs constraints 自动核对）

- 改动文件：
  - `math-modeling-code/SKILL.md`
  - `templates/stage-files/code.md`
  - `templates/stage-files/writer.md`
  - `math-modeling-review/SKILL.md`
  - `references/review-checklist.md`
  - `math-modeling-research/SKILL.md`
  - `templates/stage-files/research.md`
- commit 顺序：
  1. `docs(code): require result and constraint contracts for paper-facing numbers`
  2. `docs(research): require data provenance status and synthetic/mirror disclosure`
  3. `docs(review): make independent review operational and block unresolved major findings`
  4. `templates(records): add source command, constraint check, and confirmed-by fields`
- 工作量：中到大。若只改文档是中；若继续实现校验脚本，则应拆 PR-4。

## E. 证据文件清单

- Git 历史：
  - `git -C D:\PythonProject\数学建模skill\math-modeling-skill-suite log --oneline -- 2023A`
  - `git -C D:\PythonProject\数学建模skill\math-modeling-skill-suite log --all --oneline -n 40`
- Hash：
  - `sha256sum 2023A/paper/main.tex 2023A/outputs/main.tex 2024C/paper/main.tex 2024C/outputs/main.tex 2025B/paper/main.tex 2025B/outputs/main.tex`
- 现场文件：
  - `2023A/paper/main.tex:22`, `:276`, `:304`, `:319`
  - `2023A/research/research.md:23-24`, `:143`
  - `2023A/paper/review_report.md:60-61`, `:93-94`
  - `2023A/paper/main.log:1168`, `:1222`
  - `2024C/research/research.md:16`, `:26`, `:52`, `:95-106`, `:120`
  - `2024C/paper/main.tex:22-23`, `:47`, `:80`, `:190-194`, `:215-217`
  - `2024C/outputs/result_summary.csv:2-5`
  - `2024C/outputs/README.md:36-39`, `:62`, `:71`
  - `2024C/paper/review_report.md:54-59`, `:98-114`
  - `2024C/paper/main.log:874`, `:948-955`
  - `2025B/paper/review_report.md:41`, `:59-63`, `:129-139`
  - `2025B/paper/main.tex:298-300`, `:348-356`, `:367`
  - `2025B/outputs/README.md:74-76`
  - `2025B/outputs/SHA256SUMS.txt:35`
  - `.gitignore:1-6`
  - `2023A/.gitignore:1-57`
- Skill / references / templates：
  - `math-modeling-suite/SKILL.md:19`, `:21-31`, `:42-50`, `:56-60`, `:66-78`
  - `references/stage-gates.md:32-50`
  - `math-modeling-writer/SKILL.md:29`, `:61-73`
  - `templates/cumcm/main.tex:1-9`
  - `math-modeling-code/SKILL.md:46-60`, `:62-83`
  - `math-modeling-review/SKILL.md:8-14`, `:31-37`, `:69`
  - `references/review-checklist.md:5-31`
  - `math-modeling-research/SKILL.md:26-39`, `:53`
  - `templates/stage-files/research.md:13-16`, `:53-56`
  - `templates/stage-files/code.md:45-49`
  - `templates/stage-files/writer.md:51-56`
  - `templates/outputs/manifest-template.md:1-34`
  - `templates/outputs/README-template.md:15-26`
