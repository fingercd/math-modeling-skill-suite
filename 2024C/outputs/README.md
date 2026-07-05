# outputs/ 最终交付清单

> 本目录是 **2024 年高教社杯 C 题"农作物种植策略"** 的最终交付。
> 所有内容均为自动生成，可按 `manifest.md` 与 `SHA256SUMS.txt` 校验完整性。

## 目录结构

```
outputs/
├── main.tex                 # 论文 TeX 源
├── main.pdf                 # 论文 PDF (如有 xelatex 环境, 编译; 否则只交 .tex)
├── code/                    # 全部可运行 Python 源码
├── figures/                 # 论文引用的全部图
├── result1_1.xlsx           # 问题 1 子问 1 (waste) — 七年种植方案
├── result1_2.xlsx           # 问题 1 子问 2 (discount) — 七年种植方案
├── result2.xlsx             # 问题 2 — 蒙特卡洛 500 场景下稳健方案
├── result3.xlsx             # 问题 3 — 间作 + 替代弹性方案
├── result_summary.xlsx      # 三问核心数字 + 约束校验汇总
├── q1_summary.json          # Q1 数字
├── result2_summary.json     # Q2 数字 (均值, 标准差, CV, min/max)
├── result3_summary.json     # Q3 数字
├── ga_validation.json       # GA 交叉验证: 与贪心解差距 1.4%
├── constraint_check.json    # 13 类约束校验结果
├── result*_long.csv         # 结果长表 (地块, 年, 季, 作物, 亩数)
├── result*_scenarios.csv    # Q2/Q3 蒙特卡洛场景利润
├── README.md                # 本文件
├── manifest.md              # 文件清单 + 字段说明
├── AI_USAGE.md              # AI 工具使用披露
└── SHA256SUMS.txt           # 全部文件 SHA-256 校验
```

## 三问核心结果

| 子问题 | 7 年累计净利润 | 关键指标 |
| --- | --- | --- |
| Q1 子问 1 (waste) | **1106.79 万元** | 滞销; 保守策略 |
| Q1 子问 2 (discount) | **940.05 万元** | 50% 折价; 反直觉地低于 waste |
| Q2 (蒙特卡洛 n=500, σ=0.10) | **953.84 ± 354.40 万元** | CV=0.37; min/max=104/2069 |
| Q3 (弹性 + 间作, n=300) | **1224.01 ± 369.7 万元** | CV=0.30; 较 Q2 +28.3% |

## 复现命令

```bash
# 安装依赖
pip install -r code/requirements.txt

# 跑全流程 (确保 code/data/processed.json 与 code/data/action_space.json 已生成)
cd code
python preprocess.py                # 解析附件 → processed.json
python data_structure.py            # 动作空间压缩 → action_space.json
python q1_run.py                    # 问题 1 两个子问 → result1_1/2.xlsx
python q2_run.py --n 500 --sigma 0.10  # 问题 2
python q3_run.py --n 300 --sigma 0.10  # 问题 3
python check_constraints.py         # 13 类约束校验
python plot_results.py              # 6 张图
python result_summary.py            # 汇总到 result_summary.xlsx
python -c "from algo.ga import ga_solve; from algo.greedy import greedy_solve; print(ga_solve(mode='discount', n_years=7, pop=20, gens=10))"  # GA 验证
```

## 关键假设 (摘自 main.tex §3)

- H1: 附件 1 的 54 块地为准 (题面 82 与附件 54 不一致)
- H2: 预期销售量 = 2023 实际产量 × 1.2 buffer
- H3: 销售单价取 2023 区间中位数
- H4: 轮作约束严格 (同地块同作物不连续两季)
- H5: 每季每地单作物 (无物理间作)
- H6: 水浇地 C2 vs C8 冲突时优先 C8 (仅 Q3)

## 已知限制

1. 贪心是局部最优 (GA 验证差距 1.4%)
2. 销售量 baseline 是合成假设 (无官方数据)
3. 替代矩阵 ρ 是合成假设
4. 水浇地 C2 vs C8 严格解读冲突, Q3 优先 C8

## 匿名信息

本目录不含学校、姓名、邮箱、队号、赛区等可识别信息。