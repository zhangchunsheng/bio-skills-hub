#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗表单自动生成脚本
根据字段JSON Schema自动生成 HTML / JSON / XML / Excel 四种格式表单文件
用法: python generate_form.py <schema.json> [--outdir form_output]
"""

import json
import sys
import os
import argparse
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# 全局样式（医疗蓝主题，符合SKILL规范）
# ─────────────────────────────────────────────────────────────
CSS_STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  font-size: 14px; color: #333; background: #f5f7fa; padding: 20px;
}
.form-container {
  max-width: 860px; margin: 0 auto; background: #fff;
  border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden;
}
.form-header {
  background: linear-gradient(135deg, #1a6fc4 0%, #2196F3 100%);
  color: #fff; padding: 24px 32px;
}
.form-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.form-desc { font-size: 13px; opacity: 0.85; }
form { padding: 24px 32px; }
fieldset.form-section {
  border: 1px solid #e4e8f0; border-radius: 6px;
  padding: 16px 20px; margin-bottom: 20px; background: #fafbfc;
}
legend.section-title {
  font-size: 15px; font-weight: 600; color: #1a6fc4;
  padding: 0 8px; background: #fff;
  border: 1px solid #c7d8f0; border-radius: 4px;
}
.form-row { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 14px; }
.form-group { flex: 1 1 280px; display: flex; flex-direction: column; gap: 4px; }
.form-group.full-width { flex: 1 1 100%; }
label { font-size: 13px; color: #555; font-weight: 500; }
label .required { color: #e53935; margin-left: 2px; }
input[type=text], input[type=number], input[type=date],
input[type=email], input[type=tel], select, textarea {
  width: 100%; padding: 8px 12px; border: 1px solid #d0d7e3;
  border-radius: 4px; font-size: 14px; color: #333; background: #fff;
  transition: border-color 0.2s; font-family: inherit;
}
input:focus, select:focus, textarea:focus {
  outline: none; border-color: #2196F3; box-shadow: 0 0 0 2px rgba(33,150,243,0.15);
}
textarea { min-height: 80px; resize: vertical; }
select[multiple] { min-height: 100px; }
.radio-group, .checkbox-group { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 4px; }
.radio-item, .checkbox-item {
  display: flex; align-items: center; gap: 6px; font-size: 14px; cursor: pointer;
}
.radio-item input, .checkbox-item input {
  width: 16px; height: 16px; cursor: pointer; accent-color: #2196F3;
}
.matrix-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
.matrix-table th {
  background: #e3edf8; color: #1a6fc4; padding: 8px 10px;
  border: 1px solid #c7d8f0; text-align: center; font-weight: 600;
}
.matrix-table td { padding: 6px 8px; border: 1px solid #e0e7ef; vertical-align: middle; }
.matrix-table tr:nth-child(even) { background: #f5f8fc; }
.matrix-table td input, .matrix-table td select {
  width: 100%; padding: 4px 6px; border: 1px solid #d0d7e3;
  border-radius: 3px; font-size: 13px;
}
.file-upload-wrapper { display: flex; align-items: center; gap: 10px; }
input[type=file] {
  font-size: 13px; padding: 6px; border: 1px dashed #90b8e0;
  border-radius: 4px; background: #f0f7ff; color: #555; cursor: pointer;
}
.file-hint { font-size: 12px; color: #999; }
.form-actions {
  display: flex; justify-content: center; gap: 20px;
  padding: 20px 0 8px; border-top: 1px solid #edf0f5; margin-top: 10px;
}
.btn-primary {
  padding: 10px 36px; background: linear-gradient(135deg, #1a6fc4, #2196F3);
  color: #fff; border: none; border-radius: 20px; font-size: 15px;
  cursor: pointer; font-weight: 600; box-shadow: 0 2px 8px rgba(33,150,243,0.35);
  transition: opacity 0.2s;
}
.btn-primary:hover { opacity: 0.88; }
.btn-secondary {
  padding: 10px 36px; background: #fff; color: #666;
  border: 1px solid #d0d7e3; border-radius: 20px; font-size: 15px;
  cursor: pointer; font-weight: 500; transition: border-color 0.2s;
}
.btn-secondary:hover { border-color: #2196F3; color: #2196F3; }
"""


# ─────────────────────────────────────────────────────────────
# 控件渲染函数
# ─────────────────────────────────────────────────────────────

