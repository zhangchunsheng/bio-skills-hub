#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 诊室小结 HTML 渲染器

读取 report.json，输出自包含的单文件 HTML 报告。零第三方依赖，仅标准库。

用法:
    python3 render_report.py report.json -o 症状自查小结.html
    python3 render_report.py --print-schema        # 打印 JSON 字段模板

退出码:
    0 = 渲染成功且通过质检
    1 = 输入错误（文件缺失 / JSON 非法）
    3 = 已生成 HTML 但未通过「必须有 / 必须无」质检，需修正后重新渲染
"""

import argparse
import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------- 紧急度
#
# 面向用户只出现 label / note / action。L1-L4 是内部编号，
# 任何情况下都不得渲染进 HTML。

URGENCY = {
    "L1": {"label": "建议立即就医", "dot": "#D54941", "bg": "#FFF0ED",
           "border": "#FBD4CE", "fg": "#AD352F",
           "note": "存在需要马上处理的情况，请现在就前往急诊，必要时拨打 120",
           "action": "现在就去急诊"},
    "L2": {"label": "建议尽快就医", "dot": "#E37318", "bg": "#FFF1E9",
           "border": "#FFD9C2", "fg": "#BE5A00",
           "note": "建议这几天内到对应专科就诊，不宜再拖延，通常不需要挂急诊",
           "action": "这几天内就诊"},
    "L3": {"label": "建议安排一次就医", "dot": "#D29C08", "bg": "#FFF8E6",
           "border": "#FFE9A6", "fg": "#8E6800",
           "note": "需要线下看一次，但不用赶时间，可挑方便的时间挂号检查",
           "action": "择期挂号门诊"},
    "L4": {"label": "可以先在家观察", "dot": "#2BA471", "bg": "#E8F8F2",
           "border": "#BCEBDC", "fg": "#1D7D53",
           "note": "目前偏低危，可先居家调理并留意变化，出现新情况再就医",
           "action": "居家观察记录"},
    "": {"label": "需要医生当面判断", "dot": "#8B93A6", "bg": "#F3F5F9",
         "border": "#DCE1EB", "fg": "#5A6478",
         "note": "现有信息还不足以判断轻重，建议线下就诊由医生进一步评估",
         "action": "线下就诊评估"},
}

HISTORY_LABELS = [
    ("past_history", "既往史"),
    ("family_history", "家族史"),
    ("exam_records", "检查记录"),
    ("current_meds", "当前用药"),
    ("allergy", "过敏史"),
]

EMPTY_HISTORY = "暂无"
# 「无」是用户已明确提供的阴性病史，应正常展示；只有真正缺失的信息才收进折叠区。
EMPTY_ALIASES = ("", "未提供", "未知", "暂无")

DEFAULT_DISCLAIMER = "以上仅供参考，不替代线下就诊。如症状加重或出现危险信号，请及时就医。"
HEADER_BRAND = "健康问问·AI诊室"
REPORT_TITLE = "症状自查小结"

REF_NOTICE = ("以下资料仅供延伸阅读，不作为本次建议的判断依据。"
              "具体诊疗请以线下医生意见为准。")

# 允许写入参考资料的权威域名白名单（须与 references/evidence-search.md 保持一致）
ALLOWED_REF_DOMAINS = (
    "nhc.gov.cn", "chinacdc.cn", "nmpa.gov.cn", "cma.org.cn", "yiigle.com",
    "msdmanuals.cn", "msdmanuals.com", "who.int", "ncbi.nlm.nih.gov", "nih.gov",
    "medlineplus.gov", "cdc.gov", "mayoclinic.org", "nhs.uk", "nice.org.uk",
    "cochranelibrary.com", "aafp.org", "uptodate.com",
)
MAX_REFS = 5

# 行动计划按「当前决策顺序」呈现，而不是固定拆成就医/居家两条线。
# type 仅用于排序与安全过滤；title 是用户可见的、贴合本例的行动标题。
PLAN_TYPE_ORDER = ["immediate", "appointment", "preparation", "home", "monitoring", "follow_up", "escalation"]
PLAN_TYPE_DEFAULT_TITLE = {
    "immediate": "现在先做",
    "appointment": "优先安排",
    "preparation": "就诊前可以准备这些",
    "home": "这几天可以这样处理",
    "monitoring": "接下来重点观察",
    "follow_up": "后续如何跟进",
    "escalation": "出现这些情况不要等待",
}
# 兼容旧报告输入；新报告请直接提供 type / title / items。
LEGACY_PLAN_TYPES = {
    "现在就做": "immediate", "立即行动": "immediate", "就医安排": "appointment",
    "就诊准备": "preparation", "居家护理": "home", "饮食与作息": "home",
    "用药提示": "home", "观察与记录": "monitoring", "复诊与随访": "follow_up",
}
# L1 急症下不出现会造成延误的居家、观察或随访模块。
L1_BANNED_PLAN_TYPES = ("home", "monitoring", "follow_up")

SCHEMA = {
    "meta": {"product": HEADER_BRAND, "title": REPORT_TITLE,
             "chief_complaint_short": "<5-10 字主诉概要>"},
    "demographics": {"sex": "<女性/男性，未提供写空字符串>", "age": "<数字或空字符串>"},
    "medical_urgency_level": "<L1|L2|L3|L4。内部编号，不会渲染给用户>",
    "answer_mode": "<emergency|consult|diagnosed|standard>",
    "recommended_departments": ["<首选科室>", "<备选科室，可选，最多 2 个>"],
    "chief_complaint_raw": "<用户原话主诉，保留其用词，不要改写成医学术语>",
    "summary": "<100-200 字问诊摘要：最可能的方向 + 现在要做什么 + 急不急>",
    "answers": [{"q": "<用户原话问题，如“吃什么药”“要不要手术”>",
                 "a": "<直接回答，首句给结论。不确定就说清取决于什么>"}],
    "illness_description": "<起病、进展、伴随与否认、时间窗与趋势；必须含关键阴性信息>",
    "history": {k: f"<缺失写 {EMPTY_HISTORY}>" for k, _ in HISTORY_LABELS},
    "causes": [{"name": "<规范病名，不带“方向”后缀>",
                "support": ["<支持点：本例哪些表现指向它，命中的关键词用 **加粗**>"],
                "to_exclude": ["<待排除项：还需要什么信息或检查才能排除/确认>"]}],
    "recommended_checks": [{"name": "<检查或评估名称>",
                            "description": "<简要介绍：检查方式或观察重点，1 句>",
                            "value": "<本例中的判断价值，1 句>"}],
    "action_plan": [{"type": "<immediate|appointment|preparation|home|monitoring|follow_up|escalation>",
                     "title": "<用户可见标题，按本例写具体行动，如“建议近期安排神经内科就诊”>",
                     "items": ["<该模块下的具体动作，一条一件事，可执行>"]}],
    "action_plan_legacy_compat": "旧格式 key/value 仍可渲染；新报告必须使用 type/title/items。", 
    "items_to_bring": ["<需就医时展示，2-4 条>"],
    "questions_for_doctor": ["<需就医时展示，2-4 条问句>"],
    "observations_to_record": ["<可先观察时展示，2-4 条，可量化优先>"],
    "warning_signs": ["<2-4 条，必须带具体症状或阈值，不能只写“加重”>"],
    "references": [{"title": "<来源标题>", "source": "<机构名，如 MSD 诊疗手册>",
                    "url": "<实际检索到的 URL，须在白名单域名内>",
                    "note": "<一句话说明这条讲了什么，可选>"}],
    "disclaimer": DEFAULT_DISCLAIMER,
    "inquiry_log": [{"turn": 1, "note": "<本轮过渡话术要点，可留空>",
                     "qa": [{"q": "<问题>", "a": "<用户回答>"}]}],
}

# ---------------------------------------------------------------- 工具


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def inline(text):
    """极简 inline markdown: **粗体** / `代码`。输入先转义。"""
    s = esc(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def strip_direction_suffix(name):
    """去掉给模型用的防确诊后缀，用户侧只看病名。“痛经方向” -> “痛经”。"""
    s = str(name or "").strip()
    for suf in ("的方向", "方向", "相关"):
        if s.endswith(suf) and len(s) > len(suf):
            return s[: -len(suf)].strip("（）() 　") or s
    return s


def blocks(body):
    """把正文 body 转成 HTML：支持 ###/## 小标题、* - 列表、1. 有序列表、空行分段。"""
    out, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        if mode == "ul":
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + "</ul>")
        elif mode == "ol":
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + "</ol>")
        else:
            out.append("<p>" + "<br>".join(inline(x) for x in buf) + "</p>")
        buf, mode = [], None

    for raw in str(body or "").split("\n"):
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("#"):
            flush()
            out.append("<h4>" + inline(line.lstrip("#").strip()) + "</h4>")
            continue
        m = re.match(r"^(?:[*\-\u2022])\s+(.*)$", line)
        if m:
            if mode != "ul":
                flush()
                mode = "ul"
            buf.append(m.group(1))
            continue
        m = re.match(r"^\d+[.)]\s+(.*)$", line)
        if m:
            if mode != "ol":
                flush()
                mode = "ol"
            buf.append(m.group(1))
            continue
        if mode in ("ul", "ol"):
            buf[-1] = buf[-1] + " " + line
        else:
            mode = "p"
            buf.append(line)
    flush()
    return "".join(out)


