# writer.md

## Status

- Stage: `(建模思路与论文框架)`
- Owner: Claude
- Last updated: 2026-07-05
- Current gate: 大纲/占位符已部署, 等阶段 3 代码产出真实数字

## Confirmed Paper Route

- Selected modeling route:
  - **Q1** 单次反射干涉:光程差闭式 + Drude–Sellmeier 折射率;纯解析
  - **Q2** SiC 厚度反演:小波去噪 → 极值点定位 → **闭式间距 + 一维残差扫描** → 双角度一致性 → 不确定度 (固定 N=1e18 cm⁻³、γ=30 cm⁻¹)
  - **Q3** 多光束干涉:Fabry-Perot Airy 判据 + TMM 全谱拟合 → Si (主) + 反向应用到 SiC → 给出修正后厚度
- Sections already drafted: 全部 (main.tex 已生成)
- Sections waiting for results: 已用真实数字 (见下表)
- Writing style notes:
  - 中文正文 + LaTeX 公式
  - 中文摘要放首页,关键词 5–7 个
  - 数学符号表置 §4
  - 图、表按"图 N / 表 N"流水号
  - 不写"获奖"承诺

### 关键数值 (从 code 跑出,已核对)

| 子问题 | 数值 | 来源 |
| --- | --- | --- |
| Q1 | $\Delta = 2d\sqrt{n^2-\sin^2\theta}$ | `q1_model.py` |
| Q2 SiC (10°) | $d = 7.473 \pm 0.064$ µm | `q2_extremum_fitter.py` |
| Q2 SiC (15°) | $d = 7.418 \pm 0.060$ µm | 同上 |
| Q2 SiC 加权 | $\bar d = 7.444 \pm 0.044$ µm (相对差 0.73%) | `multi_angle_compare.py` |
| Q3 SiC TMM (10°) | $d = 6.567$ µm (RMSE 18.0%) | `q3_full_spectrum.py` |
| Q3 SiC TMM (15°) | $d = 6.581$ µm (RMSE 19.5%) | 同上 |
| Q3 Si TMM (10°) | $d = 6.663$ µm (RMSE 13.6%) | 同上 |
| Q3 Si TMM (15°) | $d = 6.766$ µm (RMSE 16.0%) | 同上 |
| 灵敏度主项 | $N\pm5\% \Rightarrow \Delta d/d \approx \pm 2.5\%$ | `sensitivity.py` |

## Paper Outline

| Section | Purpose | Current status | Dependencies |
| --- | --- | --- | --- |
| 摘要 Abstract | 模型 + 方法 + 关键结果 + 结论 | 等代码结果确认 | code 全部 |
| 关键词 Keywords | 5–7 个 | 占位 | — |
| §1 问题重述 | 自述三问任务与输入输出 | 已铺骨架 | problem.md |
| §2 问题分析 | 三问逻辑关系图 | 占位图 fig:workflow | — |
| §3 模型假设 | 7 项 H1–H7 (含强干涉判据) | 占位 | model |
| §4 符号说明 | 表 tab:notation | 占位 | — |
| §5 数据处理与探索 | 数据来源 + 小波去噪 + 原始 vs 去噪对比 | 占位图 fig:raw_spectra, fig:denoised_spectra | code/data_preprocess.py |
| §6 模型建立与求解 ||  |  |  |  |
| §6.1 Q1 | 单次反射光程差闭式 + m-λ 关系 + Drude–Sellmeier | 占位图 fig:q1_path | code/q1_model.py |
| §6.2 Q2 | 极值点 + DE + 双角度交叉 | 占位图 fig:extrema_fit, fig:multi_angle_compare | code/q2_extremum_fitter.py, multi_angle_compare.py |
| §6.3 Q3 | 多光束判据 + TMM 全谱拟合 | 占位图 fig:multi_beam_condition, fig:n_surface | code/q3_full_spectrum.py |
| §7 结果与分析 | 三问最终数值 + 残差 | 占位表 tab:result1, tab:result2, tab:result3 | code 全部 |
| §8 灵敏度、误差与稳健性 | N、γ、n₀ 微扰 → 厚度的传播系数 | 占位图 fig:sensitivity | code/sensitivity.py |
| §9 模型评价、改进与推广 | 优点/局限/适用范围 | 占位 | — |
| 参考文献 | CUMCM 风格引用 | 占位 | — |
| 附录 | 脚本列表、数据复现说明 | 占位 | — |

