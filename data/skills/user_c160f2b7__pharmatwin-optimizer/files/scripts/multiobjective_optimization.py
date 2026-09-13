#!/usr/bin/env python3
"""
PharmaTwin-Optimizer: 多目标智能优化脚本
功能：使用 NSGA-II / Bayesian Optimization 进行多目标 Pareto 优化 (Phase 5)

优化目标（默认）:
  1. Minimize T80 (溶出时间, min)        → 越小越好
  2. Minimize Degradation (稳定性, %)     → 越小越好
  3. Maximize Safety Index (安全性)       → 越大越好（如 -LD50 或 1/prob_tox）
  4. Minimize Cost (辅料成本, ¥/kg)       → 越小越好

依赖：numpy, scipy, pymoo
安装：pip install numpy scipy pymoo
"""

import sys
import argparse
import json
import warnings
from typing import Dict, List, Tuple, Optional, Callable

import numpy as np

# ─── pymoo (NSGA-II) ───────────────────────────────────────────────
try:
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.optimize import minimize
    from pymoo.visualization.scatter import Scatter
    HAS_PYMOO = True
except ImportError:
    HAS_PYMOO = False
    warnings.warn("pymoo not installed. Install with: pip install pymoo")

# ─── 贝叶斯优化 (fallback / 小数据量) ──────────────────────────────
try:
    from scipy.stats import norm
    from scipy.optimize import minimize as scipy_minimize
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern, ConstantKernel
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# ═══════════════════════════════════════════════════════════════════
#  模型代理层 — 用高斯过程代替真实实验
# ═══════════════════════════════════════════════════════════════════

class SurrogateModel:
    """高斯过程代理模型，包装多个子目标"""

    def __init__(self):
        kernel = ConstantKernel(1.0) * Matern(length_scale=1.0, nu=2.5)
        self.models: Dict[str, GaussianProcessRegressor] = {}
        self.kernel = kernel

    def fit(self, x_train: np.ndarray, y_dict: Dict[str, np.ndarray]):
        """对每个目标分别训练 GP

        Args:
            x_train: (n_samples, n_features) 训练输入
            y_dict: {目标名: (n_samples,) 训练输出}
        """
        for name, y in y_dict.items():
            # 标准化
            y_mean, y_std = np.mean(y), np.std(y)
            y_norm = (y - y_mean) / (y_std + 1e-10)
            gp = GaussianProcessRegressor(
                kernel=self.kernel,
                alpha=1e-6,
                normalize_y=True,
                n_restarts_optimizer=5,
                random_state=42,
            )
            gp.fit(x_train, y_norm)
            self.models[name] = {"gp": gp, "mean": y_mean, "std": y_std}

    def predict(self, x: np.ndarray, name: str) -> Tuple[float, float]:
        """返回(预测值, 标准差)，反标准化"""
        gp_info = self.models[name]
        y_pred_norm, y_std_norm = gp_info["gp"].predict(x.reshape(1, -1), return_std=True)
        y_pred = y_pred_norm[0] * gp_info["std"] + gp_info["mean"]
        y_std = y_std_norm[0] * gp_info["std"]
        return y_pred, y_std


# ═══════════════════════════════════════════════════════════════════
#  目标函数定义
# ═══════════════════════════════════════════════════════════════════

def default_objectives(x: np.ndarray, model: SurrogateModel) -> Dict[str, float]:
    """默认四目标函数，通过 GP 代理预测

    输入 x: [辅料A比例, 辅料B比例, API比例, 搅拌速度, 干燥温度, ...]
    输出: {目标名: 值}
    """
    t80, _ = model.predict(x, "t80")
    deg, _ = model.predict(x, "degradation")
    safety, _ = model.predict(x, "safety")
    cost, _ = model.predict(x, "cost")
    return {"t80": t80, "degradation": deg, "safety": -safety, "cost": cost}


# ═══════════════════════════════════════════════════════════════════
#  pymoo NSGA-II Problem 定义
# ═══════════════════════════════════════════════════════════════════