def nonempty_list(data, key):
    v = data.get(key)
    if not isinstance(v, list):
        return []
    return [x for x in v if str(x).strip()]


def chips(items):
    return "".join(f'<span class="chip">{inline(x)}</span>' for x in items)


def ul(items):
    return '<ul class="plain">' + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"


# ---------------------------------------------------------------- 图标（inline SVG，无外链）

ICON = {
    "cause": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round"><circle cx="12" cy="12" r="9"/>'
              '<circle cx="12" cy="12" r="3.5"/></svg>'),
    "action": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h13"/>'
               '<path d="M13 6l6 6-6 6"/></svg>'),
    "urgency": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round"><circle cx="12" cy="12" r="9"/>'
                '<path d="M12 7.5v5l3.5 2"/></svg>'),
    "hosp": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V8l8-5 8 5v13"/>'
             '<path d="M12 10v5"/><path d="M9.5 12.5h5"/></svg>'),
    "home": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M4 11l8-6.5 8 6.5V20H4z"/>'
             '<path d="M10 20v-5h4v5"/></svg>'),
}


# ---------------------------------------------------------------- 文档骨架

class Doc:
    """收集分区并同步生成目录锚点。"""

    def __init__(self):
        self.parts = []
        self.toc = []

    def raw(self, html_str):
        if html_str:
            self.parts.append(html_str)

    def section(self, title, inner, sid, cls="card"):
        if not inner:
            return
        self.toc.append((sid, title))
        self.parts.append(
            f'<section class="{cls}" id="{esc(sid)}"><h3>{esc(title)}</h3>{inner}</section>'
        )

    def render_toc(self):
        if len(self.toc) < 3:
            return ""
        items = "".join(
            f'<li><a href="#{esc(sid)}"><span class="toc-no">{idx:02d}</span>'
            f'<span class="toc-label">{esc(title)}</span></a></li>'
            for idx, (sid, title) in enumerate(self.toc, start=1)
        )
        return (f'<nav class="toc" id="toc" aria-label="报告目录">'
                f'<div class="toc-h"><span>目录</span><small>本次小结</small></div>'
                f'<ol>{items}</ol></nav>')

    def body(self):
        return "".join(self.parts)


def build_summary(data, u, causes, depts):
    """开头摘要：三件事一眼可见（最可能 / 去哪 / 急不急）+ 100-200 字概述。"""
    top = [strip_direction_suffix(c["name"]) for c in causes[:3] if c.get("name")]
    likely = "、".join(top) if top else "需医生进一步评估"
    if depts:
        act = depts[0]
        if len(depts) > 1:
            act += f" / {depts[1]}"
    else:
        act = u["action"]

    cells = [("cause", "最可能的原因", likely),
             ("action", "建议去哪", act),
             ("urgency", "紧急程度", u["label"])]
    strip = ""
    for icon, k, v in cells:
        # 紧急程度只在问诊摘要内突出，避免页眉、提示条、摘要三处重复。
        cls = "sm-cell sm-urgency" if icon == "urgency" else "sm-cell"
        style = (f' style="--urg-bg:{u["bg"]};--urg-border:{u["border"]};'
                 f'--urg-fg:{u["fg"]};--urg-dot:{u["dot"]}"' if icon == "urgency" else "")
        strip += (f'<div class="{cls}"{style}><div class="sm-ico">{ICON[icon]}</div>'
                  f'<div class="sm-k">{esc(k)}</div><div class="sm-v">{inline(v)}</div></div>')
    strip = f'<div class="sm-grid">{strip}</div>'

    text = str(data.get("summary") or "").strip()
    return strip + (f'<p class="sm-text">{inline(text)}</p>' if text else "")


