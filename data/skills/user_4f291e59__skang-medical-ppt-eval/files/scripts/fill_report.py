# -*- coding: utf-8 -*-
"""将评估数据 JSON 注入报告模板，生成独立 HTML 报告。

用法: python fill_report.py <模板> <数据json> <输出html>
"""
import json
import sys


def main() -> None:
    template_path, data_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    # 防止 JSON 中出现 </script> 破坏 HTML
    payload = payload.replace("</", "<\\/")
    if "__REPORT_DATA__" not in html:
        print("模板中未找到 __REPORT_DATA__ 占位符")
        sys.exit(1)
    html = html.replace("__REPORT_DATA__", payload)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {out_path}")


if __name__ == "__main__":
    main()
