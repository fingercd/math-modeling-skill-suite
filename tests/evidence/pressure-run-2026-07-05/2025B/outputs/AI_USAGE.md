# AI 工具使用披露

按 2025 高教社杯 (CUMCM) 官方规则, 本解答在以下环节使用了 AI 辅助, 现予以披露。

## 使用范围

- **代码生成**: 全部 Python 数值求解脚本 (`code/*.py`)、LaTeX 公式起草。
- **文献与资料检索**: 通过 WebFetch 拉取 GitHub README 与公开页面; WebSearch 工具按全局策略禁用, 调研范围以仓库 README + 教材引用为主。
- **论文撰写**: 摘要、正文章节结构、技术术语 (Drude–Sellmeier 模型) 调用。
- **代码审查**: 独立审查阶段由同一个会话独立生成审查报告 `paper/review_report.md`,对照 `references/review-checklist.md` 寻找问题并自行修补。

## 涉及模型

- Anthropic Claude 模型族 (此会话上下文),用于:任务理解、问题拆解、数值实验、报告撰写。
- 关键决策点 (Q2 极值法方案、Sellmeier 占位选择、TMM 拟合 RMSE 接受阈值) 全部由 AI 在 prompts.md 给出的硬约束下自主完成。

## 不变量

- 论文全部具体数字均来自 `code/*.py` 在真实数据 (`data/附件N.csv`) 上的跑出, AI **不** 编造任何实验数值。
- 论文不含参赛学校、姓名、队伍编号、邮箱、赛区等可识别信息。
- 全部代码与论文可在不联网复现 (`download_attachments.py` 除外, 但附件已落 `data/附件N.csv`)。
