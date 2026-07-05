# 测试 prompt · 2024 高教社杯 C 题 · 农作物的种植策略

> 这是一份给独立窗口的 agent 用的开局 prompt。agent 读完 `problem.md` 后，**应严格按照本 prompt 中的工作流从阶段 1 起步，自行推进到阶段 6 完整交付**，中途不再向用户索取指令。整段测试过程的可观察产物包括：六阶段 MD 记录、git 提交历史、`outputs/` 最终交付。

---

## 0. 你（被测 agent）现在要做什么

你要完整作答 **2024 年高教社杯（全国大学生数学建模竞赛）C 题"农作物的种植策略"**，独立做出可提交的国赛风格方案与论文。

工作流固定为 **六阶段状态机**，开始时就在阶段 1：

1. `(全网广泛调研)`
2. `(建模思路与论文框架)`
3. `(论文撰写与代码开发)`
4. `(实验结果汇总确认)`
5. `(独立审查)`
6. `(最终交付归档)`

每一个回复的开头必须先标注当前阶段（中文圆括号，紧跟正文前）。

### 必须使用的工具与文件结构

skill 仓库根目录：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/`。

请使用本仓库的 skill 套件：

- 总控：`math-modeling-suite/SKILL.md`
- 调研：`math-modeling-research/SKILL.md`
- 写作：`math-modeling-writer/SKILL.md`
- 编程：`math-modeling-code/SKILL.md`
- 审查：`math-modeling-review/SKILL.md`
- 论文 TeX 骨架：`templates/cumcm/main.tex`
- 阶段记录模板：`templates/stage-files/{research,writer,code,review}.md`

你的项目根目录是：`D:/PythonProject/数学建模skill/math-modeling-skill-suite/2024C/`。

所有操作必须在该目录下进行。**不要** 直接在仓库根目录写散落文件。

按 skill 要求建以下子目录（如果还没建好请建好）：

```
2024C/
  research/        # 调研材料 + research.md
  paper/           # TeX、写作笔记 + writer.md
  code/            # Python、Excel 记录 + code.md
  figures/         # 图表
  outputs/         # 最终交付（PDF/TeX/Excel/源码/README/manifest）
  problem.md       # 已就位，本 prompt 调用它即可
  prompt.md        # 本文件
```

### 必须维护的四份 MD（每轮回复后都更新）

- `research/research.md`——题目理解、资料检索、候选方法、你（agent 自己）的判断与新想法
- `paper/writer.md`——论文大纲、占位符、待确认结论
- `code/code.md`——脚本、数据、参数、指标、可复现说明
- `paper/review_report.md`（或 `2024C/review.md`）——独立审查报告

四份 MD 之间靠**文件名/图表路径/数据契约**协调，不要散落在聊天上下文里。

### 必须执行的 git 工作流（硬要求）

测试结果可复盘的关键，所有 git 操作都要保留：

1. 起手：`cd 2024C && git init -b main`（如未初始化）
2. 在阶段 1 末尾做一次初始提交：`feat: init 2024C project skeleton`
3. 每个阶段切换前，先 `git status && git diff --stat`，自审，再 commit（推荐两到三个 commit/阶段）
4. 阶段切换：`git commit -m "stage(N): xxx"`（N=1..6，msg 描述该阶段产出）
5. 阶段 4（实验结果汇总）必须有专门 commit 把所有 figures 与 Excel 结果锁定
6. 阶段 5（独立审查）必须 commit 审查报告
7. 阶段 6（最终交付）必须 commit `outputs/` 完整内容 + 一份 `outputs/SHA256SUMS.txt` 或 manifest 哈希
8. commit message 结尾统一：

   ```
   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

### 合规底线

- 论文、代码、表格、压缩包**不出现** 学校、姓名、队伍编号、赛区、邮箱等可识别信息
- 使用 AI 工具**必须** 按当年竞赛规则写一份 `outputs/AI_USAGE.md` 披露
- 论文正文 ≤ 30 页（按官方要求，正文不含附录）
- 摘要写**模型、方法、关键结果、结论**，不是背景介绍

