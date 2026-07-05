# 2023 高教社杯 A 题 · 定日镜场优化设计 · 最终交付

> 本目录为 CUMCM 2023 A 题"定日镜场的优化设计"的最终交付物。所有数值结论来自 `code/` 下脚本的真实运行输出,均可复现。

## 目录结构

```
outputs/
├── main.tex                       # 论文 LaTeX 源(可编译,见下)
├── main.pdf                       # 论文 PDF(如编译成功)
├── code/                          # 所有 Python 源码
│   ├── common/                    # 公共模块(astro/efficiency/MC/layout/seeds)
│   ├── q1_baseline.py             # 问题一
│   ├── q2_uniform_mirror.py       # 问题二
│   ├── q3_mixed_mirror.py         # 问题三
│   ├── sensitivity.py             # 灵敏度分析
│   ├── draw_workflow.py           # 流程图生成
│   └── run_all.py                 # 一键跑全套
├── figures/                       # 论文中使用的全部图
│   ├── modeling_workflow.pdf
│   ├── q1_monthly_efficiency.png
│   ├── q1_annual_summary.png
│   ├── q2_layout.png
│   ├── q3_mixed_layout.png
│   ├── sensitivity.png
│   └── mc_sample_bias.png
├── heliostats_baseline.csv        # Q1 baseline 1745 面镜面坐标
├── heliostats_q2.csv              # Q2 优化后镜面坐标
├── heliostats_q3.csv              # Q3 异构后镜面坐标
├── result1.xlsx                   # Q1 月表 + 年表
├── result2.xlsx                   # Q2 月表 + 年表 + 参数
├── result3.xlsx                   # Q3 月表 + 年表 + 参数
├── result_summary.xlsx            # 三问 + 灵敏度汇总
├── sensitivity.csv / .xlsx        # 灵敏度分析数据
├── README.md                      # 本文件
├── manifest.md                    # 交付清单
├── AI_USAGE.md                    # AI 工具使用声明
├── SHA256SUMS.txt                 # 全部交付物 SHA256 校验
└── q1/q2/q3/sensitivity_run.log   # 完整运行日志
```

## 环境与复现

- **Python:** 3.12.12(`C:/Users/lenovo/anaconda3/envs/pytorch/python.exe`)
- **依赖:** 见 `outputs/requirements.txt`
- **复现命令:**
  ```bash
  cd 2023A
  python -c "import sys; sys.path.insert(0,'outputs/code'); \
    import q1_baseline, q2_uniform_mirror, q3_mixed_mirror, sensitivity; \
    q1_baseline.run(n_mc=80, n_helio=1745); \
    [q2_uniform_mirror.eval_field(*c, n_mc=60, max_mirrors=10**6) for c in [(4.0,4.0,14)]]; \
    q3_mixed_mirror.eval_mixed([6,6,3],[0,0,2],3, n_mc=80, max_mirrors=10**6); \
    sensitivity.run()"
  ```
  (完整参数见 `outputs/code/q1_baseline.py` 等顶部注释)

## 编译 LaTeX

如本机装有 `xelatex`(CTeX 或 TeX Live),可:
```bash
cd 2023A/outputs
xelatex main.tex   # 第一次
xelatex main.tex   # 第二次(交叉引用)
```

如未装,只交 `main.tex` 与本目录的所有 .png/.pdf 即可;PDF 缺位不影响评分。

## 关键结果速览

| 子问题 | 配置 | η_annual | E_field (MW) | E_A (W/m²) | 60 MW 约束 |
| --- | --- | --- | --- | --- | --- |
| Q1 | 6m×6m, h=4m, 1745 面 | 0.263 | 16.06 | 255.64 | N/A(题面无) |
| Q2 | 4m, h=4m, rings=14, 1586 面 | 0.498 | 61.49 | 2423.08 | OK |
| Q3 | 近 8m/2m, 中 8m/2m, 远 5m/4m, 3167 面 | 0.208 | 124.04 | 988.32 | OK |

## 重要披露

- **附件不可下载:** 本环境无法下载官方附件(网络 451),按 problem.md 的几何与约束自合成 radial-stagger 镜场;真实附件如可获得,只需替换 `heliostats_baseline.csv` 即可。
- **Q2 改用网格枚举:** 受限时长影响,Q2 在 DE 基础上加网格枚举取最优;Q3 仍用离散 DE。
- **MC 采样数:** Q1 N_mc=80,Q2/Q3 N_mc=60–80;sensitivity N_mc=100。已用 `figures/mc_sample_bias.png` 验证 N=200 时偏差 < 1%。

## 联系方式

本交付物由自动化 agent 独立完成,不包含学校 / 姓名 / 队伍编号 / 邮箱等可识别信息。