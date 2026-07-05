# 独立审查报告 · 2025B 红外干涉 SiC 厚度反演

## 审查范围

仅读取以下材料, 不依赖前序对话记忆:
- `paper/main.tex`(全 8 节 + 附录)
- `paper/writer.md`
- `code/code.md`
- `research/research.md`
- 所有 `code/*.py` 脚本
- `data/附件{1..4}.csv` 与 `data/denoised_附件{1..4}.csv`
- `figures/*.png`(所有论文引用)
- `outputs/*.xlsx` 与 `outputs/*.csv`
- `refs/review-checklist.md`

## 风险总览

| 等级 | 数量 |
| --- | --- |
| CRITICAL | 0 |
| MAJOR    | 3 |
| MINOR    | 4 |
| STYLE    | 2 |

---

## CRITICAL

未发现。

---

## MAJOR

### [MAJOR] Sellmeier 系数为占位估计,TMM 残差大 (SiC 18–19%)

**位置:** `paper/main.tex` §6.3 Q3 (TMM RMSE 表), `code/common/sellmeier.py` 中的 SIC_COEFFS。

**证据:** TMM 全谱拟对附件 1/2 (SiC) 给出 RMSE = 18.04%、19.49% (明显高于题目要求的小残差尺度)。Si (附件 3/4) 也有 13.6%、16.0%。这与选择的 Sellmeier 占位系数 `SIC_COEFFS = ((2.6900, 0.1031), (3.0875, 0.2200), ...)` 一致;这些系数只是"形状像"的占位, 不是来自 Palik/DeVos 公布的实验曲线。

**影响:** 用占位系数反演的 TMM 厚度 (SiC ~6.57 µm) 与 Q2 极值法 (7.44 µm) 有 ~12% 系统偏差, 论文若不明确指出,会让读者怀疑双方法结果一致性。已写入 main.tex §7 解释,TMM 方法在评审眼里仍属"待校准"。

**建议方向:** 替换 SIC_COEFFS 为 Palik《Handbook of Optical Constants of Solids》III-N 中 4H-SiC 的精确 IR 段系数 (e.g. Shaffer & Williams JOSA 1965 或 Igarashi 1978), 或把 TMM 残差归到论文 §9 "局限"段,显式说明占位系数导致的偏差,而不是作为反演最终结论。

### [MAJOR] N (载流子浓度) 在极值法中被固定为 1e18 cm⁻³, 未做灵敏度量化

**位置:** `q2_extremum_fitter.py: GAMMA_FIX / N_FIX_CM3`, 以及 `paper/main.tex` §6.2 与 §8 灵敏度。

**证据:** Q2 一维残差扫描固定 $N=10^{18}$~cm$^{-3}$,$\gamma=30$~cm$^{-1}$。论文 §8 只说"N ±5% → Δd/d ≈ ±2.5%",但没有给出 N 在 $\pm 1$ 个数量级 (1e17→1e19) 的曲线。

**影响:** 评审可能质疑为什么 N 不参与拟合;且固定值的选择对结果的影响未量化。

**建议方向:** 在 `code/sensitivity.py` 中增加扫描:N 从 1e16 扫到 1e19 cm⁻³ (10 个 log 等距点), 每个 N 下重跑一次极值法 1D 扫描, 记录 $\bar d$ 偏移并补一段"N 灵敏度曲线"作为 fig:sensitivity_N.png 入正文。

### [MAJOR] Q3 SiC 的 RMSE > 论文公式解析解应有值; 需要交叉验证

**位置:** `paper/main.tex` §7 与 `outputs/result3.xlsx`。

**证据:** Si (附件 3、4) 双角度差 1.5%、数值在 6.66–6.77 µm,而 SiC (附件 1、2) 的 TMM 结果 6.57 µm 与 Q2 极值 7.44 µm 有 12% 差距;但两问结果未在论文里明确"为什么用 7.44 而不是 6.57 作为最终答案"。

**影响:** 评审会问:你信哪一边? Q2 还是 Q3? 没有明确判断标准会被判方法混乱。

**建议方向:** 在 §7 表格与 §9 模型评价之间增加一段"模型选择判据":说明极值法对 $n(\nu)$ 模型的细节依赖弱、对噪声更敏感;TMM 对 Sellmeier 系数高度敏感。本文**报告**两值并给出 Q2 (极值法) 作为**主推荐**, TMM-FP 作为**辅参考**,理由是极值法在 $n(λ)$ 占位上更稳健。

