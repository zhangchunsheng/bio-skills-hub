# 散点布局实现细节（`prism-style-plot` 内部参考）

> 本文件承载 SKILL.md 中"样本点布局"规则被折叠的实现级细节，正文只保留不变量与硬约束。**改动 `prism_theme.py` 中 `prism_bars` / `prism_boxplot` / `prism_violin` / `add_individual_dots` 时同步维护本文件**。本文件为 `prism-style-plot.md`「核心规则（权威源）」中关于镜像均衡抖动的实现级补充，规则变更以权威源为准。

## 1. 镜像均衡抖动（balanced jitter）默认参数

| 量 | 取值 | 来源 |
|---|---|---|
| 默认布局 | `layout="jitter"` | 接口默认值 |
| `balanced` | `True` | 镜像均值分布，避免单侧偏 |
| 初值采样区间 | `uniform(mid_b, max_j)` | 直接避中线带 |
| `mid_b` | `0.6·d_x` | 保证跨中线两侧最内侧点间距 ≥ 2·mid_b ≥ d_x |
| `n` 奇数时 | 1 点**随机偏侧** | 左右差 ≤1，去正中竖线规律 |
| `max_j` 上限 | `width/2` | **布局硬约束**，点绝不溢出 box/柱外 |
| `jitter_ratio` | `0.5`（默认） | 控占柱宽比例；收紧防溢出邻组 |
| 备选布局 | `layout="beeswarm"` | 点密集或审稿敏感时多列展开 |

## 2. 去规律化（v2.0.31 决定）

| 修复项 | 原规律 | 新规则 |
|---|---|---|
| min_sep 微调 | 固定交替步进 `±(0.6+0.4k)·d_x`（锯齿） | 随机方向 + 随机步长：`rng.choice([-1,1]) × rng.uniform(0.6, 1.1)·d_x` |
| 等距排开兜底 | `(n-1)×1.05·d_x` 等差数列（最规律最丑） | **删除**，物理放不下时接受轻微重叠 + 透明度补偿 |
| n 奇数点 | 强制居中 | 随机偏侧（左右差 ≤1） |

## 3. 重叠透明度补偿（`_apply_overlap_alpha`）

**触发条件**：画点后用矩形判据（圆形判据 + 组内最大重叠密度 `max_frac`）检测。

**压低规则**：

```
new_alpha = max(0.30, alpha × (1 - 0.55 × max_frac))
```

- 仅改填充面（描边透明度与填充**同步压低**）
- 无重叠时**原样返回**，常规图完全不受影响
- 物理放不下时接受轻微重叠，由透明度补偿可读性

## 4. 布局硬约束

| 约束 | 实现位置 | 触发原因 |
|---|---|---|
| `max_j ≤ width/2` | `prism_bars` / `prism_boxplot` / `prism_violin` / `add_individual_dots` | 防止点溢出 box/柱外 |
| **画点前必设 xlim/ylim** | `prism_bars`/boxplot/violin 已内置；手写循环必加 `set_xlim(-0.5, n-0.5)` | 逐组绘制时范围逐步扩展、点径换算 `d_x/d_y` 漂移，前几组点挤在一起 |

**手写多组循环模板**（Grouped 等自定义场景）：

```python
ax.set_xlim(-0.5, n - 0.5)
ax.set_ylim(min(0, data.min()) * 1.15, max(0, data.max()) * 1.15)  # v2.0.39 起支持负值
# …画点…
```

## 5. 已实现并应用此规则的全部入口

- `prism_bars` — 分组柱状图
- `prism_boxplot` — 箱线图
- `prism_violin` — 小提琴图
- `add_individual_dots` — 手绘任意图型时调用

## 6. 接口速查

```python
from prism_theme import add_individual_dots
add_individual_dots(ax, xi, group_values,
                    color=..., width=...,          # 必传：颜色与所在柱/箱半宽
                    layout="jitter",                # or "beeswarm"
                    balanced=True,                  # 默认镜像均衡
                    jitter_ratio=0.5,               # 占柱宽比例
                    dot_size=12,                    # 显式指定则不再自适应
                    alpha=None,                     # None = auto_dot_alpha
                    seed=None)                      # 留 None 即可
```

**关键约定**：多组循环时**先算统一值** `dot_size = common_point_size(total_n, n_groups)**2` 再逐组传入；勿默认逐组自适应（违反"同图所有样本点同大"）。
