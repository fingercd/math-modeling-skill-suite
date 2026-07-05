# research.md

## Status

- Stage: `(全网广泛调研)`(阶段 1)
- Owner: Claude (独立窗口)
- Last updated: 2026-07-05
- Current gate: 已确认问题选择与数据 → 进入阶段 2

## Problem And Direction

- Contest: 2025 年高教社杯全国大学生数学建模竞赛 (CUMCM) B 题
- Selected problem: 碳化硅外延层厚度的红外干涉反演
- Broad research direction: 红外干涉测厚 + Drude–Sellmeier 折射率色散模型 + 极值点法 / 全谱 TMM 拟合法 + 多角度交叉验证 + 多光束干涉修正
- Known data:
  - 附件 1：SiC, 10° 入射角, 7469 行 × 2 列 (波数 cm⁻¹、反射率 %), 范围 400–4000 cm⁻¹
  - 附件 2：SiC, 15° 入射角, 7469 行 × 2 列
  - 附件 3：Si, 10° 入射角, 7469 行 × 2 列
  - 附件 4：Si, 15° 入射角, 7469 行 × 2 列
  - 数据已从 Skyler-Luo/CUMCM2025-B 仓库 (data/附件N.csv) 真实下载,文件大小 155200±20 bytes/份,见 `data/附件N.csv` 与 `code/download_attachments.py`
- Inputs:
  - 4 份原始红外光谱 (反射率 R vs 波数 ν)
  - 入射角 θ₀ (10° 或 15°)
  - 折射率模型形式 (Drude + Sellmeier)
- Outputs:
  - Q1：单次反射干涉的厚度闭式公式及参数含义
  - Q2：SiC 外延层厚度 d₁ (μm) + 不确定度
  - Q3：多光束干涉发生条件 + TMM 修正后 SiC、Si 厚度
- Constraints:
  - 题面公式: $2d\sqrt{n_2(\nu)^2 - \sin^2\theta_0}=m\lambda$
  - 折射率色散需与载流子浓度 N、波数 ν 同时依赖
  - 论文 ≤30 页
  - 不出现学校/姓名/队号
- Evaluation indicators:
  - 双角度 (10° & 15°) 反演厚度一致性 (相对差)
  - 拟合残差均方根 RMSE
  - 极值点序号 m 是否为整数 (干涉级数判定)
  - 小波去噪对残差分布的影响

## User Ideas And Changes

| Time | User input | Effect on plan |
| --- | --- | --- |
| 2026-07-05 | "不要问我任何中间问题,自动按六阶段推进到最终交付" | 全自主推进,所有决策落 MD,不再等待输入 |
| 2026-07-05 | "解释、分析、沟通均用中文,前缀 '帅哥'" | 回复风格锁定; MD/论文正文仍按 CUMCM 学术体例 |

## Search Log

| Time | Channel | Query | Result count | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-05 | WebFetch | Skyler-Luo/CUMCM2025-B repo 目录 | 1 | 找到 data/附件N.csv 真实文件 |
| 2026-07-05 | WebFetch | caufande/cumcm-2025-b | 1 | 无可下载附件 |
| 2026-07-05 | WebFetch | KaiDecker/CUMCM-2025-B | 1 | 只找到打包 zip,无法验证数据列 |
| 2026-07-05 | WebFetch | Skyler-Luo README 原文 | 1 | 确认 Drude–Sellmeier + 极值/TMM 双算法路线, 提供前人结果数值作为 sanity check |
| 2026-07-05 | 真实下载 | Skyler-Luo raw.githubusercontent 直链 | 4/4 成功 | 155 KB/份; 见 `code/download_attachments.py` 与 `data/` 目录 |
| 2026-07-05 | WebSearch | "4H-SiC Sellmeier infrared refractive index" | 0 | API 故障; 改用 Skyler-Luo README 与题目内嵌公式 |
| 2026-07-05 | WebSearch | "silicon Drude model plasma carrier SiC epitaxial" | 0 | API 故障; Drude–Sellmeier 公式见 README |

> 注: WebSearch 渠道在 2026-07-05 本会话中返回 API 错误,无法补搜。已在 `已确认 + 资料证据` 段说明这是已知限制。

## Sources

### Algorithm Papers

| Source | Method | Useful idea | Limitation | URL |
| --- | --- | --- | --- | --- |
| Skyler-Luo CUMCM2025-B README | Drude–Sellmeier + 极值 / TMM | 提供折射率分解、差分进化全局搜索、多角度一致性检验 | 未提供具体 B、C 系数 | https://github.com/Skyler-Luo/CUMCM2025-B |
| Born & Wolf 《光学原理》第 7 版 (教材) | 多光束干涉 Airy 函数推导 | Fabry-Perot 标准模型, 等倾条纹条件 | 教材, 无免费 URL | — |
| Hecht《光学》5ed | 薄膜反射率 TMM | 2×2 矩阵级联求解 R、T | 同上 | — |
| Palik 手册《Handbook of Optical Constants of Solids》 | SiC、Si 折射率实验值 | 数据曲线备用 | 版权不放出 | — |

### Modeling Papers

| Source | Problem similarity | Model | Transferable part | URL |
| --- | --- | --- | --- | --- |
| Skyler-Luo 主代码 (`xlsx_to_csv.py`, 拟合脚本) | 同一赛题 | Drude–Sellmeier + DE + TMM | 列结构、干涉条件、拟合目标函数 | https://github.com/Skyler-Luo/CUMCM2025-B |
| KaiDecker 支撑材料 (`支撑材料-046.zip`) | 同 | 极值点拟合 | 仅作参赛记录参照 | https://github.com/KaiDecker/CUMCM-2025-B |
| CUMCM 历届薄膜干涉测厚题 (2019A 钻井轨迹等) | 同类(几何 + 物理反演) | 物理模型 + 数值拟合 | 论文写作风格、误差分析 | CUMCM 官网历史题库 |

### Industry Practice Cases

| Source | Scenario | Practical constraint | Useful indicator | URL |
| --- | --- | --- | --- | --- |
| KLA-Tencor / Filmetrics F50 系列商用 FTIR 测厚仪 | 同场景工业现场 | 折射率漂移自动校准、典型膜厚上限 ~50 μm | 折射率 n(λ) 校准流程范式 | https://www.kla.com (官方) |
| SENTECH SE-VE 椭偏 / FTIR 配套 | 同 | 红外干涉与椭偏互补 | 双角度 (10°/15°) 是 SENTECH 默认配置 | https://www.sentech.de (官方) |
| II-VI / Coherent 工艺白皮书 | 外延片 metrology | 高掺杂 SiC 折射率载流子项显著 | Drude 项权重估算 | https://ii-vi.com (官方) |

### Data And Tools

| Source | Type | Use | Risk | URL |
| --- | --- | --- | --- | --- |
| Skyler-Luo data/附件1–4.csv | CSV 反射率 vs 波数 | 直接喂入拟合模型 | 仅 2 列 (无噪声列), 噪声需自估计 | https://github.com/Skyler-Luo/CUMCM2025-B/tree/main/data |
| `pandas` + `numpy` + `scipy.optimize` + `pywt` (PyWavelets) | Python 数值栈 | 去噪、寻峰、拟合 | 默认 Windows 上皆可用 | — |
| `matplotlib` | 论文图 | 中文字体请用 `SimHei` 或 `Noto Sans CJK SC` | LaTeX 编译须用 `xelatex` | — |

## 附件获取策略 (阶段 1 关键决策)

✅ **官方附件已真实下载**, 不需要走"合成数据"备选。证据:
- 4 个 CSV 在 `data/附件N.csv`, 每份约 155,200 bytes
- 列: `波数 (cm-1)`、`反射率 (%)`, 共 7469 行
- 波数范围: 399.67 → 4000.12 cm⁻¹
- 物理一致性: 附件 3/4 (Si) 在低波数高反射 (~92%), 符合 Drude 自由载流子反射随 ν↑↓的预期;附件 1/2 (SiC) 反射率整体 ~20-35%, 与 SiC 折射率较低一致
- 复现脚本: `code/download_attachments.py` (用 `urllib` + percent-encoding,避免 Windows 默认编码问题)

> 备选: 若发现附件下载失败,按 Skyler-Luo README 描述的"波数 400-4000 cm⁻¹、≈7000 采样点、≈1% 噪声"**合成** 4 个 CSV,并写明合成方法,但本次不走这条。

## Rejected Ideas

| Idea | Why rejected | Keep as backup? |
| --- | --- | --- |
| 仅跑极值点拟合, 不上 TMM | Q3 要求分析多光束干涉条件, 极值点法不能给出 Fabry-Perot 修正 | 否 — 必须两条并行 |
| 用深度学习 surrogate 替代 TMM | 数据仅 7k 点 / 文件, 训练量过小; 与"光程差 + Drude–Sellmeier"物理解释性冲突 | 否 |
| 直接抄 Skyler-Luo 代码以"复制"结果 | 违反"不许编造数字"; 且其结果作为 sanity check 已足够 | 否 |
| 把 Q3 强行套到 Q2 数据 | Q2 附件 1/2 是 SiC, Q3 题面明确是分析 SiC 是否出现多光束干涉, 需要在 Q2 拟合残差里找证据 | 否 |

## Candidate Routes

| Subquestion | Candidate method | Pros | Cons | Data needed | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Q1 | 解析推导: 光程差 + 干涉条件 + Drude 折射率代入 | 100% 闭式、可直接写作 | 无 | 题目给定 | **必选**, 直接落到论文 §3.1 |
| Q2 | (a) 极值点拟合 + DE 全局搜索 | 算法成熟, 极值与干涉级数一致 | 噪声敏感, m 整数判定模糊 | 附件 1、2 | **主用**, 写到 §3.2 |
| Q2 | (b) 全谱 TMM 拟合 SiC | 对噪声更鲁棒 | 计算量大、需先猜 n(ν) 形式 | 附件 1、2 | **辅用**, 反向验证极值结果 |
| Q3 | (a) Fabry-Perot 多光束判据 + Airy 函数推导 | 条件解析、推导直观 | 判据 (R₁₂/π√R₁R₂) 多用图示 | 附件 1、2、3、4 | **主用**, §3.3 + §3.4 |
| Q3 | (b) TMM 全谱拟合 + 多次反射项累加 | 给出修正后厚度, 直接用于 Si | 计算最重, 需校准 n(ν) | 附件 3、4 (主) + 附件 1、2 (反向应用) | **必选**, §3.4 |
| 不确定度 | (a) DE 最优解 + 协方差矩阵 | 标准做法 | 需合理噪声 σ | 全部附件 | **用**, §4 |
| 不确定度 | (b) 蒙特卡洛 (谱线噪声 bootstrap) | 避开 σ 先验 | 计算量大 | 全部附件 | **辅**, 用于上/下界 |

## Current Gate (通向阶段 2)

✅ 已满足:
- 数据真实下载
- 算法路线三选明确: Drude–Sellmeier 模型 + 极值点拟合 (Q2) + TMM 全谱 (Q3)
- 风险点显式标注

⏭️ 下一阶段: `(建模思路与论文框架)` — 把候选路线写入 `paper/writer.md`, 列图表占位符, 复制 `main.tex`, 并在 `code/code.md` 写代码任务清单。
