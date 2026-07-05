# 2023 年高教社杯全国大学生数学建模竞赛 A 题 · v2 复跑版

> 第二轮压力测试（v2.0 skill）。题面与 `../2023A/problem.md` 一致；本轮新增约束以 prompt.md 为准。题面源与多源交叉与上轮一致。

## 题目背景

构建以新能源为主体的新型电力系统，是我国实现"碳达峰""碳中和"目标的一项重要措施。塔式太阳能光热发电是一种低碳环保的新型清洁能源技术。定日镜是塔式太阳能光热发电站收集太阳能的基本组件……（含完整题面与公式）：参考 `../2023A/problem.md`，本目录在题面层面与之等价。

## v2 本轮特别提醒（来自上轮现场复审）

1. **Q3 必须真实满足 60 MW 约束**——上轮跑出 124.04 MW 远超额定值 1 倍，违反题面"达到额定功率条件下"。本轮 v2.0 多了 `outputs/constraint_checks.json`，会强制校验每条题面约束≥/≤/=。请按"≥ 60 MW 但最好贴近 60 MW"做目标。
2. **Q2/Q3 必须在 `paper/main.tex` 里给出"为什么是这个候选"的对比表**——上轮 DE 输出结果后只交了一个数字，缺少候选淘汰理由。
3. **附件策略**：上轮因 GitHub raw 直链返回 HTTP 451 而改用自合成；本轮允许用 arXiv 公开论文 + 题目公式直接建立场地，并显式在 `research.md` 的 `Data Provenance` 段注明"合成而非真实下载"。
4. **中文字体**：本轮模板自带 `\setCJKmainfont{SimSun}` + XeLaTeX；请在 paper 中显式声明编译命令 `xelatex -interaction=nonstopmode`，outputs/figures 路径也由模板统一。
5. **结果追溯**：所有论文数字必须能在 `outputs/result_contract.json` 里查到 TeX 文本、参数、随机种子、对应 code 路径。

## 题面关键参数（与上轮一致）

- 中心东经 98.5°，北纬 39.4°，海拔 3000 m，半径 350 m
- 吸收塔 80 m，集热器 8 m × 7 m 圆柱形
- 100 m 内不安装镜，镜面 2–8 m，安装高度 2–6 m
- 邻镜中心距 ≥ 镜宽 + 5 m
- 时点：每月 21 日 9:00/10:30/12:00/13:30/15:00 共 60 时点

## 三个问题（题目要求）

### 问题 1
固定塔中心、所有镜面 6×6 m、安装高度 4 m，给定所有定日镜中心位置（附件）。计算 **年平均光学效率、年平均输出热功率 (MW)、单位镜面面积年平均输出热功率 (W/m²)**。填表 1（按月）+ 表 2（年）。

### 问题 2
额定功率 ≥ 60 MW。所有定日镜尺寸 + 安装高度相同。请设计：吸收塔位置、镜面尺寸、安装高度、镜数目、镜位置，最大化单位面积输出热功率。填表 1/2/3，并导出 `result2.xlsx`。

### 问题 3
同额定功率约束。**镜尺寸 + 安装高度可异构**。重新设计最大化单位面积输出热功率。填表 1/2/3，导出 `result3.xlsx`。

## 提交物（按 v2.0 Directory Contract）

```
2023A_v2/
  research/research.md    # 阶段 1+2 记录，含 Data Provenance
  paper/main.tex + paper/main.pdf
  paper/writer.md
  code/*.py + code/code.md
  figures/*.png|pdf
  outputs/
    main.tex + main.pdf
    README.md
    manifest.md
    AI_USAGE.md
    git-log.txt
    git-status-final.txt
    SHA256SUMS.txt
    result_contract.json
    constraint_checks.json
    figure_manifest.json
    result1.xlsx
    result2.xlsx
    result3.xlsx
    result_summary.xlsx
  tests/evidence/        # 留空（v2.0 收回归档用）
```

## v2.0 强约束

- **每阶段 commit**：格式 `stage(N): ...`（N=1..6），并把 SHA 写入对应阶段 MD
- **CRITICAL/MAJOR 不关闭禁止进 stage 6**
- `outputs/main.pdf` 若缺失，必须在 `outputs/README.md` 与 `outputs/manifest.md` 显眼披露
- 中文字体必须用模板给的 `\setCJKmainfont{SimSun}` + XeLaTeX，**不要**退回到 pdfLaTeX
