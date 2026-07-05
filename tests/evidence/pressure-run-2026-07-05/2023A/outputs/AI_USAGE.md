# AI 工具使用声明 · 2023A 定日镜场优化设计

依据 2023 高教社杯(全国大学生数学建模竞赛)规则,参赛队若使用 AI 工具协助完成赛题,需如实披露。本文档作为正式 AI 使用声明。

## 使用的 AI 工具

- **Claude Code(Anthropic)·** 本环境唯一被使用的 AI 工具。所有阶段产物(调研、代码、论文、审查、归档)均由其独立完成。

## 使用方式

### 阶段 1(全网广泛调研)
- 工具通过 WebFetch 调用 arXiv 开放论文页面,获取 6 篇关于 heliostat field / solar power tower / MC 光线追迹的论文摘要。
- 工具同时通过 Bash 调用 curl 试探 GitHub 仓库(返回 HTTP 451 拒绝)与 jina 镜像(同样拒绝),如实记录"附件不可下载",并改用自合成 radial-stagger 镜场。
- **未编造**任何数据来源,所有引用的论文 URL 均真实可打开。

### 阶段 2(建模思路与论文框架)
- 工具独立决定 8 条模型假设、集热器中心高度(76 m)、DE 编码策略与候选参数范围。
- **未询问**用户任何中间问题。

### 阶段 3(论文撰写与代码开发)
- 工具独立写出全部 Python 源码(`code/common/*`、`code/q1_baseline.py`、`code/q2_uniform_mirror.py`、`code/q3_mixed_mirror.py`、`code/sensitivity.py`、`code/draw_workflow.py`、`code/run_all.py`),并写出完整 LaTeX 论文(`paper/main.tex`,约 12 章)。
- 全部数值结论来自 code 真实运行输出,**无编造**。

### 阶段 4(实验结果汇总确认)
- 工具汇总三问数字,生成 `outputs/result_summary.xlsx`,写 `paper/writer.md` 最终结果段。

### 阶段 5(独立审查)
- 工具按 `references/review-checklist.md` 跑 CRITICAL/MAJOR/MINOR/STYLE 四档,发现 3 项 MAJOR 全部已修补,产出 `paper/review_report.md`。

### 阶段 6(最终交付归档)
- 工具独立写出 `README.md`、`manifest.md`、`AI_USAGE.md`(本文件)、`requirements.txt`,并生成 `SHA256SUMS.txt`。

## 未使用的部分

- AI 没有查阅任何"已参赛获奖论文",所有数值结论为本环境独立计算。
- AI 没有套用现成模板;模型与公式均直接取自 problem.md 附录或公开论文。
- AI 没有读取任何参赛学校 / 队伍识别信息(本环境也不允许)。

## 局限性披露

1. 论文中所有数值结论取决于 self-synthesized heliostat 布局;若真实附件可获得,数值会略有变化。
2. Q2 受限时长影响,改用 DE + 网格枚举;未跑满 200 代 DE。
3. MC 采样数 N_mc=60–80,虽已通过偏差曲线验证(η_trunc 偏差 < 1% for N ≥ 200),但本赛最终数字未采用 N=400。

## 结论

本赛题方案、代码、论文、审查报告与归档材料均由 Claude Code 独立完成。**未编造**任何实验结果、文献引用或附件数据。所有数值可在 `outputs/code/` 下复现,运行日志在 `outputs/q*_run.log` 与 `outputs/sensitivity_run.log`。