def build_illness(data):
    """病情与病史：病情概要与病史信息并列；已知病史直接展示，仅缺失项折叠。"""
    inner = ""
    cc = str(data.get("chief_complaint_raw") or "").strip()
    if cc:
        inner += (f'<div class="cc"><div class="cc-k">您的描述</div>'
                  f'<div class="cc-v">{inline(cc)}</div></div>')

    illness = str(data.get("illness_description") or "").strip()
    if illness:
        inner += f"<h4>病情概要</h4><p>{inline(illness)}</p>"

    hist = data.get("history")
    if isinstance(hist, dict):
        filled, missing = [], []
        for key, label in HISTORY_LABELS:
            val = str(hist.get(key) or "").strip()
            if val in EMPTY_ALIASES:
                missing.append(label)
            else:
                filled.append((label, val))

        inner += "<h4>病史信息</h4>"
        if filled:
            items = "".join(
                f'<div class="hist-item"><div class="hist-label">{esc(label)}</div>'
                f'<div class="hist-value">{inline(val)}</div></div>'
                for label, val in filled
            )
            inner += f'<div class="hist-list">{items}</div>'
        if missing:
            empty_items = "".join(f"<li>{esc(label)}：{EMPTY_HISTORY}</li>" for label in missing)
            inner += (f'<details class="hist"><summary>暂无补充的病史信息'
                      f'（{len(missing)} 项）</summary><ul class="plain hist-empty">'
                      f'{empty_items}</ul></details>')
    return inner


def build_causes(data, causes):
    """可能的原因：合并原「需关注方向」与「临床分析」。每条只两栏：支持点 / 待排除项。"""
    if not causes:
        return ""
    inner = ""
    for i, c in enumerate(causes, 1):
        name = strip_direction_suffix(c.get("name"))
        sup = [x for x in (c.get("support") or []) if str(x).strip()]
        exc = [x for x in (c.get("to_exclude") or []) if str(x).strip()]
        cols = ""
        if sup:
            cols += ('<div class="cz-col"><span class="cz-h cz-sup">支持点</span>'
                     + ul(sup) + "</div>")
        if exc:
            cols += ('<div class="cz-col"><span class="cz-h cz-exc">待排除项</span>'
                     + ul(exc) + "</div>")
        wrap = f'<div class="cz-cols">{cols}</div>' if (sup and exc) else cols
        inner += (f'<div class="cz"><div class="cz-name"><span class="cz-n">{i}</span>'
                  f"{inline(name)}</div>{wrap}</div>")

    rc = data.get("recommended_checks") or []
    checks = []
    for item in rc:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            desc = str(item.get("description") or "").strip()
            value = str(item.get("value") or "").strip()
        else:
            name, desc, value = str(item or "").strip(), "", ""
        if name:
            checks.append((name, desc, value))
    if checks:
        cards = ""
        for i, (name, desc, value) in enumerate(checks, 1):
            # 兼容旧版纯字符串；新版报告应由模型补全 description / value。
            desc = desc or "由医生结合症状和查体情况判断是否需要安排。"
            value = value or "帮助进一步明确病因，并判断是否需要排除相关问题。"
            cards += (f'<div class="check"><div class="check-name"><span class="check-n">{i}</span>'
                      f'{inline(name)}</div><div class="check-row"><span>检查简介</span>'
                      f'<p>{inline(desc)}</p></div><div class="check-row check-value"><span>检查价值</span>'
                      f'<p>{inline(value)}</p></div></div>')
        inner += ("<h4>医生可能会安排的检查</h4><div class=\"checks\">" + cards +
                  '</div><p class="tip">具体检查项目由线下医生根据查体情况决定。</p>')
    return inner


def collect_plan(data, lvl):
    """归一化行动模块：按决策顺序排序、跨模块去重，并兼容旧 key/value 格式。"""
    modules = []
    for sec in (data.get("action_plan") or []):
        if not isinstance(sec, dict):
            continue
        legacy_key = str(sec.get("key") or "").strip()
        plan_type = str(sec.get("type") or "").strip() or LEGACY_PLAN_TYPES.get(legacy_key, "")
        if not plan_type:
            plan_type = "appointment"
        title = str(sec.get("title") or "").strip() or legacy_key or PLAN_TYPE_DEFAULT_TITLE.get(plan_type, "接下来可以这样做")
        raw_items = sec.get("items") if "items" in sec else sec.get("value")
        items = [str(x).strip() for x in (raw_items or []) if str(x).strip()]
        if not items or (lvl == "L1" and plan_type in L1_BANNED_PLAN_TYPES):
            continue
        modules.append({"type": plan_type, "title": title, "items": items, "extras": []})

    seen = set()
    for module in modules:
        kept = []
        for item in module["items"]:
            sig = re.sub(r"[^\u4e00-\u9fff\w]", "", item)[:22]
            if sig and sig in seen:
                continue
            seen.add(sig)
            kept.append(item)
        module["items"] = kept
    modules = [m for m in modules if m["items"]]
    modules.sort(key=lambda m: PLAN_TYPE_ORDER.index(m["type"]) if m["type"] in PLAN_TYPE_ORDER else len(PLAN_TYPE_ORDER))
    return modules


