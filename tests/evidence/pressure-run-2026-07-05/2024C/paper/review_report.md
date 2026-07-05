# 独立审查报告 — 2024C 农作物种植策略

## 审查范围

- `paper/main.tex`, `paper/writer.md`
- `code/` 全部 13 个脚本 + `code/data/`
- `figures/` 6 张图
- `outputs/` 5 张 Excel + 4 个 json + 2 个 csv
- 4 份 MD（research / writer / code / 本报告）

## 严重度分级

### CRITICAL

无。

- 论文 / 代码 / 图表未出现学校、姓名、邮箱、队号等匿名信息（grep 验证）。
- 所有 xlsx 数字与 `outputs/q1_summary.json` / `result2_summary.json` / `result3_summary.json` 一致。
- 三问均有代码 + 输出 + 数字写入正文。
- AI 工具使用将在 `outputs/AI_USAGE.md` 披露（阶段 6 写入）。

### MAJOR

#### [MAJOR-1] 数据规模与题面不一致未在摘要显眼说明

- **位置**: paper/main.tex 摘要、§2 问题分析
- **证据**: problem.md 与官方 README 都描述 "82 块地块"，但附件 1 实际只有 54 行（A1–A6、B1–B14、C1–C6、D1–D8、E1–E16、F1–F4）。
- **影响**: 阅卷老师若按 "82 块地" 预期审核，可能质疑结果是否覆盖全部地块；摘要里虽提到 "54 块耕地" 但未单独说明与题面差异。
- **建议**: 在摘要末段添加一句 "题面所述 82 块地块与官方附件 1 的 54 行不一致，本文以附件为准使用 54 块地"。

#### [MAJOR-2] 关键假设 (H2) 缺乏敏感性分析

- **位置**: paper/main.tex §3 H2、writer.md 已知限制
- **证据**: 附件 2 未给出 "预期销售量"，本文以 "2023 实际产量 × 1.2" 作 baseline。但 buffer=1.2 的选取缺乏依据；若 buffer 改为 0.8 或 1.5，贪心结果可能变化 10–20%。
- **影响**: Q1 子问 1 vs 子问 2 的差异、Q2 蒙特卡洛均值、Q3 提升 28.3% 都对 baseline buffer 敏感。
- **建议**: 在灵敏度分析中加一张图 `figures/sensitivity_buffer.png`，扫描 buffer ∈ {0.5, 0.8, 1.0, 1.2, 1.5, 2.0} 看 Q1/Q3 净利润变化。

#### [MAJOR-3] Q3 提升幅度 28.3% 与公开解析 23.6% 差异未解释

- **位置**: paper/main.tex §7 结果分析与检验
- **证据**: Gua927 README 报告 "Q3 较前方案提升 23.6%"，本文 28.3%。
- **影响**: 阅卷老师可能对比公开解析质疑方法可靠性。
- **建议**: 在 §7 增加一段 "与公开解析比较"，说明差异来源 (本文 baseline buffer、ρ 矩阵贪心选择 vs 公开解析的复合机制)，承认我们的方法是简化版。

#### [MAJOR-4] 水浇地 C2 vs C8 互斥未给出明确取舍

- **位置**: paper/main.tex 摘要、§7
- **证据**: Q3 启用豆类覆盖后，水浇地 s=1 出现 56 处 "蔬菜 + 豆类" 双条目，违反 C2 严格解读。摘要说 "本文优先满足 C8 并在论文中显式标注" 但正文未给取舍论证。
- **影响**: 阅卷可能扣分（违反约束）。
- **建议**: 在 §3 H 假设增加 H6: "当 C2 与 C8 在水浇地冲突时，本文以 C8（豆类覆盖）优先，理由是题目要求 '豆科作物间作' 是 Q3 显式新增机制，故视为对 C2 的局部放宽"。

### MINOR

#### [MINOR-1] 图表中文显示为方框

- **位置**: figures/*.png
- **证据**: matplotlib 默认 DejaVu Sans 不含中文字形。
- **影响**: 论文 PDF 若插入这些图会显示方框。
- **建议**: 在 plot_results.py 顶部加 `plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']`，并 `plt.rcParams['axes.unicode_minus'] = False`。

#### [MINOR-2] tab:data-overview 表头与代码不严格对应

- **位置**: paper/main.tex §5 表
- **证据**: 表头列 "问题" 含 "缺失/异常/尺度"，但代码侧只处理 "缺失" (H2 假设)，未对 "异常/尺度" 做处理。
- **影响**: 论文与代码轻微脱节。
- **建议**: 改为 "缺失 / 异常 / 标准化" 并对应 H2 显式标注 "无异常, 无需标准化"。

#### [MINOR-3] GA 交叉验证脚本未实际跑

- **位置**: code/algo/ga.py
- **证据**: 文件存在但 stage 3 commit 信息未提及 GA 运行结果。
- **影响**: 论文提到 GA 但未给出对比数字。
- **建议**: 在阶段 6 前跑一次 GA，结果写入 outputs/ga_validation.json，并在 paper §7 加一段 "GA 验证：...，说明贪心解与 GA 解差距 < X%"。

#### [MINOR-4] main.tex 无 \bibliography 编译依赖

- **位置**: paper/main.tex
- **证据**: 参考文献用 `\bibitem` 手写而非 .bib 文件，可编译但不利于复用。
- **影响**: 评阅如需重新编译可能不便。
- **建议**: 保持现状（手写 \bibitem 在 ≤30 页论文中是常见做法），仅在 STYLE 列出。

### STYLE

- 摘要 ≈ 280 字，符合 CUMCM 摘要 ≤ 400 字习惯。
- 章节衔接清晰：重述 → 分析 → 假设 → 数据 → 模型 → 结果 → 灵敏度 → 评价 → 参考文献 → 附录。
- 术语基本统一："桶排序贪心 / 动作点 / 评估函数 / 间作 / 蒙特卡洛" 全文一致。
- minor 重复表达：摘要中"问题 1 ... 问题 2 ... 问题 3" 可精简为列表。

## 通过 / 修补建议

- CRITICAL: 0 → 直接通过
- MAJOR: 4 条 → 修补 H6 与 baseline 灵敏度后通过；其余接受并文档化
- MINOR: 4 条 → 阶段 6 前修补中文 glyph、GA 验证
- STYLE: 1 条 → 摘要可微调，不阻塞

## 修补优先级

1. **立即修补** (阶段 6 前):
   - MAJOR-1 摘要显眼说明 82 vs 54
   - MAJOR-4 H6 假设 + 显式取舍
   - MINOR-1 中文字体
   - MINOR-3 跑 GA

2. **文档化** (论文显式承认):
   - MAJOR-2 baseline buffer 灵敏度（论文加图）
   - MAJOR-3 与公开解析差异说明

3. **可接受 (无影响)**:
   - MINOR-2 / MINOR-4
   - STYLE

## 结论

通过最小修补 (4 条立即 + 2 条文档化) 后，论文满足 CUMCM 评审要求，可进入阶段 6 交付。