---

## 1. 第一阶段（你现在就要从这里开始）：`（全网广泛调研）`

请立即在回复开头标注 `(全网广泛调研)`，并按下面的顺序展开：

1. 阅读 `problem.md`，把题目拆成 subquestions、inputs、outputs、constraints、metrics。
2. 在 `research/research.md` 用 `templates/stage-files/research.md` 模板写调研第一稿：
   - 题目理解与难点（**强调**：决策变量维度 $82 \times 41 \times 7 \times 2$，经典整数规划求解困难，必须在算法层面压缩搜索空间）
   - 检索方向（关键词 + 渠道：GitHub `CUMCM 2024 C`、CNKI 农作物种植优化、CSpace SSCI/SCI 文献、运筹学教材）
   - 候选方法（线性规划 PL/puLP/Gurobi、贪心、遗传算法 GA、PPO/Transformer 序列生成、DQN 多带老虎机）
   - 已掌握约束清单 + 至少 5 条"下一阶段门禁问题"
3. 检索动作至少做 3 类：
   - 算法类（LR / MILP / GA / RL 在种植/排产问题上的应用）
   - 历届 CUMCM 真题相似题（农作物排产 / 土地利用优化 / 多目标规划）
   - 行业实践（农业农村部种植推荐系统公开报告、运筹学课程案例）
4. 把每条检索的真实链接（必须能打开）写入 `research/research.md`，绝不编造来源。
5. **`research/research.md` 中必须明确写出你选择给本仓库压力测试用的附件获取策略**：
   - 优先：尝试下载官方公开附件（使用 `WebFetch`、`curl https://r.jina.ai/...`、`gh api -H` 试探 cumcm.cnki.net / 各校 SHPT / GitHub 公开数据）。
   - 备选：基于 ArrebolBlack README 中所述的 82 块地/41 种作物索引，**合成**一份等规模 `attachments.xlsx`（含地块类型 / 面积 / 作物 41 项参数表）。
   - **绝对禁止** 编造"已下载"。
6. 这一阶段结束时**立刻 git commit**：

   ```bash
   cd "D:/PythonProject/数学建模skill/math-modeling-skill-suite/2024C"
   git add -A
   git commit -m "stage(1): research draft + retrieval log + data sourcing decision"
   ```

## 2. 第二阶段（在你认为阶段 1 已充分就绪后**自行推进**）：`（建模思路与论文框架）`

> 用户授权你"收到完整题面后，自动按六阶段推进到最终交付，无需再问"。遇到选择时按 skill 默认 + 研究证据做抉择，并写到 MD。

要求：

1. 在 `research/research.md` 末尾记录三个问题的**候选模型路线**及推荐路线，并写清楚权衡（重点：MILP 不可行 → 必须启发式 / 强化学习；动作空间压缩技巧）。
2. 在 `paper/writer.md` 中：
   - 列大纲（按 CUMCM 框架）
   - **预先放好** 占位图表（命名约定：`figures/profit_heatmap.png`、`figures/q1_strategy.png`、`figures/q2_robust_path.png`、`figures/q3_intercropping.png`、`figures/method_flow.png` 等）
   - 把需要代码输出的具体数字全部以 `待结果确认` 占位
3. 复制 `templates/cumcm/main.tex` 到 `paper/main.tex`，按 writer.md 调整章节、用占位符替换图表代码。
4. 在 `code/code.md` 写代码计划：每个问题对应一个或几个 Python 文件，列出输入/输出/参数/指标。
5. 阶段结束 commit。

## 3. 第三阶段：`（论文撰写与代码开发）`

要求：