def build_plan(data, lvl, plan):
    """接下来怎么做：按当前决策顺序呈现可选行动模块，不固定分成两条线。"""
    bring = nonempty_list(data, "items_to_bring")
    ask = nonempty_list(data, "questions_for_doctor")
    obs = nonempty_list(data, "observations_to_record")
    modules = [dict(m, extras=list(m.get("extras") or [])) for m in plan]

    def get_or_create(plan_type, title):
        existing = next((m for m in modules if m["type"] == plan_type), None)
        if existing:
            return existing
        module = {"type": plan_type, "title": title, "items": [], "extras": []}
        modules.append(module)
        return module

    # 资料和就诊提问属于「准备」动作，合并到同一个行动模块，不另造一条线。
    if bring or ask:
        preparation = get_or_create("preparation", "就诊前可以准备这些")
        if bring:
            preparation["extras"].append(("建议携带", bring))
        if ask:
            preparation["extras"].append(("可以问医生", ask))
    # 观察记录属于一个完整的后续动作；L1 不提供居家观察路径。
    if obs and lvl != "L1":
        monitoring = get_or_create("monitoring", "接下来重点观察")
        monitoring["extras"].append(("观察与记录", obs))

    modules = [m for m in modules if m["items"] or m["extras"]]
    modules.sort(key=lambda m: PLAN_TYPE_ORDER.index(m["type"]) if m["type"] in PLAN_TYPE_ORDER else len(PLAN_TYPE_ORDER))

    inner = '<div class="plan-stack">'
    for n, module in enumerate(modules, 1):
        items = ul(module["items"]) if module["items"] else ""
        extras = ""
        for label, values in module["extras"]:
            extras += f'<div class="pl-extra"><h4>{esc(label)}</h4>{ul(values)}</div>'
        inner += (f'<div class="plan-module"><div class="pl-h"><span class="pl-n">{n}</span>'
                  f'{esc(module["title"])}</div>{items}{extras}</div>')
    return inner + "</div>"


def build_answers(data):
    """针对性答问：用户问“吃什么药/要不要手术/怎么办”时，先直接回答原话问题。"""
    items = [x for x in (data.get("answers") or [])
             if isinstance(x, dict) and str(x.get("q", "")).strip()
             and str(x.get("a", "")).strip()]
    if not items:
        return ""
    inner = ""
    for x in items:
        inner += (f'<div class="qa-card"><div class="qa-q">'
                  f'<span class="qa-mark">问</span>{inline(x["q"])}</div>'
                  f'<div class="qa-a">{blocks(x["a"])}</div></div>')
    return inner


def ref_domain_ok(url):
    try:
        host = (urlparse(str(url)).hostname or "").lower()
    except ValueError:
        return False
    if not host:
        return False
    return any(host == d or host.endswith("." + d) for d in ALLOWED_REF_DOMAINS)


def build_references(data):
    refs = data.get("references")
    if not isinstance(refs, list):
        return "", []
    kept, dropped = [], []
    for r in refs:
        if not isinstance(r, dict):
            continue
        title = str(r.get("title") or "").strip()
        url = str(r.get("url") or "").strip()
        if not title or not url:
            dropped.append(title or url or "(空条目)")
            continue
        if not url.lower().startswith(("http://", "https://")) or not ref_domain_ok(url):
            dropped.append(f"{title} <{url}>")
            continue
        kept.append((title, str(r.get("source") or "").strip(),
                     url, str(r.get("note") or "").strip()))
    if not kept:
        return "", dropped
    kept = kept[:MAX_REFS]
    items = ""
    for title, source, url, note in kept:
        src = f'<span class="src">{esc(source)}</span>' if source else ""
        nt = f'<p class="rnote">{inline(note)}</p>' if note else ""
        items += (f'<li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">'
                  f"{inline(title)}</a>{src}{nt}</li>")
    return f'<p class="rnotice">{esc(REF_NOTICE)}</p><ol class="refs">{items}</ol>', dropped


def build_log(data):
    log = data.get("inquiry_log")
    if not isinstance(log, list) or not log:
        return ""
    turns = []
    for entry in log:
        if not isinstance(entry, dict):
            continue
        qa = [x for x in (entry.get("qa") or [])
              if isinstance(x, dict) and str(x.get("q", "")).strip()]
        if not qa and not str(entry.get("note", "")).strip():
            continue
        note = str(entry.get("note") or "").strip()
        note_html = f'<p class="note">{inline(note)}</p>' if note else ""
        items = "".join(
            f'<div class="qa"><div class="q">{inline(x.get("q"))}</div>'
            f'<div class="a">{inline(x.get("a") or "未作答")}</div></div>'
            for x in qa
        )
        turns.append(
            f'<div class="turn"><div class="turn-h">第 {esc(entry.get("turn", "?"))} 轮</div>'
            f"{note_html}{items}</div>"
        )
    if not turns:
        return ""
    return ('<details class="log"><summary>展开查看本次问诊的完整问答记录'
            f"（共 {len(turns)} 轮）</summary>" + "".join(turns) + "</details>")


# ---------------------------------------------------------------- 质检门禁

DOSAGE_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:mg|毫克|g|克|ml|毫升|片|粒|袋|支|滴|IU|万单位)")
ABSOLUTE_RE = re.compile(r"确诊为|诊断为|你得的是|必然是|肯定是|就是[\u4e00-\u9fff]{1,6}病")
EMPTY_COMFORT_RE = re.compile(r"不用担心|不必担心|放心吧|别担心|完全没事|肯定没事|不用紧张")
THRESHOLD_RE = re.compile(r"\d|突然|持续|无法|不能|超过|以上|剧烈|大量|反复|新出现")
NEGATIVE_RE = re.compile(r"否认|无[\u4e00-\u9fff]|没有|未见|未出现|阴性|不伴")
# 空泛红旗：整条只有这类词就不算「可执行」
VAGUE_WARN_RE = re.compile(r"(?:症状)?(?:明显)?(?:加重|恶化|不适|不舒服|变严重|加剧)(?:时)?")
PROMO_RE = re.compile(r"挂号链接|预约挂号|点击(?:购买|下单|咨询|领取)|扫码|加微信|优惠")


def collect_safety_texts(data, causes):
    """收集模型生成、会展示给用户的建议性文本，供安全质检统一扫描。

    不扫描用户原话、问答记录和既往用药史，避免把用户自述的剂量误判为模型开方；
    其余模型生成且会进入报告的字段必须覆盖新版与旧版结构。
    """
    texts = [str(data.get(k) or "") for k in ("summary", "illness_description")]

    for answer in (data.get("answers") or []):
        if isinstance(answer, dict):
            texts.append(str(answer.get("a") or ""))

    for cause in causes:
        if isinstance(cause, dict):
            texts.append(str(cause.get("name") or ""))
            texts.extend(str(x) for x in (cause.get("support") or []))
            texts.extend(str(x) for x in (cause.get("to_exclude") or []))

    for check in (data.get("recommended_checks") or []):
        if isinstance(check, dict):
            texts.extend(str(check.get(k) or "") for k in ("name", "description", "value"))
        else:  # 兼容旧版仅写检查名称的列表
            texts.append(str(check))

    for sec in (data.get("action_plan") or []):
        if isinstance(sec, dict):
            texts.append(str(sec.get("title") or ""))
            texts.extend(str(x) for x in (sec.get("items") or []))
            texts.extend(str(x) for x in (sec.get("value") or []))  # 兼容旧格式

    for key in ("warning_signs", "items_to_bring", "questions_for_doctor", "observations_to_record"):
        texts.extend(str(x) for x in nonempty_list(data, key))
    return texts


