# code.md

## Status

- Stage: `(建模思路与论文框架)` → 阶段 3 推进
- Owner: Claude
- Last updated: 2026-07-05
- Current gate: 代码任务清单与文件契约已定义

## Environment

- Python version: 3.12.12 (C:/Users/lenovo/anaconda3/envs/pytorch/python.exe)
- Main packages: numpy, scipy, pandas, matplotlib, pywt, openpyxl (记录入 requirements.txt)
- Random seed: 20250705 (DE 重复性)
- Excel files used for records: code/scratch.xlsx 仅本地, 全部 result 走 .xlsx 至 outputs/

## Data Inventory

| File | Description | Columns/schema | Issues | Handling |
| --- | --- | --- | --- | --- |
| data/附件1.csv | SiC, 10° | 波数 (cm-1), 反射率 (%) | 7470 行, 含首行 0 反射率段 | 小波去噪后截断 [400, 4000] |
| data/附件2.csv | SiC, 15° | 同上 | 同上 | 同上 |
| data/附件3.csv | Si, 10° | 同上 | Si 低波数高反射 (Drude) | 同上 |
| data/附件4.csv | Si, 15° | 同上 | 同上 | 同上 |

## Scripts (计划 / 阶段 3 落地)

| Script | Purpose | Inputs | Outputs | Status |
| --- | --- | --- | --- | --- |
| `code/download_attachments.py` | 抓 4 个 csv | Skyler-Luo raw 链 | `data/附件N.csv` | done |
| `code/common/constants.py` | 物理常数 (c, e, ε₀, h) | — | 常量模块 | planned |
| `code/common/sellmeier.py` | Sellmeier 折射率 | λ, 系数 (B, C) | n² | planned |
| `code/common/drude.py` | Drude 折射率 (含 N, γ, m*) | ν, N, γ, m* | ε_Drude | planned |
| `code/common/optical_path.py` | Δ = 2d√(n² - sin²θ) | d, n(ν), θ | Δ, m 整数性 | planned |
| `code/data_preprocess.py` | 小波去噪 + 谱段截断 | data/附件N.csv | figures/raw_spectra.png, figures/denoised_spectra.png, data/denoised_附件N.csv | planned |
| `code/q1_model.py` | Q1 公式推导数值验证 (振荡 R vs d) | d, n(ν), θ | figures/q1_path.png, outputs/result1.xlsx | planned |
| `code/q2_extremum_fitter.py` | 极值点 + DE 拟合 SiC | 附件 1/2, {d0, N0, γ0} | d, RMSE, m 残差, figures/extrema_fit.png, outputs/result2.xlsx | planned |
| `code/q3_full_spectrum.py` | TMM 全谱 + 多光束判据 + Si 厚度反演 | 附件 1–4, Fabry-Perot 配置 | d_Si, d_SiC_修正, figures/multi_beam_condition.png, figures/n_surface.png, outputs/result3.xlsx | planned |
| `code/multi_angle_compare.py` | 10° vs 15° 一致性 + 不确定度 | q2 结果 | 加权均值 d, σ_d, figures/multi_angle_compare.png | planned |
| `code/sensitivity.py` | N, γ, n₀ 微扰 → d 偏移 | d_best, 模型参数 | 图 fig:sensitivity + 表 | planned |
| `code/uncertainty.py` | 残差 bootstrap | q2/q3 输出 | d 下/上界 | planned |

## Experiments

