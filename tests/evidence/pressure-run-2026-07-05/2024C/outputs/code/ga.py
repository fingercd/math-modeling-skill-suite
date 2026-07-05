"""algo/ga.py — GA 交叉验证 (简化版).

种群 30, 代数 30, 单点交叉 + 位翻转变异, fitness = -总利润 (最小化).
为了复现性, 用固定种子.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from objective import evaluate_solution
from data_structure import load_processed

DATA = Path(__file__).resolve().parent.parent / "data"


def ga_solve(mode="discount", n_years=7, pop=30, gens=30, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    processed = load_processed()
    actions = json.loads((DATA / "action_space.json").read_text(encoding="utf-8"))["actions"]
    n_actions = len(actions)
    crops = processed["crops"]
    plots = processed["plots"]

    def decode(chrom):
        """chrom: 二值向量, 长度 n_actions; 转 x dict."""
        x = {}
        for i, bit in enumerate(chrom):
            if bit:
                a = actions[i]
                x[(a["plot"], a["crop"], a["season"], 2024)] = plots[a["plot"]]["area"]
        return x

    def fitness(chrom):
        x = decode(chrom)
        return -evaluate_solution(processed, {"actions": actions}, x, mode=mode)

    # 初始化
    popu = [np.random.randint(0, 2, n_actions).tolist() for _ in range(pop)]
    best_fit = float("inf")
    best_chrom = None
    for g in range(gens):
        fits = [fitness(c) for c in popu]
        idx = int(np.argmin(fits))
        if fits[idx] < best_fit:
            best_fit = fits[idx]
            best_chrom = popu[idx]
        # 精英 + 锦标赛选择
        new_pop = [popu[idx]]
        while len(new_pop) < pop:
            i, j = random.sample(range(pop), 2)
            a = popu[i] if fits[i] < fits[j] else popu[j]
            new_pop.append(a[:])
        # 交叉 + 变异
        for i in range(1, pop, 2):
            if i + 1 >= pop:
                break
            if random.random() < 0.7:
                pt = random.randint(1, n_actions - 1)
                a, b = new_pop[i][:], new_pop[i+1][:]
                new_pop[i][pt:] = b[pt:]
                new_pop[i+1][pt:] = a[pt:]
        for i in range(pop):
            for k in range(n_actions):
                if random.random() < 0.01:
                    new_pop[i][k] = 1 - new_pop[i][k]
        popu = new_pop
    return decode(best_chrom), -best_fit


if __name__ == "__main__":
    x, profit = ga_solve(mode="discount", n_years=7, pop=20, gens=10)
    print(f"GA 7 年累计 (discount) = {profit/1e4:.2f} 万元, 动作数={sum(1 for v in x.values() if v>0)}")