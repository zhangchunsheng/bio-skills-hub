#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗表单登记系统生成脚本
根据字段 JSON Schema，自动生成完整的 Flask + SQLite 登记系统
包含：
  - Flask后端（app.py）：API接口、数据存储、历史查询
  - SQLite数据库初始化脚本（init_db.py）
  - 前端页面（templates/index.html）：支持录入、提交、历史查询
  - 静态资源（static/style.css）
  - requirements.txt
  - README.md
用法: python generate_system.py <schema.json> [--outdir registry_system]
"""

import json
import os
import sys
import argparse
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────

def safe_id(s):
    """转换为合法Python/SQL标识符"""
    import re
    s = re.sub(r'[^\w]', '_', str(s))
    if s[0].isdigit():
        s = 'f_' + s
    return s.lower()


def field_to_sql_type(ftype):
    """字段类型转SQLite列类型"""
    mapping = {
        "text": "TEXT",
        "textarea": "TEXT",
        "number": "REAL",
        "date": "TEXT",
        "select": "TEXT",
        "radio": "TEXT",
        "checkbox": "TEXT",
        "multiselect": "TEXT",
        "multi-select": "TEXT",
        "file": "TEXT",
        "matrix": "TEXT",
    }
    return mapping.get(ftype, "TEXT")


# ─────────────────────────────────────────────────────────────
# 生成 Flask app.py
# ─────────────────────────────────────────────────────────────

def gen_app_py(schema):
    form_name = schema.get("form_name", "医疗登记系统")
    fields = schema.get("fields", [])
    
    # 生成字段列表（用于API文档注释）
    field_list = "\n".join(
        f'    # {f.get("label","")}: {f.get("type","text")} | id={f["id"]}'
        for f in fields
    )
    
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{form_name} — 后端服务
Flask + SQLite 医疗数据登记系统
自动生成于: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "registry.db")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "data", "uploads")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.json")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 数据库连接
# ─────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库，创建表结构"""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    fields = schema.get("fields", [])
    cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT",
            "created_at TEXT NOT NULL",
            "updated_at TEXT",
            "submitter TEXT",
            "status TEXT DEFAULT \\'draft\\'"]
    for field in fields:
        fid = field["id"]
        col_type = {{"text":"TEXT","textarea":"TEXT","number":"REAL","date":"TEXT",
                    "select":"TEXT","radio":"TEXT","checkbox":"TEXT",
                    "multiselect":"TEXT","multi-select":"TEXT",
                    "file":"TEXT","matrix":"TEXT"}}.get(field.get("type","text"), "TEXT")
        cols.append(f"  {{fid}} {{col_type}}")
    
    create_sql = "CREATE TABLE IF NOT EXISTS form_records (\\n  " + ",\\n  ".join(cols) + "\\n)"
    
    # 历史版本表（audit log）
    audit_sql = """CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  record_id INTEGER,
  action TEXT,
  changed_by TEXT,
  changed_at TEXT,
  snapshot TEXT
)"""
    
    conn = get_db()
    try:
        conn.execute(create_sql)
        conn.execute(audit_sql)
        conn.commit()
        print(f"[DB] Initialized: {{DB_PATH}}")
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# API 路由
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/schema", methods=["GET"])
def get_schema():
    """获取表单Schema定义"""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return jsonify({{"success": True, "data": schema}})


@app.route("/api/records", methods=["POST"])
def create_record():
    """新增表单记录"""
    try:
        data = request.get_json(force=True) or {{}}
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 加载schema以获取字段列表
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        valid_fields = {{f["id"] for f in schema.get("fields", [])}}
        
        # 过滤有效字段
        record_data = {{}}
        for fid in valid_fields:
            if fid in data:
                val = data[fid]
                # 列表/dict类型转JSON字符串
                if isinstance(val, (list, dict)):
                    val = json.dumps(val, ensure_ascii=False)
                record_data[fid] = val
        
        record_data["created_at"] = now
        record_data["updated_at"] = now
        record_data["submitter"] = data.get("_submitter", "anonymous")
        record_data["status"] = data.get("_status", "submitted")
        
        cols = ", ".join(record_data.keys())
        placeholders = ", ".join(["?"] * len(record_data))
        sql = f"INSERT INTO form_records ({{cols}}) VALUES ({{placeholders}})"
        
        conn = get_db()
        try:
            cursor = conn.execute(sql, list(record_data.values()))
            record_id = cursor.lastrowid
            # 写入audit_log
            conn.execute(
                "INSERT INTO audit_log (record_id, action, changed_by, changed_at, snapshot) VALUES (?,?,?,?,?)",
                (record_id, "CREATE", record_data.get("submitter", "anon"), now, json.dumps(record_data, ensure_ascii=False))
            )
            conn.commit()
            return jsonify({{"success": True, "id": record_id, "message": "记录已保存"}}), 201
        finally:
            conn.close()
    
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500


