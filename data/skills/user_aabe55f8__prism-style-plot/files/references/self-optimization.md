# 技能自我优化协议（Self-Optimization Protocol）

本文件定义 `prism-style-plot` 技能如何在**每次使用**中积累经验、修复缺陷、演进能力。
它不是"技能自己偷偷跑代码",而是把"发现坑 → 修 → 验证 → 记录"的闭环**写进技能本身**,
由加载本技能的智能体（agent）在每次任务收尾时按本协议执行。

## 架构现实（先讲清楚边界）

- 技能是静态文件（`SKILL.md` + `scripts/` + `references/`）,没有后台进程。
- "自我优化" = agent 在每次出图/出报告后,主动复盘本轮是否踩坑/被纠正/临时打补丁,
  并按下面的规则把改进写回技能文件,同时记入 `learnings.jsonl`。
- 一切自动修改都必须**可验证、可回退、可审计**(见下方护栏)。

## 触发时机

**每次任务完成 Phase 4 交付后,无条件进入 Phase 5 自我优化复盘**(用户已选定此模式)。
不需要用户主动说"复盘"——这是默认动作。

## 复盘时检查什么（信号源）

1. **运行报错**:本轮脚本是否抛过异常?是否出现过 FutureWarning/DeprecationWarning?
2. **用户纠正**:用户是否指出过问题(如"y 轴不对""p 值不精确""配色全蓝")?
3. **手动补丁**:本轮是否为了绕过坑而手写了本应内置的逻辑(如临时 `set_facecolor`、
   手动给 bracket 定 y 高度、手动拼 p 值字符串)?——这类补丁是最该被固化的信号。
4. **能力缺口**:用户是否想要某个图型/统计/格式,而当前脚本没有现成函数?
5. **文档歧义**:用户是否因 SKILL.md / references 表述不清而误解(如把 box 图误报成 Mean±SEM)?

## 问题分类与处置规则

| type | 含义 | 默认处置（本模式=安全修复自动改） |
|---|---|---|
| `bug` | 脚本缺陷导致报错或图形/统计错误 | **安全则自动修**;模糊则记日志待确认 |
| `convention` | 用户明确提出的硬性规则(如 p 值必须精确) | **自动写入**脚本/文档并记日志 |
| `doc` | SKILL.md/references 表述不清或缺失 | **自动补强文档**并记日志 |
| `gap` | 缺失的图型/统计/格式函数 | 清晰且低风险的**加法**自动加;否则记日志待确认 |
| `ambiguous` | 不确定是不是真问题 / 不确定怎么修 | **只记日志,不改文件,向用户展示待确认** |

## 安全修复闸门（同时满足才允许"自动改"）

一项改动只有在**全部满足**以下 5 条时,才可在不打扰用户的情况下自动应用:

1. **可复现**:有明确的触发条件(报错信息 / 用户原话 / 一个能稳定复现的输入),不是猜测。
2. **局部性**:改动集中在一个函数或一处文档段落,爆炸半径小。
3. **可验证**:能用一个已有的或随手写的 verify 脚本 + 纯 `import` 检查验证无回归。
4. **非破坏性**:不改公开函数签名(或仅做纯加法的新函数);不引入新外部依赖。
5. **可回退**:改动前后状态可记入 `learnings.jsonl`(含 `files_changed` 与 `resolution`),随时可还原。

任一不满足 → 归入 `ambiguous` / `pending_confirmation`,**只写日志、不动文件**,并向用户说明待确认。

## 闭环工作流（Phase 5）

```
1. 收尾 Phase 4 后,按"信号源"5 项逐项回顾本轮。
2. 每项发现 → 分类(type)+ 判定是否满足"安全修复闸门"。
3. 满足闸门:
     a. 直接改技能文件(SKILL.md / scripts / references);
     b. 立刻跑回归:先 `python -c "import prism_theme"` 确保不崩,
        再跑一个 verify 脚本确认图形/统计正确;
     c. 回归通过 → 用 log_learning.py 记 status=applied;
        回归失败 → 还原改动,记 status=reverted,并向用户报告。
4. 不满足闸门 → log_learning.py 记 status=pending_confirmation,
   在回复中把条目亮给用户,请其拍板。
5. 全程 trust-but-verify:改完用 Read 复查改动确实落盘。
```

## 护栏（防技能随着时间"越改越烂"）