class FormulationProblem(ElementwiseProblem):
    """pymoo 配方多目标问题"""

    def __init__(
        self,
        n_var: int,
        xl: np.ndarray,
        xu: np.ndarray,
        objective_fn: Callable,
        surrogate: SurrogateModel,
    ):
        super().__init__(
            n_var=n_var,
            n_obj=4,
            xl=xl,
            xu=xu,
        )
        self.objective_fn = objective_fn
        self.surrogate = surrogate

    def _evaluate(self, x, out, *args, **kwargs):
        objectives = self.objective_fn(x, self.surrogate)
        out["F"] = [
            objectives["t80"],
            objectives["degradation"],
            objectives["safety"],  # 已在 default_objectives 中取负
            objectives["cost"],
        ]


# ═══════════════════════════════════════════════════════════════════
#  贝叶斯优化 (主动学习版)
# ═══════════════════════════════════════════════════════════════════

class BayesianOptimizer:
    """贝叶斯优化器（数据量 ≤ 30 时使用）"""

    def __init__(self, n_iter: int = 20, n_initial: int = 5):
        self.n_iter = n_iter
        self.n_initial = n_initial
        self.surrogate = None

    def expected_improvement(self, x: np.ndarray, gp: GaussianProcessRegressor, y_best: float) -> float:
        """Expected Improvement 采集函数"""
        mu, sigma = gp.predict(x.reshape(1, -1), return_std=True)
        sigma = sigma[0] + 1e-10
        gamma = (y_best - mu[0]) / sigma
        ei = (y_best - mu[0]) * norm.cdf(gamma) + sigma * norm.pdf(gamma)
        return -ei  # scipy 最小化用负值

    def optimize(
        self,
        x_init: np.ndarray,
        y_init: Dict[str, np.ndarray],
        bounds: List[Tuple[float, float]],
    ) -> Dict:
        """执行贝叶斯优化循环

        Args:
            x_init: (n_initial, n_features) 初始实验数据
            y_init: {目标名: (n_initial,)}
            bounds: 每个维度的 (下限, 上限) 列表

        Returns:
            {"best_x": ..., "best_y": ..., "history": [...]}
        """
        n_dim = x_init.shape[1]
        self.surrogate = SurrogateModel()
        combined_y = sum(
            y_init[k] / (np.max(np.abs(y_init[k])) + 1e-10)
            for k in y_init
        )

        x = x_init.copy()
        y_combined = combined_y.copy()
        history = []

        for iteration in range(self.n_iter):
            # 训练 GP
            kernel = ConstantKernel(1.0) * Matern(length_scale=np.ones(n_dim), nu=2.5)
            gp = GaussianProcessRegressor(
                kernel=kernel, alpha=1e-6, normalize_y=True, n_restarts_optimizer=3
            )
            gp.fit(x, y_combined)
            y_best = np.min(y_combined)

            # 优化 EI 采集函数
            best_ei = float("inf")
            best_candidate = None
            for _ in range(10):  # 多起点
                x0 = np.array([
                    np.random.uniform(low, high) for low, high in bounds
                ])
                res = scipy_minimize(
                    lambda xv: self.expected_improvement(xv, gp, y_best),
                    x0,
                    bounds=bounds,
                    method="L-BFGS-B",
                )
                if res.fun < best_ei:
                    best_ei = res.fun
                    best_candidate = res.x

            if best_candidate is None:
                break

            # 模拟"真实"目标（这里用 GP 均值近似，实际时应做实验）
            y_new_combined, _ = gp.predict(best_candidate.reshape(1, -1), return_std=True)
            x = np.vstack([x, best_candidate])
            y_combined = np.append(y_combined, y_new_combined[0])

            history.append({
                "iteration": iteration + 1,
                "x": best_candidate.tolist(),
                "y": y_new_combined[0],
            })

        best_idx = np.argmin(y_combined)
        return {
            "best_x": x[best_idx].tolist(),
            "best_y": float(y_combined[best_idx]),
            "n_iterations": self.n_iter,
            "history": history,
        }


# ═══════════════════════════════════════════════════════════════════
#  输出与报告
# ═══════════════════════════════════════════════════════════════════