def _required_star(field):
    return '<span class="required">*</span>' if field.get("required") else ""


def render_text(field):
    fid = field["id"]
    ph = field.get("placeholder", "")
    req = "required" if field.get("required") else ""
    return (f'<input type="text" id="{fid}" name="{fid}" '
            f'placeholder="{ph}" {req}>')


def render_textarea(field):
    fid = field["id"]
    ph = field.get("placeholder", "")
    req = "required" if field.get("required") else ""
    return (f'<textarea id="{fid}" name="{fid}" '
            f'placeholder="{ph}" rows="4" {req}></textarea>')


def render_number(field):
    fid = field["id"]
    ph = field.get("placeholder", "")
    mn = f'min="{field["min"]}"' if "min" in field else ""
    mx = f'max="{field["max"]}"' if "max" in field else ""
    req = "required" if field.get("required") else ""
    return (f'<input type="number" id="{fid}" name="{fid}" '
            f'placeholder="{ph}" {mn} {mx} {req}>')


def render_date(field):
    fid = field["id"]
    req = "required" if field.get("required") else ""
    return (f'<input type="date" id="{fid}" name="{fid}" '
            f'placeholder="yyyy-mm-dd" {req}>')


def render_select(field):
    fid = field["id"]
    req = "required" if field.get("required") else ""
    options_html = '<option value="">请选择</option>\n'
    for opt in field.get("options", []):
        if isinstance(opt, dict):
            v, t = opt.get("value", ""), opt.get("label", "")
        else:
            v = t = opt
        options_html += f'        <option value="{v}">{t}</option>\n'
    return (f'<select id="{fid}" name="{fid}" {req}>\n'
            f'        {options_html}      </select>')


def render_radio(field):
    items = []
    for opt in field.get("options", []):
        if isinstance(opt, dict):
            v, t = opt.get("value", ""), opt.get("label", "")
        else:
            v = t = opt
        items.append(
            f'<label class="radio-item">'
            f'<input type="radio" name="{field["id"]}" value="{v}"> {t}</label>'
        )
    return ('<div class="radio-group">\n        '
            + '\n        '.join(items) + '\n      </div>')


def render_checkbox(field):
    items = []
    for opt in field.get("options", []):
        if isinstance(opt, dict):
            v, t = opt.get("value", ""), opt.get("label", "")
        else:
            v = t = opt
        items.append(
            f'<label class="checkbox-item">'
            f'<input type="checkbox" name="{field["id"]}" value="{v}"> {t}</label>'
        )
    return ('<div class="checkbox-group">\n        '
            + '\n        '.join(items) + '\n      </div>')


def render_multiselect(field):
    fid = field["id"]
    options_html = ""
    for opt in field.get("options", []):
        if isinstance(opt, dict):
            v, t = opt.get("value", ""), opt.get("label", "")
        else:
            v = t = opt
        options_html += f'        <option value="{v}">{t}</option>\n'
    return (f'<select id="{fid}" name="{fid}" multiple>\n'
            f'        {options_html}      </select>')


def render_file(field):
    fid = field["id"]
    accept = field.get("accept", ".pdf,.jpg,.png,.docx")
    hint = field.get("hint", "支持PDF/图片/Word，单个文件不超过10MB")
    return (f'<div class="file-upload-wrapper">\n'
            f'        <input type="file" id="{fid}" name="{fid}" accept="{accept}">\n'
            f'        <span class="file-hint">{hint}</span>\n'
            f'      </div>')


def render_matrix(field):
    cols = field.get("matrix_columns", [])
    if not cols:
        return '<p style="color:#999">（矩阵列未定义）</p>'
    rows = field.get("initial_rows", 3)

    thead = "".join(f"<th>{c.get('label','')}</th>" for c in cols)
    def make_row():
        cells = ""
        for c in cols:
            ct = c.get("type", "text")
            if ct == "date":
                cells += '<td><input type="date"></td>'
            elif ct == "select":
                opts = "".join(
                    f'<option value="{o.get("value","") if isinstance(o,dict) else o}">'
                    f'{o.get("label","") if isinstance(o,dict) else o}</option>'
                    for o in c.get("options", [])
                )
                cells += f'<td><select><option value="">-</option>{opts}</select></td>'
            elif ct == "number":
                cells += '<td><input type="number" style="width:70px"></td>'
            else:
                cells += f'<td><input type="text" placeholder="{c.get("placeholder","")}"></td>'
        return f"<tr>{cells}</tr>"

    tbody = "\n          ".join(make_row() for _ in range(rows))
    return (f'<table class="matrix-table">\n'
            f'        <thead><tr>{thead}</tr></thead>\n'
            f'        <tbody>\n          {tbody}\n        </tbody>\n'
            f'      </table>')


