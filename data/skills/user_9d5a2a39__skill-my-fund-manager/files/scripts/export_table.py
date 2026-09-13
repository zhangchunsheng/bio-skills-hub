"""
基金经理数据表格导出模块
导出已蒸馏基金经理的名单、投资风格、十大重仓信息。
Excel（openpyxl，自动安装）优先，fallback 到 CSV（标准库，零依赖）。
"""

import os
import csv
from datetime import datetime

import _common
from _common import log, read_json, write_json, ROSTER_PATH, MANAGERS_DIR, EXPORTS_DIR, load_manager, list_manager_files


def _ensure_openpyxl():
    """确保 openpyxl 可用；缺失时自动安装，失败返回 None（用 CSV）"""
    try:
        import openpyxl
        return openpyxl
    except ImportError:
        log.info("openpyxl 未安装，尝试自动安装...")
        try:
            import subprocess, sys
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "openpyxl"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            import openpyxl
            log.info("openpyxl 安装成功")
            return openpyxl
        except Exception as e:
            log.warning(f"openpyxl 安装失败({e})，回退到 CSV")
            return None


def _gather_all_data():
    """收集所有已蒸馏经理的数据"""
    roster = read_json(ROSTER_PATH, default={"managers": []})
    managers_data = []

    for entry in roster.get("managers", []):
        mgr_id = entry["id"]
        mgr = load_manager(mgr_id) or {}
        managers_data.append({
            "id": mgr_id,
            "name": entry.get("name", mgr.get("name", "")),
            "company": entry.get("company", mgr.get("company", "")),
            "status": entry.get("status", ""),
            "add_date": entry.get("add_date", ""),
            "last_refresh": entry.get("last_refresh", ""),
            "bio": mgr.get("bio", ""),
            "specialty": mgr.get("specialty", ""),
            "style_tags": ", ".join(mgr.get("style_tags", [])),
            "style_code": mgr.get("style_code", ""),
            "industry_preference": ", ".join(mgr.get("industry_preference", [])),
            "viewpoint_human": mgr.get("viewpoint_human", ""),
            "style_dna": mgr.get("style_dna", ""),
            "top_holdings": mgr.get("top_holdings", []),
            "holdings_report_date": mgr.get("holdings_report_date", ""),
            "tenure_return": entry.get("tenure_return", mgr.get("tenure_return", "")),
            "performance": mgr.get("performance", {}),
        })

    return managers_data


def export_roster_csv(output_path=None):
    """导出名单为 CSV"""
    if not output_path:
        output_path = os.path.join(EXPORTS_DIR, f"roster_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")

    managers = _gather_all_data()
    headers = ["序号", "姓名", "基金公司", "状态", "擅长领域", "风格标签", "风格码", "任职回报", "添加日期", "最后刷新"]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i, m in enumerate(managers):
            writer.writerow([
                i + 1, m["name"], m["company"], m["status"],
                m["specialty"], m["style_tags"], m["style_code"],
                m["tenure_return"], m["add_date"], m["last_refresh"],
            ])

    log.info(f"名单 CSV 已导出：{output_path}（{len(managers)}人）")
    return output_path


def export_style_csv(output_path=None):
    """导出投资风格为 CSV"""
    if not output_path:
        output_path = os.path.join(EXPORTS_DIR, f"style_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")

    managers = _gather_all_data()
    headers = ["姓名", "公司", "投资风格简介", "擅长领域", "风格标签", "风格码", "行业偏好", "季报人话观点", "思维DNA"]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for m in managers:
            writer.writerow([
                m["name"], m["company"], m["bio"], m["specialty"],
                m["style_tags"], m["style_code"], m["industry_preference"],
                m["viewpoint_human"][:500], m["style_dna"][:500],
            ])

    log.info(f"投资风格 CSV 已导出：{output_path}")
    return output_path


def export_holdings_csv(output_path=None):
    """导出十大重仓为 CSV"""
    if not output_path:
        output_path = os.path.join(EXPORTS_DIR, f"holdings_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")

    managers = _gather_all_data()
    headers = ["经理姓名", "公司", "排名", "股票代码", "股票名称", "总占比(%)", "出现次数", "覆盖基金数", "报告期"]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for m in managers:
            for rank, h in enumerate(m.get("top_holdings", [])[:20]):
                writer.writerow([
                    m["name"], m["company"], rank + 1,
                    h.get("code", ""), h.get("name", ""),
                    h.get("total_ratio", ""), h.get("appear_count", ""),
                    h.get("fund_count", ""), m["holdings_report_date"],
                ])

    log.info(f"十大重仓 CSV 已导出：{output_path}")
    return output_path