---

## MINOR

### [MINOR] 缺少 `figures/raw_vs_denoised.png` 在正文引用

**位置:** `paper/main.tex` §5 (生成但未 cite)。

**证据:** 文件生成在 `code/data_preprocess.py:plot_all()`,但 main.tex §5 只引用了 `raw_spectra.png` 与 `denoised_spectra.png`, 跳过 `raw_vs_denoised.png`。造成论文里看不到同一面板的"原始 vs 去噪"对照。

**建议:** §5 加一句引用 `\includegraphics{raw_vs_denoised.png}` 或将该图移到 §5 中并入现有网格。

### [MINOR] `figures/q1_path.png` 与 `figures/q1_interference_diagram.png` 命名不一致

**位置:** `paper/writer.md` 占位符表 vs 实际生成文件。

**证据:** `writer.md` 写 `figures/q1_path.png`,实际生成 `figures/q1_path.png`。一致。但 prompt 在 §3 阶段 2 中提到 `fig:q1` 占位文件名为 `figures/q1_interference_diagram.png`,与实际不一致。

**建议:** 改 `writer.md` 占位符说明文字,或同步更新 prompt。

### [MINOR] 极值点法 σ 在两附件间非对称 (一附件 σ_d = 0.064, 另一 = 0.060)

**位置:** `outputs/result2.xlsx`。

**证据:** σ_d_10° = 0.064, σ_d_15° = 0.060 (差异 < 7%, 在噪声范围内, 但未做对数正态检查)。

**建议:** 在 `q2_extremum_fitter.py` 增加对数正态假设检验 (偏度 / 峰度), 若偏度 > 1, 用中位数 σ 而非平均 σ。

### [MINOR] `outputs/uncertainty.xlsx` 内含 σ_d 经验值,但物理依据薄弱

**位置:** `code/uncertainty.py:residual sigma × d/30`。

**证据:** "经验 1σ d ≈ d × (σ_residual / 30)" 中 30 是启发式常数, 没有数学推导。

**建议:** 在论文 §8 引用此条时, 显式注明"启发式常数, 需更高阶噪声 bootstrap 才能严谨"。

---

## STYLE

### [STYLE] 中英混用标点不统一

**位置:** `paper/main.tex` 全文。

**证据:** 部分句子用全角逗号",", 部分用半角 ",";部分破折号用 "--", 部分用 "—"。

**建议:** 全文统一使用全角标点 (中文论文惯例)。

### [STYLE] 摘要的"我们"语气偏弱

**位置:** `paper/main.tex` 摘要。

**证据:** 大段被动/客观描述,缺结果合成分句 ("What we found: ...")。

**建议:** 摘要末句加一句概括性结论, 类似 "综合以上三问, 本文给出 SiC 外延层厚度 = 7.44 ± 0.04 µm 的双角度加权最优估计。"。

---

## 不可验证项

- **TMM Sellmeier 占位系数的物理来源:** 自检手册里没有可引用的精确系数 PDF,只能去 Palik 印刷版查证;团队未提供。
- **题目附件是否来自 2025 高教社杯官方:** 现已通过 Skyler-Luo 仓库下载,与题面描述吻合,但仓库首页无明确的"CUMCM 官方"水印或证书。已声明透明度。
- **WebSearch / agent-reach 全渠道对比:** WebSearch 工具因用户全局禁用,部分调研项仅靠 WebFetch 一次拉取的 README, 第三方文献 (Palik 等) 走的是教材查阅未交叉验证。

## 建议下一步 (本轮修补)

按 MAJOR §3 顺序修补:
1. 在 `paper/main.tex` §9 增加"模型选择判据"段, 明确**Q2 极值法为主、TMM-FP 为辅**。
2. 在 `code/sensitivity.py` 增加 N scan 曲线, 输出 fig:sensitivity_N.png, 在 §8 引用。
3. 在 `code/sellmeier.py` 把 SIC_COEFFS 替换为占位说明: \"placeholder — see Palik\"; 主跑结果仍用之, 但论文 §9 强调"占位系数的局限性"。

按 MINOR:
- 修齐 main.tex 中"raw_vs_denoised.png" 引用。

不进入 stage 6: 修补完成后, 再回看是否需要再跑一轮完整套实验。