RENDER_MAP = {
    "text": render_text,
    "textarea": render_textarea,
    "number": render_number,
    "date": render_date,
    "select": render_select,
    "radio": render_radio,
    "checkbox": render_checkbox,
    "multiselect": render_multiselect,
    "multi-select": render_multiselect,
    "file": render_file,
    "matrix": render_matrix,
}


def render_field_html(field):
    ftype = field.get("type", "text")
    renderer = RENDER_MAP.get(ftype, render_text)
    control = renderer(field)
    fid = field["id"]
    label = field.get("label", fid)
    req_star = _required_star(field)
    full = " full-width" if ftype in ("textarea", "matrix", "checkbox", "file") else ""
    return (f'      <div class="form-group{full}">\n'
            f'        <label for="{fid}">{label}{req_star}</label>\n'
            f'        {control}\n'
            f'      </div>')


# ─────────────────────────────────────────────────────────────
# 原生 HTML 控件渲染（bare，参照 form_template.html 风格）
# 不含标题、CSS样式、操作按钮；只输出 <form> 内的原始表单控件
# ─────────────────────────────────────────────────────────────

def render_native_control(field):
    """渲染原生HTML控件，不包含任何class/style，与form_template.html风格一致"""
    fid = field["id"]
    ftype = field.get("type", "text")
    opts = field.get("options", [])
    ph = field.get("placeholder", "")

    if ftype == "text":
        req = " required" if field.get("required") else ""
        return f'<input type="text" name="{fid}" placeholder="{ph}"{req}>'

    elif ftype == "textarea":
        req = " required" if field.get("required") else ""
        return f'<textarea name="{fid}" rows="5" cols="30"{req}></textarea>'

    elif ftype == "number":
        mn = f' min="{field["min"]}"' if "min" in field else ""
        mx = f' max="{field["max"]}"' if "max" in field else ""
        req = " required" if field.get("required") else ""
        return f'<input type="number" name="{fid}" placeholder="{ph}"{mn}{mx}{req}>'

    elif ftype == "date":
        req = " required" if field.get("required") else ""
        return f'<input type="date" name="{fid}"{req}>'

    elif ftype == "select":
        req = " required" if field.get("required") else ""
        lines = [f'<select name="{fid}"{req}>']
        for opt in opts:
            v, t = (opt.get("value", ""), opt.get("label", "")) if isinstance(opt, dict) else (opt, opt)
            lines.append(f'    <option value="{v}">{t}</option>')
        lines.append('</select>')
        return "\n".join(lines)

    elif ftype == "radio":
        lines = []
        for opt in opts:
            v, t = (opt.get("value", ""), opt.get("label", "")) if isinstance(opt, dict) else (opt, opt)
            lines.append(f'<input type="radio" name="{fid}" value="{v}"> {t}')
        return "\n".join(lines)

    elif ftype in ("checkbox", "multiselect", "multi-select"):
        lines = []
        for opt in opts:
            v, t = (opt.get("value", ""), opt.get("label", "")) if isinstance(opt, dict) else (opt, opt)
            lines.append(f'<input type="checkbox" name="{fid}" value="{v}"> {t}')
        return "\n".join(lines)

    elif ftype == "file":
        accept = field.get("accept", ".pdf,.jpg,.png,.docx")
        return f'<input type="file" name="{fid}" accept="{accept}">'

    elif ftype == "matrix":
        cols = field.get("matrix_columns", [])
        rows_n = field.get("initial_rows", 3)
        if not cols:
            return '<!-- 矩阵列未定义 -->'
        lines = ['<table border="1" cellpadding="4" cellspacing="0">']
        # 表头行
        header_cells = "".join(f"<td>{c.get('label', '')}</td>" for c in cols)
        lines.append(f'    <tr>{header_cells}</tr>')
        # 数据行
        for _ in range(rows_n):
            row_cells = ""
            for c in cols:
                ct = c.get("type", "text")
                if ct == "date":
                    row_cells += "<td><input type=\"date\"></td>"
                elif ct == "select":
                    opts2 = c.get("options", [])
                    os_str = "".join(
                        f'<option value="{o.get("value","") if isinstance(o,dict) else o}">'
                        f'{o.get("label","") if isinstance(o,dict) else o}</option>'
                        for o in opts2
                    )
                    row_cells += f"<td><select><option value=\"\">-</option>{os_str}</select></td>"
                elif ct == "number":
                    row_cells += "<td><input type=\"number\"></td>"
                else:
                    cph = c.get("placeholder", "")
                    row_cells += f'<td><input type="text" placeholder="{cph}"></td>'
            lines.append(f'    <tr>{row_cells}</tr>')
        lines.append('</table>')
        return "\n".join(lines)

    else:
        return f'<input type="text" name="{fid}">'