def qc(data, doc_html, causes, depts, lvl, plan):
    """机械化质检：必须有 4 项 / 必须无 5 项。"""
    must_have = []
    ill = str(data.get("illness_description") or "").strip()
    must_have.append(("病情概要（含关键阴性信息）",
                      bool(ill) and bool(NEGATIVE_RE.search(ill)),
                      "illness_description 需含否认/没有/未见等关键阴性信息"))
    must_have.append(("明确行动指令（去哪 + 什么时候）",
                      bool(depts) and lvl in ("L1", "L2", "L3", "L4"),
                      "recommended_departments 不能为空，且必须定级 L1-L4"))
    warn = nonempty_list(data, "warning_signs")
    # 「可执行」= 每条都是具体症状（不能只写“加重/不舒服”），且至少半数带明确阈值
    concrete = [w for w in warn
                if len(re.sub(r"[^\u4e00-\u9fff\w]", "", w)) >= 6
                and not VAGUE_WARN_RE.fullmatch(re.sub(r"[^\u4e00-\u9fff]", "", w))]
    with_thr = [w for w in warn if THRESHOLD_RE.search(w)]
    must_have.append(("可执行红旗触发条件（带症状或阈值）",
                      len(warn) >= 2 and len(concrete) == len(warn)
                      and len(with_thr) * 2 >= len(warn),
                      "warning_signs 至少 2 条；每条须写具体症状（不能只写“加重”），"
                      "且至少半数带阈值（数值/突然/持续/无法/剧烈等）"))
    must_have.append(("行动计划", len(plan) >= 1,
                      "action_plan 至少 1 个分组且含具体动作"))

    joined = "\n".join(collect_safety_texts(data, causes))

    must_not = []
    m = DOSAGE_RE.search(joined)
    if m and str(data.get("answer_mode")) != "diagnosed":
        must_not.append(("未确诊即给具体药名 + 剂量", f"命中 {m.group(0)!r}"))
    m = ABSOLUTE_RE.search(joined)
    if m:
        must_not.append(("绝对化诊断表述", f"命中 {m.group(0)!r}"))
    for url in re.findall(r'href="(https?://[^"]+)"', doc_html):
        if not ref_domain_ok(url):
            must_not.append(("商业外链或导流链接", url))
            break
    m = PROMO_RE.search(joined)
    if m:
        must_not.append(("导流或商业引导措辞", f"命中 {m.group(0)!r}"))
    disc = str(data.get("disclaimer") or DEFAULT_DISCLAIMER).strip()
    core = disc[:16]
    if core and doc_html.count(core) > 1:
        must_not.append(("重复出现的免责声明",
                         f"“{core}…” 出现 {doc_html.count(core)} 次，应仅在页脚一次"))
    m = EMPTY_COMFORT_RE.search(joined)
    if m:
        must_not.append(("空洞安抚代替实际建议", f"命中 {m.group(0)!r}"))
    return must_have, must_not


# ---------------------------------------------------------------- CSS

