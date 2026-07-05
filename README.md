# 数学建模竞赛多 Skill 套装

这是一套给数学建模竞赛用的 AI agent 工作流。它不是某一道题的答案，而是一套流程规范和模板，帮你把调研、建模、写论文、写代码、汇总结果、独立审查和最终交付分开管理。

当前版本：`v2.0.0`。

适合这些场景：

- 高教社杯/CUMCM 国赛
- 校赛、五一赛、电工杯等中文数学建模竞赛
- 需要建模手、编程手、论文手协作的项目
- 想让 AI agent 按阶段推进，而不是一上来就乱写代码或乱写论文

## 你会得到什么

这个仓库里有 5 个 skill：

| Skill | 什么时候用 |
| --- | --- |
| `math-modeling-suite` | 总控入口。负责六阶段流程、目录规范、阶段切换和最终交付 |
| `math-modeling-research` | 调研阶段用。整理题目、资料、算法论文、模型论文、行业案例 |
| `math-modeling-writer` | 论文阶段用。生成国赛风格 LaTeX 框架、图表占位和 `writer.md` |
| `math-modeling-code` | 代码阶段用。写 Python 代码、记录 Excel 结果、生成图表和 `code.md` |
| `math-modeling-review` | 最后审查用。独立检查论文、代码、图表、支撑材料和合规风险 |

还有一批模板：

- `templates/cumcm/main.tex`：国赛风格论文骨架
- `templates/stage-files/research.md`：调研记录模板
- `templates/stage-files/writer.md`：论文记录模板
- `templates/stage-files/code.md`：代码实验记录模板
- `templates/stage-files/review.md`：审查报告模板
- `templates/first-response.md`：第一次启动时的回复模板
- `templates/tables/result-table-template.md`：结果表格模板
- `templates/figures/flowchart-placeholder.md`：流程图占位模板
- `templates/contracts/*.json`：结果、约束、图表三类机器可读合同
- `templates/project/.gitignore`：比赛项目推荐忽略规则

2.0 新增了三类只读校验脚本：

- `scripts/validate_skill_suite.py`：检查 skill 套装本身是否完整。
- `scripts/validate_project_delivery.py`：检查某个比赛项目是否满足交付契约。
- `scripts/run_regression_checks.py`：用 2023A / 2024C / 2025B 压测 evidence 验证校验器能抓住 1.0 暴露的问题。

## 最简单的用法

把整个仓库交给你的 AI agent，然后让它先读：

```text
请使用 math-modeling-suite，按六阶段流程帮我完成数学建模竞赛项目。
```

如果你的工具支持 skill 目录，可以把 5 个 skill 目录复制到你的 skills 目录：

```text
math-modeling-suite/
math-modeling-research/
math-modeling-writer/
math-modeling-code/
math-modeling-review/
```

如果你的工具不支持 skill，也可以直接让 agent 阅读对应的 `SKILL.md` 文件。

## 比赛项目应该怎么建目录

每个具体比赛项目建议建成这样：

```text
your-contest-project/
  research/   调研资料和 research.md
  paper/      论文 TeX、写作素材和 writer.md
  code/       Python 脚本、Excel 记录和 code.md
  figures/    流程图、实验图、结果图
  outputs/    最终论文、代码、图表、支撑材料、README、manifest
```

最终交付只看 `outputs/`。不要到处翻聊天记录、临时文件和散落图片来拼最终版。

2.0 对论文源文件和最终交付做了明确约定：

- `paper/main.tex` 是写作源。
- `outputs/main.tex` 是最终交付副本。
- `outputs/main.pdf` 是最终 PDF；如果缺失，必须在 `outputs/README.md` 和 `outputs/manifest.md` 显眼说明。
- `outputs/result_contract.json` 记录论文里的每个数字来自哪里。
- `outputs/constraint_checks.json` 记录约束、可行性和一致性检查。
- `outputs/figure_manifest.json` 记录 TeX 图引用、真实文件、来源脚本和 SHA256。

## 六个阶段

agent 每次回复前都要标注当前阶段：

1. `(全网广泛调研)`
2. `(建模思路与论文框架)`
3. `(论文撰写与代码开发)`
4. `(实验结果汇总确认)`
5. `(独立审查)`
6. `(最终交付归档)`

用户说“继续”“进入下一阶段”“方案批准”“推进”等意思相近的话，就可以进入下一阶段。不需要固定口令。

但每个阶段退出前必须做检查点：

