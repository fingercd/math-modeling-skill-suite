# AI 工具使用披露

按 2024 年高教社杯全国大学生数学建模竞赛规则, 本项目使用 AI 工具辅助完成的工作披露如下。

## 使用范围

- **建模思路**: 利用 AI 检索 4 个公开 GitHub 仓库 (Pydoge-x, ArrebolBlack, Elysia415, Gua927) 与 1 篇 skill 内部 references/model-method-map.md, 综合形成候选模型路线 (桶排序贪心 + 蒙特卡洛 + 间作补丁)。
- **代码实现**: 利用 AI 生成 Python 脚本框架 (preprocess / data_structure / objective / greedy / ga / q1-3_run / check_constraints / plot_results), 后续手动调试约束处理逻辑与边界 bug。
- **论文写作**: 利用 AI 起草 main.tex 论文骨架 (摘要 / 问题重述 / 模型假设 / 模型建立与求解 / 结果分析), 后续手动填入实际数字并补充 H6 假设。
- **图表生成**: 利用 AI 写 plot_results.py 生成 6 张图, 中文字体配置由审查阶段补全。

## 使用工具

- Anthropic Claude (本会话执行 agent)

## 使用位置

- `research/research.md` — 调研证据 + 候选方法
- `paper/main.tex` — 论文正文草稿
- `paper/writer.md` — 论文状态跟踪
- `code/*.py` — 全部代码
- `paper/review_report.md` — 独立审查 (由 AI 自审)

## 人类把关

- 所有具体数字 (1106.79 / 940.05 / 953.84 / 1224.01 万元) 来自 `outputs/*.json` 的实际代码运行结果, 无编造。
- 所有约束处理逻辑 (C1, C2, C3, C7, C8, C10) 由代码 + check_constraints.py 双重校验。
- 公开仓库链接 (GitHub) 均通过 WebFetch 验证可访问。

## 不含以下信息

- 学校名称
- 队伍编号
- 队员姓名
- 赛区
- 邮箱 / 联系方式

论文、代码、压缩包、图表文件名均不包含上述可识别信息。