@app.route("/api/records", methods=["GET"])
def list_records():
    """查询历史记录（支持分页和条件过滤）"""
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        search = request.args.get("search", "").strip()
        date_from = request.args.get("date_from", "")
        date_to = request.args.get("date_to", "")
        status = request.args.get("status", "")
        
        offset = (page - 1) * page_size
        
        where_clauses = []
        params = []
        
        if search:
            # 在所有TEXT字段中搜索
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = json.load(f)
            text_fields = [f["id"] for f in schema.get("fields", [])
                          if f.get("type","text") in ("text","textarea","select","radio")]
            if text_fields:
                search_conditions = " OR ".join(f"{{fid}} LIKE ?" for fid in text_fields)
                where_clauses.append(f"({{search_conditions}})")
                params.extend([f"%{{search}}%"] * len(text_fields))
        
        if date_from:
            where_clauses.append("created_at >= ?")
            params.append(date_from)
        if date_to:
            where_clauses.append("created_at <= ?")
            params.append(date_to + " 23:59:59")
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        conn = get_db()
        try:
            total = conn.execute(f"SELECT COUNT(*) FROM form_records {{where_sql}}", params).fetchone()[0]
            rows = conn.execute(
                f"SELECT * FROM form_records {{where_sql}} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [page_size, offset]
            ).fetchall()
            
            records = []
            for row in rows:
                r = dict(row)
                # 尝试反序列化JSON字段
                for k, v in r.items():
                    if isinstance(v, str) and v.startswith(("[", "{{")):
                        try:
                            r[k] = json.loads(v)
                        except Exception:
                            pass
                records.append(r)
            
            return jsonify({{
                "success": True,
                "data": records,
                "pagination": {{
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }}
            }})
        finally:
            conn.close()
    
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500


@app.route("/api/records/<int:record_id>", methods=["GET"])
def get_record(record_id):
    """获取单条记录"""
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM form_records WHERE id = ?", (record_id,)).fetchone()
        if not row:
            return jsonify({{"success": False, "error": "记录不存在"}}), 404
        r = dict(row)
        for k, v in r.items():
            if isinstance(v, str) and v.startswith(("[", "{{")):
                try:
                    r[k] = json.loads(v)
                except Exception:
                    pass
        return jsonify({{"success": True, "data": r}})
    finally:
        conn.close()


@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    """更新记录"""
    try:
        data = request.get_json(force=True) or {{}}
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        valid_fields = {{f["id"] for f in schema.get("fields", [])}}
        
        update_data = {{}}
        for fid in valid_fields:
            if fid in data:
                val = data[fid]
                if isinstance(val, (list, dict)):
                    val = json.dumps(val, ensure_ascii=False)
                update_data[fid] = val
        update_data["updated_at"] = now
        
        set_clause = ", ".join(f"{{k}} = ?" for k in update_data.keys())
        sql = f"UPDATE form_records SET {{set_clause}} WHERE id = ?"
        
        conn = get_db()
        try:
            # 先取旧数据存快照
            old = conn.execute("SELECT * FROM form_records WHERE id = ?", (record_id,)).fetchone()
            if not old:
                return jsonify({{"success": False, "error": "记录不存在"}}), 404
            
            conn.execute(sql, list(update_data.values()) + [record_id])
            conn.execute(
                "INSERT INTO audit_log (record_id, action, changed_by, changed_at, snapshot) VALUES (?,?,?,?,?)",
                (record_id, "UPDATE", data.get("_submitter", "anon"), now, json.dumps(dict(old), ensure_ascii=False))
            )
            conn.commit()
            return jsonify({{"success": True, "message": "记录已更新"}})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500