def export_excel(output_path=None):
    """导出多 sheet Excel（名单+风格+重仓）"""
    openpyxl = _ensure_openpyxl()
    if not openpyxl:
        log.warning("openpyxl 不可用，改用 CSV 导出")
        p1 = export_roster_csv()
        p2 = export_style_csv()
        p3 = export_holdings_csv()
        return {"format": "csv", "files": [p1, p2, p3]}

    if not output_path:
        output_path = os.path.join(EXPORTS_DIR, f"fund_managers_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")

    managers = _gather_all_data()
    wb = openpyxl.Workbook()

    # Sheet 1: 名单
    ws1 = wb.active
    ws1.title = "基金经理名单"
    headers1 = ["序号", "姓名", "基金公司", "状态", "擅长领域", "风格标签", "风格码", "任职回报", "添加日期", "最后刷新"]
    ws1.append(headers1)
    for col in range(1, len(headers1) + 1):
        ws1.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
    for i, m in enumerate(managers):
        ws1.append([
            i + 1, m["name"], m["company"], m["status"],
            m["specialty"], m["style_tags"], m["style_code"],
            m["tenure_return"], m["add_date"], m["last_refresh"],
        ])
    ws1.column_dimensions["A"].width = 6
    ws1.column_dimensions["B"].width = 10
    ws1.column_dimensions["C"].width = 15

    # Sheet 2: 投资风格
    ws2 = wb.create_sheet("投资风格")
    headers2 = ["姓名", "公司", "投资风格简介", "擅长领域", "风格标签", "风格码", "行业偏好", "季报人话观点", "思维DNA"]
    ws2.append(headers2)
    for col in range(1, len(headers2) + 1):
        ws2.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
    for m in managers:
        ws2.append([
            m["name"], m["company"], m["bio"], m["specialty"],
            m["style_tags"], m["style_code"], m["industry_preference"],
            m["viewpoint_human"][:500], m["style_dna"][:500],
        ])
    ws2.column_dimensions["C"].width = 40
    ws2.column_dimensions["H"].width = 50
    ws2.column_dimensions["I"].width = 60

    # Sheet 3: 十大重仓
    ws3 = wb.create_sheet("十大重仓")
    headers3 = ["经理姓名", "公司", "排名", "股票代码", "股票名称", "总占比(%)", "出现次数", "覆盖基金数", "报告期"]
    ws3.append(headers3)
    for col in range(1, len(headers3) + 1):
        ws3.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
    for m in managers:
        for rank, h in enumerate(m.get("top_holdings", [])[:20]):
            ws3.append([
                m["name"], m["company"], rank + 1,
                h.get("code", ""), h.get("name", ""),
                h.get("total_ratio", ""), h.get("appear_count", ""),
                h.get("fund_count", ""), m["holdings_report_date"],
            ])
    ws3.column_dimensions["D"].width = 12
    ws3.column_dimensions["E"].width = 15

    # Sheet 4: 业绩数据
    ws4 = wb.create_sheet("业绩数据")
    headers4 = ["姓名", "公司", "基金代码", "基金名称", "近1月(%)", "近3月(%)", "近6月(%)", "近1年(%)", "近3年(%)", "今年以来(%)", "管理费率(%)"]
    ws4.append(headers4)
    for col in range(1, len(headers4) + 1):
        ws4.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
    for m in managers:
        perf = m.get("performance", {})
        funds = perf.get("funds", [])
        if not funds:
            ws4.append([m["name"], m["company"], "", "", "", "", "", "", "", "", ""])
        for f in funds:
            returns = f.get("returns", {})
            ws4.append([
                m["name"], m["company"], f.get("fund_code", ""), f.get("fund_name", ""),
                returns.get("近1月", ""), returns.get("近3月", ""), returns.get("近6月", ""),
                returns.get("近1年", ""), returns.get("近3年", ""), returns.get("今年以来", ""),
                f.get("fee_rate", ""),
            ])

    wb.save(output_path)
    log.info(f"Excel 已导出：{output_path}（{len(managers)}人，4个sheet）")
    return {"format": "excel", "file": output_path}


def export_all(format="auto"):
    """导出全部数据。format: auto/excel/csv"""
    if format == "auto":
        openpyxl = _ensure_openpyxl()
        format = "excel" if openpyxl else "csv"

    if format == "excel":
        return export_excel()
    else:
        p1 = export_roster_csv()
        p2 = export_style_csv()
        p3 = export_holdings_csv()
        return {"format": "csv", "files": [p1, p2, p3]}


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python export_table.py excel [输出路径]   # 导出Excel(多sheet)")
        print("  python export_table.py csv [输出目录]     # 导出CSV(3个文件)")
        print("  python export_table.py auto               # 自动选择格式")
        sys.exit(1)

    fmt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None

    result = export_all(format=fmt)
    if result.get("format") == "excel":
        print(f"✅ Excel 导出成功：{result['file']}")
    else:
        print(f"✅ CSV 导出成功（{len(result['files'])}个文件）：")
        for f in result["files"]:
            print(f"   {f}")