def format_pareto_front(results: np.ndarray, var_names: List[str]) -> List[Dict]:
    """将 Pareto 前沿结果格式化为可读列表"""
    pareto_list = []
    for i, sol in enumerate(results):
        entry = {
            "solution_id": i + 1,
            "objectives": {
                "T80 (min)": round(sol[0], 2),
                "Degradation (%)": round(sol[1], 2),
                "Safety Index": round(-sol[2], 4) if sol[2] < 0 else round(sol[2], 4),
                "Cost (¥/kg)": round(sol[3], 2),
            },
        }
        if len(sol) > 4:
            entry["variables"] = {
                name: round(val, 4)
                for name, val in zip(var_names, sol[4:])
            }
        pareto_list.append(entry)
    return pareto_list


def monte_carlo_robustness(
    best_x: np.ndarray,
    objective_fn: Callable,
    surrogate: SurrogateModel,
    n_samples: int = 500,
    noise_std: float = 0.02,
) -> Dict:
    """蒙特卡洛模拟评估配方鲁棒性

    Args:
        best_x: Pareto 最优解
        objective_fn: 目标函数
        surrogate: 代理模型
        n_samples: 采样次数
        noise_std: 输入噪声标准差（相对于变量范围）

    Returns:
        CQA 分布的 90% 置信区间
    """
    n_var = len(best_x)
    x_range = np.ones(n_var)  # 归一化假设
    samples = np.zeros((n_samples, n_var))
    objectives_samples = []

    for i in range(n_samples):
        noise = np.random.normal(0, noise_std * x_range, n_var)
        x_perturbed = best_x + noise
        # 约束到 [0, 1] (假设输入已在 [0, 1] 范围)
        x_perturbed = np.clip(x_perturbed, 0, 1)
        samples[i] = x_perturbed
        objs = objective_fn(x_perturbed, surrogate)
        objectives_samples.append(objs)

    # 统计
    result = {}
    for key in ["t80", "degradation", "safety", "cost"]:
        vals = [o[key] for o in objectives_samples]
        result[key] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "p5": float(np.percentile(vals, 5)),
            "p95": float(np.percentile(vals, 95)),
        }
    return result