@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    """删除记录（软删除，更新status=deleted）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    try:
        old = conn.execute("SELECT * FROM form_records WHERE id = ?", (record_id,)).fetchone()
        if not old:
            return jsonify({{"success": False, "error": "记录不存在"}}), 404
        conn.execute("UPDATE form_records SET status='deleted', updated_at=? WHERE id=?", (now, record_id))
        conn.execute(
            "INSERT INTO audit_log (record_id, action, changed_by, changed_at, snapshot) VALUES (?,?,?,?,?)",
            (record_id, "DELETE", "user", now, json.dumps(dict(old), ensure_ascii=False))
        )
        conn.commit()
        return jsonify({{"success": True, "message": "记录已删除"}})
    finally:
        conn.close()


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """获取统计概要"""
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM form_records WHERE status != 'deleted'").fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = conn.execute(
            "SELECT COUNT(*) FROM form_records WHERE created_at LIKE ? AND status != 'deleted'",
            (today + "%",)
        ).fetchone()[0]
        return jsonify({{"success": True, "data": {{"total": total, "today": today_count}}}})
    finally:
        conn.close()


@app.route("/api/export", methods=["GET"])
def export_csv():
    """导出记录为CSV"""
    import csv
    import io
    from flask import Response
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    fields = schema.get("fields", [])
    
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM form_records WHERE status != 'deleted' ORDER BY created_at DESC"
        ).fetchall()
    finally:
        conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    # 写表头：id + 创建时间 + 各字段中文名
    header = ["记录ID", "创建时间", "提交人", "状态"] + [f.get("label", f["id"]) for f in fields]
    writer.writerow(header)
    for row in rows:
        r = dict(row)
        data_row = [r.get("id"), r.get("created_at"), r.get("submitter"), r.get("status")]
        for f in fields:
            val = r.get(f["id"], "")
            if isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            data_row.append(val)
        writer.writerow(data_row)
    
    return Response(
        "\ufeff" + output.getvalue(),  # UTF-8 BOM for Excel compatibility
        mimetype="text/csv",
        headers={{"Content-Disposition": f"attachment; filename=records_export_{{today}}.csv"}}
    )


if __name__ == "__main__":
    init_db()
    print(f"[INFO] Starting {form_name} registry server...")
    print(f"[INFO] Open: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
'''


# ─────────────────────────────────────────────────────────────
# 生成 templates/index.html（完整前端，含录入+历史查询）
# ─────────────────────────────────────────────────────────────

def gen_index_html(schema):
    form_name = schema.get("form_name", "医疗登记系统")
    fields = schema.get("fields", [])
    btype_map = {"CLN": "临床类", "MGT": "管理类", "RES": "研究类"}
    btype = btype_map.get(schema.get("business_type", ""), "")
    
    # 生成各字段的HTML控件（用于Jinja2模板内联，但这里直接用JS动态渲染）
    # 把schema中fields转换为JS可用的JSON
    fields_js = json.dumps(fields, ensure_ascii=False, indent=2)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{form_name} — 数据登记系统</title>
  <style>
    /* ── 全局 ── */
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      font-size: 14px; background: #eef2f7; color: #333;
    }}
    /* ── 顶部导航 ── */
    .navbar {{
      background: linear-gradient(135deg, #1a6fc4 0%, #2196F3 100%);
      color: #fff; padding: 0 32px; height: 56px;
      display: flex; align-items: center; justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0,0,0,0.18);
    }}
    .navbar-title {{ font-size: 18px; font-weight: 700; letter-spacing: 0.5px; }}
    .navbar-sub {{ font-size: 12px; opacity: 0.8; margin-top: 2px; }}
    .navbar-stats {{ display: flex; gap: 24px; }}
    .stat-item {{ text-align: center; }}
    .stat-num {{ font-size: 22px; font-weight: 700; }}
    .stat-label {{ font-size: 11px; opacity: 0.8; }}
    /* ── 主体布局 ── */
    .main-wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px 16px; }}
    /* ── Tab切换 ── */
    .tabs {{ display: flex; gap: 2px; margin-bottom: 20px; }}
    .tab-btn {{
      padding: 10px 28px; border: none; cursor: pointer;
      font-size: 14px; font-weight: 600; border-radius: 6px 6px 0 0;
      background: #d0ddf0; color: #5577aa; transition: all 0.2s;
    }}
    .tab-btn.active {{ background: #fff; color: #1a6fc4; box-shadow: 0 -2px 6px rgba(0,0,0,0.08); }}
    /* ── 卡片 ── */
    .card {{
      background: #fff; border-radius: 0 8px 8px 8px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 28px 32px;
    }}
    /* ── 表单区 ── */
    .form-section {{
      border: 1px solid #e4e8f0; border-radius: 6px; padding: 16px 20px;
      margin-bottom: 20px; background: #fafbfd;
    }}
    .form-section-title {{
      font-size: 14px; font-weight: 700; color: #1a6fc4;
      margin-bottom: 14px; padding-bottom: 8px;
      border-bottom: 2px solid #e3edf8;
      display: flex; align-items: center; gap: 8px;
    }}
    .form-section-title::before {{
      content: ""; display: inline-block; width: 4px; height: 16px;
      background: #1a6fc4; border-radius: 2px;
    }}
    .form-grid {{ display: flex; flex-wrap: wrap; gap: 16px; }}
    .form-group {{ flex: 1 1 280px; display: flex; flex-direction: column; gap: 5px; }}
    .form-group.full-width {{ flex: 1 1 100%; }}
    label.form-label {{ font-size: 13px; color: #555; font-weight: 500; }}
    label.form-label .req {{ color: #e53935; margin-left: 2px; }}
    input[type=text], input[type=number], input[type=date],
    input[type=email], select, textarea {{
      width: 100%; padding: 8px 12px; border: 1px solid #d0d7e3;
      border-radius: 4px; font-size: 14px; color: #333;
      font-family: inherit; transition: border-color 0.2s;
    }}
    input:focus, select:focus, textarea:focus {{
      outline: none; border-color: #2196F3;
      box-shadow: 0 0 0 2px rgba(33,150,243,0.15);
    }}
    textarea {{ min-height: 72px; resize: vertical; }}
    .radio-group, .checkbox-group {{ display: flex; flex-wrap: wrap; gap: 12px; padding-top: 4px; }}
    .radio-group label, .checkbox-group label {{
      display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 14px;
    }}
    .radio-group input, .checkbox-group input {{
      width: 15px; height: 15px; accent-color: #2196F3;
    }}
    /* ── 矩阵表格 ── */
    .matrix-wrap {{ overflow-x: auto; }}
    .matrix-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .matrix-table th {{
      background: #e3edf8; color: #1a6fc4; padding: 7px 10px;
      border: 1px solid #c7d8f0; text-align: center; white-space: nowrap;
    }}
    .matrix-table td {{ padding: 5px 7px; border: 1px solid #e0e7ef; }}
    .matrix-table tr:nth-child(even) {{ background: #f5f8fc; }}
    .matrix-table td input, .matrix-table td select {{
      width: 100%; padding: 4px 6px; border: 1px solid #d0d7e3;
      border-radius: 3px; font-size: 13px; min-width: 80px;
    }}
    .btn-add-row {{
      margin-top: 6px; padding: 4px 14px; font-size: 12px;
      background: #e8f4fd; color: #1a6fc4; border: 1px solid #90c5f0;
      border-radius: 4px; cursor: pointer;
    }}
    /* ── 操作按钮 ── */
    .form-actions {{
      display: flex; gap: 16px; justify-content: center;
      padding: 20px 0 4px; border-top: 1px solid #edf0f5; margin-top: 16px;
    }}
    .btn {{
      padding: 10px 32px; border: none; border-radius: 20px;
      font-size: 15px; font-weight: 600; cursor: pointer; transition: opacity 0.2s;
    }}
    .btn-primary {{ background: linear-gradient(135deg,#1a6fc4,#2196F3); color: #fff; }}
    .btn-primary:hover {{ opacity: 0.88; }}
    .btn-secondary {{ background: #fff; color: #666; border: 1px solid #d0d7e3; }}
    .btn-secondary:hover {{ border-color: #2196F3; color: #2196F3; }}
    .btn-danger {{ background: #fff; color: #e53935; border: 1px solid #f5a5a3; }}
    .btn-sm {{ padding: 5px 14px; font-size: 12px; border-radius: 12px; }};
    /* ── 历史查询区 ── */
    .search-bar {{
      display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;
      padding: 16px 20px; background: #f5f8ff; border-radius: 6px; margin-bottom: 16px;
    }}
    .search-bar .form-group {{ flex: 1 1 200px; min-width: 160px; }}
    .search-bar input, .search-bar select {{
      padding: 7px 10px; border: 1px solid #d0d7e3; border-radius: 4px;
      font-size: 13px; width: 100%;
    }}
    .search-bar label {{ font-size: 12px; color: #888; margin-bottom: 3px; display: block; }}
    .btn-search {{
      padding: 7px 22px; background: #1a6fc4; color: #fff; border: none;
      border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600;
      white-space: nowrap; height: 34px; align-self: flex-end;
    }}
    .btn-export {{
      padding: 7px 18px; background: #fff; color: #1a6fc4;
      border: 1px solid #90c5f0; border-radius: 4px; cursor: pointer;
      font-size: 13px; height: 34px; align-self: flex-end;
    }}
    /* ── 数据表格 ── */
    .data-table-wrap {{ overflow-x: auto; }}
    .data-table {{
      width: 100%; border-collapse: collapse; font-size: 13px; min-width: 700px;
    }}
    .data-table th {{
      background: #1a6fc4; color: #fff; padding: 10px 12px;
      text-align: left; white-space: nowrap; font-weight: 600;
    }}
    .data-table td {{ padding: 9px 12px; border-bottom: 1px solid #edf0f5; vertical-align: middle; }}
    .data-table tr:hover td {{ background: #f0f7ff; }}
    .data-table td.actions {{ white-space: nowrap; }}
    .badge {{
      display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 600;
    }}
    .badge-submitted {{ background: #e8f5e9; color: #388e3c; }}
    .badge-draft {{ background: #fff3e0; color: #f57c00; }}
    .badge-deleted {{ background: #ffebee; color: #e53935; }}
    /* ── 分页 ── */
    .pagination {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 12px 0 0; font-size: 13px; color: #666;
    }}
    .page-btns {{ display: flex; gap: 6px; }}
    .page-btn {{
      width: 30px; height: 30px; border: 1px solid #d0d7e3; background: #fff;
      border-radius: 4px; cursor: pointer; font-size: 13px; color: #555;
    }}
    .page-btn.active {{ background: #1a6fc4; color: #fff; border-color: #1a6fc4; }}
    /* ── 详情弹窗 ── */
    .modal-overlay {{
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
      z-index: 1000; justify-content: center; align-items: flex-start;
      padding: 40px 16px; overflow-y: auto;
    }}
    .modal-overlay.open {{ display: flex; }}
    .modal {{
      background: #fff; border-radius: 10px; width: 100%; max-width: 800px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2); overflow: hidden;
    }}
    .modal-header {{
      background: linear-gradient(135deg,#1a6fc4,#2196F3);
      color: #fff; padding: 16px 24px; display: flex; justify-content: space-between;
    }}
    .modal-header h3 {{ font-size: 16px; font-weight: 700; }}
    .modal-close {{
      background: none; border: none; color: #fff; font-size: 22px; cursor: pointer;
    }}
    .modal-body {{ padding: 24px; max-height: 70vh; overflow-y: auto; }}
    .detail-row {{ display: flex; padding: 8px 0; border-bottom: 1px solid #f0f3f8; }}
    .detail-label {{ width: 160px; flex-shrink: 0; font-weight: 600; color: #555; font-size: 13px; }}
    .detail-value {{ flex: 1; font-size: 13px; color: #333; word-break: break-all; }}
    /* ── 通知 ── */
    .toast {{
      position: fixed; bottom: 30px; right: 30px; z-index: 2000;
      padding: 12px 24px; border-radius: 8px; color: #fff; font-size: 14px;
      font-weight: 600; box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      animation: slideIn 0.3s ease; display: none;
    }}
    .toast.show {{ display: block; }}
    .toast.success {{ background: #43a047; }}
    .toast.error {{ background: #e53935; }}
    @keyframes slideIn {{ from {{ transform: translateX(100px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  </style>
</head>
<body>

<!-- 顶部导航 -->
<div class="navbar">
  <div>
    <div class="navbar-title">📋 {form_name}</div>
    <div class="navbar-sub">{btype} 数据登记系统 | Flask + SQLite</div>
  </div>
  <div class="navbar-stats">
    <div class="stat-item"><div class="stat-num" id="totalCount">-</div><div class="stat-label">总记录数</div></div>
    <div class="stat-item"><div class="stat-num" id="todayCount">-</div><div class="stat-label">今日新增</div></div>
  </div>
</div>

<!-- 主体 -->
<div class="main-wrap">
  <!-- Tab按钮 -->
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('form')">📝 新增记录</button>
    <button class="tab-btn" onclick="switchTab('history')">📊 历史查询</button>
  </div>

  <!-- Tab: 表单录入 -->
  <div id="tab-form" class="card">
    <form id="registryForm" onsubmit="submitForm(event)">
      <!-- 表单字段由JS动态渲染 -->
      <div id="formBody"></div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">💾 提交保存</button>
        <button type="reset" class="btn btn-secondary" onclick="resetForm()">🔄 重置</button>
      </div>
    </form>
  </div>

  <!-- Tab: 历史查询 -->
  <div id="tab-history" class="card" style="display:none">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="form-group">
        <label>关键词搜索</label>
        <input type="text" id="searchKeyword" placeholder="姓名/编号/诊断…" onkeydown="if(event.key==='Enter') loadHistory()">
      </div>
      <div class="form-group">
        <label>开始日期</label>
        <input type="date" id="searchDateFrom">
      </div>
      <div class="form-group">
        <label>结束日期</label>
        <input type="date" id="searchDateTo">
      </div>
      <div class="form-group">
        <label>状态</label>
        <select id="searchStatus">
          <option value="">全部</option>
          <option value="submitted">已提交</option>
          <option value="draft">草稿</option>
        </select>
      </div>
      <button class="btn-search" onclick="loadHistory()">🔍 查询</button>
      <button class="btn-export" onclick="exportCSV()">⬇️ 导出CSV</button>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrap">
      <table class="data-table">
        <thead id="tableHead"></thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
    <div class="pagination">
      <span id="pageInfo">共 0 条记录</span>
      <div class="page-btns" id="pageBtns"></div>
    </div>
  </div>
</div>

<!-- 详情弹窗 -->
<div class="modal-overlay" id="detailModal">
  <div class="modal">
    <div class="modal-header">
      <h3>📄 记录详情</h3>
      <button class="modal-close" onclick="closeModal()">×</button>
    </div>
    <div class="modal-body" id="detailBody"></div>
  </div>
</div>

<!-- Toast通知 -->
<div class="toast" id="toast"></div>

<script>
// ── 从后端加载Schema并动态渲染表单 ──
const FIELDS = {fields_js};
let currentPage = 1;
const PAGE_SIZE = 20;

// 页面加载
window.onload = () => {{
  renderForm();
  loadStats();
}};

// ── Tab切换 ──
function switchTab(tab) {{
  document.querySelectorAll('.tab-btn').forEach((b, i) => {{
    b.classList.toggle('active', (i===0 && tab==='form') || (i===1 && tab==='history'));
  }});
  document.getElementById('tab-form').style.display = tab === 'form' ? '' : 'none';
  document.getElementById('tab-history').style.display = tab === 'history' ? '' : 'none';
  if (tab === 'history') loadHistory();
}};

// ── 渲染表单 ──
function renderForm() {{
  const groups = {{}};
  FIELDS.forEach(f => {{
    const g = f.group || '其他';
    if (!groups[g]) groups[g] = [];
    groups[g].push(f);
  }});
  
  const body = document.getElementById('formBody');
  body.innerHTML = '';
  
  for (const [gName, fields] of Object.entries(groups)) {{
    const sec = document.createElement('div');
    sec.className = 'form-section';
    sec.innerHTML = `<div class="form-section-title">${{gName}}</div><div class="form-grid" id="grid-${{gName.replace(/\\s/g,'_')}}"></div>`;
    body.appendChild(sec);
    const grid = sec.querySelector('.form-grid');
    fields.forEach(f => grid.appendChild(buildControl(f)));
  }}
}}

function buildControl(f) {{
  const div = document.createElement('div');
  const fullWidth = ['textarea','matrix','checkbox','file'].includes(f.type);
  div.className = 'form-group' + (fullWidth ? ' full-width' : '');
  
  const reqMark = f.required ? '<span class="req">*</span>' : '';
  let ctrl = '';
  
  switch(f.type) {{
    case 'text':
      ctrl = `<input type="text" name="${{f.id}}" id="${{f.id}}" placeholder="${{f.placeholder||''}}" ${{f.required?'required':''}}>`;
      break;
    case 'textarea':
      ctrl = `<textarea name="${{f.id}}" id="${{f.id}}" placeholder="${{f.placeholder||''}}" ${{f.required?'required':''}}></textarea>`;
      break;
    case 'number':
      ctrl = `<input type="number" name="${{f.id}}" id="${{f.id}}" placeholder="${{f.placeholder||''}}" ${{f.min!=null?'min='+f.min:''}} ${{f.max!=null?'max='+f.max:''}} ${{f.required?'required':''}}>`;
      break;
    case 'date':
      ctrl = `<input type="date" name="${{f.id}}" id="${{f.id}}" ${{f.required?'required':''}}>`;
      break;
    case 'select':
      ctrl = `<select name="${{f.id}}" id="${{f.id}}" ${{f.required?'required':''}}><option value="">请选择</option>`
           + (f.options||[]).map(o => `<option value="${{o.value||o}}">${{o.label||o}}</option>`).join('')
           + '</select>';
      break;
    case 'radio':
      ctrl = `<div class="radio-group">`
           + (f.options||[]).map(o => `<label><input type="radio" name="${{f.id}}" value="${{o.value||o}}" ${{f.required?'required':''}}> ${{o.label||o}}</label>`).join('')
           + '</div>';
      break;
    case 'checkbox':
    case 'multiselect':
    case 'multi-select':
      ctrl = `<div class="checkbox-group">`
           + (f.options||[]).map(o => `<label><input type="checkbox" name="${{f.id}}" value="${{o.value||o}}"> ${{o.label||o}}</label>`).join('')
           + '</div>';
      break;
    case 'file':
      ctrl = `<input type="file" name="${{f.id}}" id="${{f.id}}" accept="${{f.accept||'.pdf,.jpg,.png,.docx'}}">`;
      break;
    case 'matrix':
      ctrl = buildMatrix(f);
      break;
    default:
      ctrl = `<input type="text" name="${{f.id}}" id="${{f.id}}">`;
  }}
  
  div.innerHTML = `<label class="form-label" for="${{f.id}}">${{f.label}}${{reqMark}}</label>${{ctrl}}`;
  return div;
}}

function buildMatrix(f) {{
  const cols = f.matrix_columns || [];
  const rows = f.initial_rows || 3;
  if (!cols.length) return '';
  
  const makeRow = () => '<tr>' + cols.map(c => {{
    let cell = '';
    if (c.type === 'date') cell = '<input type="date">';
    else if (c.type === 'number') cell = '<input type="number" style="width:80px">';
    else if (c.type === 'select') {{
      cell = '<select><option value="">-</option>' + (c.options||[]).map(o=>`<option value="${{o.value||o}}">${{o.label||o}}</option>`).join('') + '</select>';
    }} else cell = `<input type="text" placeholder="${{c.placeholder||''}}">`;
    return `<td>${{cell}}</td>`;
  }}).join('') + '</tr>';
  
  const matrixId = 'matrix_' + f.id;
  const thead = '<tr>' + cols.map(c=>`<th>${{c.label}}</th>`).join('') + '</tr>';
  let tbody = '';
  for (let i=0; i<rows; i++) tbody += makeRow();
  
  return `<div class="matrix-wrap">
    <table class="matrix-table" id="${{matrixId}}">
      <thead>${{thead}}</thead>
      <tbody>${{tbody}}</tbody>
    </table>
    <button type="button" class="btn-add-row" onclick="addMatrixRow('${{matrixId}}')">+ 添加行</button>
  </div>`;
}}

function addMatrixRow(tableId) {{
  const table = document.getElementById(tableId);
  const fid = tableId.replace('matrix_','');
  const f = FIELDS.find(x=>x.id===fid);
  if (!f) return;
  const cols = f.matrix_columns || [];
  const tr = document.createElement('tr');
  cols.forEach(c => {{
    const td = document.createElement('td');
    let inp;
    if (c.type==='date') {{ inp = document.createElement('input'); inp.type='date'; }}
    else if (c.type==='number') {{ inp = document.createElement('input'); inp.type='number'; inp.style.width='80px'; }}
    else if (c.type==='select') {{
      inp = document.createElement('select');
      inp.innerHTML = '<option value="">-</option>' + (c.options||[]).map(o=>`<option value="${{o.value||o}}">${{o.label||o}}</option>`).join('');
    }} else {{ inp = document.createElement('input'); inp.type='text'; inp.placeholder=c.placeholder||''; }}
    td.appendChild(inp); tr.appendChild(td);
  }});
  table.querySelector('tbody').appendChild(tr);
}}

// ── 提交表单 ──
function submitForm(e) {{
  e.preventDefault();
  const data = {{}};
  
  FIELDS.forEach(f => {{
    const ftype = f.type;
    if (ftype === 'checkbox' || ftype === 'multiselect' || ftype === 'multi-select') {{
      const checked = [...document.querySelectorAll(`[name="${{f.id}}"]:checked`)].map(el=>el.value);
      data[f.id] = checked;
    }} else if (ftype === 'matrix') {{
      const table = document.getElementById('matrix_' + f.id);
      if (table) {{
        const rows = [...table.querySelectorAll('tbody tr')];
        const cols = f.matrix_columns || [];
        data[f.id] = rows.map(tr => {{
          const cells = tr.querySelectorAll('td input, td select');
          const row = {{}};
          cols.forEach((c, i) => row[c.label] = cells[i]?.value || '');
          return row;
        }});
      }}
    }} else if (ftype === 'file') {{
      // 附件暂不上传，仅记录文件名
      const el = document.getElementById(f.id);
      data[f.id] = el?.files?.[0]?.name || '';
    }} else {{
      const el = document.getElementById(f.id) || document.querySelector(`[name="${{f.id}}"]`);
      data[f.id] = el?.value || '';
    }}
  }});
  
  data['_submitter'] = 'web_user';
  data['_status'] = 'submitted';
  
  fetch('/api/records', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify(data)
  }})
  .then(r => r.json())
  .then(res => {{
    if (res.success) {{
      showToast('✅ 记录已保存 (ID: ' + res.id + ')', 'success');
      document.getElementById('registryForm').reset();
      loadStats();
    }} else {{
      showToast('❌ 提交失败: ' + res.error, 'error');
    }}
  }})
  .catch(err => showToast('❌ 网络错误: ' + err, 'error'));
}}

function resetForm() {{
  renderForm();
}}

// ── 统计数字 ──
function loadStats() {{
  fetch('/api/stats')
    .then(r=>r.json())
    .then(res=>{{
      if (res.success) {{
        document.getElementById('totalCount').textContent = res.data.total;
        document.getElementById('todayCount').textContent = res.data.today;
      }}
    }}).catch(()=>{{}});
}}

// ── 加载历史记录 ──
function loadHistory(page) {{
  page = page || 1;
  currentPage = page;
  
  const keyword = document.getElementById('searchKeyword').value;
  const dateFrom = document.getElementById('searchDateFrom').value;
  const dateTo = document.getElementById('searchDateTo').value;
  const status = document.getElementById('searchStatus').value;
  
  const params = new URLSearchParams({{
    page, page_size: PAGE_SIZE,
    search: keyword, date_from: dateFrom, date_to: dateTo, status
  }});
  
  fetch('/api/records?' + params)
    .then(r=>r.json())
    .then(res=>{{
      if (res.success) renderTable(res.data, res.pagination);
    }}).catch(err => showToast('加载失败: ' + err, 'error'));
}}

function renderTable(records, pagination) {{
  // 表头：显示前5个字段 + 操作
  const showFields = FIELDS.slice(0, 5);
  const thead = document.getElementById('tableHead');
  thead.innerHTML = '<tr>'
    + '<th style="width:60px">ID</th>'
    + '<th style="width:140px">创建时间</th>'
    + showFields.map(f=>`<th>${{f.label}}</th>`).join('')
    + '<th style="width:80px">状态</th>'
    + '<th style="width:100px">操作</th>'
    + '</tr>';
  
  const tbody = document.getElementById('tableBody');
  if (!records.length) {{
    tbody.innerHTML = '<tr><td colspan="' + (showFields.length+4) + '" style="text-align:center;color:#999;padding:24px">暂无记录</td></tr>';
  }} else {{
    tbody.innerHTML = records.map(r => {{
      const statusBadge = {{
        'submitted': '<span class="badge badge-submitted">已提交</span>',
        'draft': '<span class="badge badge-draft">草稿</span>',
        'deleted': '<span class="badge badge-deleted">已删除</span>'
      }}[r.status] || r.status;
      
      const cells = showFields.map(f => {{
        let val = r[f.id];
        if (Array.isArray(val)) val = val.join('、');
        if (typeof val === 'object' && val !== null) val = JSON.stringify(val);
        val = val || '-';
        if (String(val).length > 20) val = val.substring(0, 20) + '…';
        return `<td>${{val}}</td>`;
      }}).join('');
      
      return `<tr>
        <td>${{r.id}}</td>
        <td>${{(r.created_at||'').substring(0,16)}}</td>
        ${{cells}}
        <td>${{statusBadge}}</td>
        <td class="actions">
          <button class="btn btn-sm btn-secondary" onclick="viewRecord(${{r.id}})">详情</button>
          ${{r.status!=='deleted'?`<button class="btn btn-sm btn-danger" onclick="deleteRecord(${{r.id}})">删除</button>`:''}}
        </td>
      </tr>`;
    }}).join('');
  }}
  
  // 分页
  const {{total, total_pages}} = pagination;
  document.getElementById('pageInfo').textContent = `共 ${{total}} 条记录`;
  const pageBtns = document.getElementById('pageBtns');
  pageBtns.innerHTML = '';
  
  for (let i=1; i<=Math.min(total_pages, 10); i++) {{
    const btn = document.createElement('button');
    btn.className = 'page-btn' + (i===currentPage?' active':'');
    btn.textContent = i;
    btn.onclick = () => loadHistory(i);
    pageBtns.appendChild(btn);
  }}
}}

// ── 查看详情 ──
function viewRecord(id) {{
  fetch('/api/records/' + id)
    .then(r=>r.json())
    .then(res=>{{
      if (!res.success) return;
      const r = res.data;
      const body = document.getElementById('detailBody');
      
      const systemFields = [
        ['记录ID', r.id],
        ['创建时间', r.created_at],
        ['更新时间', r.updated_at],
        ['提交人', r.submitter],
        ['状态', r.status]
      ];
      
      let html = systemFields.map(([k,v]) => `
        <div class="detail-row">
          <div class="detail-label">${{k}}</div>
          <div class="detail-value">${{v||'-'}}</div>
        </div>`).join('');
      
      FIELDS.forEach(f => {{
        let val = r[f.id];
        if (val === null || val === undefined) val = '-';
        if (Array.isArray(val)) val = val.join('、');
        if (typeof val === 'object') val = JSON.stringify(val, null, 2);
        html += `<div class="detail-row">
          <div class="detail-label">${{f.label}}</div>
          <div class="detail-value" style="white-space:pre-wrap">${{val||'-'}}</div>
        </div>`;
      }});
      
      body.innerHTML = html;
      document.getElementById('detailModal').classList.add('open');
    }});
}}

function closeModal() {{
  document.getElementById('detailModal').classList.remove('open');
}}

// ── 删除记录 ──
function deleteRecord(id) {{
  if (!confirm('确认删除此记录？（软删除，可恢复）')) return;
  fetch('/api/records/' + id, {{method: 'DELETE'}})
    .then(r=>r.json())
    .then(res=>{{
      if (res.success) {{
        showToast('记录已删除', 'success');
        loadHistory(currentPage);
        loadStats();
      }} else showToast('删除失败: ' + res.error, 'error');
    }});
}}

// ── 导出CSV ──
function exportCSV() {{
  window.open('/api/export', '_blank');
}}

// ── Toast通知 ──
function showToast(msg, type) {{
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show ' + type;
  setTimeout(() => el.classList.remove('show'), 3000);
}}

// 点击弹窗遮罩关闭
document.getElementById('detailModal').addEventListener('click', function(e) {{
  if (e.target === this) closeModal();
}});
</script>
</body>
</html>'''


# ─────────────────────────────────────────────────────────────
# 生成 requirements.txt
# ─────────────────────────────────────────────────────────────

def gen_requirements():
    return """flask>=2.3.0
