#!/usr/bin/env python3
"""
临床试验样本量计算器（Sample Size Calculator for Clinical Trials）

纯 Python 标准库实现，零第三方依赖。支持 I-IV 期临床试验方案设计中常见的样本量估算场景。

支持范围：
  - 结局类型: 均数(连续性) / 率(二分类)
  - 设计类型: 两样本平行组 / 配对设计(均数差)
  - 检验框架: 优效性(superiority) / 非劣效性(non-inferiority) / 等效性(equivalence)
  - 脱落率调整: 输出调整后每组例数与总例数

说明：
  - 生存类终点(时间-事件)因需入组模式/随访时长假设，不在本脚本范围，
    请使用 PASS / nQuery / R(powerSurvEpi, gsDesign) 等专业软件，本脚本给出逻辑框架参考。
  - 结果均为理论估算，实际样本量须由合格统计师结合临床与法规因素确认。

用法示例：
  # 优效性，两样本率：试验组 70% vs 对照组 50%，双侧 alpha=0.05，把握度 80%，脱落率 15%
  python sample_size_calculator.py --endpoint proportion --design parallel \
      --framework superiority --p1 0.70 --p2 0.50 \
      --alpha 0.05 --power 0.80 --dropout 0.15

  # 非劣效性，两样本均数：预期组间差 0，非劣效界值 2，标准差 8，单侧 alpha=0.025
  python sample_size_calculator.py --endpoint mean --design parallel \
      --framework non-inferiority --delta 0 --margin 2 --sigma 8 \
      --alpha 0.025 --power 0.90

  # 等效性，两样本均数：等效界值 5，标准差 15
  python sample_size_calculator.py --endpoint mean --design parallel \
      --framework equivalence --margin 5 --sigma 15 \
      --alpha 0.05 --power 0.80

  # 配对设计(均数差)
  python sample_size_calculator.py --endpoint mean --design paired \
      --framework superiority --delta 3 --sigma_d 6 --alpha 0.05 --power 0.80
"""

import argparse
import math
import sys


# ---------------------------------------------------------------------------
# 标准正态分布分位数（基于互补误差函数二分法，精度 ~1e-10，零依赖）
# ---------------------------------------------------------------------------
def _norm_ppf(p: float, tol: float = 1e-12) -> float:
    """标准正态分布反函数：P(Z <= z) = p，返回 z。p 需在 (0, 1)。"""
    if not 0.0 < p < 1.0:
        raise ValueError(f"p 必须在 (0, 1) 区间，收到 {p}")
    # 极尾使用有理近似初始化，加速收敛
    if p < 0.5:
        return -_norm_ppf(1.0 - p)
    # 在 [0, 10] 内二分查找
    lo, hi = 0.0, 10.0
    while _norm_cdf(hi) < p:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _norm_cdf(z: float) -> float:
    """标准正态分布 CDF：Phi(z)，基于 math.erfc。"""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _z_alpha(alpha: float, two_sided: bool) -> float:
    """根据 alpha 与单/双侧返回对应正态分位数。"""
    if two_sided:
        return _norm_ppf(1.0 - alpha / 2.0)
    return _norm_ppf(1.0 - alpha)


# ---------------------------------------------------------------------------
# 样本量公式
# ---------------------------------------------------------------------------
def n_mean_parallel(delta: float, sigma: float, alpha: float, power: float,
                    margin: float = 0.0, framework: str = "superiority",
                    two_sided: bool = False) -> int:
    """
    两样本平行组、均数类结局。
    superiority / non-inferiority: n = 2*(Z1-a + Z1-b)^2 * sigma^2 / delta_eff^2
      - superiority:     delta_eff = delta（预期组间差）
      - non-inferiority: delta_eff = delta + margin（注意符号：margin 为正值界值，
        试验组-对照组差 > -margin 即非劣效，有效差异 = delta + margin）
    equivalence: n = 2*(Z1-a/2 + Z1-b)^2 * sigma^2 / margin^2（假设真实效应=0，双侧）
    """
    if sigma <= 0:
        raise ValueError("sigma 必须 > 0")
    z_beta = _norm_ppf(power)
    if framework == "equivalence":
        if margin <= 0:
            raise ValueError("等效性必须提供 margin > 0")
        z_alpha = _z_alpha(alpha, two_sided=True)
        denom = margin ** 2
    else:
        z_alpha = _z_alpha(alpha, two_sided=two_sided)
        eff = delta + (margin if framework == "non-inferiority" else 0.0)
        if eff <= 0:
            raise ValueError("有效差异必须 > 0：优效需 delta>0，非劣效需 delta+margin>0")
        denom = eff ** 2
    n = 2.0 * (z_alpha + z_beta) ** 2 * sigma ** 2 / denom
    return math.ceil(n)


