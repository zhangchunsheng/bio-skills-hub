"""
report_renderer.py — 报告模板渲染与格式转换器
按指定模板组装报告，支持Markdown/HTML/腾讯文档三种输出。

用法:
    python report_renderer.py --input risk_scored.json --format markdown --output report.md
    python report_renderer.py --input risk_scored.json --format html --output report.html
    python report_renderer.py --input risk_scored.json --format tencent-docs --output report.md
"""
import argparse
import json
import os
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(template_name):
    """加载模板文件"""
    path = os.path.join(SKILL_DIR, "assets", template_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fmt_date(iso_string):
    """格式化ISO日期字符串为可读格式"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_string


def urgency_icon(urgency):
    """紧急程度图标"""
    return {"高": "🔴", "中": "🟡", "低": "🟢"}.get(urgency, "⚪")


def render_policy_overview(policies):
    """渲染政策清单概览表"""
    if not policies:
        return "本期无新增政策。\n"

    lines = [
        "| # | 发布机构 | 政策标题 | 日期 | 机构类别 | 紧急度 | 风险 |",
        "|---|---------|---------|------|---------|-------|------|"
    ]

    for i, p in enumerate(policies, 1):
        title = (p.get("title", "N/A")[:50] + "...") if len(p.get("title", "")) > 50 else p.get("title", "N/A")
        risk_label = p.get("risk", {}).get("label", "N/A")
        lines.append(
            f"| {i} | {p.get('_agency_name', 'N/A')} | {title} | "
            f"{p.get('date', 'N/A')} | {p.get('_agency_type', 'N/A')} | "
            f"{urgency_icon(p.get('urgency', ''))} | {risk_label} |"
        )

    return "\n".join(lines) + "\n"


def render_policy_detail(policy, index):
    """渲染单条政策的深度分析"""
    title = policy.get("title", "N/A")
    source = policy.get("_agency_name", "N/A")
    date = policy.get("date", "N/A")
    url = policy.get("url", "N/A")
    policy_type = policy.get("policy_type", "N/A")
    urgency = policy.get("urgency", "N/A")
    risk = policy.get("risk", {})
    snippet = policy.get("snippet", "暂无摘要")

    # 四维度影响分析
    impact = policy.get("impact_analysis", {})
    drug_impact = impact.get("drug_safety", impact.get("药监", "待分析"))
    insurance_impact = impact.get("medical_insurance", impact.get("医保", "待分析"))
    tcm_impact = impact.get("tcm", impact.get("中医药", "待分析"))
    health_impact = impact.get("health_commission", impact.get("卫健委", "待分析"))

    # 分岗位建议
    advice = policy.get("action_advice", {})

    lines = [
        f"\n### 政策 #{index}：{title}\n",
        f"- **来源**：{source} | **发布日期**：{date}",
        f"- **原文链接**：{url}",
        f"- **政策类型**：{policy_type}",
        f"- **生效时间**：{policy.get('effective_date', '待确认')}",
        f"- **时限分级**：{policy.get('time_classification', '待分类')}",
        f"",
        f"#### 政策要点摘要",
        f"> {snippet}",
        f"",
        f"#### 分维度影响分析",
        f"**（A）药监维度**：{drug_impact}",
        f"**（B）医保维度**：{insurance_impact}",
        f"**（C）中医药维度**：{tcm_impact}",
        f"**（D）卫健委维度**：{health_impact}",
        f"",
        f"#### 分岗位行动建议",
    ]

    if advice:
        lines.append("| 岗位 | What（影响什么） | So What（影响多大） | Now What（现在做什么） |")
        lines.append("|------|-----------------|--------------------|----------------------|")
        for role_key in ["合规", "GA", "MA", "Mkt", "高管"]:
            role_advice = advice.get(role_key, {})
            lines.append(
                f"| {role_key} | {role_advice.get('what', '—')} | "
                f"{role_advice.get('so_what', '—')} | {role_advice.get('now_what', '—')} |"
            )
    else:
        lines.append("_暂未生成行动建议_")

    lines.append(f"\n#### 风险评级")
    lines.append(f"- 影响程度：{risk.get('impact', 'N/A')}/5 | 发生概率：{risk.get('probability', 'N/A')}/5")
    lines.append(f"- 风险等级：{risk.get('label', 'N/A')}（{risk.get('score', 'N/A')}/25）")
    lines.append(f"- 建议动作：{risk.get('action', 'N/A')}")

    return "\n".join(lines)


def render_markdown(data, template_name="report_default.md"):
    """渲染完整Markdown报告"""
    meta = data.get("meta", {})
    policies = data.get("policies", [])
    risk_summary = meta.get("risk_summary", {})

    # 加载模板
    try:
        template = load_template(template_name)
    except FileNotFoundError:
        template = None

    report = []
    report.append("═══════════════════════════════════════")
    report.append("# 医药政策雷达 · 监测报告")
    report.append("═══════════════════════════════════════")
    report.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**最终有效政策**：{meta.get('final_count', len(policies))} 条")
    report.append(f"**风险分布**：🔴{risk_summary.get('red', 0)} 🟡{risk_summary.get('yellow', 0)} 🟢{risk_summary.get('green', 0)}")
    report.append("")

    # 执行摘要
    report.append("---")
    report.append("## 一、执行摘要")
    report.append("")

    red_policies = [p for p in policies if p.get("risk", {}).get("level") == "red"]
    if red_policies:
        report.append("### ⚠️ 本期高风险预警")
        for p in red_policies:
            report.append(f"- **{p.get('title', 'N/A')}** — {p.get('_agency_name', '')} ({p.get('risk', {}).get('score', 'N/A')}/25)")
    else:
        report.append("✅ 本期无红色预警政策。")
    report.append("")

    # 政策清单概览
    report.append("---")
    report.append("## 二、政策清单概览")
    report.append("")
    report.append(render_policy_overview(policies))
    report.append("")

    # 逐条深度分析
    report.append("---")
    report.append("## 三、逐条深度分析")
    for i, policy in enumerate(policies, 1):
        report.append(render_policy_detail(policy, i))
        report.append("")

    # 综合趋势
    report.append("---")
    report.append("## 四、综合趋势研判")
    report.append("")
    report.append("- 本周政策热词：（由认知切片分析生成）")
    report.append("- 跨省政策趋同/差异信号：（由认知切片分析生成）")
    report.append("- 需持续跟踪的政策窗口：（由认知切片分析生成）")
    report.append("")

    # 检索日志
    report.append("---")
    report.append("## 五、检索日志")
    report.append("")
    report.append("| 时间 | 覆盖范围 | 原始命中 | 去重 | 噪音过滤 | 最终有效 |")
    report.append("|------|---------|---------|------|---------|---------|")
    report.append(
        f"| {datetime.now().strftime('%H:%M')} | "
        f"全国31省×4机构 | {meta.get('total_raw', 'N/A')} | "
        f"-{meta.get('duplicates_removed', 'N/A')} | "
        f"-{meta.get('noise_removed', 'N/A')} | "
        f"{meta.get('final_count', 'N/A')} |"
    )
    report.append("")

    report.append("---")
    report.append("*本报告由医药政策雷达AI自动生成，仅供参考，不作为法律意见。*")

    return "\n".join(report)


def render_html(data):
    """将Markdown报告转换为HTML"""
    md_content = render_markdown(data)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>医药政策雷达 · 监测报告</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 960px; margin: 40px auto; padding: 20px; line-height: 1.8; color: #1a1a1a; }}
  h1 {{ color: #c0392b; border-bottom: 3px solid #c0392b; padding-bottom: 10px; }}
  h2 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 30px; }}
  h3 {{ color: #34495e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px; }}
  th, td {{ border: 1px solid #ddd; padding: 10px 12px; text-align: left; }}
  th {{ background: #34495e; color: #fff; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  .risk-red {{ color: #e74c3c; font-weight: bold; }}
  .risk-yellow {{ color: #f39c12; font-weight: bold; }}
  .risk-green {{ color: #27ae60; }}
  blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #555; margin: 10px 0; }}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{md_content}</pre>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="渲染医药政策监测报告")
    parser.add_argument("--input", required=True, help="风险评估后的JSON文件")
    parser.add_argument("--format", default="markdown",
                        choices=["markdown", "html", "tencent-docs"],
                        help="输出格式")
    parser.add_argument("--template", default="report_default.md",
                        help="模板文件名（仅markdown格式）")
    parser.add_argument("--output", default="report.md", help="输出文件路径")
    args = parser.parse_args()

    data = load_input(args.input)

    if args.format == "html":
        content = render_html(data)
        if not args.output.endswith(".html"):
            args.output = args.output.rsplit(".", 1)[0] + ".html"
    else:
        content = render_markdown(data, args.template)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] 报告已生成 → {args.output} (格式: {args.format})")

    # 腾讯文档提示
    if args.format == "tencent-docs":
        print("[INFO] 腾讯文档格式：请通过腾讯文档MCP连接器将内容写入在线文档。")


if __name__ == "__main__":
    main()
