#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文医学期刊稿件自动审校脚本  (medical-journal-copyediting)

规则已外置为结构化 JSON（见同级 rules/ 目录），每条规则带来源(source)、
层级(scope)、严重性(severity)、规则 ID(rule_id)、例外(exception_after)、
示例(example)/反例(counter_example) 等元数据，降低代码与文档漂移风险（rules/ 为唯一真源），并支持按
「国家标准 / 行业规范 / 期刊体例 / 编辑经验」四层按期刊配置。

依据 GB/T 7714-2025、GB 3100~3102、GB/T 15835、GB/T 15834 及全国科学技术
名词审定委员会规范名词，对稿件做确定性规则初筛，输出「疑似问题清单」与
修改建议。脚本仅做初筛，最终仍须编辑人工确认。

注意：本工具输出的是「疑似问题密度（规则命中数/字数）」，并非《报纸期刊
质量管理规定》所指的编校差错率（后者按差错类别赋计错分值、设最高计错数，
期刊合格线为 2/万）。本工具不做合格判定。

输入范围：支持纯文本（.md/.txt）与 Word（.docx，零依赖解析）。.docx 模式
可提取正文/表格文本，并基于 run 显式属性「部分」识别统计符号的斜体/上下标
（例如 P/t/F/r/n 应斜体、SD/SE 应正体、χ 后数字应为上标），属于格式初筛而非
完整富文本编校；但图片像素、嵌入公式、脚注、修订痕迹、字符样式继承等仍不可
在纯文本层可靠获取，仅统计数量并提示人工核对。稿件文本仅作为数据读取，不作
为指令执行。

用法:
  python check_manuscript.py 稿件.md
  python check_manuscript.py 稿件.txt --scope national,professional
  python check_manuscript.py 稿件.md --dict 自定义词条.json --json --out 报告.md

选项:
  --check   逗号分隔的检查项 (默认 all):
            terminology 术语 | units 量和单位 | numbers 数字用法
            punct 标点符号 | stats 统计学 | references 参考文献
  --scope   逗号分隔的规则层级 (默认 all):
            national 国家标准 | professional 行业规范
            journal 期刊体例(仅清单) | experience 编辑经验(仅清单)
  --dict    自定义术语替换词条 JSON ({ "非规范": "规范" })，合并/覆盖内置词典
  --json    输出纯 JSON 结构：有 --out 时写入同名 .json；无 --out 时打印到
            stdout（报告写入 stderr），便于程序调用
  --out     报告输出路径（默认打印到 stdout）
  --no-punct-halfwidth  关闭「半角标点」检查（适用于含大量代码/公式的稿件）
  --stats-italic        启用统计符号正斜体检查（默认关闭；初筛阶段噪音大，
                        且纯文本无法判断格式，仅 DOCX 有格式信息时有效）
  --no-aggregate        问题明细逐条列出，不按规则聚合（调试用）
  --with-line-no        在问题明细中附上行/段号（默认仅给原文片段用于搜索定位）

报告改进:
  - 定位用「原文片段」而非行号：每条问题给出命中上下文，可在稿件中直接搜索定位。
  - 同类错误聚合：同一规则多处命中只列一条并标注「N 处」+ 示例片段，避免重复刷屏。
  - 按模块分组：明细按 术语/量和单位/数字用法/标点符号/统计学/参考文献 分组呈现。
