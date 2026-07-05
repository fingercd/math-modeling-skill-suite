"""全局随机种子集中管理。所有 MC / DE 随机源必须从这里取种子。"""
SEED = 20230705


def get_rng():
    """返回已 seed 的 numpy.random.Generator 实例。"""
    import numpy as np
    return np.random.default_rng(SEED)