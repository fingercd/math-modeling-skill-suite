# 2025B · 红外干涉法反演碳化硅外延层厚度

2025 年高教社杯 (CUMCM) B 题。完整解答论文、复现代码、全部图表、Excel 表格与审查报告。

## 目录结构

```
outputs/
├── main.tex                      # 可编译的论文源 (含全部数学公式 + 图)
├── README.md                     # 本文件
├── manifest.md                   # 文件清单与哈希
├── AI_USAGE.md                   # AI 工具使用披露
├── SHA256SUMS.txt                # 全部交付物的 SHA256
├── code/                         # 全部可运行 Python 源码
│   ├── common/                   # 折射率/光程等共享模块
│   ├── data_preprocess.py        # 小波去噪
│   ├── download_attachments.py   # 抓 4 个附件 CSV
│   ├── q1_model.py               # Q1 闭式公式 + 折射率演示
│   ├── q2_extremum_fitter.py     # Q2 极值点 + 闭式间距 + 1D 扫描
│   ├── q3_full_spectrum.py       # Q3 Airy/TMM 全谱拟合
│   ├── multi_angle_compare.py    # 双角度加权
│   ├── sensitivity.py            # 参数扰动 → Δd/d
│   ├── sensitivity_N.py          # N 扫描 → d 稳定性
│   ├── uncertainty.py            # 残差经验 1σ_d
│   ├── make_result_summary.py    # 汇总 excel
│   ├── run_all.py                # 一键端到端复现
│   └── download_attachments.py
├── figures/                      # 论文使用的全部图 (PNG)
├── result1.xlsx                  # Q1 公式推导结果表
├── result2.xlsx                  # Q2 SiC 厚度与残差
├── result3.xlsx                  # Q3 TMM 全谱反演
├── multi_angle_summary.xlsx      # 多角度加权汇总
├── sensitivity.xlsx              # 参数灵敏度扰动
├── sensitivity_N.xlsx            # N 扫描 d(N)
├── uncertainty.xlsx              # 经验 1σ_d
└── result_summary.xlsx           # 全部结果合并封面
```

## 关键数值

| 子问题 | 结果 |
| --- | --- |
| Q1 闭式 | $\Delta = 2 d\sqrt{n^2-\sin^2\theta}$; $d = m / (2\sqrt{n^2-\sin^2\theta}\,\tilde{\nu})$ |
| Q2 SiC 极值 (10°) | $d = 7.473 \pm 0.064$ µm |
| Q2 SiC 极值 (15°) | $d = 7.418 \pm 0.060$ µm |
| Q2 SiC 加权 | $\bar d = 7.444 \pm 0.044$ µm (相对差 0.73%) |
| Q3 SiC TMM (辅) | $d \approx 6.57$ µm RMSE ~18% (受占位 Sellmeier 影响) |
| Q3 Si TMM | 10°: 6.66 µm, 15°: 6.77 µm (相对差 1.5%) |
| 灵敏度主项 | $N \pm 5\% \Rightarrow \Delta d/d \approx \pm 2.5\%$ |

## 一键复现

环境: Python 3.12+, 安装依赖:

```bash
pip install -r requirements.txt
```

执行完整流水线:

```bash
cd outputs/code
python run_all.py             # 重建所有图 + Excel
python make_result_summary.py # 生成 outputs/result_summary.xlsx
```

复现后所有图表与 Excel 写入 `outputs/figures/` 与 `outputs/` 根。

## LaTeX 编译

推荐 `xelatex` (中文 ctex 套件要求):

```bash
cd outputs
xelatex -interaction=nonstopmode main.tex   # 两次以生成目录
xelatex -interaction=nonstopmode main.tex
```

如未安装 TeX 套件, 直接打开 `main.tex` 即可被任意 LaTeX 编辑器编译。

## 不可验证项与已知局限

- Sellmeier 占位系数: `code/common/sellmeier.py: SIC_COEFFS` 是占位估计, 对 Q3 TMM 残差贡献较大。Q2 极值法对 $n(\tilde\nu)$ 形状依赖弱, 故 Q2 = 7.44 µm 作为本文主推荐值。
- WebSearch 工具按用户全局策略禁用, 调研仅依赖 WebFetch 直链与 README 引用; 文献交叉验证以教材与公开数据为基础。
- TMM Sellmeier 替换请参考 Palik《Handbook of Optical Constants of Solids》SiC/Si 卷。