def generate_html_native(schema, outpath):
    """
    生成原生HTML代码文件（bare HTML）
    格式参照 form_template.html：仅含 <form>...</form> 的纯控件代码
    不含 DOCTYPE/head/style/标题/提交按钮，可直接嵌入任意页面
    """
    lines = ['<form>']
    lines.append('')

    groups = {}
    for f in schema.get("fields", []):
        g = f.get("group", "其他")
        groups.setdefault(g, []).append(f)

    first_group = True
    for g_name, fields in groups.items():
        if not first_group:
            lines.append('')
        first_group = False
        lines.append(f'     <!-- {g_name} -->')
        for f in fields:
            label = f.get("label", f["id"])
            req_mark = "（必填）" if f.get("required") else ""
            ctrl = render_native_control(f)
            ftype = f.get("type", "text")
            if ftype == "matrix":
                lines.append(f'     {label}：<br>')
                for ctrl_line in ctrl.split("\n"):
                    lines.append(f'     {ctrl_line}')
                lines.append('     <br>')
            else:
                # 多行控件（radio/checkbox/select）—— 控件可能跨多行
                ctrl_lines = ctrl.split("\n")
                if len(ctrl_lines) == 1:
                    lines.append(f'     {label}{req_mark}：{ctrl_lines[0]}<br>')
                else:
                    lines.append(f'     {label}{req_mark}：{ctrl_lines[0]}')
                    for cl in ctrl_lines[1:]:
                        lines.append(f'     {cl}')
                    lines.append('     <br>')
        lines.append('')

    lines.append(' </form>')

    with open(outpath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"  [NATIVE_HTML] -> {outpath}")


# ─────────────────────────────────────────────────────────────
# HTML 生成
# ─────────────────────────────────────────────────────────────