# sqlite3 is built-in to Python standard library
# No additional database driver needed
"""


# ─────────────────────────────────────────────────────────────
# 生成 README.md
# ─────────────────────────────────────────────────────────────

def gen_readme(schema):
    form_name = schema.get("form_name", "医疗登记系统")
    return f"""# {form_name} — 数据登记系统

自动生成的医疗数据登记系统，基于 **Flask + SQLite**。

## 快速启动

```bash
# 1. 安装依赖
pip install flask

# 2. 启动服务
python app.py

# 3. 浏览器访问
http://localhost:5000
```

## 功能说明

| 功能 | 说明 |
|------|------|
| 表单录入 | 动态渲染所有字段，支持提交保存到 SQLite |
| 历史查询 | 关键词/日期范围/状态过滤，分页展示 |
| 记录详情 | 弹窗查看完整记录内容 |
| 软删除 | 删除标记为 deleted，保留审计日志 |
| CSV导出 | 一键导出全部记录为 Excel 兼容 CSV |
| 统计面板 | 实时显示总记录数和今日新增 |

## 目录结构

```
registry_system/
├── app.py               # Flask 后端服务
├── schema.json          # 表单字段定义
├── requirements.txt     # Python依赖
├── templates/
│   └── index.html       # 前端页面
├── data/
│   ├── registry.db      # SQLite 数据库（运行时自动创建）
│   └── uploads/         # 附件上传目录
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schema` | 获取表单定义 |
| POST | `/api/records` | 新增记录 |
| GET | `/api/records` | 查询记录列表（支持分页+过滤）|
| GET | `/api/records/:id` | 获取单条记录 |
| PUT | `/api/records/:id` | 更新记录 |
| DELETE | `/api/records/:id` | 软删除记录 |
| GET | `/api/stats` | 统计概要 |
| GET | `/api/export` | 导出 CSV |

