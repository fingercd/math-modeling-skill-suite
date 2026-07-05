# 2025 年高教社杯全国大学生数学建模竞赛 B 题 · v2 复跑版

> 第二轮 skill v2.0 压力测试。本目录在题面层面与 `../2025B/problem.md` 等价；本轮新增约束以 prompt.md 为准。

## v2 本轮特别提醒（来自上轮现场复审）

1. **Sellmeier / Drude 系数**：上轮使用占位系数（与 Palik 手册实验曲线有差距），导致 TMM 残差 13-19%。本轮 v2.0 prompt 强制要求：先在 `research/research.md` 的 `Data Provenance` 段写明系数来源；如果仍使用占位，必须显式承认"系数的局限性"，并在论文 §7 / §9 把 Q2（极值法）与 Q3（TMM-FP）结果**明确选其一作为主推荐**，给出选择判据。
2. **Q2 与 Q3 厚度差 12% 的处理**：上轮给出 7.44 µm（极值）与 6.57 µm（TMM），**未给出主推荐判据**。本轮 prompt 强制：必须在论文 §7 与 §9 写"模型选择判据"段，**选一个**作为论文最终答案，**另一个**作辅参考并解释为什么。
3. **N（载流子浓度）扫描**：上轮固定 N=1e18；本轮要求 N ∈ [1e16, 1e19]（10 个 log 等距点）的曲线写入 `outputs/sensitivity_N.xlsx` 与 `figures/sensitivity_N.png`，并在 §灵敏度分析 引用。
4. **中文字体**：v2.0 模板自带 `\setCJKmainfont{SimSun}` + XeLaTeX。
5. **结果追溯**：每数字 → `result_contract.json` → code 路径 + 种子 + 参数。

## 题面核心要点（与上轮一致）

碳化硅（SiC）外延层厚度红外干涉反演：
- Q1：单次反射/透射干涉闭式公式 + 数值验证
- Q2：对附件 1/2（SiC, 10°/15°）求厚度 + 不确定度
- Q3：多光束干涉判据 + 附件 3/4（Si）TMM 修正 + 反向作用于附件 1/2

输入：4 份红外光谱（波数 cm⁻¹, 反射率 %）· 输出：SiC/Si 厚度 + 不确定度 + 多角度一致性。

## 提交物（v2.0 Directory Contract）

```
2025B_v2/outputs/
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
  multi_angle_summary.xlsx
  sensitivity.xlsx
  sensitivity_N.xlsx
  uncertainty.xlsx
  result1.xlsx  result2.xlsx  result3.xlsx
  result_summary.xlsx
  code/
  figures/
```

## v2.0 强约束

- 每阶段 commit；CRITICAL/MAJOR 不关闭禁 stage 6
- `outputs/main.pdf` 缺失必须显眼披露
- 论文正文 ≤ 30 页；匿名；AI_USAGE.md
- 中文字体用模板自带 SimSun + XeLaTeX
