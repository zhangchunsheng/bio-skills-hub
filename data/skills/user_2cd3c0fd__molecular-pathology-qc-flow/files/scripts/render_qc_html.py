#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把质控定义和知识条目渲染为单文件 HTML 配置方案。

说明：HTML 渲染职责独立于下载目录解析和 Draw.io 持久化。
Author: WangYunL
"""

from __future__ import annotations

import html
import json
import re
from datetime import date
from html.parser import HTMLParser
from typing import Any


BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
TAG_PATTERN = re.compile(r"<[^>]+>")


class HtmlValidationError(ValueError):
    """表示生成的 HTML 不满足交付要求。"""


def plain_text(value: Any) -> str:
    """把节点中的 HTML 换行转换为纯文本。"""
    text = html.unescape(str(value or ""))
    text = BR_PATTERN.sub(" / ", text)
    return html.unescape(TAG_PATTERN.sub("", text)).strip()


def e(value: Any) -> str:
    """转义所有外部文本，避免破坏 HTML。"""
    return html.escape(plain_text(value), quote=True)


def _status_badge(status: str) -> str:
    """生成证据状态徽标。"""
    mapping = {
        "confirmed": ("已确认", "ok"),
        "inferred": ("推断", "warn"),
        "unknown": ("待确认", "muted"),
        "conflict": ("冲突", "bad"),
    }
    label, css = mapping.get(status, (status or "待确认", "muted"))
    return f'<span class="badge {css}">{e(label)}</span>'


def _project_profile(entry: dict[str, Any] | None) -> str:
    """渲染项目专有的基因、通道和来源信息。"""
    profile = (entry or {}).get("project_profile")
    if not isinstance(profile, dict):
        return '<p class="muted">当前知识索引没有项目专用范围表，需补充试剂 IFU、SOP 或项目资料。</p>'
    mutation = profile.get("mutation_genes") or []
    fusion = profile.get("fusion_genes") or []
    channels = profile.get("observed_channels") or []
    return f"""
      <div class="profile-grid">
        <article class="mini-card"><span class="eyebrow">报告名称</span><strong>{e(profile.get('report_title'))}</strong></article>
        <article class="mini-card"><span class="eyebrow">突变类基因</span><strong>{e('、'.join(mutation) or '待确认')}</strong></article>
        <article class="mini-card"><span class="eyebrow">融合/剪接类基因</span><strong>{e('、'.join(fusion) or '待确认')}</strong></article>
        <article class="mini-card"><span class="eyebrow">模板中观察到的通道</span><strong>{e('、'.join(channels) or '待确认')}</strong></article>
      </div>
      <div class="callout warn"><strong>命名边界</strong>{e(profile.get('naming_note') or '项目简称的具体分组含义需由项目资料确认。')}</div>
    """


def _unresolved_items(
    diagram: dict[str, Any], nodes: list[dict[str, Any]], project_entry: dict[str, Any] | None
) -> list[str]:
    """汇总所有明确待确认项。"""
    items = [str(item) for item in (project_entry or {}).get("pending_items") or []]
    method = str(diagram.get("method") or "")
    if "待确认" in method or "未确定" in method:
        items.append("具体试剂、平台、扩增化学、分析软件及其版本需要确认。")
    for source in diagram.get("sources") or []:
        if not isinstance(source, dict):
            continue
        if source.get("evidence_status") in {"unknown", "inferred", "conflict"}:
            items.append(
                f"来源“{source.get('title')}”的证据状态为 {source.get('evidence_status')}，需人工复核适用范围。"
            )
    if any((node.get("condition") or {}).get("operator") == "CUSTOM" for node in nodes):
        items.append("流程中的 CUSTOM 判断节点需要用匹配版本 SOP/IFU 补充结构化阈值或明确人工判读规则。")
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique


def build_qc_html(
    spec: dict[str, Any],
    diagram: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    project_entry: dict[str, Any] | None,
    technology_entry: dict[str, Any] | None,
    drawio_filename: str,
) -> str:
    """生成包含项目说明、质控点、来源和配置 JSON 的完整 HTML。"""
    project_summary = str((project_entry or {}).get("summary") or "暂无项目专用说明。")
    project_principle = str((project_entry or {}).get("principle") or "具体方法原理待项目资料确认。")
    technology_summary = str((technology_entry or {}).get("summary") or "暂无技术专用说明。")
    scope_note = str((project_entry or {}).get("scope_note") or "阈值必须绑定具体试剂、平台和实验室验证。")
    node_rows: list[str] = []
    for index, node in enumerate(nodes, start=1):
        condition = node.get("condition") if isinstance(node.get("condition"), dict) else {}
        node_rows.append(
            "<tr>"
            f"<td>{index}</td><td><code>{e(node.get('id'))}</code></td>"
            f"<td>{e(node.get('stage'))}</td><td>{e(node.get('type'))}</td>"
            f"<td>{e(node.get('label'))}</td>"
            f"<td>{e(condition.get('expression') or '—')}</td>"
            f"<td>{e(node.get('terminal_result') or '—')}</td>"
            "</tr>"
        )
    edge_rows = [
        "<tr>"
        f"<td><code>{e(edge.get('source'))}</code></td>"
        f"<td>{e(edge.get('label') or '顺序')}</td>"
        f"<td><code>{e(edge.get('target'))}</code></td>"
        f"<td>{e(edge.get('branch') or 'next')}</td>"
        "</tr>"
        for edge in edges
    ]
    source_rows = []
    for source in diagram.get("sources") or []:
        location = source.get("url") or source.get("path") or "未提供"
        source_rows.append(
            "<tr>"
            f"<td><code>{e(source.get('id'))}</code></td>"
            f"<td>{e(source.get('title'))}</td>"
            f"<td>{_status_badge(str(source.get('evidence_status') or 'unknown'))}</td>"
            f"<td>{e(source.get('version'))}</td>"
            f"<td class=\"path\">{e(location)}</td>"
            f"<td>{e(source.get('scope_note'))}</td>"
            "</tr>"
        )
    unresolved = _unresolved_items(diagram, nodes, project_entry)
    unresolved_html = "".join(f"<li>{e(item)}</li>" for item in unresolved) or "<li>未识别到自动待确认项，仍需实验室负责人完成适用性审核。</li>"
    stages = "".join(f"<span>{e(stage)}</span>" for stage in diagram.get("stages") or [])
    spec_json = html.escape(json.dumps(spec, ensure_ascii=False, indent=2))
    generated_on = date.today().isoformat()

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="generator" content="molecular-pathology-qc-flow/1.2">
  <meta name="author" content="WangYunL">
  <title>{e(diagram.get('name'))}配置方案</title>
  <style>
    :root{{--bg:#f4f7fb;--panel:#fff;--ink:#172033;--muted:#667085;--line:#dfe5ef;--brand:#155eef;--brand2:#0b3a82;--soft:#edf4ff;--ok:#087a55;--okbg:#eaf8f2;--warn:#9a6700;--warnbg:#fff7dd;--bad:#b42318;--badbg:#fff0ee;--shadow:0 12px 34px rgba(31,50,81,.09);--mono:"Cascadia Code","Consolas",monospace;--sans:"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif}}
    *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.72 var(--sans)}}
    .wrap{{max-width:1220px;margin:auto;padding:30px 24px 60px}} .cover{{position:relative;overflow:hidden;border-radius:20px;padding:38px 42px;color:#fff;background:linear-gradient(135deg,var(--brand2),var(--brand));box-shadow:var(--shadow)}}
    .cover:after{{content:"QC";position:absolute;right:24px;bottom:-55px;font:900 150px/1 var(--sans);opacity:.08}} .kicker{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;opacity:.78}} h1{{margin:8px 0 10px;font-size:30px;line-height:1.28}} .cover p{{max-width:850px;margin:0;opacity:.9}}
    .meta{{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}} .meta span,.stages span{{border-radius:999px;padding:5px 11px;font-size:12px}} .meta span{{background:rgba(255,255,255,.14)}}
    nav{{position:sticky;top:10px;z-index:2;display:flex;gap:8px;overflow:auto;margin:18px 0;padding:10px;background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:12px;backdrop-filter:blur(8px)}} nav a{{white-space:nowrap;color:var(--brand2);text-decoration:none;padding:5px 9px;border-radius:7px}} nav a:hover{{background:var(--soft)}}
    section{{margin:18px 0;padding:26px 28px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 16px rgba(31,50,81,.04)}} h2{{display:flex;align-items:center;gap:10px;margin:0 0 18px;font-size:20px}} h2 b{{display:grid;place-items:center;width:30px;height:30px;border-radius:9px;background:var(--brand);color:#fff;font-size:14px}} h3{{margin:22px 0 10px;font-size:16px}} p{{margin:8px 0}} .muted{{color:var(--muted)}}
    .facts,.profile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}} .fact,.mini-card{{border:1px solid var(--line);border-radius:12px;padding:15px 16px;background:#fbfcfe}} .fact span,.eyebrow{{display:block;color:var(--muted);font-size:12px;margin-bottom:4px}} .mini-card strong{{display:block;font-size:14px}}
    .stages{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}} .stages span{{background:var(--soft);color:var(--brand2);font-weight:600}} .callout{{margin:14px 0;padding:13px 16px;border-left:4px solid var(--brand);border-radius:0 10px 10px 0;background:var(--soft)}} .callout.warn{{border-color:#f0a000;background:var(--warnbg)}} .callout strong{{display:block;margin-bottom:3px}}
    table{{width:100%;border-collapse:separate;border-spacing:0;margin:12px 0;font-size:13px;border:1px solid var(--line);border-radius:12px;overflow:hidden}} th,td{{padding:10px 11px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);vertical-align:top;text-align:left}} th:last-child,td:last-child{{border-right:0}} tr:last-child td{{border-bottom:0}} thead th{{background:#eef3fa;color:#344054;font-weight:650}} tbody tr:nth-child(even){{background:#fbfcfe}} code{{font:12px var(--mono);color:#174ea6;background:#eef4ff;border-radius:5px;padding:2px 5px}} .path{{max-width:230px;word-break:break-all}}
    .badge{{display:inline-block;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700}} .badge.ok{{color:var(--ok);background:var(--okbg)}} .badge.warn{{color:var(--warn);background:var(--warnbg)}} .badge.bad{{color:var(--bad);background:var(--badbg)}} .badge.muted{{color:#475467;background:#eef2f6}}
    .file-card{{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:15px 18px;border:1px dashed #8bb1f7;background:#f7faff;border-radius:12px}} .file-card strong{{word-break:break-all}} details{{margin-top:12px}} summary{{cursor:pointer;color:var(--brand);font-weight:650}} pre{{overflow:auto;max-height:620px;padding:18px;border-radius:12px;background:#111827;color:#e5e7eb;font:12px/1.55 var(--mono)}} ul{{padding-left:21px}} li{{margin:5px 0}} footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:24px}}
    @media(max-width:760px){{.wrap{{padding:14px 10px 38px}}.cover{{padding:26px 22px}}h1{{font-size:24px}}section{{padding:20px 16px}}nav{{top:4px}}table{{display:block;overflow-x:auto}}}}
    @media print{{body{{background:#fff}}.wrap{{max-width:none;padding:0}}nav{{display:none}}section,.cover{{box-shadow:none;break-inside:avoid}}details:not([open])>*:not(summary){{display:block}}}}
  </style>
</head>
<body>
<div class="wrap">
  <header class="cover">
    <div class="kicker">Molecular pathology quality control</div>
    <h1>{e(diagram.get('name'))}配置方案</h1>
    <p>{e(project_summary)}</p>
    <div class="meta"><span>技术：{e(diagram.get('technology'))}</span><span>方法：{e(diagram.get('method'))}</span><span>项目：{e(diagram.get('project'))}</span><span>版本：v1.2</span></div>
  </header>
  <nav><a href="#overview">项目概况</a><a href="#scope">检测范围</a><a href="#qc">质控节点</a><a href="#flow">分支关系</a><a href="#sources">来源</a><a href="#pending">待确认</a><a href="#config">配置 JSON</a></nav>

  <section id="overview"><h2><b>1</b>项目概况</h2>
    <div class="facts">
      <div class="fact"><span>技术</span><strong>{e(diagram.get('technology'))}</strong></div>
      <div class="fact"><span>方法</span><strong>{e(diagram.get('method'))}</strong></div>
      <div class="fact"><span>项目</span><strong>{e(diagram.get('project'))}</strong></div>
      <div class="fact"><span>质控范围</span><strong>{e(diagram.get('qc_stage'))}</strong></div>
    </div>
    <h3>技术是什么</h3><p>{e(technology_summary)}</p>
    <h3>项目是什么</h3><p>{e(project_summary)}</p><p>{e(project_principle)}</p>
    <div class="stages">{stages}</div>
    <div class="callout"><strong>适用边界</strong>{e(scope_note)}</div>
  </section>

  <section id="scope"><h2><b>2</b>检测范围与项目资料</h2>{_project_profile(project_entry)}</section>

  <section id="qc"><h2><b>3</b>质控节点</h2>
    <p class="muted">判断节点中的“依据 SOP/IFU”是强制人工确认项，不表示系统已经拥有对应阈值。</p>
    <table><thead><tr><th>#</th><th>ID</th><th>阶段</th><th>类型</th><th>节点内容</th><th>判断条件</th><th>终点</th></tr></thead><tbody>{''.join(node_rows)}</tbody></table>
  </section>

  <section id="flow"><h2><b>4</b>流程图与分支关系</h2>
    <div class="file-card"><span>同目录 Draw.io 流程图</span><strong>{e(drawio_filename)}</strong></div>
    <table><thead><tr><th>起点</th><th>分支</th><th>终点</th><th>语义</th></tr></thead><tbody>{''.join(edge_rows)}</tbody></table>
  </section>

  <section id="sources"><h2><b>5</b>来源与证据状态</h2>
    <table><thead><tr><th>ID</th><th>标题</th><th>状态</th><th>版本</th><th>位置</th><th>适用范围</th></tr></thead><tbody>{''.join(source_rows)}</tbody></table>
  </section>

  <section id="pending"><h2><b>6</b>待确认项</h2><div class="callout warn"><strong>在补齐前不得把占位条件当成正式阈值</strong><ul>{unresolved_html}</ul></div></section>

  <section id="config"><h2><b>7</b>结构化配置</h2>
    <p>下面的 v1.1 JSON 已嵌入本 HTML，便于审核与后续系统配置；下载目录默认只交付 HTML 和 Draw.io 两个文件。</p>
    <details><summary>展开查看配置 JSON</summary><pre>{spec_json}</pre></details>
  </section>

  <footer>作者：WangYunL · 生成日期：{generated_on} · 本方案不能替代实验室现行 SOP、试剂 IFU、方法验证或临床判读。</footer>
</div>
</body>
</html>
"""


class _StructureParser(HTMLParser):
    """统计 HTML 根结构，用于交付前轻量校验。"""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.meta_charset = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        if tag == "meta" and any(key == "charset" and value == "utf-8" for key, value in attrs):
            self.meta_charset = True


def validate_qc_html(content: str) -> None:
    """拒绝缺失根结构、UTF-8 声明或中文替换字符的 HTML。"""
    if "\ufffd" in content:
        raise HtmlValidationError("HTML 包含中文替换字符。")
    parser = _StructureParser()
    parser.feed(content)
    for tag in ("html", "head", "title", "body"):
        if tag not in parser.tags:
            raise HtmlValidationError(f"HTML 缺少 {tag} 标签。")
    if not parser.meta_charset:
        raise HtmlValidationError("HTML 缺少 UTF-8 charset 声明。")
    if 'name="generator" content="molecular-pathology-qc-flow/1.2"' not in content:
        raise HtmlValidationError("HTML 缺少生成器标识。")