CSS = """
:root{--blue:#0052D9;--blue-d:#0B357A;--blue-l:#F2F6FE;--blue-b:#D5E2FA;
--ink:#1A2233;--ink2:#4A5568;--ink3:#8B93A6;--line:#E5E9F2;--bg:#F5F7FB;--card:#FFF;
--grn:#1D7D53;--grn-l:#E8F8F2;--grn-b:#BCEBDC;--amb:#8E6800;--amb-l:#FFF8E6;--amb-b:#FFE9A6;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
background:var(--bg);color:var(--ink);line-height:1.75;font-size:15px;
padding:32px 16px;-webkit-font-smoothing:antialiased}
.wrap{max-width:1020px;margin:0 auto}
header{color:var(--ink);border:1px solid #DCE6F6;border-bottom:none;border-radius:16px 16px 0 0;
padding:26px 34px;background:linear-gradient(120deg,#FFF 0%,#F4F8FF 100%)}
.hd-lockup{display:flex;align-items:center;gap:14px}
.hd-mark{width:40px;height:40px;flex:0 0 40px;border-radius:11px;background:var(--blue);color:#FFF;
box-shadow:0 5px 12px rgba(0,82,217,.18);font-size:25px;font-weight:300;line-height:38px;text-align:center}
.hd-copy{min-width:0}
.hd-brand{font-size:12px;font-weight:600;letter-spacing:.08em;color:var(--blue-d);line-height:1.3}
header h1{font-size:27px;font-weight:650;margin:3px 0 0;letter-spacing:0;color:var(--ink)}
.hd-context{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:8px;font-size:13px;line-height:1.45}
.hd-complaint{font-weight:500;color:var(--ink2)}
.hd-person{padding-left:10px;border-left:1px solid #C9D5E8;color:var(--ink3)}
.hd-note{margin-left:auto;font-size:12px;color:var(--ink3);white-space:nowrap;padding-left:16px}
main{background:var(--card);border:1px solid var(--line);border-top:none;
border-radius:0 0 16px 16px;padding:8px 30px 30px;box-shadow:0 1px 3px rgba(16,24,40,.05)}
.layout{display:grid;grid-template-columns:196px minmax(0,1fr);gap:30px;align-items:start}
.side{position:sticky;top:20px;padding-top:22px}
.content{min-width:0}
.card{padding:22px 0;border-bottom:1px solid var(--line)}
.card:last-of-type{border-bottom:none;padding-bottom:8px}
h3{font-size:16px;font-weight:600;color:var(--blue-d);margin-bottom:12px;
padding-left:11px;border-left:3px solid var(--blue)}
h4{font-size:14.5px;font-weight:600;color:var(--ink);margin:16px 0 6px}
p{margin:8px 0;color:var(--ink2)}
strong{color:var(--ink);font-weight:600}
code{background:var(--blue-l);border-radius:4px;padding:1px 5px;font-size:13px}
ul,ol{margin:8px 0 8px 20px;color:var(--ink2)}
li{margin:5px 0}
ul.plain{list-style:none;margin:6px 0 0}
ul.plain li{position:relative;padding-left:17px}
ul.plain li:before{content:"";position:absolute;left:2px;top:.72em;width:5px;height:5px;
border-radius:50%;background:var(--blue);opacity:.5}
p.tip{font-size:13px;color:var(--ink3);margin-top:7px}
.toc{position:relative;border:1px solid var(--line);border-radius:12px;padding:13px 11px 10px;background:#FBFCFE}
.toc:before{content:"";position:absolute;left:24px;top:50px;bottom:18px;width:1px;background:#DDE6F4}
.toc-h{display:flex;align-items:baseline;justify-content:space-between;padding:0 7px 9px;
font-size:12px;font-weight:650;color:var(--ink2);letter-spacing:.08em;border-bottom:1px solid var(--line)}
.toc-h small{font-size:10.5px;font-weight:500;color:var(--ink3);letter-spacing:0}
.toc ol{margin:7px 0 0;list-style:none;font-size:13px}
.toc li{position:relative;margin:0}
.toc a{position:relative;z-index:1;display:flex;align-items:center;gap:9px;padding:7px 7px;color:var(--ink2);
text-decoration:none;line-height:1.35;border-radius:7px;transition:background .15s,color .15s}
.toc-no{display:inline-flex;align-items:center;justify-content:center;flex:0 0 22px;width:22px;height:22px;
border:1px solid #D8E2F1;border-radius:50%;background:#FFF;color:var(--blue-d);font-size:10px;font-weight:650;line-height:1}
.toc-label{min-width:0}
.toc a:hover{color:var(--blue-d);background:var(--blue-l)}
.toc a:hover .toc-no{color:#FFF;background:var(--blue);border-color:var(--blue)}
.toc a:active{color:var(--blue-d);background:#EAF1FD}
.sm-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sm-cell{background:var(--blue-l);border:1px solid var(--blue-b);border-radius:10px;
padding:13px 15px}
.sm-cell.sm-urgency{background:var(--urg-bg,var(--amb-l));border-color:var(--urg-border,var(--amb-b))}
.sm-ico{width:19px;height:19px;color:var(--blue);margin-bottom:6px}
.sm-cell.sm-urgency .sm-ico{color:var(--urg-fg,var(--amb))}
.sm-ico svg{width:100%;height:100%;display:block}
.sm-k{font-size:11.5px;color:var(--ink3);letter-spacing:.04em;margin-bottom:2px}
.sm-v{font-size:15px;font-weight:600;color:var(--blue-d);line-height:1.45}
.sm-cell.sm-urgency .sm-v{color:var(--urg-fg,var(--amb))}
.sm-text{margin-top:13px;font-size:15px;color:var(--ink2)}
.cc{border-left:3px solid var(--blue-b);background:#FAFBFD;border-radius:0 8px 8px 0;
padding:10px 15px;margin-bottom:4px}
.cc-k{font-size:11.5px;color:var(--ink3);letter-spacing:.04em}
.cc-v{font-size:15px;color:var(--ink);margin-top:2px}
.hist-list{margin-top:2px;border-top:1px solid var(--line)}
.hist-item{display:grid;grid-template-columns:86px minmax(0,1fr);gap:14px;padding:10px 2px;border-bottom:1px solid var(--line)}
.hist-label{font-size:13px;font-weight:500;color:var(--ink3)}
.hist-value{font-size:14.5px;color:var(--ink2);line-height:1.65}
details.hist{margin-top:11px;border:1px dashed #D7E0EE;border-radius:9px;background:#FAFBFD}
details.hist summary{cursor:pointer;padding:9px 13px;font-size:13px;font-weight:500;color:var(--ink3)}
details.hist .hist-empty{margin:0 13px 11px;font-size:13px;color:var(--ink3)}
details.hist .hist-empty li{margin:4px 0}
table.kv{border-collapse:collapse;font-size:14px}
table.kv th{width:82px;text-align:left;font-weight:500;color:var(--ink3);
padding:7px 12px 7px 0;vertical-align:top;white-space:nowrap}
table.kv td{padding:7px 0;color:var(--ink2);border-bottom:1px solid var(--line)}
table.kv tr:last-child td{border-bottom:none}
table.kv td.muted{color:var(--ink3)}
.cz{border:1px solid var(--line);border-radius:10px;padding:14px 17px;margin:11px 0}
.cz-name{font-size:15.5px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:9px}
.cz-n{flex:0 0 21px;height:21px;border-radius:50%;background:var(--blue);color:#fff;
font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center}
.cz-cols{display:grid;grid-template-columns:1fr;gap:13px;margin-top:11px}
.cz-col+.cz-col{padding-top:13px;border-top:1px dashed var(--line)}
.cz-h{font-size:11.5px;font-weight:600;letter-spacing:.05em;padding:2px 9px;
border-radius:11px;display:inline-block}
.cz-sup{color:var(--grn);background:var(--grn-l);border:1px solid var(--grn-b)}
.cz-exc{color:var(--amb);background:var(--amb-l);border:1px solid var(--amb-b)}
.cz-col ul.plain li:before{background:var(--ink3);opacity:.45}
.checks{margin-top:10px}
.check{border:1px solid var(--line);border-radius:9px;background:#FCFDFE;padding:13px 15px;margin:9px 0}
.check-name{display:flex;align-items:center;gap:8px;font-size:14.5px;font-weight:600;color:var(--ink)}
.check-n{display:inline-flex;align-items:center;justify-content:center;flex:0 0 19px;width:19px;height:19px;
border-radius:50%;background:var(--blue-l);border:1px solid var(--blue-b);color:var(--blue-d);font-size:10.5px;font-weight:650}
.check-row{display:grid;grid-template-columns:62px minmax(0,1fr);gap:9px;margin-top:8px;font-size:13.5px;line-height:1.6}
.check-row>span{font-size:11.5px;color:var(--ink3);padding-top:2px}
.check-row p{margin:0;font-size:13.5px;color:var(--ink2)}
.check-value{padding-top:8px;border-top:1px dashed var(--line)}
.check-value>span{color:var(--blue-d)}
.chip{display:inline-block;background:var(--blue-l);border:1px solid var(--blue-b);
color:var(--blue-d);border-radius:16px;padding:4px 13px;font-size:13.5px;margin:0 7px 7px 0}
.plan-stack{border-top:1px solid var(--line)}
.plan-module{position:relative;padding:15px 2px 14px 34px;border-bottom:1px solid var(--line)}
.plan-module:last-child{border-bottom:none}
.plan-module:before{content:"";position:absolute;left:10px;top:0;bottom:0;width:1px;background:#DDE6F4}
.plan-module:first-child:before{top:27px}
.plan-module:last-child:before{bottom:calc(100% - 27px)}
.qa-card{border:1px solid var(--blue-b);background:var(--blue-l);border-radius:11px;
padding:15px 18px;margin:11px 0}
.qa-q{display:flex;align-items:flex-start;gap:9px;font-size:15.5px;font-weight:600;
color:var(--blue-d);line-height:1.5}
.qa-mark{flex:0 0 21px;height:21px;margin-top:2px;border-radius:6px;background:var(--blue);
color:#fff;font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center}
.qa-a{margin-top:9px;padding-left:30px}
.qa-a p{margin:6px 0;color:var(--ink2)}
.qa-a p:first-child{margin-top:0}
.qa-a ul,.qa-a ol{margin:7px 0 7px 19px}
.pl-h{position:relative;font-size:15px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:9px;line-height:1.45}
.pl-n{position:absolute;right:100%;margin-right:13px;z-index:1;flex:0 0 21px;width:21px;height:21px;border-radius:50%;background:#FFF;
border:1px solid var(--blue-b);color:var(--blue-d);font-size:10.5px;font-weight:650;
display:flex;align-items:center;justify-content:center}
.plan-module>ul{margin-top:7px;margin-bottom:0}
.pl-extra{margin-top:12px;padding-top:10px;border-top:1px dashed var(--line)}
.pl-extra h4{margin:0 0 4px;font-size:13.5px;color:var(--ink2)}
.pl-extra ul{margin-bottom:0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:14px}
.grid>div>h4{margin-top:0}
.warn{background:#FFF7F5;border:1px solid #FBD4CE;border-radius:10px;padding:15px 18px}
.warn h3{color:#AD352F;border-left-color:#D54941;margin-bottom:9px}
.warn ul.plain li:before{background:#D54941;opacity:.75}
.warn ul.plain li{color:#7A2A25}
.soft{background:var(--amb-l);border:1px solid var(--amb-b);border-radius:10px;padding:15px 18px}
.soft h3{color:var(--amb);border-left-color:#D29C08;margin-bottom:9px}
.soft ul.plain li:before{background:#D29C08;opacity:.8}
.soft ul.plain li{color:#6B5000}
.refbox p.rnotice{font-size:12.5px;color:var(--ink3);background:#FAFBFD;
border:1px dashed var(--line);border-radius:7px;padding:9px 13px;margin:0 0 13px}
ol.refs{margin:0 0 0 19px;font-size:14px}
ol.refs li{margin:11px 0;color:var(--ink2)}
ol.refs a{color:var(--blue);text-decoration:none;font-weight:500;border-bottom:1px solid var(--blue-b)}
ol.refs .src{display:inline-block;margin-left:8px;font-size:11.5px;color:var(--blue-d);
background:var(--blue-l);border:1px solid var(--blue-b);border-radius:11px;padding:1px 9px;
vertical-align:1px;white-space:nowrap}
ol.refs p.rnote{margin:4px 0 0;font-size:13px;color:var(--ink3);line-height:1.6}
.log{margin-top:22px;border:1px solid var(--line);border-radius:10px;background:#FAFBFD}
.log summary{cursor:pointer;padding:13px 18px;font-size:14px;font-weight:500;color:var(--blue-d)}
.turn{padding:2px 18px 14px}
.turn-h{font-size:12.5px;font-weight:600;color:var(--ink3);letter-spacing:.05em;margin:8px 0 7px}
.turn .note{font-size:13.5px;color:var(--ink3);font-style:italic;margin:0 0 9px}
.qa{border-left:2px solid var(--blue-b);padding:2px 0 2px 13px;margin:9px 0}
.qa .q{font-size:13.5px;color:var(--ink2)}
.qa .a{font-size:14px;color:var(--blue-d);font-weight:500;margin-top:2px}
footer{margin-top:20px;padding:15px 18px;background:var(--blue-l);
border:1px solid var(--blue-b);border-radius:10px;font-size:13px;color:var(--ink2)}
footer .gen{margin-top:7px;font-size:12px;color:var(--ink3)}
@media(max-width:980px){
.layout{grid-template-columns:1fr;gap:0}
.side{position:static;padding-top:18px}
.toc{padding:13px 15px 12px}
.toc:before{display:none}
.toc ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:2px 12px}
.toc a{padding:7px 6px}}
@media(max-width:640px){body{padding:14px 10px}
header{padding:20px 19px 22px}header h1{font-size:23px}.hd-mark{width:36px;height:36px;flex-basis:36px;line-height:34px;font-size:22px}.hd-note{display:none}
main{padding-left:19px;padding-right:19px}
.grid,.cz-cols,.sm-grid{grid-template-columns:1fr;gap:12px}
.hist-item,.check-row{grid-template-columns:1fr;gap:2px;padding:9px 0}
.check-row>span{padding-top:0}.check-value{padding-top:9px}
.toc ol{grid-template-columns:1fr}.qa-a{padding-left:0}}
@media print{body{background:#fff;padding:0}main{border:none;box-shadow:none}
.log,.side{display:none}details.hist{border:none}
.layout{grid-template-columns:1fr}.hd-deco{display:none}}
"""