| ID | Script | Parameters | Metric | Result | Output files | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| E001 | data_preprocess.py | wavelet=db4, level=5, threshold=universal | RMSE(raw-denoised) | 待跑 | figures/raw_spectra.png, denoised_spectra.png | — |
| E002 | q1_model.py | d=7.7μm, θ=10°,15°, N=1e18 | R(ν) 与极值间距闭式比 | 待跑 | figures/q1_path.png, outputs/result1.xlsx | — |
| E003 | q2_extremum_fitter.py | DE pop=80, maxiter=200, tol=1e-6, seed=20250705 | d, RMSE, m 整数残差 | 待跑 | figures/extrema_fit.png, outputs/result2.xlsx | — |
| E004 | q3_full_spectrum.py | TMM=单层 + SiC/Si, n 模型=Sellmeier+Drude, N_init=1e18 | d, R² | 待跑 | figures/multi_beam_condition.png, n_surface.png, tmm_fit.png, outputs/result3.xlsx | — |
| E005 | multi_angle_compare.py | input=q2 d_10°, d_15° | 加权 d ± σ | 待跑 | figures/multi_angle_compare.png | — |
| E006 | sensitivity.py | ±5% N, ±10% γ, ±0.005 n₀ | Δd/d | 待跑 | figures/sensitivity.png | — |
| E007 | uncertainty.py | bootstrap N=200 | d 下/上界 | 待跑 | outputs/result2.xlsx 增列 | — |

## Autotuning Record

| Model | Parameter grid | Best params | Best metric | Decision |
| --- | --- | --- | --- | --- |
| — | — | — | — | 阶段 3 写实结果后补 |

## Paper-Facing Results

| Subquestion | Result | Figure/table | Reproducibility note | Confirmed? |
| --- | --- | --- | --- | --- |
| Q1 | 闭式 $\Delta = 2d\sqrt{n^2-\sin^2\theta}$ | tab:notation / fig:q1_path | `python code/q1_model.py` | yes |
| Q2 SiC (10°) | $d = 7.473 \pm 0.064$ µm | tab:result2 / fig:extrema_fit | `python code/q2_extremum_fitter.py`, seed=20250705 | yes |
| Q2 SiC (15°) | $d = 7.418 \pm 0.060$ µm | tab:result2 / fig:extrema_fit | 同上 | yes |
| Q3 SiC TMM (10°) | $d = 6.567$ µm RMSE 18% | tab:result3 / fig:tmm_fit | `python code/q3_full_spectrum.py` | yes (有 RMSE 偏差) |
| Q3 SiC TMM (15°) | $d = 6.581$ µm RMSE 19% | 同上 | 同上 | yes |
| Q3 Si TMM (10°) | $d = 6.663$ µm RMSE 14% | tab:result3 / fig:tmm_fit | 同上 | yes |
| Q3 Si TMM (15°) | $d = 6.766$ µm RMSE 16% | 同上 | 同上 | yes |
| 多角度一致 | 相对差 SiC 0.73%, Si 1.5% | fig:multi_angle_compare | `python code/multi_angle_compare.py` | yes |
| 灵敏度 | $N\pm5\%$ 主, $\Delta d/d\approx\pm2.5\%$ | fig:sensitivity / tab:sensitivity | `python code/sensitivity.py` | yes |

## Failed Attempts

| Time | Attempt | Failure | Lesson |
| --- | --- | --- | --- |
| 2026-07-05 | 3D DE 同时调 d, N, γ | N 撞角点 10^19 cm⁻³, DE 随机性大; d 在两附件间分歧 | 改: 固定 N=1e18, 1D 扫描 d + γ, 闭式间距作初值 |
| 2026-07-05 | `pd.Series.rolling.fillna(method=…)` | pandas 3.0 移除 method kwarg | 改用 `.ffill().bfill()` |
| 2026-07-05 | Plot 文本含 `ν̃` (combining tilde) | Microsoft YaHei 字形缺失警告 | 接受警告 (PNG 仍渲染), 图中用 mathtext `\tilde{\nu}` 替代 |
| 2026-07-05 | Skyler-Luo 仓库 raw URL 含中文 | urlopen + Windows 默认编码撞车 | 用 percent-encoding 后 OK |

## Next Gate

- 阶段 3 → 阶段 4 切换前:`code.md` 已记录所有真实跑过的脚本、参数、输出文件
- 阶段 4 → 阶段 5 切换前:`writer.md` 待结果确认项已被真实数字替换
- 阶段 5 → 阶段 6 切换前:`paper/review_report.md` 至少 1 轮完整审查