- 更新当前阶段 MD。
- 运行并记录 `git status --short`。
- 能提交时创建阶段 commit，并把 commit SHA 写入阶段 MD。
- 写清楚未解决风险和下一阶段门禁。
- 阶段 5 如果还有未关闭的 `CRITICAL` 或 `MAJOR`，不能进入阶段 6，除非用户在 manifest 中显式豁免。

## 第一轮怎么开始

如果你只知道“我要做高教社杯 A 题”，可以这样说：

```text
我要参加高教社杯，请帮我做 A 题。先按 math-modeling-suite 的流程来。
```

agent 应该先停在 `(全网广泛调研)`，不会直接写代码或写最终论文。它会要求你提供：

- 题面
- 附件数据
- 官方提交要求
- 你们队伍的大致分工
- 是否允许检索公开背景资料和历史相似题

## 三个必须维护的文件

每一轮对话后，agent 都要更新对应的 MD 文件。

| 文件 | 记录什么 |
| --- | --- |
| `research/research.md` | 题目理解、检索记录、资料来源、候选模型、用户新想法 |
| `paper/writer.md` | 论文结构、图表占位、表格占位、待确认结论、修改意见 |
| `code/code.md` | 脚本、输入数据、输出图表、参数、指标、失败记录、可复现说明 |

这三个文件是交接用的。编程手和论文手不在同一台电脑上时，先看这三个文件。

## 代码规则

默认只支持：

- Python：主要计算、建模、画图
- Excel：记录数据、结果表、人工检查

适合让 agent 直接尝试的内容：

- 数据清洗
- 分类、回归、聚类、无监督聚类
- 传统机器学习
- 统计分析
- 优化求解
- 论文图表生成

不默认承诺跑完：

- 深度学习长时间训练
- 大模型训练或微调
- 需要 GPU 的大实验

遇到这类任务，agent 应该写训练脚本和调参说明，让用户自己训练和调参。

代码结果进入论文前，必须同步到 `outputs/result_contract.json`；关键约束和一致性检查必须同步到 `outputs/constraint_checks.json`。

## 论文规则

默认按 CUMCM/高教社杯风格组织：

- 摘要
- 问题重述
- 问题分析
- 模型假设
- 符号说明
- 数据处理
- 模型建立与求解
- 结果分析与检验
- 灵敏度、误差或稳健性分析
- 模型评价、改进与推广
- 参考文献
- 附录

`templates/cumcm/main.tex` 已经预留了流程图、结果表、问题一/二结果图和灵敏度分析图的位置。真实图表生成后，通常只要改文件名或放入同名文件即可。

论文中每个 `\includegraphics{...}` 最终都应出现在 `outputs/figure_manifest.json` 里。最终检查以 `outputs/` 为准。

## 最后一定要审查

`math-modeling-review` 是独立审查 skill。它不应该凭聊天记忆判断，也不应该帮你编造结果。它只看你提供的论文、代码、图表和阶段记录，然后按严重程度输出问题：

- `CRITICAL`：可能导致退赛、结果矛盾、代码缺失、匿名信息泄露等
- `MAJOR`：模型、验证、公式、图表、复现存在明显问题
- `MINOR`：格式、引用、单位、caption 等小问题
- `STYLE`：表达润色问题

2.0 的规则更硬：审查报告中只要还有未关闭的 `CRITICAL` 或 `MAJOR`，就不能进入最终归档。用户确实要带风险交付时，需要在 `outputs/manifest.md` 记录豁免原因。

## 怎么验证

在仓库根目录运行：

```powershell
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/validate_skill_suite.py --root .
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/run_regression_checks.py --root .
```

验证一个具体比赛项目：

```powershell
C:/Users/lenovo/anaconda3/envs/pytorch/python.exe scripts/validate_project_delivery.py --project path/to/your-contest-project
```

`tests/evidence/pressure-run-2026-07-05/` 保存了 2023A / 2024C / 2025B 三题压测产物。它们不是参考答案，而是 2.0 校验器的回归证据。

## 重要提醒

- 比赛期间不要公开发布或讨论实时赛题内容。
- 论文、代码、图表和压缩包文件名不要出现学校、姓名、赛区等身份信息。
- 使用 AI 工具要按当年比赛规则披露。
- 代码结果和论文结论必须一致。
- 摘要不要写成背景介绍，要写模型、方法、关键结果和结论。

## 许可证

本项目使用 MIT License。你可以复制、修改和二次分发，但请保留许可证说明。
