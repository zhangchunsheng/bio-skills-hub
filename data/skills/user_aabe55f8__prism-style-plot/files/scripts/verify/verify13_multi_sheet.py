"""verify13（v2.7.2）：单 Excel 多 sheet 一键读取 → 合并面板图。

验证新增的 read_excel_sheets() 能正确读出同一 Excel 中多个工作表，
每个 sheet 独立走长/宽格式判别，并无损走通 compose_panel_figure 合并流程。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import pandas as pd  # noqa: E402
from verify_common import make_groups  # noqa: E402
from prism_theme import (  # noqa: E402
    read_excel_sheets,
    compose_panel_figure,
    build_stats_report,
    oneway_anova_tukey,
    prism_bars,
    add_pairwise_brackets,
    apply_prism_theme,
)

OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)


def main():
    labels = ["Sham", "TBI", "TBI+Treat"]
    # 三个 sheet，每组均值差异明显以确保 ANOVA 显著
    specs = {
        "Cytokine_A": (10.0, 12.0, 16.0),
        "Cytokine_B": (8.0, 9.5, 13.0),
        "Cytokine_C": (5.0, 7.0, 9.5),
    }

    # 1) 造一个含 3 个 sheet 的 xlsx（宽格式：每列一组）
    xlsx_path = os.path.join(OUT, "verify13_multisheet.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        for idx, (sheet, base) in enumerate(specs.items()):
            groups = make_groups(
                n_per_group=6, n_groups=3, base=base, sd=0.6, seed=100 + idx
            )
            df = pd.DataFrame({labels[i]: groups[i] for i in range(3)})
            df.to_excel(w, sheet_name=sheet, index=False)

    # 2) 一键读多 sheet
    infos = read_excel_sheets(xlsx_path)
    assert len(infos) == 3, f"应读出 3 个 sheet，实际 {len(infos)}"
    for info in infos:
        assert info["format"] == "wide", info
        assert len(info["groups"]) == 3
        assert info["sheet"] in specs
        # source 改写为 "路径::Sheet名"
        assert "::" in info["source"], info["source"]

    # 3) 循环生成 panels 并合并
    apply_prism_theme()
    panels = []
    for info in infos:
        groups = info["groups"]
        labels_ = info["labels"]
        res = oneway_anova_tukey(groups, labels_)

        def draw(ax, groups=groups, labels_=labels_, res=res):
            prism_bars(ax, groups, labels_)
            add_pairwise_brackets(ax, res["pairwise"], labels=labels_)

        rep = build_stats_report(
            "anova_tukey", description=info["sheet"],
            groups=groups, labels=labels_,
        )
        panels.append({
            "draw": draw,
            "name": info["sheet"],
            "stats_md": rep,
            "title": info["sheet"],
        })

    res = compose_panel_figure(
        panels, out_dir=OUT, name="verify13_combined",
        panel_shape="square", font_scale=1.0,
    )
    assert res["combined_png"] and os.path.exists(res["combined_png"])
    assert res["master_html"] and os.path.exists(res["master_html"])
    for p in res["panels"]:
        for key in ("png", "pdf", "report_html"):
            assert p.get(key) and os.path.exists(p[key]), \
                f"面板 {p['name']} 缺 {key}"
        assert p.get("report_md"), f"面板 {p['name']} 缺 report_md（统计报告内容）"

    print(f"[verify13] 读出 {len(infos)} 个 sheet：{[i['sheet'] for i in infos]}")
    print("[verify13] 合并图:", res["combined_png"])
    print("[verify13] 总报告:", res["master_html"])
    print("[verify13] OK")


if __name__ == "__main__":
    main()
