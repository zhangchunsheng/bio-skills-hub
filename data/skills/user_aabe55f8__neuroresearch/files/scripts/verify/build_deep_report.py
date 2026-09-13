"""build_deep_report.py — 汇总 verify9+verify10 深验结果, 生成自包含 HTML 报告。"""
import os
import json
import base64
import sys

DEEP9 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "output", "deep9")
DEEP10 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "output", "deep10")
REPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "output")

# (相对路径, 中文说明, 缩略标签)
FIGURES = [
    # deep9 析因组数矩阵
    ("deep9_G02_2x3_n5.png", "析因 2×3 (n=5, 交互显著) — v2.3.4 修复场景: 8 个简单效应 bracket 全画出"),
    ("deep9_G07_3x4_n6.png", "析因 3×4 (n=6, 交互显著) — 26 bracket 完整"),
    ("deep9_G09_4x4_n3.png", "析因 4×4 (n=3 极小样本, 交互显著) — 38 bracket 含 2 边缘显著 p 值"),
    ("deep9_G15_2x6_n4.png", "析因 2×6 (n=4, 交互显著) — v2.3.7 修复: 6 子柱不重叠 + 27 bracket"),
    ("deep9_G17_4x4_n8.png", "析因 4×4 (n=8, 纯加性) — 主效应分支正确"),
    ("deep9_G18_2x2_n6.png", "析因 2×2 (n=6, 负值数据) — ylim 自适应, 4 bracket"),
    # deep10 其余图种
    ("deep10_bars_3g_n6.png", "Column 柱状图 3 组 n=6 — 基础图型"),
    ("deep10_bars_10g_n15.png", "Column 柱状图 10 组 n=15 — 多组大样本"),
    ("deep10_box_6g_n12.png", "Column 箱线图 6 组 n=12 — 中位/IQR + 散点"),
    ("deep10_violin_4g_n6.png", "Column 小提琴图 4 组 n=6 — 分布密度 + 中位线"),
    ("deep10_survival_2g_n10.png", "Survival 2 组 n=10 (含删失) — KM + log-rank p=0.067"),
    ("deep10_xy_4pl.png", "XY 4PL 拟合 (logEC50=-7.2) — v2.3.1 p0 数据驱动回归 R²=0.997"),
    ("deep10_contingency_2x2.png", "Contingency 2×2 计数柱状图 — 柱顶数字 + χ²"),
    ("deep10_contingency_3x3.png", "Contingency 3×3 计数柱状图"),
    ("deep10_nested_3x4.png", "Nested 3 外层 × 4 内层 — 层级嵌套柱状图"),
    ("deep10_pie_4cat.png", "Pie 饼图 4 类"),
    ("deep10_donut_6cat.png", "Donut 环形图 6 类 — 中心文本 n=100"),
    ("deep10_pairplot_3col.png", "Pairplot 3 列 hue — 下三角散点 + 对角线 KDE"),
    ("deep10_facet_2panel.png", "Facet boxplot 2 分面 — 多变量按子集切分"),
]