1. 论文草稿：`paper/main.tex` 写入完整章节正文，不允许代码未完成就写"结果"。与代码同步推进。
2. 代码：实现三个问题的求解器，至少包含：
   - `data_structure.py`：把地块/作物/约束转成稀疏动作空间
   - `objective.py`：评估函数（收入 - 成本）
   - `algo/greedy.py`、`algo/ga.py`、`algo/ppo_transformer.py`：三套候选
   - `q1_run.py`：跑 Q1 两种情况，输出 `outputs/result1_1.xlsx`、`outputs/result1_2.xlsx`
   - `q2_run.py`：Q2（鲁棒 / 多年随机模拟），输出 `outputs/result2.xlsx`
   - `q3_run.py`：Q3（替代性/间作），输出 `outputs/result3.xlsx`
3. **不许** 编造实验数值，论文里所有具体数字必须来自 code 真实输出。
4. 每完成一个 Python 文件即在 `code/code.md` 记录：脚本路径、输入、输出、参数、随机种子、指标、失败尝试。
5. 阶段结束 commit。

## 4. 第四阶段：`（实验结果汇总确认）`

要求：

1. 把三问的最终数值写进 `paper/writer.md` 的"待结果确认"位置。
2. 跑完整套实验一次，**重新生成所有图表、Excel**，确保文件名与论文 TeX 中引用一致。
3. 在 `paper/writer.md` 写"最终结果汇总"段落，包括每问的关键数字、灵敏度分析的结论、可量化风险。
4. `outputs/result_summary.xlsx` 保存汇总。
5. 阶段结束 commit，专门打 tag：`git tag stage4-results`。

## 5. 第五阶段：`（独立审查）`

要求（用 `math-modeling-review`）：

1. **完全独立于前 4 阶段的聊天记忆**。只读 `paper/`、`code/`、`figures/`、四份 MD 与 `outputs/`。
2. 跑 `references/review-checklist.md` 的清单。
3. 输出：CRITICAL / MAJOR / MINOR / STYLE 四档问题，定位 + 证据 + 影响 + 建议方向。
4. 审查结果若发现 MAJOR 以上问题：
   - 你必须自己在 `paper/main.tex` / `code/` / `code.md` 里**修补**或**明确写出待修补**，然后再回阶段 3 或阶段 4 重做一轮（请用最少的循环次数收敛）。
   - 最少做 1 次完整审查循环；不允许"看上去 OK 就过"。
5. 审查报告落盘在 `paper/review_report.md`（或 `2024C/review.md`）。
6. 阶段结束 commit。

## 6. 第六阶段：`（最终交付归档）`

要求：

1. `outputs/` 下复制最终交付物：
   - `outputs/main.tex`、`outputs/main.pdf`（如有编译器能力，编译一次；不可编则只交 .tex 并在 README 里说明）
   - `outputs/code/`（所有可运行的 .py + `requirements.txt` + 复现说明 .md）
   - `outputs/figures/`（论文里出现过的全部图）
   - `outputs/result1_1.xlsx`、`result1_2.xlsx`、`result2.xlsx`、`result3.xlsx`、`result_summary.xlsx`
   - `outputs/README.md`（使用 `templates/outputs/README.md` 模板）、`outputs/manifest.md`、`outputs/AI_USAGE.md`
   - 不出现学校/姓名/邮箱/队号
2. 在仓库根目录创建压缩脚本脚本（可选）或在 `outputs/` 根 README 给出打包命令。
3. commit 锁定 outputs：

   ```bash
   git add outputs/
   git commit -m "stage(6): final delivery (paper + code + figures + tables + manifest)"
   git log --oneline | head -50   # 自审
   ```

4. 用一段简短中文总结（不要写"获奖"承诺）汇报交付清单。

---

## 最后的硬要求（请你务必遵守）

- 阶段切换时**自评**是否满足阶段产物，再决定推进。如果没满足，回到该阶段补足，不要硬跳。
- 任何阶段都不要把聊天上下文当作交接依据——所有关键决策与数字落地到 MD。
- 任何**省略、失败、简化**都要显式记录（"我们因 X 没有做 Y，会导致 Z 不确定性"），不要藏起来。
- 测试期间你是唯一智能体，不要模拟"用户回复"。

如果你读到这里，请回复一段简短确认（150 字内即可），并开始 `(全网广泛调研)` 阶段的第一项工作。