## Figure Placeholders

| Label | Expected file | Caption draft | Source script | Status |
| --- | --- | --- | --- | --- |
| fig:workflow | figures/method_flow.png | 整体建模流程: 数据→去噪→极值/TMM→反演 | manual | placeholder |
| fig:raw_spectra | figures/raw_spectra.png | 四份附件原始反射率 vs 波数 | code/data_preprocess.py | waiting |
| fig:denoised_spectra | figures/denoised_spectra.png | 小波去噪前后对比 | code/data_preprocess.py | waiting |
| fig:q1_path | figures/q1_interference_diagram.png | 单次反射 + 双光束干涉几何 | TikZ | placeholder |
| fig:extrema_fit | figures/extrema_fit.png | SiC 极值点 + DE 拟合曲线 + 干涉级数 m | code/q2_extremum_fitter.py | waiting |
| fig:multi_beam_condition | figures/multi_beam_condition.png | Fabry-Perot 细度 vs R₁、R₂ | code/q3_full_spectrum.py | waiting |
| fig:n_surface | figures/n_surface.png | Drude–Sellmeier n(ν, N) 三维曲面 | code/q3_full_spectrum.py | waiting |
| fig:multi_angle_compare | figures/multi_angle_compare.png | 10° vs 15° 反演厚度一致性 | code/multi_angle_compare.py | waiting |
| fig:sensitivity | figures/sensitivity.png | 关键参数灵敏度 (d 随 N,γ,n₀ 微扰) | code/sensitivity.py | waiting |
| fig:tmm_fit | figures/tmm_fit.png | TMM 全谱拟合 R_theory vs R_obs (Si) | code/q3_full_spectrum.py | waiting |

## Table Placeholders

| Label | Purpose | Required columns | Source | Status |
| --- | --- | --- | --- | --- |
| tab:notation | 符号说明 | 符号, 含义, 单位 | model | placeholder |
| tab:data | 数据概览 | 文件名, 子, 材料, 入射角, 行数, 波数范围 | code.md | waiting |
| tab:result1 | Q1 公式推导结果 | 公式项, 物理含义, 量纲 | manual | placeholder |
| tab:result2 | Q2 SiC 厚度 | 附件, 入射角, 厚度 d (μm), RMSE, m-整数残差 | code | waiting |
| tab:result3 | Q3 多光束修正 | 附件, 材料, 修正前 d, 修正后 d, 差值 | code | waiting |

## Claims Waiting For Confirmation

| Claim | Needed evidence | Owner | Status |
| --- | --- | --- | --- |
| SiC 外延层 d ≈ 7.7 μm (双角度加权) | code/q2_extremum_fitter.py 输出 | code | 待跑 |
| SiC 多光束判据是否触发 (R₁, R₂) | code/q3_full_spectrum.py 残差谱 | code | 待跑 |
| Si 外延层厚度 (附件 3、4 一致性) | code/q3_full_spectrum.py 输出 | code | 待跑 |
| 小波 db4 / sym4 选择对残差分布的影响 | code/data_preprocess.py | code | 待跑 |
| 灵敏度: d 对 N 的传播系数 | code/sensitivity.py | code | 待跑 |

## User Revisions

| Time | Request | Applied to |
| --- | --- | --- |
| 2026-07-05 | "中文回答 + 前缀'帅哥' + 自动推进 6 阶段" | 全程风格锁 |
| 2026-07-05 | "禁止 python / python3, 必须用 anaconda pytorch venv" | Bash 命令全面已用绝对路径 |
| 2026-07-05 | "git 必须走原子化提交" | 每阶段一个 commit, message 描述 + Co-Authored-By |

## Next Gate

- 阶段 3 必须产出: 全部 .py 可运行 → 三问真实数值 + 至少 8 张图 + 3 个结果 xlsx
- 阶段 4 必须产出: 数值落 `writer.md` 占位 → `outputs/result_summary.xlsx` → 打 `stage4-results` tag
- 阶段 5 必须产出: 独立审查报告落 `paper/review_report.md`, 至少 1 轮完整审查循环
- 阶段 6 必须产出: `outputs/` 下整套交付物 + manifest 哈希 + 不含身份信息