# ---------------------------------------------------------------- 主渲染


def normalize_causes(data):
    """读 causes；兼容旧版 differential_directions（只有名称、无两栏）。"""
    out = []
    raw = data.get("causes")
    if isinstance(raw, list):
        for c in raw:
            if isinstance(c, dict) and str(c.get("name") or "").strip():
                out.append(c)
    if out:
        return out
    return [{"name": n, "support": [], "to_exclude": []}
            for n in nonempty_list(data, "differential_directions")]


def render(data):
    lvl = str(data.get("medical_urgency_level") or "").strip().upper()
    if lvl not in URGENCY:
        lvl = ""
    u = URGENCY[lvl]

    meta = data.get("meta") or {}
    demo = data.get("demographics") or {}
    product = str(meta.get("product") or HEADER_BRAND)
    # 历史输入中可能遗留旧标题；所有用户侧与文件侧标题统一为当前产品名。
    title = REPORT_TITLE
    cc = str(meta.get("chief_complaint_short") or data.get("chief_complaint_raw") or "").strip()
    if len(cc) > 24:
        cc = cc[:24].rstrip() + "…"
    sex = str(demo.get("sex") or "").strip()
    age = str(demo.get("age") or "").strip()
    person = " · ".join(x for x in (sex, f"{age}岁" if age.isdigit() else age) if x)

    # 页眉承载报告身份与必要的本次信息；不展示就医紧迫性，避免与摘要重复。
    # 页眉品牌固定为当前产品名，避免历史输入遗留旧品牌文案。
    brand = HEADER_BRAND
    context = ""
    if cc or person:
        context = '<div class="hd-context">' + (
            f'<span class="hd-complaint">{esc(cc)}</span>' if cc else ""
        ) + (f'<span class="hd-person">{esc(person)}</span>' if person else "") + '</div>'
    head = (f'<header><div class="hd-lockup"><div class="hd-mark" aria-hidden="true">+</div>'
            f'<div class="hd-copy"><div class="hd-brand">{esc(brand)}</div>'
            f'<h1>{esc(title)}</h1>{context}</div>'
            f'<div class="hd-note">本次问诊整理</div></div></header>')

    causes = normalize_causes(data)
    depts = nonempty_list(data, "recommended_departments")[:2]
    plan = collect_plan(data, lvl)

    doc = Doc()
    doc.section("问诊摘要", build_summary(data, u, causes, depts), "sec-summary")
    doc.section("先回答你的问题", build_answers(data), "sec-answers")
    doc.section("病情与病史", build_illness(data), "sec-illness")
    doc.section("可能的原因", build_causes(data, causes), "sec-causes")
    doc.section("接下来怎么做", build_plan(data, lvl, plan), "sec-plan")

    # 兼容旧版 narrative（新结构下通常不写）
    for item in (data.get("narrative") or []):
        if isinstance(item, dict) and str(item.get("body", "")).strip():
            h = str(item.get("heading") or "补充说明").strip()
            doc.section(h, blocks(item.get("body")), "sec-n-" + re.sub(r"\W+", "", h)[:12])

    warn = nonempty_list(data, "warning_signs")
    if warn:
        wt = ("出现以下情况请立即拨打 120 或直奔急诊" if lvl == "L1"
              else "出现以下情况请尽快就医")
        cls = "card warn" if lvl in ("L1", "L2") else "card soft"
        doc.section(wt, ul(warn), "sec-warn", cls=cls)

    refbox, dropped = build_references(data)
    if refbox:
        doc.section("参考资料", refbox, "sec-refs", cls="card refbox")

    disc = str(data.get("disclaimer") or DEFAULT_DISCLAIMER).strip() or DEFAULT_DISCLAIMER
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    foot = (f"<footer>{inline(disc)}"
            f'<div class="gen">本报告由 {esc(product)} 依据本次对话内容自动生成 · {esc(now)}</div></footer>')

    t = f"{title} · {cc}" if cc else title
    toc = doc.render_toc()
    content = f'<div class="content">{doc.body()}{build_log(data)}</div>'
    shell = (f'<div class="layout"><aside class="side">{toc}</aside>{content}</div>'
             if toc else content)
    out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
           f"<title>{esc(t)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
           f'<div class="wrap">{head}<main>{shell}</main>{foot}</div>\n</body>\n</html>\n')
    return out, dropped, causes, depts, lvl, plan


