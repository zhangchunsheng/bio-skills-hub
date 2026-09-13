# verify — prism-style-plot 回归验证套件

技能自带的回归验证脚本,随技能包分发,换机器不丢验证能力。

## 文件

| 文件 | 覆盖范围 |
|---|---|
| `verify_common.py` | 公共工具:模拟数据生成(`make_groups`)、重叠检查、PASS/FAIL 报告 |
| `verify1_column.py` | Column 表三大图型:prism_bars / prism_boxplot / prism_violin + ttest/ANOVA 统计 |
| `verify2_others.py` | 其他表型:Grouped 手写分组柱、Survival KM、XY 4PL/linear、Contingency |
| `verify3_edge.py` | 边界场景:大样本 n、长标签旋转、多组配色越界、边缘显著、ns 隐藏、zorder 图层 |
| `verify4_twoway_posthoc.py` | Two-way ANOVA 事后比较:交互显著→简单效应 / 纯加性→主效应 |
| `verify5_grouped_annotated.py` | Grouped 图上简单效应显著性标注(交互数据,48h 起效示例) |
| `verify12_combined_panel.py` | v2.7.0 多数据集合并面板图 + 总报告(compose_panel_figure / build_master_report) |
| `run_all.py` | **一键回归入口**(推荐入口,跑固定 15 个 verify；无参数=全套) |
| `run_full_suite.py` | **v2.3.1 新增**:glob 自动发现 `verify*.py`/`test*.py`(适合用户自定义 verify 工作区) |

## 运行方式

```bash
# 遵循技能环境约定:先取 venv 解释器
PY=$(python ../../scripts/ensure_env.py 2>/dev/null || python scripts/ensure_env.py)

# 入口 1:跑固定 6 个官方 verify(传统入口,自动清理 output/)
$PY scripts/verify/run_all.py
$PY scripts/verify/run_all.py --keep-output   # 保留产物供人工复查

# 入口 2 (v2.3.1+):glob 自动发现当前目录所有 verify*.py + test*.py
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
