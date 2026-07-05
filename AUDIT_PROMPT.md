# 复审 prompt · 三道题独立复盘 + skill 缺陷评估

> 给独立 agent（codex 等）的开局 prompt。一次性把所有体检材料、已知问题、要交付的复审报告说清楚，避免反复追问。

---

## 0. 你现在要做什么

我们刚用本仓库的 `math-modeling-skill-suite` 跑了一次"全自动压力测试"：选了 2023 高教社杯 A 题、2024 C 题、2025 B 题三道真题，让三个独立窗口的 agent 在 Windows 笔记本上全程无人干预地从阶段 1 推到阶段 6。我们紧接着做了一轮体检，发现了一系列问题。

你要做的两件事：

1. **独立复盘三道题的产物**——验证我们归纳的问题是否站得住脚，**不要**直接复用我的结论，请自己读证据自己判断。
2. **给出本仓库 skill 的改进方案**——读所有 5 个 `SKILL.md`、`references/`、`templates/`，指出每处与三道题现场证据冲突的具体条款、可执行补丁的修改草稿。

你不必再开任何外网搜索。三道题的 git 历史 + 文件树就是全部证据。

---

## 1. 体检材料位置

skill 根目录：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/`

### 三道题项目目录
- `2023A/` — 2023 高教社杯 A 题·定日镜场优化设计
- `2024C/` — 2024 高教社杯 C 题·农作物的种植策略
- `2025B/` — 2025 高教社杯 B 题·碳化硅外延层厚度反演

每个目录下都有：
- `research/research.md`、`paper/writer.md`、`code/code.md`、`paper/review_report.md` 四份 MD
- `paper/main.tex` + `paper/main.pdf` + `figures/`
- `outputs/`：最终交付区（main.tex/main.pdf/result*.xlsx/figures/code/AI_USAGE.md/manifest.md/SHA256SUMS.txt/README.md）
- `code/`：全部 Python 源码
- `problem.md`（题面）、`prompt.md`（测试指令）

### Git 历史（关键证据）
```
git log --all --oneline -n 40      # 看 commit 数 / stage(1)~stage(6) 落地情况
git log --stat -- 2023A            # 看每道题各自 commit 包含哪些文件
git status --ignored --short       # 看当前未被跟踪的文件 + 被忽略的临时文件
```

**重要**：2023A 仅 1 条 commit（脚手架），后面 6 个阶段的工作都在 untracked 状态；这是流程门禁失效的硬证据。2024C/2025B 有完整 6 阶段 commit。

---

## 2. 我们观察到的已知问题（不要再重新发现，直接拿去交叉验证）

### 论文格式 / 模板
- `templates/cumcm/main.tex` 默认带 `\tableofcontents` + `\newpage`，CUMCM 官方风格不要求目录
- hyperref 没设 `colorlinks=true` 等，导致参考文献 / 引用出现"蓝色框"边
- 没显式字体声明（系统默认 SimSun），行距/字号都靠 ctexart 默认
- `\graphicspath{{../figures/}{figures/}}`：图搜索路径指 `paper/`，把同一份 TeX 复制到 `outputs/` 后几乎肯定**不能再编译**

### 流程合规
- 2023A 阶段产物全部在未跟踪状态，违反"每个阶段必须 git commit"的硬约定
- paper/ 与 outputs/ 内容字节级相同，违反 skill 的"最终交付只看 outputs/"目录契约
- `paper/main.tex` 与 `outputs/main.tex` 不是 from-source 的唯一真相，分裂成两份
- 2025B 没有 `outputs/main.pdf`（只有 paper/main.pdf），说明 stage 6 复制动作不完整

### 内容 / 数据
- **2023A Q3 输出 124 MW 违反题面 60 MW 约束**（应 ≤ 60 或 ≥ 60，但 124 远高于 60 上限的含义未交代）
- **2024C 用 54 行而非题面 82 行**——research.md 诚实记录差异，问题是 public summary 没有显眼说明
- **2024C 七年累计利润 1106/940 万元比公开优秀论文低一个数量级**（Gua927 报告 3761/9359 万元）——实现可能是简化版贪心，没跟 GA/RL 对比结果
- **2025B Q2 极值法 7.44 µm 与 Q3 TMM 法 6.57 µm 相差 12%**——review 报告提出"为什么选 Q2 作为主推荐"但论文里没给出判据
- 2025B 的 Sellmeier 系数是占位估计（不是 Palik/DeVos 的实验曲线），TMM 残差 13–19%

### 代码 / 资源
- 2024C / 2025B 的 `__pycache__/` 进了 git，因为没有项目级 `.gitignore`
- 2023A 的 `.gitignore` 由 agent 自创且重复了同一规则

### 审查独立性
- 3 份 `review_report.md` 都是 agent 自写自我审查，**实际并未完全独立**——5 阶段要求"独立审查"，但 agent 仍持有阶段 1-4 的记忆
- review 报告里多处出现"已修 / 部分修补 / 未 re-run"，**修补实际上没有 finish**

---

## 3. 你（codex）要做的事——分两阶段

### 阶段 A. 现场复盘（先做）

请**独立**按下列顺序读取证据，并对每个问题给出"成立 / 部分成立 / 我看到相反证据"判定：

| # | 待你独立验证的问题 | 必要命令 / 文件 |
|---|---|---|
| 1 | 2023A 是否真没做 stage(1..6) commit | `git log --oneline -- 2023A` |
| 2 | 三道题 paper/main.tex 与 outputs/main.tex 字节是否真相同 | `sha256sum 2023A/paper/main.tex 2023A/outputs/main.tex` |
| 3 | 2025B 是否真没有 outputs/main.pdf | `ls 2025B/outputs/main.pdf` |
| 4 | Q3=124 MW 是否真违反 60 MW 约束 | grep `paper/main.tex` 找 `124.04` 和 `60 MW` 出现处 |
| 5 | 2024C 利润是否真比公开论文低 | 对比 Gua927/CUMCM2024-C README 与 2024C outputs/result*.xlsx |
| 6 | 2025B Q2/Q3 厚度差 12% 是否真实且论文是否给出选哪个 | grep `7.44` `6.57` `主推荐` `判据` 在 main.tex |
| 7 | matplotlib 中文字体是否真在 figures 里变成了方框 | 2024C/figures/*.png，PNG 图像在 reviews 里已 MINOR-1 自承 |
| 8 | hyperref 蓝色框是否真在论文最后一页出现 | 看 paper/main.pdf 最后一页，搜 `hyperref` 颜色说明 |
| 9 | 2024C/2025B __pycache__ 是否真入库 | `ls 2024C/code/__pycache__ 2025B/code/__pycache__` |
| 10 | review 自报修补是否真完成 | 抽查 `paper/review_report.md` 第 N 行提到的修补点，对比 TeX/PDF/Excel 实际状态 |

请把每条结论写到一个表格里，列名建议：
- **问题编号**、**证据命令**、**观察**、**你的判定**、**必要时引用文件路径:行号**

### 阶段 B. Skill 缺陷归纳（基于你阶段 A 的证据）

读以下文件后请对每一处给出**"条款 → 怎么改 → 改动 diff 草稿"**三件套：

```
math-modeling-suite/SKILL.md
math-modeling-research/SKILL.md
math-modeling-writer/SKILL.md
math-modeling-code/SKILL.md
math-modeling-review/SKILL.md

references/stage-gates.md
references/cumcm-2026-notes.md
references/model-method-map.md
references/review-checklist.md
references/cross-device-collaboration.md
references/code-tuning-guide.md

templates/first-response.md
templates/stage-files/*.md
templates/cumcm/main.tex
templates/figures/flowchart-placeholder.md
templates/tables/result-table-template.md
templates/outputs/*.md
```

请特别关注：
1. **是否在 SUITE 一层就把"每阶段必须 git commit"列入阶段门禁**——目前漏
2. **CUMCM TeX 模板是否给了完整字体 / 版式 / 链接处理**——目前是 CTeX 默认 + 默认 1.2 行距
3. **paper vs outputs 目录契约**——目前 paper 和 outputs 不是 from-source 唯一来源
4. **代码与论文一致性检测**——目前全靠人手
5. **审查独立性**——目前同 agent 自审，没真正切断上下文
6. **成品压缩包/文件名匿名合规**——目前只口头约定，没脚本校验
7. **附件获取失败 → 数据合成透明度**——目前有提到但 evaluation 没落实

## 4. 输出格式（请按这个格式给我最终报告）

```markdown
# 复审报告 · 2026-07-05 · 三题 + skill

## A. 现场复盘表
| # | 问题 | 你的判定 | 证据 |
|---|------|---------|------|

## B. Skill 缺陷归纳（按 SKILL.md / references / templates 分文件给）
### B.1 math-modeling-suite/SKILL.md
- 问题1：[位置:行号] + 现状描述
- 修复1：diff 草稿（用 ```yaml/code/diff 块给出）
### B.2 math-modeling-research/SKILL.md
...
### B.3 templates/cumcm/main.tex
...

## C. 三类问题严重度分级
- CRITICAL：可能导致脱稿、跑通率低、退赛风险
- MAJOR：质量核心，有可补可放
- MINOR：文字 / 体验

## D. 改进 PR 拆分建议
按以下维度拆：
- PR-1 流程门禁（commit 强制 + 阶段门禁脚本）
- PR-2 论文骨架 + 目录契约（CUMCM TeX + paper/outputs 同步）
- PR-3 一致性检测 + 审稿（code vs paper vs constraints 自动核对）
每个 PR：改动文件清单 + commit 顺序 + 落地工作量

## E. 证据文件清单
列出你引用的 file:line + git log 行号
```

---

## 5. 约束

- **不要做新一轮的现场操作**（不再跑脚本、不再生成 PDF）——只需读 + 静态判断
- 可以 read / grep / git log / git diff，不要 commit 或修改任何文件
- 三道题的 `paper/main.tex` `outputs/main.tex` 字节比较请用 `sha256sum`，不要 `diff`
- 输出"缺陷"必须给 file:line 引用
- 给"修复"必须给可粘贴的 diff 草稿（一两条 commit 能合入的颗粒度）

---

## 6. 报告落盘位置

请把报告写到 `D:/PythonProject/数学建模skill/math-modeling-skill-suite/AUDIT_REPORT.md`，这样我也能从这个仓库里直接读。

---

如果你读到这里，请用 5 行以内回我确认"开始现场复盘表 §A 第 1 项"再继续执行。整段测试旨在找出 skill 还能改进的盲区，欢迎反驳我们既有的判断。