def n_mean_paired(delta: float, sigma_d: float, alpha: float, power: float,
                  margin: float = 0.0, framework: str = "superiority",
                  two_sided: bool = False) -> int:
    """
    配对设计（交叉设计阶段差等）、均数差结局。
    n = (Z + Z)^2 * sigma_d^2 / eff^2；等效性用双侧 alpha 与 margin。
    """
    if sigma_d <= 0:
        raise ValueError("sigma_d 必须 > 0")
    z_beta = _norm_ppf(power)
    if framework == "equivalence":
        if margin <= 0:
            raise ValueError("等效性必须提供 margin > 0")
        z_alpha = _z_alpha(alpha, two_sided=True)
        denom = margin ** 2
    else:
        z_alpha = _z_alpha(alpha, two_sided=two_sided)
        eff = delta + (margin if framework == "non-inferiority" else 0.0)
        if eff <= 0:
            raise ValueError("有效差异必须 > 0")
        denom = eff ** 2
    n = (z_alpha + z_beta) ** 2 * sigma_d ** 2 / denom
    return math.ceil(n)


def n_prop_parallel(p1: float, p2: float, alpha: float, power: float,
                    margin: float = 0.0, framework: str = "superiority",
                    two_sided: bool = False) -> int:
    """
    两样本平行组、率类结局（正态近似，率差尺度）。
    n = (Z1-a + Z1-b)^2 * [p1(1-p1)+p2(1-p2)] / delta_eff^2
      - superiority:     delta_eff = p1 - p2
      - non-inferiority: delta_eff = p1 - p2 + margin
      - equivalence:     双侧，delta_eff = margin（假设 p1=p2）
    """
    if not (0.0 < p1 < 1.0) or not (0.0 < p2 < 1.0):
        raise ValueError("p1/p2 必须在 (0,1) 区间")
    z_beta = _norm_ppf(power)
    var = p1 * (1.0 - p1) + p2 * (1.0 - p2)
    if framework == "equivalence":
        if margin <= 0:
            raise ValueError("等效性必须提供 margin > 0")
        z_alpha = _z_alpha(alpha, two_sided=True)
        denom = margin ** 2
    else:
        z_alpha = _z_alpha(alpha, two_sided=two_sided)
        eff = (p1 - p2) + (margin if framework == "non-inferiority" else 0.0)
        if eff <= 0:
            raise ValueError("有效差异必须 > 0")
        denom = eff ** 2
    n = (z_alpha + z_beta) ** 2 * var / denom
    return math.ceil(n)


def adjust_dropout(n_per_group: int, n_groups: int, dropout: float) -> tuple:
    """脱落率调整：n_adj = ceil(n / (1 - dropout))，返回 (每组调整例数, 总调整例数)。"""
    if not 0.0 <= dropout < 1.0:
        raise ValueError("dropout 必须在 [0, 1) 区间")
    if dropout == 0.0:
        return n_per_group, n_per_group * n_groups
    n_adj = math.ceil(n_per_group / (1.0 - dropout))
    return n_adj, n_adj * n_groups


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="临床试验样本量计算器（均数/率、平行/配对、优效/非劣效/等效）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--endpoint", choices=["mean", "proportion"], required=True,
                   help="结局类型：均数(mean) / 率(proportion)")
    p.add_argument("--design", choices=["parallel", "paired"], default="parallel",
                   help="设计类型：两样本平行(parallel) / 配对(paired，仅均数)")
    p.add_argument("--framework", choices=["superiority", "non-inferiority", "equivalence"],
                   default="superiority", help="检验框架")
    # 均数参数
    p.add_argument("--delta", type=float, default=None,
                   help="预期组间均数差 / 配对均数差（优效必填；非劣效可为 0 或预期差）")
    p.add_argument("--sigma", type=float, default=None, help="结局标准差（平行均数必填）")
    p.add_argument("--sigma_d", type=float, default=None, help="配对差标准差（配对设计必填）")
    # 率参数
    p.add_argument("--p1", type=float, default=None, help="试验组预期事件率（率类必填）")
    p.add_argument("--p2", type=float, default=None, help="对照组预期事件率（率类必填）")
    # 通用
    p.add_argument("--margin", type=float, default=0.0,
                   help="非劣效/等效界值（delta 单位，率类为率差）")
    p.add_argument("--alpha", type=float, default=0.05, help="I 类错误率")
    p.add_argument("--power", type=float, default=0.80, help="把握度（1 - beta）")
    p.add_argument("--two-sided", action="store_true",
                   help="优效/非劣效用双侧 alpha（默认单侧；等效性恒为双侧）")
    p.add_argument("--dropout", type=float, default=0.0,
                   help="预期脱落率（0~1，如 0.15 表示 15%）")
    p.add_argument("--groups", type=int, default=2, help="组数（通常 2）")
    return p


def _main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    if not (0 < args.alpha < 1):
        sys.exit(f"错误：alpha 必须在 (0,1)，收到 {args.alpha}")
    if not (0 < args.power < 1):
        sys.exit(f"错误：power 必须在 (0,1)，收到 {args.power}")

    framework_zh = {"superiority": "优效性", "non-inferiority": "非劣效性", "equivalence": "等效性"}
    side_zh = "双侧" if (args.two_sided or args.framework == "equivalence") else "单侧"

    try:
        if args.endpoint == "mean":
            if args.design == "paired":
                if args.sigma_d is None:
                    sys.exit("错误：配对设计需要 --sigma_d")
                if args.framework != "equivalence" and args.delta is None:
                    sys.exit("错误：优效/非劣效需要 --delta")
                n = n_mean_paired(args.delta or 0.0, args.sigma_d, args.alpha, args.power,
                                  args.margin, args.framework, args.two_sided)
                label = "配对设计（均数差）"
                n_groups = 1
            else:
                if args.sigma is None:
                    sys.exit("错误：平行均数设计需要 --sigma")
                if args.framework != "equivalence" and args.delta is None:
                    sys.exit("错误：优效/非劣效需要 --delta")
                n = n_mean_parallel(args.delta or 0.0, args.sigma, args.alpha, args.power,
                                    args.margin, args.framework, args.two_sided)
                label = "两样本平行组（均数）"
                n_groups = args.groups
        else:  # proportion
            if args.p1 is None or args.p2 is None:
                sys.exit("错误：率类需要 --p1 与 --p2")
            n = n_prop_parallel(args.p1, args.p2, args.alpha, args.power,
                                args.margin, args.framework, args.two_sided)
            label = "两样本平行组（率）"
            n_groups = args.groups

        n_adj, total_adj = adjust_dropout(n, n_groups, args.dropout)
    except ValueError as e:
        sys.exit(f"错误：{e}")

    print("=" * 62)
    print("临床试验样本量估算结果")
    print("=" * 62)
    print(f"设计         : {label}")
    print(f"检验框架     : {framework_zh[args.framework]}（{side_zh}，alpha = {args.alpha}）")
    print(f"把握度       : {args.power:.0%}（beta = {1 - args.power:.0%}）")
    if args.framework != "equivalence":
        print(f"检验方向     : {'双侧' if args.two_sided else '单侧'}")
    if args.framework in ("non-inferiority", "equivalence"):
        print(f"界值(margin) : {args.margin}")
    if args.framework == "superiority":
        print(f"预期效应     : {args.delta if args.endpoint=='mean' else f'{args.p1} vs {args.p2}'}")
    print("-" * 62)
    print(f"每组例数（未调整） : {n}")
    print(f"总例数（未调整）   : {n * n_groups}")
    print(f"脱落率             : {args.dropout:.0%}")
    print(f"每组例数（调整后） : {n_adj}")
    print(f"总例数（调整后）   : {total_adj}")
    print("=" * 62)
    print("注：结果为依据正态近似公式的理论估算。生存类终点请使用")
    print("    PASS / nQuery / R(powerSurvEpi, gsDesign) 等专业软件。")
    print("    实际样本量须由合格统计师结合临床与法规因素确认。")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