def main():
    ap = argparse.ArgumentParser(description="渲染 AI 诊室小结 HTML 报告")
    ap.add_argument("report", nargs="?", help="report.json 路径")
    ap.add_argument("-o", "--output", help="输出 HTML 路径")
    ap.add_argument("--print-schema", action="store_true", help="打印 JSON 字段模板")
    ap.add_argument("--no-qc", action="store_true", help="跳过质检（不推荐）")
    args = ap.parse_args()

    if args.print_schema:
        print(json.dumps(SCHEMA, ensure_ascii=False, indent=2))
        return 0
    if not args.report:
        ap.error("需要提供 report.json 路径，或使用 --print-schema")

    src = Path(args.report)
    if not src.is_file():
        print(f"[错误] 找不到文件: {src}", file=sys.stderr)
        return 1
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[错误] JSON 解析失败: {e}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("[错误] report.json 顶层必须是对象", file=sys.stderr)
        return 1

    if args.output:
        out = Path(args.output)
    else:
        cc = re.sub(r"[^\w\u4e00-\u9fff]+", "",
                    str((data.get("meta") or {}).get("chief_complaint_short") or "")) or "问诊"
        out = src.parent / f"症状自查小结_{cc}_{_dt.datetime.now():%Y%m%d-%H%M}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc, dropped, causes, depts, lvl, plan = render(data)
    out.write_text(doc, encoding="utf-8")

    print(f"[完成] {out}")
    print(f"       {URGENCY[lvl]['label']} · 科室 {'/'.join(depts) or '未给出'}"
          f" · 可能原因 {len(causes)} 条 · 输入行动模块 {len(plan)} 个")
    nrefs = doc.count('<li><a href="http')
    if nrefs:
        print(f"       参考资料 {nrefs} 条")
    if dropped:
        print(f"[警告] {len(dropped)} 条参考资料被丢弃（不在白名单域名内或缺 URL）:",
              file=sys.stderr)
        for d in dropped:
            print(f"       - {d}", file=sys.stderr)

    if args.no_qc:
        return 0
    must_have, must_not = qc(data, doc, causes, depts, lvl, plan)
    bad = [x for x in must_have if not x[1]]
    print("\n--- 质检 ---")
    for name, ok_, hint in must_have:
        print(f"  {'✓' if ok_ else '✗'} 必须有：{name}" + ("" if ok_ else f"  → {hint}"))
    if must_not:
        for name, detail in must_not:
            print(f"  ✗ 必须无：{name}  → {detail}")
    else:
        print("  ✓ 必须无：5 项均未触发")
    if bad or must_not:
        print("\n[质检未通过] HTML 已生成，但请修正上述问题后重新渲染。", file=sys.stderr)
        return 3
    print("  通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