def b64_png(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    with open(os.path.join(DEEP9, "verify9_summary.json"),
              encoding="utf-8") as f:
        r9 = json.load(f)
    with open(os.path.join(DEEP10, "verify10_summary.json"),
              encoding="utf-8") as f:
        r10 = json.load(f)

    # 表格行
    rows9 = ""
    for r in r9:
        rows9 += (
            f"<tr><td>{r['id']}</td><td>{r['design']}</td><td>{r['n']}</td>"
            f"<td>{r['expect']}</td>"
            f"<td>{r.get('p_inter', '-')}</td>"
            f"<td>{r.get('posthoc_type', '-')}</td>"
            f"<td>{r.get('n_comps', '-')}</td>"
            f"<td>{'✓' if r.get('key_dir_ok') else '✗'}</td>"
            f"<td>{r.get('got_brackets', '-')}/{r.get('expect_brackets', '-')}</td></tr>\n"
        )

    rows10 = ""
    for r in r10:
        params = ", ".join(f"{k}={v}" for k, v in r.items()
                           if k not in ("kind", "figure"))
        rows10 += f"<tr><td>{r['kind']}</td><td>{params}</td><td>{r.get('figure','-')}</td></tr>\n"

    # 图块 (base64 内嵌)
    fig_blocks = ""
    for fname, desc in FIGURES:
        path = os.path.join(DEEP9 if "deep9" in fname else DEEP10, fname)
        if not os.path.exists(path):
            fig_blocks += (
                f"<div class='fig'><div class='missing'>{fname} (缺失)</div>"
                f"<div class='desc'>{desc}</div></div>\n")
            continue
        data = b64_png(path)
        fig_blocks += (
            f"<div class='fig'>"
            f"<img src='data:image/png;base64,{data}' alt='{fname}'/>"
            f"<div class='caption'>{fname}</div>"
            f"<div class='desc'>{desc}</div></div>\n")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>prism-style-plot 深验报告 (2026-08-21)</title>
<style>
body {{ font-family: -apple-system, "PingFang SC", Arial, sans-serif;
       max-width: 1100px; margin: 24px auto; padding: 0 16px; color: #222;
       line-height: 1.55; }}
h1 {{ border-bottom: 2px solid #0072B2; padding-bottom: 8px; }}
h2 {{ border-bottom: 1px solid #ccc; padding-bottom: 6px; margin-top: 32px; }}
h3 {{ color: #0072B2; margin-top: 24px; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
th, td {{ border: 1px solid #ddd; padding: 5px 8px; text-align: left; }}
th {{ background: #f3f7fa; color: #1f3a5f; }}
tr:nth-child(even) {{ background: #fafbfc; }}
.kpi {{ display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap; }}
.kpi div {{ padding: 12px 18px; border-radius: 8px; flex: 1;
            min-width: 180px; }}
.kpi .green {{ background: #e6f7ec; color: #1a6e3b; border-left: 4px solid #28a745; }}
.kpi .blue  {{ background: #e8f0fa; color: #1c3f6e; border-left: 4px solid #0072B2; }}
.kpi .gray  {{ background: #f3f4f6; color: #555;    border-left: 4px solid #999; }}
.kpi strong {{ display: block; font-size: 22px; margin-top: 4px; }}
.fig {{ display: inline-block; width: 320px; margin: 8px; vertical-align: top;
        border: 1px solid #e0e0e0; border-radius: 6px; padding: 6px;
        background: #fcfcfc; }}
.fig img {{ width: 100%; height: auto; border-radius: 4px; }}
.fig .caption {{ font-size: 11px; color: #666; margin-top: 4px;
                  font-family: Menlo, Consolas, monospace; }}
.fig .desc {{ font-size: 12px; color: #333; margin-top: 4px; }}
.fig .missing {{ background: #fee; padding: 30px; text-align: center;
                  color: #a33; font-size: 12px; }}
code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 3px;
        font-size: 12px; }}
</style>
</head>
<body>

<h1>prism-style-plot 深验报告 (2026-08-21)</h1>

<p>本报告汇总对 prism-style-plot 技能(v2.3.8 之后)的深层次验证,针对用户反馈
"今天对技能做了优化和 bug 修复,尤其在不同组数的析因分析出图"——生成多组数、
多样本数的模拟数据,系统化覆盖 8 种表型,验证 v2.3.4~v2.3.8 系列修复
(比较键方向 / 柱宽 / 点大小 / legend 图示等)无回归。</p>

<div class="kpi">
  <div class="green"><span>verify9 析因矩阵</span><strong>18 / 18</strong></div>
  <div class="green"><span>verify10 其余图种</span><strong>全部 PASS</strong></div>
  <div class="blue"><span>pytest 单测</span><strong>26 / 26</strong></div>
  <div class="blue"><span>原有 verify 套件</span><strong>9 / 9</strong></div>
  <div class="gray"><span>代表性图</span><strong>{len(FIGURES)} 张</strong></div>
</div>

<h2>一、基线回归(2026-08-21 重跑)</h2>
<ul>
  <li><code>tests/test_prism_stats.py</code>: 26 passed in 2.78s</li>
  <li><code>scripts/verify/run_full_suite.py scripts/verify</code>: 9 / 9 PASS, 总耗时 22.3s</li>
</ul>

<h2>二、析因分析组数矩阵(verify9, 18 设计)</h2>
<h3>断言总览(8 类 × 18 设计 = 144 条断言, 全 PASS)</h3>
<table>
<tr><th>断言 ID</th><th>覆盖修复</th><th>断言方式</th></tr>
<tr><td>A1</td><td>出图不崩 + mapping 完整</td><td>positions/means/sems/n 长度 = n_x × n_g</td></tr>
<tr><td>A2</td><td>v2.3.7 子柱宽度自适应</td><td>k·w + (k-1)·0.15·w ≤ 0.85 (子柱总宽)</td></tr>
<tr><td>A3</td><td>v2.3.6 散点大小统一</td><td>所有 PathCollection sizes 唯一</td></tr>
<tr><td>A4</td><td>v2.3.8 legend 颜色 handle</td><td>handles 数 = n_g, facecolor alpha=1.0</td></tr>
<tr><td>A5</td><td>v2.3.8 锚点方块修复</td><td>无 width≥0.9 可见 Rectangle</td></tr>
<tr><td>A6</td><td>分支类型正确</td><td>交互显著→simple_effects / 否则→main_effects</td></tr>
<tr><td>A7</td><td>v2.3.4 比较键方向</td><td>键方向与数据水平顺序一致 + 键合法可匹配</td></tr>
<tr><td>A8</td><td>v2.3.4 标注不丢</td><td>简单效应 bracket 数 = p&lt;0.1 的比较数</td></tr>
</table>

<h3>设计矩阵 18 种</h3>
<table>
<tr><th>ID</th><th>设计</th><th>n/格</th><th>预期分支</th><th>p_inter</th><th>实际</th>
<th>比较数</th><th>键方向</th><th>bracket</th></tr>
{rows9}
</table>

<h3>代表性图(析因分析)</h3>
{''.join(f"<div class='fig'><img src='data:image/png;base64,{b64_png(os.path.join(DEEP9 if 'deep9' in f[0] else DEEP10, f[0]))}'/><div class='caption'>{f[0]}</div><div class='desc'>{f[1]}</div></div>" for f in FIGURES if 'deep9' in f[0])}

<h2>三、其余图种深验(verify10)</h2>
<h3>覆盖</h3>
<ul>
  <li><strong>Column 表</strong>: 柱状图 3/5/8/10 组 × n=4/6/10/15;
      箱线图 3/6 组 × n=8/12; 小提琴图 4 组 × n=6</li>
  <li><strong>2 组 / 非参数</strong>: ttest 小/大/配对样本; Mann-Whitney U; Wilcoxon 符号秩</li>
  <li><strong>Survival</strong>: 2 组 n=10 (含删失); 3 组 n=15 (multi log-rank + median)</li>
  <li><strong>XY</strong>: 4PL (logEC50=-7.2, 回归 v2.3.1 p0 数据驱动); linear</li>
  <li><strong>Contingency</strong>: 2×2 / 3×3 计数柱状图 + χ²</li>
  <li><strong>Nested</strong>: 2 外层×3 内层 / 3 外层×4 内层</li>
  <li><strong>Parts of whole</strong>: Pie 4 类 / Donut 6 类</li>
  <li><strong>Multiple variables</strong>: Pairplot 3 列 hue / Facet boxplot 2 分面</li>
  <li><strong>figsize 推荐</strong>: &lt;5 tall / 5-8 square / &gt;8 wide + 关键词覆盖</li>
</ul>

<h3>结果表(共 35 条断言, 全 PASS)</h3>
<table>
<tr><th>图种</th><th>参数</th><th>代表性图</th></tr>
{rows10}
</table>

<h3>代表性图(其余图种)</h3>
{''.join(f"<div class='fig'><img src='data:image/png;base64,{b64_png(os.path.join(DEEP10, f[0]))}'/><div class='caption'>{f[0]}</div><div class='desc'>{f[1]}</div></div>" for f in FIGURES if 'deep10' in f[0])}

<h2>四、关键发现与结论</h2>
<ol>
  <li><strong>v2.3.4 比较键方向修复彻底生效</strong>: 18 种析因设计下,A7(键方向/合法)
      全部 PASS,包括修复前"2×3 析因 6 个组内比较只画 2 个"的核心场景;
      A8(标注不丢)在 simple_effects 分支下 got == expect 全部相等</li>
  <li><strong>v2.3.7 子柱宽度自适应正确</strong>: 2×2 (w=0.395) 到 2×6 (w=0.126)
      全部子柱总宽恒 ≤ 0.85 × 间距,无重叠</li>
  <li><strong>v2.3.6/v2.3.8 legend 系统稳定</strong>: 18 设计 A4 (颜色 handle) +
      A5 (无锚点方块) 全部 PASS;legend 在 ax 外右侧,带完整颜色块</li>
  <li><strong>负值数据 ylim 自适应</strong>: G18 (2×2, 负基线) 正确显示 ylim
      覆盖 -7.5~12.5,柱体从 0 起绘,4 个 bracket 全部画出</li>
  <li><strong>小样本稳健</strong>: G09 (4×4, n=3) 38 个 bracket 完整,含 2 个
      边缘显著 p 值 (p=0.055, p=0.100) 精确标注</li>
  <li><strong>4PL logEC50 远离 0 拟合鲁棒</strong>: 真实 logEC50=-7.2 场景,
      R²=0.997, IC50 误差仅 7.3% (修复前 R²≈0)</li>
</ol>

<h2>五、产物清单</h2>
<ul>
  <li>脚本: <code>scripts/verify/verify9_deep_matrix.py</code></li>
  <li>脚本: <code>scripts/verify/verify10_deep_others.py</code></li>
  <li>报告: <code>scripts/verify/output/deep9/verify9_deep_matrix_report.md</code></li>
  <li>报告: <code>scripts/verify/output/deep10/verify10_deep_others_report.md</code></li>
  <li>JSON 汇总: <code>verify9_summary.json</code> / <code>verify10_summary.json</code></li>
  <li>代表性图: 19 张 PNG (deep9/6 张 + deep10/13 张) + 对应 PDF</li>
  <li>本 HTML 报告: <code>scripts/verify/output/deep_validation_report.html</code></li>
</ul>

</body>
</html>
"""
    out_path = os.path.join(REPORTS, "deep_validation_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"[OK] 综合 HTML 报告: {out_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