def generate_html(schema, outpath):
    form_name = schema.get("form_name", "医疗表单")
    btype_map = {"CLN": "临床类", "MGT": "管理类", "RES": "研究类"}
    btype = btype_map.get(schema.get("business_type", ""), schema.get("business_type", ""))
    src = schema.get("source_document", "")
    version = schema.get("version", "1.0")
    desc = f"业务类型：{btype} | 版本：{version}" + (f" | 来源：{src}" if src else "")

    # 按group分组字段
    groups = {}
    for f in schema.get("fields", []):
        g = f.get("group", "其他")
        groups.setdefault(g, []).append(f)

    sections_html = ""
    for g_name, fields in groups.items():
        rows_html = ""
        i = 0
        while i < len(fields):
            f = fields[i]
            ftype = f.get("type", "text")
            if ftype in ("textarea", "matrix", "checkbox", "file"):
                rows_html += f'    <div class="form-row">\n{render_field_html(f)}\n    </div>\n'
                i += 1
            else:
                # 尝试两个一行
                row_fields = [render_field_html(f)]
                if i + 1 < len(fields) and fields[i+1].get("type","text") not in ("textarea","matrix","checkbox","file"):
                    row_fields.append(render_field_html(fields[i+1]))
                    i += 2
                else:
                    i += 1
                rows_html += f'    <div class="form-row">\n' + "\n".join(row_fields) + f'\n    </div>\n'

        sections_html += (
            f'  <fieldset class="form-section">\n'
            f'    <legend class="section-title">{g_name}</legend>\n'
            f'{rows_html}'
            f'  </fieldset>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{form_name}</title>
  <style>{CSS_STYLE}</style>
</head>
<body>
  <div class="form-container">
    <div class="form-header">
      <h2 class="form-title">{form_name}</h2>
      <p class="form-desc">{desc}</p>
    </div>
    <form id="medical-form" onsubmit="handleSubmit(event)">
{sections_html}
      <div class="form-actions">
        <button type="submit" class="btn-primary">提交</button>
        <button type="reset" class="btn-secondary">重置</button>
      </div>
    </form>
  </div>
  <script>
    function handleSubmit(e) {{
      e.preventDefault();
      const data = new FormData(e.target);
      const obj = {{}};
      data.forEach((v, k) => {{
        if (obj[k]) {{
          obj[k] = [].concat(obj[k], v);
        }} else {{
          obj[k] = v;
        }}
      }});
      console.log('表单数据:', JSON.stringify(obj, null, 2));
      alert('表单已提交（控制台可查看数据）');
    }}
  </script>
</body>
</html>"""

    with open(outpath, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  [HTML] -> {outpath}")


# ─────────────────────────────────────────────────────────────
# JSON 生成（直接输出schema，加上示例数据）
# ─────────────────────────────────────────────────────────────

def generate_json(schema, outpath):
    # 生成示例数据
    example = {}
    for f in schema.get("fields", []):
        fid = f["id"]
        ftype = f.get("type", "text")
        opts = f.get("options", [])
        if ftype == "text":
            example[fid] = f.get("placeholder", "示例文本")
        elif ftype == "textarea":
            example[fid] = "（示例长文本描述）"
        elif ftype == "number":
            example[fid] = 0
        elif ftype == "date":
            example[fid] = datetime.today().strftime("%Y-%m-%d")
        elif ftype in ("select", "radio"):
            example[fid] = opts[0]["value"] if opts and isinstance(opts[0], dict) else (opts[0] if opts else "")
        elif ftype in ("checkbox", "multiselect", "multi-select"):
            example[fid] = [opts[0]["value"] if isinstance(opts[0], dict) else opts[0]] if opts else []
        elif ftype == "file":
            example[fid] = "（附件路径或Base64）"
        elif ftype == "matrix":
            cols = f.get("matrix_columns", [])
            example[fid] = [{c.get("label", ""): "" for c in cols}]
        else:
            example[fid] = ""

    output = {
        "schema": schema,
        "example_data": example
    }
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)
    print(f"  [JSON] -> {outpath}")


# ─────────────────────────────────────────────────────────────
# XML 生成
# ─────────────────────────────────────────────────────────────

def _xml_escape(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_xml(schema, outpath):
    form_name = _xml_escape(schema.get("form_name", "医疗表单"))
    btype = schema.get("business_type", "CLN")
    genre = schema.get("genre_type", "")
    src = _xml_escape(schema.get("source_document", ""))
    version = schema.get("version", "1.0")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # 按group分组
    groups = {}
    for f in schema.get("fields", []):
        g = f.get("group", "其他")
        groups.setdefault(g, []).append(f)

    sections_xml = ""
    for sec_idx, (g_name, fields) in enumerate(groups.items(), 1):
        sec_id = f"section_{sec_idx:03d}"
        fields_xml = ""
        for f_idx, f in enumerate(fields, 1):
            fid = _xml_escape(f.get("id", f"field_{f_idx}"))
            label = _xml_escape(f.get("label", ""))
            ftype = f.get("type", "text")
            required = "true" if f.get("required") else "false"
            ph = _xml_escape(f.get("placeholder", ""))

            dtype_map = {
                "text": "string", "textarea": "string", "number": "decimal",
                "date": "date", "select": "string", "radio": "string",
                "checkbox": "array", "multiselect": "array", "multi-select": "array",
                "file": "binary", "matrix": "array"
            }
            dtype = dtype_map.get(ftype, "string")

            opts_xml = ""
            if f.get("options"):
                opts_list = ""
                for opt in f["options"]:
                    if isinstance(opt, dict):
                        v, t = _xml_escape(opt.get("value", "")), _xml_escape(opt.get("label", ""))
                    else:
                        v = t = _xml_escape(str(opt))
                    opts_list += f'          <Option value="{v}">{t}</Option>\n'
                opts_xml = f'          <Options>\n{opts_list}          </Options>\n'

            matrix_xml = ""
            if ftype == "matrix":
                cols = f.get("matrix_columns", [])
                cols_xml = ""
                for c in cols:
                    ct = _xml_escape(c.get("type", "text"))
                    cl = _xml_escape(c.get("label", ""))
                    copts = c.get("options", [])
                    copts_xml = ""
                    if copts:
                        copts_list = ""
                        for co in copts:
                            cv = _xml_escape(co.get("value","") if isinstance(co,dict) else co)
                            ct2 = _xml_escape(co.get("label","") if isinstance(co,dict) else co)
                            copts_list += f'              <Option value="{cv}">{ct2}</Option>\n'
                        copts_xml = f'            <Options>\n{copts_list}            </Options>\n'
                    cols_xml += f'          <Column type="{ct}" label="{cl}">\n{copts_xml}          </Column>\n'
                rows = f.get("initial_rows", 3)
                matrix_xml = (f'          <MatrixColumns>\n{cols_xml}          </MatrixColumns>\n'
                              f'          <InitialRows>{rows}</InitialRows>\n')

            fields_xml += (
                f'        <Field id="{fid}" order="{f_idx}">\n'
                f'          <Label>{label}</Label>\n'
                f'          <FieldCode>{fid}</FieldCode>\n'
                f'          <ControlType>{ftype}</ControlType>\n'
                f'          <DataType>{dtype}</DataType>\n'
                f'          <Required>{required}</Required>\n'
                f'          <Placeholder>{ph}</Placeholder>\n'
                f'{opts_xml}'
                f'{matrix_xml}'
                f'        </Field>\n'
            )

        sections_xml += (
            f'    <Section id="{sec_id}" name="{_xml_escape(g_name)}" order="{sec_idx}">\n'
            f'      <Fields>\n{fields_xml}      </Fields>\n'
            f'    </Section>\n'
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<MedicalForm xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             version="{version}"
             createDate="{now}">

  <FormMeta>
    <FormName>{form_name}</FormName>
    <FormCode>FORM_{datetime.now().strftime('%Y%m%d%H%M%S')}</FormCode>
    <BusinessType>{btype}</BusinessType>
    <GenreType>{_xml_escape(genre)}</GenreType>
    <SourceDocument>{src}</SourceDocument>
    <Version>{version}</Version>
    <CreateTime>{now}</CreateTime>
  </FormMeta>

  <FormSections>
{sections_xml}  </FormSections>

</MedicalForm>"""

    with open(outpath, "w", encoding="utf-8") as fh:
        fh.write(xml)
    print(f"  [XML]  -> {outpath}")


# ─────────────────────────────────────────────────────────────
# Excel 生成（使用openpyxl）
# ─────────────────────────────────────────────────────────────

def generate_excel(schema, outpath):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    except ImportError:
        print(f"  [WARN] openpyxl not installed, skip Excel. Run: pip install openpyxl")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "表单字段定义"

    # 表头
    headers = ["字段名（中文）", "字段编码", "所属分组", "控件类型", "数据类型",
               "是否必填", "可选项（分号分隔）", "占位提示文字", "填写示例"]
    header_fill = PatternFill(start_color="1A6FC4", end_color="1A6FC4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.append(headers)
    for col_idx, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    # 控件类型选项（用于数据验证）
    type_options = '"text,textarea,number,date,select,radio,checkbox,multiselect,file,matrix"'

    # 数据行
    type_map = {
        "text": "string", "textarea": "string", "number": "decimal",
        "date": "date", "select": "string", "radio": "string",
        "checkbox": "array", "multiselect": "array", "multi-select": "array",
        "file": "binary", "matrix": "array"
    }

    example_map = {
        "text": "王小明", "textarea": "详细描述内容", "number": "25",
        "date": datetime.today().strftime("%Y-%m-%d"),
        "select": "（选项1）", "radio": "（选项1）",
        "checkbox": "选项1;选项2", "multiselect": "选项1;选项2",
        "file": "report.pdf", "matrix": "行1-列1|行1-列2"
    }

    row_idx = 2
    for f in schema.get("fields", []):
        ftype = f.get("type", "text")
        opts = f.get("options", [])
        opts_str = ";".join(
            (o.get("label", "") if isinstance(o, dict) else str(o)) for o in opts
        )
        if ftype == "matrix":
            cols = f.get("matrix_columns", [])
            opts_str = ";".join(c.get("label", "") for c in cols)

        row = [
            f.get("label", ""),
            f.get("id", ""),
            f.get("group", ""),
            ftype,
            type_map.get(ftype, "string"),
            "是" if f.get("required") else "否",
            opts_str,
            f.get("placeholder", ""),
            example_map.get(ftype, "示例值")
        ]
        ws.append(row)

        # 样式
        row_fill_color = "EDF4FF" if row_idx % 2 == 0 else "FFFFFF"
        row_fill = PatternFill(start_color=row_fill_color, end_color=row_fill_color, fill_type="solid")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.fill = row_fill
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = border
        row_idx += 1

    # 调整列宽
    col_widths = [20, 20, 14, 14, 12, 10, 30, 24, 20]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 28

    # 数据验证（控件类型列）
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1=type_options, allow_blank=True)
    dv.sqref = f"D2:D{row_idx}"
    ws.add_data_validation(dv)

    # 冻结首行
    ws.freeze_panes = "A2"

    # 第二个sheet：示例说明
    ws2 = wb.create_sheet("控件类型说明")
    ws2.append(["控件类型", "中文名称", "使用场景", "对应HTML元素"])
    guide_fill = PatternFill(start_color="1A6FC4", end_color="1A6FC4", fill_type="solid")
    for col_idx in range(1, 5):
        cell = ws2.cell(row=1, column=col_idx)
        cell.fill = guide_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center")
    types_guide = [
        ("text", "单行文本", "姓名、编号等短文本", "<input type='text'>"),
        ("textarea", "长文本", "描述、备注等长文本", "<textarea>"),
        ("number", "数字", "年龄、剂量、次数", "<input type='number'>"),
        ("date", "日期", "就诊日期、出生日期", "<input type='date'>"),
        ("select", "下拉选择", "科室、分级等单选", "<select>"),
        ("radio", "单选按钮", "性别、是否", "<input type='radio'>"),
        ("checkbox", "多选框", "并发症、药物种类", "<input type='checkbox'>"),
        ("multiselect", "多选下拉", "多选项下拉菜单", "<select multiple>"),
        ("file", "附件上传", "检验报告、知情书", "<input type='file'>"),
        ("matrix", "矩阵表格", "检验检查批量记录", "<table> with inputs"),
    ]
    for row in types_guide:
        ws2.append(list(row))
    for col_idx in range(1, 5):
        ws2.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = 22

    print(f"  [XLSX] -> {outpath}")


# ─────────────────────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="医疗表单自动生成工具")
    parser.add_argument("schema_file", help="字段Schema JSON文件路径")
    parser.add_argument("--outdir", default="form_output", help="输出目录（默认form_output）")
    parser.add_argument("--with-system", action="store_true",
                        help="同时生成完整Flask+SQLite登记系统")
    args = parser.parse_args()

    if not os.path.exists(args.schema_file):
        print(f"❌ 文件不存在：{args.schema_file}")
        sys.exit(1)

    with open(args.schema_file, "r", encoding="utf-8") as fh:
        schema = json.load(fh)

    os.makedirs(args.outdir, exist_ok=True)
    form_name_safe = schema.get("form_name", "form").replace(" ", "_").replace("/", "_")
    base = os.path.join(args.outdir, form_name_safe)

    print(f"\n[INFO] Generating form: {schema.get('form_name','MedicalForm')}")
    print(f"       BusinessType: {schema.get('business_type','CLN')}")
    print(f"       Fields: {len(schema.get('fields', []))}")
    print()

    generate_html(schema, base + ".html")
    generate_html_native(schema, base + "_native.html")
    generate_json(schema, base + "_schema.json")
    generate_xml(schema, base + ".xml")
    generate_excel(schema, base + "_template.xlsx")

    print(f"\n[OK] All files generated at: {args.outdir}/")

    # 可选：生成完整登记系统
    if args.with_system:
        print(f"\n[INFO] Generating Flask+SQLite registry system...")
        try:
            import importlib.util, sys as _sys
            gs_path = os.path.join(os.path.dirname(__file__), "generate_system.py")
            spec = importlib.util.spec_from_file_location("generate_system", gs_path)
            gs_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gs_mod)
            sys_dir, zip_path = gs_mod.generate_system(schema, args.outdir)
            print(f"\n[OK] Registry system generated!")
            print(f"     Directory: {sys_dir}")
            print(f"     Package:   {zip_path}")
        except Exception as e:
            print(f"  [WARN] Failed to generate system: {e}")


if __name__ == "__main__":
    main()