## 数据库表结构

- `form_records` — 主数据表，字段来自 schema.json
- `audit_log` — 操作审计日志，记录每次 CREATE/UPDATE/DELETE

自动生成于：{datetime.now().strftime("%Y-%m-%d %H:%M")}
"""


# ─────────────────────────────────────────────────────────────
# 生成 start.bat / start.sh 启动脚本
# ─────────────────────────────────────────────────────────────

def gen_start_bat(form_name):
    return f"""@echo off
chcp 65001 >nul
title {form_name} - 医疗数据登记系统
color 0B

echo ============================================================
echo   {form_name}
echo   医疗数据登记系统  [Flask + SQLite]
echo ============================================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo   下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查并安装依赖...
pip install flask -q
if errorlevel 1 (
    echo [错误] Flask 安装失败，请检查网络或手动执行: pip install flask
    pause
    exit /b 1
)
echo       OK - Flask 已就绪

echo.
echo [2/3] 初始化数据库...
if not exist "data" mkdir data
echo       OK - 数据目录已创建

echo.
echo [3/3] 启动服务...
echo       访问地址：http://localhost:5000
echo       按 Ctrl+C 可停止服务
echo.
echo ============================================================

:: 延迟2秒后自动打开浏览器
start /min "" cmd /c "timeout /t 2 >nul && start http://localhost:5000"