- **每次自动改动必须跟一次回归验证**;验证失败立即还原,绝不带病交付。
- **日志只追加(append-only)**,不修改历史条目;`files_changed` 与 `resolution` 让改动可还原。
- **公开 API 稳定优先**:新能力用"加法"(新函数)而不是改旧签名;确需改签名时,保留旧名做兼容别名。
- **定期瘦身**:`learnings.jsonl` 超过 ~50 条后,把旧条目整块归档到
  `references/learnings-archive-<日期>.jsonl`(逐条原文,可追溯),归纳为
  本文件末尾"历史案例"区的主题化清单,`learnings.jsonl` 只保留最近 20 条,
  避免日志无限膨胀。执行归档后可用 `python scripts/log_learning.py --check` 体检。

## 学习日志格式 `learnings.jsonl`

每行一条 JSON(UTF-8, 无 BOM),字段:

| 字段 | 类型 | 说明 |
|---|---|---|
| `ts` | str | ISO-8601 时间戳(带时区) |
| `task` | str | 触发本轮复盘的任务简述 |
| `type` | str | `bug`/`convention`/`doc`/`gap`/`ambiguous` |
| `trigger` | str | 触发信号(报错原文 / 用户原话 / 手动补丁描述) |
| `issue` | str | 问题具体描述 |
| `resolution` | str | 做了什么(改了哪个函数/哪段文档) |
| `files_changed` | list[str] | 受影响文件相对技能根目录的路径 |
| `status` | str | `applied` / `pending_confirmation` / `reverted` |
| `verified_by` | str | 回归验证手段(如 `verify_box_v2.py` 或 `import prism_theme`) |
| `safe_auto` | bool | 是否走了"安全修复自动改"通道 |

辅助脚本 `scripts/log_learning.py`:

```bash
# 记录一条(自动改)
python scripts/log_learning.py --type bug --trigger "boxplot 三个箱体全蓝" \
  --issue "sns.boxplot 不显式传 palette= 时默认全蓝" \
  --resolution "新增 prism_boxplot() 内置 palette+hue" \
  --files "scripts/prism_theme.py" --status applied \
  --verified "verify_box_v2.py" --safe-auto

# 列出最近 10 条
python scripts/log_learning.py --list 10
```

## 历史案例（长期记忆,供快速参考）

> 下列为本技能开发期发现的真实坑,已固化进脚本,列此备查——这是技能的**长期记忆**(人类可读、随包分发)。
>
> **三层记忆模型（消除协议期望落差）**：
> 1. **`learnings.jsonl`（活日志 / 滚动工作记录）**：agent 每次任务收尾按本协议追加的结构化 JSON 行(append-only),`log_learning.py --list/--check` 是其入口。全新克隆时此文件可能为空——脚本已优雅降级(打印"暂无记录"、不报错);本技能已**预播种 34 条历史案例**,使其开箱即用。
> 2. **本「历史案例」块（长期记忆）**：上述 jsonl 的主题化、人类可读沉淀,随包持久保留,是技能机构知识主体。
> 3. **`references/learnings-archive-<日期>.jsonl`（冷存储,按需生成）**：当 `learnings.jsonl` 超过 ~50 条时,旧条目整块归档到此(见上方护栏),jsonl 仅保留最近 20 条。**该归档文件不随包预发,由瘦身流程在触发阈值时生成,切勿依赖其预先存在。**

### 环境与可移植性
1. **ensure_env.py Windows pip 路径**(`bug`)→ `pip.exe` 实际在 `Scripts/`(Win) / `bin/`(POSIX),用 `sub` 变量动态拼接;venv 路径从 `sys.executable` 动态推导,禁止硬编码用户名,防共享技能时重复装包。
2. **statsmodels 依赖缺失**(`gap`)→ `build_stats_report('twoway')` 需要 statsmodels,加入 ensure_env REQUIRED。
3. **save_figure Windows 路径**(`gap`)→ `_default_out_dir()`:类 Unix 沙箱保留 `/sandbox/workspace/output`,Windows 回退 `cwd/output`,防生成 `C:\sandbox`。