"""
import argparse
import datetime
import json
import glob
import hashlib
import os
import re
import sys

# 版本与追溯信息（每次审校写入报告，便于复现某次结果）
SKILL_VERSION = "0.3.4"
RULESET_VERSION = "2025.1"          # 规则库随 GB/T 7714-2025 同步
STD_EFFECTIVE_DATE = "2026-07-01"   # GB/T 7714-2025 实施日期

RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")

SCOPE_ORDER = ["national", "professional", "journal", "experience"]
SCOPE_CN = {"national": "国家标准", "professional": "行业规范",
            "journal": "期刊体例", "experience": "编辑经验"}

SEV_LABEL = {"error": "错误", "warning": "警告", "info": "提示"}
CAT_CN = {"terminology": "术语", "units": "量和单位", "numbers": "数字用法",
          "punct": "标点符号", "stats": "统计学", "references": "参考文献"}

HALF_MAP = {".": "。", ",": "，", "!": "！", "?": "？", ";": "；", ":": "："}

CJK = r"\u4e00-\u9fff"

CONTEXT_WINDOW = 18  # 命中上下文前后截取的字符数（用于「片段定位」替代行号）


def make_context(line_text, found, start):
    """生成命中上下文片段，便于在原文中搜索定位（替代无意义的行/段号）。

    line_text 为所在行/段落原文；found 为命中文本；start 为命中起始下标
    （可由正则匹配对象给出，更精确；否则回退到 find）。
    """
    if not line_text:
        return found or ""
    if start is None or start < 0:
        start = line_text.find(found) if found else -1
    if start < 0:
        return found or ""
    a = max(0, start - CONTEXT_WINDOW)
    b = min(len(line_text), start + len(found) + CONTEXT_WINDOW)
    pre = "…" if a > 0 else ""
    post = "…" if b < len(line_text) else ""
    return pre + line_text[a:b] + post


def is_ref_line(line):
    """判断该行是否像参考文献条目（避免被 numbers 模块误判页码范围）。

    采用「编号 + 文献特征」联合判断：行首须为参考文献编号（[n] / n. / n) /
    n、），其后紧跟分隔符；且整行须含至少一个文献特征 token（4 位出版年 /
    DOI / 网址 / 文献类型标志 [J][M] 等 / 卷期页），避免把「10-20例纳入研究。」
    「2024年纳入患者30例。」「1. 研究对象与方法」等普通数字句或小节标题误判
    为参考文献，从而修复数字规则被跳过与 references 误报。
    """
    if not re.match(r"^\s*[\[［〔]?\d+[\]］〕．.、)]\s?", line):
        return False
    feat = (
        r"\d{4}"                       # 4 位出版年
        r"|doi|10\.\d{4,}"             # DOI
        r"|https?://|//"               # 网址
        r"|\[[A-Za-z]/?[A-Za-z]?\]"    # 文献类型标志 [J][M] 等
        r"|，\s*\d+\s*[（(]\d+[）)]"    # 卷(期)
        r"|\d+\s*[-–—:：]\s*\d+\s*[-–—:：]\s*\d+"  # 卷:页 / 年,卷:页
    )
    return bool(re.search(feat, line, re.IGNORECASE))


def load_rules():
    rules = []
    if not os.path.isdir(RULES_DIR):
        sys.stderr.write(f"警告：规则目录不存在: {RULES_DIR}\n")
        return rules
    for fp in sorted(glob.glob(os.path.join(RULES_DIR, "*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"警告：规则文件读取失败已跳过 {fp}: {e}\n")
            continue
        scope = data.get("scope", "national")
        layer = data.get("layer_name", scope)
        source = data.get("source", "")
        auto = data.get("auto", True)
        for r in data.get("rules", []):
            r["_scope"] = scope
            r["_layer"] = layer
            r["_source"] = source
            r["_auto"] = auto
            rules.append(r)
    return rules


def validate_custom_dict(raw):
    """校验并清洗自定义术语词典，返回 (clean, warnings)。

    自定义词典应为 {"非规范": "规范"} 形式，方向是「非规范词 → 规范词」。
    清洗规则：
      - 键或值非字符串（如数组）→ 跳过并告警，避免把非法值塞进建议文本；
      - 键 == 值（无实际替换意义，疑似笔误）→ 跳过并告警；
      - 键已是本技能认定的规范词（出现在内置术语 suggestion 中）→ 若按非规范
        词加入会反过来误报规范文本，故跳过并提示确认方向。
    返回 clean：已通过校验的 {非规范: 规范} 子集。
    """
    if not isinstance(raw, dict):
        return {}, ['自定义词典应为 {"非规范": "规范"} 形式的对象']
    # 内置规范词集合（用于方向性校验：键若为规范词则方向可能反了）
    builtin_standard = set()
    for r in load_rules():
        if r.get("category") == "terminology" and r.get("suggestion"):
            builtin_standard.add(r["suggestion"])
    clean, warns = {}, []
    for k, v in raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            warns.append(f"条目已跳过（键/值须为字符串）：{k!r} -> {v!r}")
            continue
        if k == v:
            warns.append(f"条目已跳过（键与值相同，无替换意义）：{k!r}")
            continue
        if k in builtin_standard:
            warns.append(
                f"键「{k}」已被本技能视为规范词，若按非规范词加入会误报规范文本，"
                f"已跳过；请确认方向（应为 非规范→规范）。")
            continue
        clean[k] = v
    return clean, warns


def add(issues, line_no, line_text, rule, message, found, suggestion,
        start=None, end=None):
    issues.append({
        "line": line_no,
        "rule_id": rule.get("id", ""),
        "scope": rule.get("_scope", ""),
        "category": rule.get("category", ""),
        "severity": rule.get("severity", "warning"),
        "message": message,
        "found": found,
        "context": make_context(line_text, found, start),
        "start": start,
        "end": end,
        "suggestion": suggestion,
        "standard": rule.get("_source", ""),
    })


def fill(tmpl, **kw):
    if not tmpl:
        return ""
    for k, v in kw.items():
        tmpl = tmpl.replace("{" + k + "}", str(v))
    return tmpl


def _emit(rule, line, i, issues, found, m, seen):
    cap = rule.get("capture")
    left = right = repl = ""
    if m and cap == "range":
        try:
            left = m.group(1)
            right = m.group(2)
        except IndexError:
            pass
    elif m and cap == "repl":
        repl = HALF_MAP.get(found, found)
    msg = fill(rule.get("message", ""), found=found, left=left, right=right,
               repl=repl, suggestion=rule.get("suggestion", ""))
    if cap == "repl":
        sug = f"改为「{repl}」"
    else:
        sug = fill(rule.get("suggestion", ""), found=found, left=left,
                   right=right, repl=repl)
    add(issues, i, line, rule, msg, found, sug,
        m.start() if m else None, m.end() if m else None)


def apply_regex_rule(rule, line, i, issues, seen, disabled_ids):
    rid = rule.get("id", "")
    if rid in disabled_ids:
        return
    if rule.get("ref_only") and not is_ref_line(line):
        return
    # 参考文献条目按 GB/T 7714 使用半角 ". " 作字段分隔符，正文半角标点检查
    # 不应在参考文献行触发，避免把标准分隔符误报为「应改全角」（P2-2 回归）
    if rid == "PUN-HALF" and is_ref_line(line):
        return
    if rule.get("exclude_pattern") and re.search(rule["exclude_pattern"], line):
        return
    try:
        rx = re.compile(rule["pattern"])
    except re.error as e:
        sys.stderr.write(f"警告：规则 {rid} 正则无效已跳过: {e}\n")
        return
    dedupe = rule.get("dedupe_key")
    if rule.get("whole_line"):
        if not rx.search(line):
            return
        if dedupe and dedupe in seen:
            return
        _emit(rule, line, i, issues, line.strip()[:50], None, seen)
        if dedupe:
            seen.add(dedupe)
        return
    for m in rx.finditer(line):
        found = m.group(0)
        sk = rule.get("skip_context")
        if sk:
            ctx = line[max(0, m.start() - 3):m.start()]
            if any(c in ctx for c in sk):
                continue
        if rule.get("skip_if_year"):
            left = m.group(1) if m.groups() else found
            if re.fullmatch(r"\d{4}", left or ""):
                continue
        if dedupe and dedupe in seen:
            continue
        _emit(rule, line, i, issues, found, m, seen)
        if dedupe:
            seen.add(dedupe)


def apply_substr_rule(rule, line, i, issues, disabled_ids):
    rid = rule.get("id", "")
    if rid in disabled_ids:
        return
    if rule.get("ref_only") and not is_ref_line(line):
        return
    if rule.get("exclude_pattern") and re.search(rule["exclude_pattern"], line):
        return
    wrong = rule["pattern"]
    start = 0
    while True:
        idx = line.find(wrong, start)
        if idx == -1:
            break
        after = line[idx + len(wrong): idx + len(wrong) + 4]
        exc = rule.get("exception_after", [])
        if any(e in after for e in exc):
            start = idx + len(wrong)
            continue
        found = wrong
        msg = fill(rule.get("message", ""), found=found,
                   suggestion=rule.get("suggestion", ""))
        sug = fill(rule.get("suggestion", ""), found=found)
        add(issues, i, line, rule, msg, found, sug, idx, idx + len(wrong))
        start = idx + len(wrong)


def is_italic_at(runs, pos):
    """返回字符位置 pos 所在 run 的斜体属性（不在任何 run 区间则 False）。"""
    for r in runs:
        if r["start"] <= pos < r["end"]:
            return r.get("italic", False)
    return False


def is_superscript_at(runs, pos):
    """返回字符位置 pos 所在 run 的上标属性（不在任何 run 区间则 False）。"""
    for r in runs:
        if r["start"] <= pos < r["end"]:
            return r.get("vertAlign") == "superscript"
    return False


# 统计符号正斜体规则（依据 GB 3102.11）。仅 DOCX 模式（有 runs 格式信息）有效。
# 每条为 (正则, 符号名, 严重性) 三元组：单字母符号加 (?<![A-Za-z]) 词边界，
# 避免 min=/mean=/sin= 等子串被误判为样本量 n 或概率 P；希腊统计符号（β/α/μ/σ/Δ
# 应斜体、Σ 应正体）补充常见覆盖率，统一以 info 级提示以控制初筛噪音。
STAT_ITALIC_PATTERNS = [
    (r"(?<![A-Za-z])[Pp]\s*[<>=≠]", "P/p", "warning"),
    (r"(?<![A-Za-z])[tFr]\s*[=<>(]", "t/F/r", "warning"),
    (r"(?<![A-Za-z])n\s*[=<>(]", "n", "warning"),
    (r"χ\s*[²2]?\s*[<>=≠]", "χ²", "warning"),
    (r"(?<![A-Za-z])[βαμσΔ]\s*[\s<>=≠±]", "希腊统计符号", "info"),
]
STAT_UPRIGHT_PATTERNS = [
    (r"SD(?![A-Za-z])", "SD", "warning"),
    (r"SE(?![A-Za-z])", "SE", "warning"),
    (r"Σ(?![A-Za-z])", "Σ", "info"),
]


def check_stats_italic(text, runs, i, issues):
    """在 DOCX 模式检查统计符号正斜体（纯文本无格式信息，不调用）。"""
    for pat, name, sev in STAT_ITALIC_PATTERNS:
        for m in re.finditer(pat, text):
            if not is_italic_at(runs, m.start()):
                add(issues, i, text,
                    {"id": "STAT-ITALIC", "category": "stats",
                     "severity": sev, "_source": "GB 3102.11",
                     "_scope": "professional"},
                    f"统计符号「{name}」应排斜体（命中：{m.group(0).strip()}）",
                    m.group(0).strip(), "将符号改为斜体（italic）", m.start())
    for pat, name, sev in STAT_UPRIGHT_PATTERNS:
        for m in re.finditer(pat, text):
            if is_italic_at(runs, m.start()):
                add(issues, i, text,
                    {"id": "STAT-UPRIGHT", "category": "stats",
                     "severity": sev, "_source": "GB 3102.11",
                     "_scope": "professional"},
                    f"「{name}」应排正体（命中：{m.group(0)}）",
                    m.group(0), "将符号改为正体（非 italic）", m.start())
    # 上下标校验（依据 GB 3102.11）：χ 后的数字应为上标（superscript）。
    for m in re.finditer(r"χ\s*([²2])\s*[<>=≠]", text):
        if not is_superscript_at(runs, m.start(1)):
            add(issues, i, text,
                {"id": "STAT-SUP", "category": "stats", "severity": "info",
                 "_source": "GB 3102.11", "_scope": "professional"},
                f"χ 后的「{m.group(1)}」应为上标（superscript），命中：{m.group(0).strip()}",
                m.group(0).strip(), "将上标数字设为上标（superscript）",
                m.start(1), m.end(1))


def dedupe_overlapping_terms(issues):
    """抑制被更长术语完全覆盖的短命中（最长匹配优先）。

    例：'红血球'中出现'血球'、'机能性'中出现'机能'、'白血球'中出现'血球'——
    只保留覆盖区间更长的那条，避免同一概念重复报告。独立出现的短词
    （不在任何更长词区间内）不受影响。
    """
    term_spans = [(idx, it) for idx, it in enumerate(issues)
                  if it.get("category") == "terminology"
                  and it.get("start") is not None and it.get("end") is not None]
    if not term_spans:
        return issues
    # 按命中长度降序（长词优先入选），长度相同按 start 升序
    order = sorted(term_spans,
                   key=lambda kv: (kv[1]["end"] - kv[1]["start"], -kv[1]["start"]),
                   reverse=True)
    keep = set()
    for idx, it in order:
        s, e = it["start"], it["end"]
        covered = any(issues[k]["start"] <= s and e <= issues[k]["end"]
                      for k in keep if k != idx)
        if not covered:
            keep.add(idx)
    # 保留全部非术语命中，仅对术语做最长匹配去重叠（避免误删其他模块问题）
    return [it for idx, it in enumerate(issues)
            if it.get("category") != "terminology" or idx in keep]


def run(text_or_lines, scopes, checks, custom_terms, disabled_ids,
        image_count=0, stats_italic=False):
    if isinstance(text_or_lines, str):
        lines = text_or_lines.split("\n")
    else:
        lines = text_or_lines
    rules = load_rules()

    # 合并自定义术语：覆盖内置 suggestion，或追加新词条
    if custom_terms:
        # 方向性校验（待办#1）：键==值 或 键为内置规范词时跳过并告警，
        # 避免把规范文本误报为非规范。无论通过 main() 还是直接 run() 都生效。
        custom_terms, cwarns = validate_custom_dict(custom_terms)
        for w in cwarns:
            sys.stderr.write("警告：" + w + "\n")
        if not custom_terms:
            sys.stderr.write("警告：自定义词典无有效条目，使用内置词典继续。\n")
        existing = {r["pattern"]: r for r in rules
                    if r.get("category") == "terminology"}
        for w, rr in custom_terms.items():
            if w in existing:
                existing[w]["suggestion"] = rr
            else:
                rules.append({
                    "id": "CUSTOM-" + hashlib.md5(w.encode("utf-8")).hexdigest()[:6],
                    "category": "terminology", "severity": "warning",
                    "pattern": w, "is_regex": False, "suggestion": rr,
                    "message": "疑似非规范医学名词「{found}」，建议改为「{suggestion}」",
                    "exception_after": [],
                    "_scope": "professional", "_layer": "自定义",
                    "_source": "用户自定义", "_auto": True,
                })

    issues = []
    seen = set()
    for r in rules:
        if not r.get("_auto", True):
            continue
        if r.get("_scope") not in scopes:
            continue
        if checks and r.get("category") not in checks:
            continue
        for i, raw in enumerate(lines, 1):
            line = raw["text"] if isinstance(raw, dict) else raw
            runs = raw.get("runs") if isinstance(raw, dict) else None
            # 参考文献行的数字格式归 references 模块处理，避免页码 30-36
            # 被 numbers 模块误判为「数值范围应用～」（审查报告 P0 冲突点）
            if r.get("category") == "numbers" and is_ref_line(line):
                continue
            if r.get("is_regex"):
                apply_regex_rule(r, line, i, issues, seen, disabled_ids)
            else:
                apply_substr_rule(r, line, i, issues, disabled_ids)
    # 统计符号正斜体检查（仅 DOCX 模式有 runs 时；纯文本无法判断格式）
    if (not checks or "stats" in checks) and stats_italic:
        for i, raw in enumerate(lines, 1):
            if isinstance(raw, dict) and raw.get("runs"):
                check_stats_italic(raw["text"], raw["runs"], i, issues)
    issues = dedupe_overlapping_terms(issues)
    issues.sort(key=lambda x: (x["line"], x["category"], x["rule_id"]))
    return issues, lines, rules, image_count


def run_meta(rules):
    """生成版本/追溯元信息，写入报告头部便于复现某次审校。"""
    return {
        "skill_version": SKILL_VERSION,
        "ruleset_version": RULESET_VERSION,
        "std_effective_date": STD_EFFECTIVE_DATE,
        "run_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rules": len(rules),
    }


CAT_ORDER = ["terminology", "units", "numbers", "punct", "stats", "references"]


def aggregate_by_rule(issues):
    """按 (rule_id, category) 聚合同类命中：统计次数并收集最多 3 个上下文示例。

    解决「同类错误重复报」问题——同一规则在多处命中只计一条，并列出示例片段。
    """
    groups = {}
    order = []
    for it in issues:
        key = (it["rule_id"], it["category"])
        if key not in groups:
            groups[key] = {
                "rule_id": it["rule_id"], "category": it["category"],
                "severity": it["severity"], "scope": it["scope"],
                "message": it["message"], "suggestion": it["suggestion"],
                "standard": it["standard"], "count": 0,
                "examples": [], "lines": [],
            }
            order.append(key)
        g = groups[key]
        g["count"] += 1
        ctx = it.get("context") or it.get("found") or ""
        if ctx and ctx not in g["examples"] and len(g["examples"]) < 3:
            g["examples"].append(ctx)
        if it["line"] not in g["lines"]:
            g["lines"].append(it["line"])
    return [groups[k] for k in order]


def build_report(issues, lines, rules, scopes, path, image_count=0,
                 aggregate=True, with_line_no=False, stats_italic=False):
    total_chars = sum(len(l["text"]) if isinstance(l, dict) else len(l)
                      for l in lines)
    by_cat, by_sev, by_scope = {}, {}, {}
    for it in issues:
        by_cat[it["category"]] = by_cat.get(it["category"], 0) + 1
        by_sev[it["severity"]] = by_sev.get(it["severity"], 0) + 1
        by_scope[it["scope"]] = by_scope.get(it["scope"], 0) + 1
    density = (len(issues) / total_chars * 10000) if total_chars else 0
    meta = run_meta(rules)

    out = []
    out.append("# 医学稿件自动审校报告（初筛）")
    out.append("")
    out.append(f"- 来源文件：`{path}`")
    out.append(f"- 全文约 {total_chars} 字符（{total_chars/10000:.2f} 万字）")
    out.append(f"- 启用层级：{', '.join(SCOPE_CN.get(s, s) for s in scopes)}")
    out.append(f"- 疑似问题合计：**{len(issues)}** 处"
               + ("（已按规则聚合，同类仅列一次）" if aggregate else "（逐条列出）"))
    out.append("")
    out.append("## 版本与追溯")
    out.append("")
    out.append(f"- 技能版本：**{meta['skill_version']}**｜规则库版本：**{meta['ruleset_version']}**")
    out.append(f"- 标准生效日期：{meta['std_effective_date']}（GB/T 7714-2025 等现行标准）")
    out.append(f"- 运行时间：{meta['run_time']}｜规则总数：{meta['total_rules']}")
    out.append("")
    out.append("## 统计概览")
    out.append("")
    out.append("| 严重性 | 数量 |")
    out.append("|--------|------|")
    for s in ("error", "warning", "info"):
        if by_sev.get(s):
            out.append(f"| {SEV_LABEL[s]} | {by_sev[s]} |")
    out.append("")
    out.append("| 检查项 | 数量 |")
    out.append("|--------|------|")
    for c, n in by_cat.items():
        out.append(f"| {CAT_CN.get(c, c)} | {n} |")
    out.append("")
    out.append("| 规则层级 | 命中数 |")
    out.append("|----------|--------|")
    for s in SCOPE_ORDER:
        if by_scope.get(s):
            out.append(f"| {SCOPE_CN[s]} | {by_scope[s]} |")
    out.append("")
    out.append("> 提示：规则命中密度（疑似问题数/万字）约 **"
               f"{density:.2f}**，仅反映初筛问题规模，**不等于**"
               "《报纸期刊质量管理规定》所指编校差错率"
               "（后者按差错类别赋计错分值、设最高计错数，期刊合格线为 2/万）。"
               "本工具不做合格判定，须人工复核。")
    out.append("")
    out.append("## 问题明细（按模块分组）")
    out.append("")
    out.append("> 定位说明：每条问题给出**原文片段**（可在稿件中直接搜索定位），"
               + ("默认不附行/段号；加 `--with-line-no` 可显示行号。" if not with_line_no else "")
               + " 同类问题已聚合为「N 处」并列举示例片段。")
    out.append("")
    for cat in CAT_ORDER:
        cat_issues = [it for it in issues if it["category"] == cat]
        if not cat_issues:
            continue
        out.append(f"### {CAT_CN.get(cat, cat)}（{len(cat_issues)} 处）")
        out.append("")
        if aggregate:
            for g in aggregate_by_rule(cat_issues):
                loc = (" " + "/".join(f"L{x}" for x in g["lines"][:5]) + " "
                       if with_line_no else "")
                out.append(
                    f"- **{g['count']} 处**{loc}"
                    f"`{g['rule_id']}` `[{SEV_LABEL[g['severity']]}]` {g['message']}")
                for ex in g["examples"]:
                    out.append(f"  - 原文片段：_{ex}_")
                out.append(f"  - 建议：{g['suggestion']} ｜ 依据：{g['standard']}")
        else:
            for it in cat_issues:
                loc = f"L{it['line']} " if with_line_no else ""
                out.append(
                    f"- {loc}`{it['rule_id']}` `[{SEV_LABEL[it['severity']]}]` {it['message']}")
                out.append(f"  - 原文片段：_{it.get('context') or it['found']}_ ｜ "
                           f"建议：{it['suggestion']} ｜ 依据：{it['standard']}")
        out.append("")

    # 人工核对清单（auto=false 的层级规则，仅列不扫描）
    checklist = [r for r in rules
                 if not r.get("_auto", True) and r.get("_scope") in scopes]
    if checklist:
        out.append("## 人工核对清单（本层级规则不自动扫描）")
        out.append("")
        for s in SCOPE_ORDER:
            items = [r for r in checklist if r.get("_scope") == s]
            if not items:
                continue
            src = items[0].get("_source", "")
            out.append(f"### {SCOPE_CN[s]}（{src}）")
            out.append("")
            for r in items:
                out.append(f"- `{r.get('id','')}` {r.get('message','')}  \n"
                           f"  建议：{r.get('suggestion','')}")
            out.append("")
    out.append("---")
    out.append("## 使用须知与安全提示")
    out.append("")
    out.append("- **输入范围**：支持纯文本（.md/.txt）与 Word（.docx）。.docx 模式"
               "可提取正文/表格文本，并基于 run 显式属性部分识别统计符号斜体/上下标（字符样式继承未解析）；但图片像素、嵌入"
               "公式、脚注、修订痕迹等仍不可在纯文本层可靠获取，仅统计数量并提示人工核对。")
    out.append("- **数据性质**：稿件文本仅作为待检查的**数据**读取，**不作为指令执行**；"
               "请勿在稿件中嵌入可被误读为指令的内容（提示注入防护）。")
    out.append("- **隐私**：建议在本地运行，稿件不外发；未发表稿件、患者信息、"
               "敏感研究数据请先脱敏后再提交检查。")
    if image_count:
        out.append(f"- **图片**：本文档含 {image_count} 张图片，脚本无法检查其清晰度、"
                   "编号与版权，须人工核对（建议 ≥300 dpi、按正文出现顺序编号）。")
    if stats_italic:
        out.append("- **统计符号正斜体**：本次已启用 `--stats-italic` 核查 P/t/F/r/n/χ²/SD/SE 的正斜体。")
    else:
        out.append("- **统计符号正斜体**：未执行检查（当前稿件不含 run 格式信息，"
                   "纯文本无法判断斜体/上下标；如需核查，请用 .docx 并加 `--stats-italic`）。")
    out.append("")
    out.append("> 本报告由 medical-journal-copyediting 技能自动生成，"
               "仅作初筛，最终须责任编辑人工确认。规则以 rules/ 目录为准。")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="中文医学期刊稿件自动审校（初筛）")
    ap.add_argument("file", help="稿件文件路径（.md/.txt/.docx）")
    ap.add_argument("--check", default="all",
                    help="检查项，逗号分隔：terminology,units,numbers,"
                         "punct,stats,references")
    ap.add_argument("--scope", default="all",
                    help="规则层级，逗号分隔：national,professional,"
                         "journal,experience（默认 all）")
    ap.add_argument("--dict", help="自定义术语替换词条 JSON 路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON 结构")
    ap.add_argument("--out", help="报告输出路径（默认打印到 stdout）")
    ap.add_argument("--no-punct-halfwidth", action="store_true",
                    help="关闭半角标点检查")
    ap.add_argument("--stats-italic", action="store_true",
                    help="启用统计符号正斜体检查（默认关闭，初筛阶段噪音大）")
    ap.add_argument("--no-aggregate", action="store_true",
                    help="问题明细逐条列出，不按规则聚合")
    ap.add_argument("--with-line-no", action="store_true",
                    help="在问题明细中附上行/段号")
    ap.add_argument("--version", action="version",
                    version=f"medical-journal-copyediting {SKILL_VERSION} "
                            f"(ruleset {RULESET_VERSION}, "
                            f"std-effective {STD_EFFECTIVE_DATE})")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        sys.stderr.write(f"文件不存在: {args.file}\n")
        sys.exit(2)

    # 解析检查项
    valid_checks = {"terminology", "units", "numbers", "punct",
                    "stats", "references"}
    if args.check == "all":
        checks = []
    else:
        checks = [c.strip() for c in args.check.split(",") if c.strip()]
        unknown = [c for c in checks if c not in valid_checks]
        if unknown:
            sys.stderr.write(f"警告：未知检查项将被忽略：{unknown}\n")
        checks = [c for c in checks if c in valid_checks]
    if args.check != "all" and not checks:
        sys.stderr.write("错误：无有效检查项。\n")
        sys.exit(2)

    # 解析层级
    if args.scope == "all":
        scopes = list(SCOPE_ORDER)
    else:
        scopes = [s.strip() for s in args.scope.split(",") if s.strip()]
        unknown = [s for s in scopes if s not in SCOPE_ORDER]
        if unknown:
            sys.stderr.write(f"警告：未知层级将被忽略：{unknown}\n")
        scopes = [s for s in scopes if s in SCOPE_ORDER]
    if not scopes:
        sys.stderr.write("错误：无有效层级。\n")
        sys.exit(2)

    disabled_ids = set()
    if args.no_punct_halfwidth:
        disabled_ids.add("PUN-HALF")

    custom_terms = {}
    if args.dict:
        try:
            with open(args.dict, encoding="utf-8") as f:
                custom_terms = json.load(f)
            if not isinstance(custom_terms, dict):
                raise ValueError("自定义词典应为 {\"非规范\": \"规范\"} 形式的对象")
        except Exception as e:
            sys.stderr.write(f"读取自定义词典失败，使用内置词典继续: {e}\n")
            custom_terms = {}

    ext = os.path.splitext(args.file)[1].lower()
    # 纯文本（.md/.txt）无 run 格式信息，统计符号正斜体检查无法判断，自动降级
    stats_eff = args.stats_italic
    if args.stats_italic and ext != ".docx":
        sys.stderr.write("警告：纯文本稿件不含 run 格式信息，--stats-italic 已自动"
                         "降级，统计符号正斜体检查未执行；如需检查请改用 .docx。\n")
        stats_eff = False
    if ext == ".docx":
        try:
            from parse_docx import parse_docx
        except ImportError:
            sys.stderr.write("错误：parse_docx 模块缺失。\n")
            sys.exit(2)
        lines, image_count = parse_docx(args.file)
        issues, lines, rules, image_count = run(
            lines, scopes, checks, custom_terms, disabled_ids, image_count,
            stats_italic=stats_eff)
    else:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
        issues, lines, rules, image_count = run(
            text, scopes, checks, custom_terms, disabled_ids,
            stats_italic=stats_eff)

    report = build_report(issues, lines, rules, scopes, args.file, image_count,
                          aggregate=not args.no_aggregate,
                          with_line_no=args.with_line_no,
                          stats_italic=stats_eff)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        if args.json:
            json_path = os.path.splitext(args.out)[0] + ".json"
            meta = run_meta(rules)
            json.dump({
                "skill_version": meta["skill_version"],
                "ruleset_version": meta["ruleset_version"],
                "std_effective_date": meta["std_effective_date"],
                "run_time": meta["run_time"],
                "total_rules": meta["total_rules"],
                "image_count": image_count,
                "issues": issues,
                "total": len(issues),
                "density_per_10k": round(
                    len(issues) / sum(
                        len(l["text"]) if isinstance(l, dict) else len(l)
                        for l in lines) * 10000, 2)
                if lines else 0,
            }, open(json_path, "w", encoding="utf-8"),
                ensure_ascii=False, indent=2)
        sys.stderr.write(f"报告已写入: {args.out}\n")
    else:
        if args.json:
            sys.stderr.write(report + "\n")
            meta = run_meta(rules)
            print(json.dumps({
                "skill_version": meta["skill_version"],
                "ruleset_version": meta["ruleset_version"],
                "std_effective_date": meta["std_effective_date"],
                "run_time": meta["run_time"],
                "total_rules": meta["total_rules"],
                "image_count": image_count,
                "issues": issues, "total": len(issues)},
                ensure_ascii=False, indent=2))
        else:
            print(report)


if __name__ == "__main__":
    main()