:: 启动Flask服务
python app.py

echo.
echo [服务已停止]
pause
"""


def gen_start_sh(form_name):
    return f"""#!/bin/bash
echo "============================================================"
echo "  {form_name}"
echo "  医疗数据登记系统  [Flask + SQLite]"
echo "============================================================"
echo ""

# 检查Python
if ! command -v python3 &>/dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "[1/3] 安装依赖..."
pip3 install flask -q && echo "      OK - Flask 已就绪"

echo "[2/3] 初始化目录..."
mkdir -p data && echo "      OK - 数据目录已创建"

echo "[3/3] 启动服务..."
echo "      访问地址：http://localhost:5000"
echo "      按 Ctrl+C 可停止服务"
echo ""

# 延迟后打开浏览器（macOS/Linux）
(sleep 2 && (open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null)) &

python3 app.py
"""


# ─────────────────────────────────────────────────────────────
# 主函数：生成完整系统目录
# ─────────────────────────────────────────────────────────────

def generate_system(schema, outdir):
    form_name_safe = schema.get("form_name", "registry").replace(" ", "_").replace("/", "_")
    sys_dir = os.path.join(outdir, form_name_safe + "_registry")
    
    os.makedirs(sys_dir, exist_ok=True)
    os.makedirs(os.path.join(sys_dir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(sys_dir, "data"), exist_ok=True)
    
    # app.py
    app_code = gen_app_py(schema)
    with open(os.path.join(sys_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write(app_code)
    print(f"  [APP.PY]       -> {sys_dir}/app.py")
    
    # schema.json（复制）
    with open(os.path.join(sys_dir, "schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"  [SCHEMA.JSON]  -> {sys_dir}/schema.json")
    
    # templates/index.html
    html_code = gen_index_html(schema)
    with open(os.path.join(sys_dir, "templates", "index.html"), "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"  [INDEX.HTML]   -> {sys_dir}/templates/index.html")
    
    # requirements.txt
    with open(os.path.join(sys_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(gen_requirements())
    print(f"  [REQUIREMENTS] -> {sys_dir}/requirements.txt")
    
    # README.md
    with open(os.path.join(sys_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(gen_readme(schema))
    print(f"  [README.MD]    -> {sys_dir}/README.md")
    
    # 启动脚本
    with open(os.path.join(sys_dir, "start.bat"), "w", encoding="utf-8") as f:
        f.write(gen_start_bat(schema.get("form_name", "Registry")))
    with open(os.path.join(sys_dir, "start.sh"), "w", encoding="utf-8") as f:
        f.write(gen_start_sh(schema.get("form_name", "Registry")))
    print(f"  [START SCRIPTS]-> start.bat / start.sh")
    
    # 打包为zip
    import zipfile
    zip_path = os.path.join(outdir, form_name_safe + "_registry.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(sys_dir):
            # 跳过data目录（运行时自动创建）
            dirs[:] = [d for d in dirs if d != "data"]
            for file in files:
                fp = os.path.join(root, file)
                arcname = os.path.relpath(fp, outdir)
                zf.write(fp, arcname)
    print(f"  [ZIP PACKAGE]  -> {zip_path}")
    
    return sys_dir, zip_path


def main():
    parser = argparse.ArgumentParser(description="医疗表单登记系统生成工具")
    parser.add_argument("schema_file", help="字段Schema JSON文件路径")
    parser.add_argument("--outdir", default="form_output", help="输出目录")
    args = parser.parse_args()
    
    if not os.path.exists(args.schema_file):
        print(f"[ERROR] File not found: {args.schema_file}")
        sys.exit(1)
    
    with open(args.schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    os.makedirs(args.outdir, exist_ok=True)
    
    print(f"\n[INFO] Generating registry system: {schema.get('form_name')}")
    sys_dir, zip_path = generate_system(schema, args.outdir)
    print(f"\n[OK] Registry system generated!")
    print(f"     Directory: {sys_dir}")
    print(f"     Package:   {zip_path}")
    print(f"     Start: cd {sys_dir} && python app.py")


if __name__ == "__main__":
    main()