# ═══════════════════════════════════════════════════════════════════
#  CLI 入口
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="PharmaTwin-Optimizer: 多目标智能优化 (NSGA-II + Bayesian)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--method",
        choices=["nsga2", "bayesian"],
        default="nsga2",
        help="优化算法 (默认: nsga2; 数据 ≤30 用 bayesian)",
    )
    parser.add_argument(
        "--n-var",
        type=int,
        default=5,
        help="决策变量维度 (默认: 5)",
    )
    parser.add_argument(
        "--pop-size",
        type=int,
        default=50,
        help="NSGA-II 种群大小 (默认: 50)",
    )
    parser.add_argument(
        "--n-gen",
        type=int,
        default=100,
        help="NSGA-II 迭代代数 (默认: 100)",
    )
    parser.add_argument(
        "--n-iter-bayesian",
        type=int,
        default=20,
        help="贝叶斯优化迭代次数 (默认: 20)",
    )
    parser.add_argument(
        "--mc-samples",
        type=int,
        default=500,
        help="蒙特卡洛鲁棒性分析采样数 (0 = 跳过)",
    )
    parser.add_argument(
        "--var-names",
        nargs="+",
        default=["辅料A%", "辅料B%", "API%", "搅拌速度(rpm)", "干燥温度(°C)"],
        help="决策变量名称列表 (默认5个)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出 JSON 文件路径",
    )

    args = parser.parse_args()

    # ── 生成模拟训练数据（演示用 ── 实际使用时替换为真实数据）──
    np.random.seed(42)
    n_train = 30
    x_train = np.random.rand(n_train, args.n_var)
    y_t80 = 10 + 80 * x_train[:, 0] + 20 * np.sin(3 * x_train[:, 2]) + 5 * np.random.randn(n_train)
    y_deg = 2 + 15 * x_train[:, 1] + 3 * np.random.randn(n_train)
    y_safety = 0.5 + 0.4 * x_train[:, 3] - 0.2 * x_train[:, 4] + 0.1 * np.random.randn(n_train)
    y_cost = 100 + 200 * x_train[:, 0] + 150 * x_train[:, 1] + 50 * np.random.randn(n_train)

    y_train = {
        "t80": y_t80,
        "degradation": y_deg,
        "safety": y_safety,
        "cost": y_cost,
    }

    # ── 构建代理模型 ──
    print(">>> 训练 GP 代理模型...")
    surrogate = SurrogateModel()
    surrogate.fit(x_train, y_train)
    print(f"    模型已训练 ({n_train} 数据点)")

    # ── 约束边界（归一化 [0, 1] 空间）──
    xl = np.zeros(args.n_var)
    xu = np.ones(args.n_var)
    bounds = [(0.0, 1.0)] * args.n_var

    # ── 优化 ──
    if args.method == "bayesian":
        print(f">>> 贝叶斯优化 ({args.n_iter_bayesian} 次迭代)...")
        bo = BayesianOptimizer(n_iter=args.n_iter_bayesian)
        result = bo.optimize(x_train[:5], y_train, bounds)
        print(f"    最优解: {result['best_x']}")
        print(f"    最优值(组合): {result['best_y']:.4f}")

        pareto_list = []

    else:  # nsga2 (default)
        if not HAS_PYMOO:
            print("ERROR: pymoo not installed. Run: pip install pymoo", file=sys.stderr)
            sys.exit(1)

        print(f">>> NSGA-II 优化 (种群{args.pop_size}, {args.n_gen}代)...")
        problem = FormulationProblem(
            n_var=args.n_var,
            xl=xl,
            xu=xu,
            objective_fn=default_objectives,
            surrogate=surrogate,
        )

        algorithm = NSGA2(
            pop_size=args.pop_size,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(prob=1.0 / args.n_var, eta=20),
            eliminate_duplicates=True,
        )

        res = minimize(
            problem,
            algorithm,
            ("n_gen", args.n_gen),
            verbose=False,
        )

        print(f"    Pareto 前沿非支配解数: {len(res.F)}")
        pareto_list = format_pareto_front(
            np.hstack([res.F, res.X]),
            args.var_names,
        )

        # ├─ 最优折中解（最小化所有目标的加权和）──
        weights = np.array([0.3, 0.3, 0.3, 0.1])  # T80:Deg:Safety:Cost
        normalized_F = (res.F - res.F.min(axis=0)) / (res.F.max(axis=0) - res.F.min(axis=0) + 1e-10)
        scores = normalized_F @ weights
        best_idx = np.argmin(scores)
        best_x = res.X[best_idx]
        best_f = res.F[best_idx]

        print(f"\n>>> 最优折中解 (weighted sum):")
        print(f"    变量: {dict(zip(args.var_names, np.round(best_x, 4)))}")
        print(f"    T80={best_f[0]:.2f}min, Deg={best_f[1]:.2f}%, "
              f"Safety={-best_f[2]:.4f}, Cost={best_f[3]:.2f}¥/kg")

        result_obj = {
            "method": "NSGA-II",
            "population_size": args.pop_size,
            "n_generations": args.n_gen,
            "n_pareto_solutions": len(res.F),
            "pareto_front": pareto_list,
            "best_compromise": {
                "variables": dict(zip(args.var_names, np.round(best_x, 4).tolist())),
                "objectives": {
                    "T80 (min)": round(float(best_f[0]), 2),
                    "Degradation (%)": round(float(best_f[1]), 2),
                    "Safety Index": round(float(-best_f[2]), 4),
                    "Cost (¥/kg)": round(float(best_f[3]), 2),
                },
            },
        }

        # ── 蒙特卡洛鲁棒性分析 ──
        if args.mc_samples > 0:
            print(f"\n>>> 蒙特卡洛鲁棒性分析 ({args.mc_samples} 次采样)...")
            mc_result = monte_carlo_robustness(
                best_x, default_objectives, surrogate, n_samples=args.mc_samples
            )
            result_obj["robustness_90p_ci"] = mc_result
            for key, val in mc_result.items():
                print(f"    {key}: mean={val['mean']:.2f}, "
                      f"90%CI=[{val['p5']:.2f}, {val['p95']:.2f}]")

        result = result_obj

    # ── 输出 ──
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n>>> 结果已写入: {args.output}")
    else:
        print("\n>>> 优化结果 (JSON):")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
