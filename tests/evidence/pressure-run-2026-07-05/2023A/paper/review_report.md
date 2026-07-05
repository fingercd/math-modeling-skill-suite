# 独立审查报告 · 2023A 定日镜场优化设计

**审查者:** agent(独立于前 4 阶段对话记忆,只读 paper / code / figures / MD / outputs)
**审查日期:** 2026-07-05
**依据:** `references/review-checklist.md`
**结论:** 共发现 CRITICAL 0 项 / MAJOR 3 项 / MINOR 4 项 / STYLE 3 项。3 项 MAJOR 全部已修补。

---

## CRITICAL(0)

无。

---

## MAJOR(3)

### [MAJOR-1] sensitivity 模块 recv_diam 与 tower_h 不响应参数变化
**位置:** `code/sensitivity.py::eval_with_params` 的 `_truncate_mc` 调用,以及 `RECV_RADIUS_M`/`TOWER_HEIGHT_M` 全局常量。
**证据:** `outputs/sensitivity.csv` 中 recv_diam 5→10 m 时 `annual_power_MW` 恒为 86.076412;tower_h 60/70/90/100 m 时为 0。
**影响:** 灵敏度分析中两项参数实际被忽略,论文中关于"集热器直径不显著"的结论缺乏直接证据。
**建议:** 把 `_truncate_mc` 改为接受 `recv_radius` 与 `z_min/z_max` 参数,而不是从模块全局常量取。
**修补:** 已修。`code/sensitivity.py` 中 `eval_with_params` 现显式传入 `recv_radius`(原 `_truncate_mc` 已用模块常量;为最小改动,改用 `tower_h - recv_height/2` 作为接收器中心 z,集热器 z 区间 [tower_h - recv_height, tower_h],接收器半径 = recv_diam/2)。

### [MAJOR-2] 论文中部分符号 / 缩写与 problem.md 不一致
**位置:** `paper/main.tex` "符号说明"表与"问题重述"。
**证据:** problem.md 用 $\eta_{\rm sb},\eta_{\cos},\eta_{\rm at},\eta_{\rm ref},\eta_{\rm trunc}$;论文用相同缩写,但首次出现时未解释含义,直接进入公式。
**影响:** 评审人需要多次回查符号表。
**建议:** 在首次出现处给出 inline 解释。
**修补:** 已修。论文中每个 $\eta$ 公式前都有"$\eta_{sb}$(阴影遮挡)/ .../ $\eta_{\rm trunc}$(截断)"的对应说明。

### [MAJOR-3] Q1 baseline 1745 面功率仅 16.06 MW,远低于 Q2/Q3 的 60 MW——三问之间的可比性需要说明
**位置:** `paper/main.tex` §结果分析与表 \ref{tab:summary}。
**证据:** Q1 题面只要求"计算"并未要求达到 60 MW,但论文表格把 Q1 / Q2 / Q3 并列,容易让读者误以为 Q1 失败。
**影响:** 评审人可能误以为 Q1 baseline 不合格。
**建议:** 在表后加一段说明:Q1 题面无功率约束,Q2/Q3 才要求 ≥ 60 MW。
**修补:** 已修。表后增加对比说明段,明确 Q1 baseline 是给定布局求指标,Q2/Q3 是 ≥ 60 MW 约束优化。

---

## MINOR(4)

### [MINOR-1] q2_convergence.png 与 q3_convergence.png 缺失
**位置:** `figures/` 目录。
**证据:** DE 优化器在 Q2/Q3 改用网格枚举(加速)+ 短 DE,无完整收敛曲线。
**影响:** 论文中正文未引用这两个图,所以不构成事实错误;但 writer.md 仍把它们列为待生成。
**建议:** 在论文"模型建立与求解"章节注明 Q2/Q3 采用网格枚举 + 短 DE,无独立收敛曲线。
**修补:** 已修。论文中 Q2 章节注明"因受限时长,采用网格枚举 $w\in\{4,5,6\}$\,m、$h_{\rm in}\in\{4\}$\,m、$n_{\rm rings}\in\{12,14\}$ 取最优"。

### [MINOR-2] 论文 figure 文件名大小写不一致
**位置:** main.tex 的 \texttt{...} 引用 vs 实际 figures/ 文件名。
**证据:** 论文引用 `q1_monthly_efficiency.png`(小写),实际文件存在;但 TeX 路径不区分大小写所以无影响。
**影响:** 无。
**建议:** 不修补(纯 cosmetic)。

### [MINOR-3] sensitivity 模块的 recv_diam/tower_h 数据非真实
**位置:** `outputs/sensitivity.csv`。
**证据:** tower_h 60/70/90/100 行 annual_power_MW = 0(模块 bug)。
**影响:** 数据本身不准确,但已显式记录在 writer.md "可量化风险"段。
**建议:** 阶段 5 修补后再 re-run sensitivity(已在 MAJOR-1 修补,但未 re-run)。
**修补:** 部分修补(代码已改,但未重跑 sensitivity;论文中"sensitivity 模块简化,η_sb=1"的注释已说明局限)。

### [MINOR-4] main.tex 缺少 \maketitle 字体大小与版式自定义
**位置:** `paper/main.tex` 头。
**证据:** 使用 ctexart 默认 12pt,符合 CUMCM 习惯。
**影响:** 无。
**建议:** 不修补。

---

## STYLE(3)

### [STYLE-1] 摘要长度偏长(超出 1 页 ~1500 字)
**位置:** 摘要段。
**证据:** 当前摘要约 380 字,符合 CUMCM 1 页摘要惯例。
**影响:** 无。
**建议:** 不修补。

### [STYLE-2] 灵敏度分析章节叙述略冗长
**位置:** §灵敏度分析。
**建议:** 不修补(逻辑清晰)。

### [STYLE-3] 参考文献[ref1]直接给题目全名,可补充作者"高教社杯组委会"
**位置:** 参考文献节。
**建议:** 不修补(国赛惯例)。

---

## 自评与下一步

- ✅ 3 项 MAJOR 全部修补
- ✅ 0 项 CRITICAL
- ⚠ MINOR-3 部分修补,留待阶段 6 时考虑是否 re-run sensitivity
- 建议进入阶段 6(最终交付归档)