### 统计正确性与报告
4. **p 值禁用 `<` 阈值写法**(`convention`)→ `format_p()` 一律输出 scipy 实际精确值;下溢兜底 `p=<1e-300`(唯一例外),覆盖 0 / IEEE 最小正双精度。
5. **下溢假 0 值**(`bug`)→ 下溢分支判定收紧为 `p < 1e-300 or not isfinite(p)`,防 `p=0.000e+00` 误导。
6. **p_to_stars(NaN) 误标星号**(`bug`)→ 开头 `not np.isfinite(p)` → 返回 `('', False)` 不标。
7. **完整统计报告**(`gap`)→ `build_stats_report()` + `write_report()`,文件名与图同名(`_report.md`)。
8. **ttest 报告图注误用 ANOVA**(`bug`)→ `format_legend` 调用必须传 `stat_method=method`。
9. **ttest 报告缺前提检验/CI**(`convention`)→ 补 Shapiro 每组 + Levene(自动选 Welch/Student) + 95% CI 列。
10. **配对 t 检验报告**(`gap`)→ `build_stats_report('ttest', paired=True)` 透传 `ttest_two_groups(paired=True)`。
11. **twoway/survival 报告单薄**(`gap`)→ 补齐描述统计/partial η²/事件删失数/中位生存期/Figure Legend;Residual 行不造假数值。
12. **多组生存仅比前两组**(`gap`)→ `_logrank_multi()`:Peto 法整体 χ²(k−1) + 两两比较。
13. **格式错误统计报告:组数 ≥3 严禁两两 t 检验**(`convention`)→ ANOVA + 事后检验一次完成。

### 散点布局与点大小
14. **小样本 jitter 偏侧 + list 输入报错**(`bug`)→ linspace 均衡基准 + 对称小扰动;开头 `np.asarray(values, float)`。
15. **点大小逐组不一致**(`bug`)→ 整图统一:以全图最大 n 算一次,`common_point_size` 全图共用。
16. **点径下限 4pt / 上限 5pt**(`convention`)→ 防 n 大时不可识别、n 小时过大。
17. **n 大散点遮盖**(`convention`)→ `auto_dot_alpha`:按 avg_n 自适应透明度,只压填充面,黑描边不透明。
18. **x 轴长标签重叠**(`convention`)→ `_maybe_rotate_xticklabels`:标签宽 > 刻度间距自动 45° + 右对齐。

### seaborn 兼容性
19. **boxplot 三箱体全蓝**(`bug`)→ `prism_boxplot()` 显式 `palette=colors, hue="Group", legend=False`。
20. **seaborn 0.13+ ax.artists 迁移到 ax.patches**(`bug`)→ 取箱体/设 alpha 必须兼容遍历 `ax.artists + ax.patches`。
21. **box 边框被散点盖**(`bug`)→ 填充留 zorder=2,边框独立线框重绘 zorder=4(`get_path().get_extents()` 兼容 PathPatch)。

### 显著性标注与 y 轴
22. **多组 bracket 重叠**(`bug`)→ `add_pairwise_brackets()` 按 x 跨度降序自动分层,支持 `(label_i,label_j,p)` 直传。
23. **混合标注规则**(`convention`,多次演进)→ 当前:p<0.05 星号、[0.05,0.1) 标精确 p 值、p≥0.1 不标;星号偏移 -0.03 span 骑线、p 值 0。
24. **y 轴顶部刻度缺失**(`bug`)→ `set_nice_ylim()` 收尾到漂亮刻度并补顶部标签。
25. **y 轴丑小数刻度**(`bug`)→ `_floor_half_step()`:刻度只取 0.5 倍数,兜底对齐 `max(0.5, round(step/0.5)*0.5)`。
26. **ylim 留白 ≤1.3×**(`convention`)→ `_nice_ylim_top` max_ticks=9 防拥挤,超限放宽 11 重算;层高 LH=0.043。
27. **dose-response/Grouped 无 y 轴收尾**(`bug`)→ 公开函数 `finish_axes()`;`prism_xy_fit` 内部自动调用。

### 图形封装缺口
28. **缺小提琴图封装**(`gap`)→ `prism_violin()`,API 与 boxplot 一致,内置 palette、`inner=None`。
29. **缺 Survival/XY 封装**(`gap`)→ `prism_survival()`(KM+删失+log-rank+中位虚线)、`prism_xy_fit()`(4PL/linear+R²+IC50),纯加法不破坏旧 API。
30. **配色仅 2 套**(`gap`)→ 扩为 4 套:Okabe-Ito / Paul Tol Bright / Paul Tol Muted / IBM Design Library。

### 文档一致性
31. **box 图误报 Mean±SEM**(`doc`)→ 箱线图 `error_type="median (IQR) shown as box; individual points overlaid"`。
32. **table-mapping Survival 写 lifelines**(`doc`)→ 实际内置 Peto 法,文档修正。
33. **statistics-guide 缺下溢例外**(`doc`)→ 补"仅数值下溢例外 p=<1e-300"。
34. **返回值类型混淆**(`doc`)→ `ttest_two_groups` 返回 **tuple**,`oneway_anova_tukey` 返回 **dict**;`get_palette` 返回 **dict** 不可切片,用 `palette_sequence` 取 list。
