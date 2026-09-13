# verify — prism-style-plot 回归验证套件

技能自带的回归验证脚本,随技能包分发,换机器不丢验证能力。

## 文件

| 文件 | 覆盖范围 |
|---|---|
| `verify_common.py` | 公共工具:模拟数据生成(`make_groups`)、重叠检查、PASS/FAIL 报告 |
| `verify1_column.py` | Column 表三大图型:prism_bars / prism_boxplot / prism_violin + ttest/ANOVA 统计 |
| `verify2_others.py` | 其他表型:Grouped 手写分组柱、Survival KM、XY 4PL/linear、Contingency |
| `verify3a_dot_size.py` | 散点尺寸与配色(点径算法、大样本透明度、多组循环色)— v2.3.0 拆分自 verify3_edge |
| `verify3b_zorder_layout.py` | 散点布局与 zorder 层级(抖动均衡、标签旋转、error bar 最顶层)— v2.3.0 拆分自 verify3_edge |
| `verify3c_edge_cases.py` | 边界场景与统计报告(大样本 n、长标签、边缘显著、ns 隐藏、Nested/Parts of whole/Pairplot)— v2.3.0 拆分自 verify3_edge |
| `verify4_twoway_posthoc.py` | Two-way ANOVA 事后比较:交互显著→简单效应 / 纯加性→主效应 |
| `verify5_grouped_annotated.py` | Grouped 图上简单效应显著性标注(交互数据,48h 起效示例) |
| `verify6_figsize_recommend.py` | 画布推荐层:recommend_shape / recommend_figsize 全分支断言(分组数分档、关键词覆盖) |
| `verify7_ylim_small.py` | y 轴值域 <1 的绘图回归(细粒度刻度) |
| `verify8_ylim_small_allsigns.py` | <1 值域修复向全图型推广回归(bars/box/violin/grouped/nested/xy_fit) |
| `verify9_deep_matrix.py` | Grouped 析因设计组数矩阵深验(2×2 … 6×2 共 18 种设计) |
| `verify10_deep_others.py` | 其余图种深验(组数/样本数差异化;含 pairplot/facet_boxplot 的 `run_multivar()`) |
| `verify11_deep_edge.py` | 深度边界/性能回归(warnings-as-errors 轰击全部绘图函数、3×1000 点墙钟断言) |
| `build_deep_report.py` | 汇总 verify9+verify10 深验结果,生成自包含 HTML 报告 |
| `run_all.py` | **一键回归入口**(推荐入口;默认全套 13 个,`--quick` 快速档 10 个,按改动类型选档) |
| `run_full_suite.py` | glob 自动发现 `verify*.py`/`test*.py`(适合用户自定义 verify 工作区) |

## 运行方式

```bash
# 遵循技能环境约定:先取 venv 解释器
PY=$(python ../../scripts/ensure_env.py 2>/dev/null || python scripts/ensure_env.py)

# 入口 1:一键回归(传统入口,自动清理 output/;默认全套 13 个,并行执行)
$PY scripts/verify/run_all.py
$PY scripts/verify/run_all.py --keep-output   # 保留产物供人工复查
$PY scripts/verify/run_all.py --quick         # 快速档:跳过 3 个深度脚本(verify9/10/11),~30s
$PY scripts/verify/run_all.py --only stats    # 统计档:verify1/2/4/9/10/11
$PY scripts/verify/run_all.py --only plot     # 绘图档:verify3a/3b/3c/5/6/7/8
$PY scripts/verify/run_all.py --only edge     # 边界档:verify11 单独跑深度边界/性能

# 入口 2:glob 自动发现当前目录所有 verify*.py + test*.py
# 适合用户把自己的 verify 脚本放同一目录,无需修改注册表
$PY scripts/verify/run_full_suite.py           # Markdown 表格输出
$PY scripts/verify/run_full_suite.py --json    # CI 友好 JSON 输出
$PY scripts/verify/run_full_suite.py /path/to  # 自定义 verify 目录
```

单跑一个用例(调试时):

```bash
$PY scripts/verify/verify1_column.py
```

## 输出

- 产物(PNG/PDF/_report.md)写入 `output/` 子目录,默认在回归全部通过后清理;
- 退出码 0 = 全部 PASS,1 = 存在 FAIL;
- 新增用例:命名 `verifyN_*.py` 放入本目录,并在 `run_all.py` 的
  `VERIFY_SCRIPTS` 注册。

## 维护约定

- 每次对 `scripts/prism_theme.py` 做改动,先 `python -c "import prism_theme"` 确认不崩,
  再跑 `run_all.py` 确认无回归;
- 回归失败立即还原改动,并记 `status=reverted` 到 learnings.jsonl。
- **`output/` 不参与技能包分发**：该目录是回归运行的副产物
  (PNG/PDF/_report.md/html),体积可达 1.5M+,只应存在于本地。
  交付/分享技能包前用 `run_all.py`(默认自动清理)或手动清空 `output/`,
  **不要把 `output/` 内容带进技能包**。`run_all.py` 默认行为已满足此约定;
  如需在沙箱环境(回收站不可用)手动清理,直接删除 `output/` 内文件即可。
- **新增验证脚本必须带失败退出码**：每个 `verifyN_*.py` 结尾必须
  `sys.exit(1 if fails else 0)`(无 fails 列表时用 `sys.exit(0 if ok else 1)`)——
  `run_all.py` 靠子进程退出码判定 PASS/FAIL,缺退出码会让脚本内 FAIL
  被误报为 PASS("假绿",v2.1.1 教训)。
