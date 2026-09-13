"""公共工具:验证脚本共用的数据生成与检查函数。"""
import numpy as np

SEED = 42


def rng():
    return np.random.default_rng(SEED)


def make_groups(n_per_group=6, n_groups=3, base=(10.0, 12.0, 16.0),
                sd=1.5, seed=42):
    """生成 Column 表模拟数据:每组 n 个,均值 base,标准差 sd。"""
    r = np.random.default_rng(seed)
    return [r.normal(m, sd, n_per_group) for m in base]


def check_point_overlap(ax, tol=0.02):
    """检查图上同组散点是否有视觉重叠(矩形判据)。返回重叠对数。"""
    from matplotlib.collections import PathCollection
    colls = [c for c in ax.collections if isinstance(c, PathCollection)]
    n_overlap = 0
    for coll in colls:
        offsets = coll.get_offsets()
        if len(offsets) < 2:
            continue
        sizes = coll.get_sizes()
        if len(sizes) == 0:
            continue
        pt = np.sqrt(sizes[0])
        # 转换为数据坐标:点径近似用 figure 尺寸估算
        ax.figure.canvas.draw()
        inv = ax.transData.inverted()
        # 取 (0,0) 和 (pt,0) 两点的数据坐标差作为 d_x
        p0 = inv.transform((0, 0))
        p1 = inv.transform((pt * 0.55, 0))  # 近似点半径
        d_x = abs(p1[0] - p0[0])
        p2 = inv.transform((0, pt * 0.55))
        d_y = abs(p2[1] - p0[1])
        pts = np.asarray(offsets)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if abs(pts[i, 0] - pts[j, 0]) < d_x and abs(pts[i, 1] - pts[j, 1]) < d_y:
                    n_overlap += 1
    return n_overlap


def report(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok
