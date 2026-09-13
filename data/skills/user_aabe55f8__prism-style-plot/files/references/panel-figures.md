# 多数据集合并面板图与总报告

当用户说"把多张图画在一起""像 Nature 那样 A/B/C"或"汇总成一个报告文档"时使用。`read_excel_sheets()` 支持单 Excel 多 sheet 一键读取（见下方约定）。

核心函数 `compose_panel_figure(panels, out_dir, name, ...)` 把**多张独立数据集合并成一张 Nature 风格多面板大图**，并（默认）同时保留每张图的独立 PNG/PDF 与独立统计报告；`build_master_report(...)` 再生成一份**合并总报告 HTML**——顶部放合并面板图，下方依次列出各面板独立统计报告（图 + 表 + Figure Legend），可双击即看。

## 调用契约

```python
from prism_theme import compose_panel_figure, build_master_report, build_stats_report, write_report

panels = []
for ds in datasets:                       # 遍历每个 Excel/CSV
    groups, labels = read_table(ds)       # 或你自己的读表逻辑
    res = oneway_anova_tukey(groups, labels)
    # 该面板画到"给定 ax"的回调（关键：所有 prism_* 都支持 ax 参数）
    def draw(ax, groups=groups, labels=labels, res=res):
        prism_bars(ax, groups, labels)
        add_pairwise_brackets(ax, res["pairwise"], labels=labels)
    report_md = build_stats_report("anova_tukey", description=ds.name,
                                    groups=groups, labels=labels)
    panels.append({
        "draw": draw,                    # 必填：callable(ax)
        "name": ds.stem,                 # 独立文件名前缀
        "stats_md": report_md,            # 该面板独立 Markdown 报告
        "title": ds.stem,                # 面板小标题（可选）
    })

# 自动生成合并面板图 + 独立原图 + 独立统计报告 + 总 HTML 报告
result = compose_panel_figure(
    panels, out_dir="output", name="Figure_1",
    layout="auto",                        # 自动网格：2→1×2, 3→1×3, 4→2×2, 5–6→2×3
    panel_titles=["A cytokine", "B cytokine", "C cytokine"],
    panel_shape="square",                 # cm 形态：tall(3×5)/square(5×5)/wide(7×5)
    font_scale=1.0,                       # 在主题"基线 −4"基础上再缩放
)
# result["combined_png/pdf"]：合并大图
# result["master_html"]：总报告 HTML（合并图 + 各面板独立统计依次列出）
# result["panels"]：每面板独立产物路径清单
```

## 关键约定

- **每张数据各自统计、各自出独立报告**；合并图只是视觉组合，不篡改独立统计。
- 每个面板的 `draw` 回调必须接受 `ax` 作为首个位置参数，且**不在内部调用 `plt.show()` / 创建新 figure**。
- `layout="auto"` 按面板数自动排布：2→`1×2`，3→`1×3`，4→`2×2`，5–6→`2×3`，7–9→`3×3`，>9→4 列。
- 也支持 `layout=(rows, cols)` 自定义，格子不够会抛 `ValueError`。
- `standalone=False` 可关闭独立原图/报告，只产出合并大图与总 HTML（不推荐；默认 `standalone=True`）。
- 自动加 A/B/C… 字母标注在每张面板左上角；若传了 `suptitle`，合并图顶部再加总标题。
- **画布严格走 cm 预设**：`panel_shape="tall"` → 单面板 3×5 cm，`"square"` → 5×5 cm，`"wide"` → 7×5 cm；也可用 `panel_size_cm=(6, 5)` 直接指定；合并图总尺寸按面板数 + 间距自动推算。
- **字号从主题派生**：A/B/C 标注与总标题跟随 `apply_prism_theme` 的 "基线 −4" 字号（`font_scale` 可缩放），不再硬编码。
- 总报告 HTML 内嵌合并图 base64，并提供"Download combined PDF"按钮；每面板独立统计报告正文也被内嵌，且带各自独立 HTML 报告的链接。

## 单 Excel 多 sheet 一键成面板

数据可放在同一个 Excel 的不同 sheet：用 `read_excel_sheets(path)` 一次读出所有 sheet（每个 sheet 独立走长/宽格式判别、自动取 ylabel），返回 `list[dict]`，每个元素带 `"sheet"`（工作表名，作面板标题）与 `"source"`（`路径::Sheet名`）。再循环生成 panels 即可——不必为每个 sheet 单独发一个文件：

```python
from prism_theme import (read_excel_sheets, compose_panel_figure,
                         build_stats_report, oneway_anova_tukey,
                         prism_bars, add_pairwise_brackets)

infos = read_excel_sheets("all_data.xlsx")   # 读全部 sheet；或 sheets=["A","B","C"] 指定
panels = []
for info in infos:                            # 每张 sheet = 一个面板
    groups, labels = info["groups"], info["labels"]
    ylabel = info["ylabel"]
    res = oneway_anova_tukey(groups, labels)
    def draw(ax, groups=groups, labels=labels, res=res, ylabel=ylabel):
        prism_bars(ax, groups, labels)
        add_pairwise_brackets(ax, res["pairwise"], labels=labels)
        if ylabel:
            ax.set_ylabel(ylabel)
    report_md = build_stats_report("anova_tukey", description=info["sheet"],
                                    groups=groups, labels=labels)
    panels.append({"draw": draw, "name": info["sheet"],
                   "stats_md": report_md, "title": info["sheet"]})

result = compose_panel_figure(panels, out_dir="output", name="Figure_1",
                               panel_shape="square", font_scale=1.0)
```

若不同 sheet 表型不同（如某 sheet 是生存数据、某 sheet 是剂量-响应），循环里按 `info["format"]` / 业务判断选择对应的 `prism_*` 与统计量即可，不必统一。空 sheet 默认跳过。
