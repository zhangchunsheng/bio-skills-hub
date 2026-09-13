#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extras —— 五个来自「市场验证过的高频需求」的增强能力。

来源：交叉统计 8 个高热度 Excel 数据清洗教程（Chandoo、MyOnlineTrainingHub、
Simon Sez IT、Kenji Explains 四个英文视频源，加四个中文教程源）后出现频次最高的、
且本技能原本没有覆盖的能力：

  1. 重复值检测      8/8  —— 断层第一
  2. 复合列拆分      6/8  —— 对应 Excel 的「分列」
  3. 模式提取        5/8  —— 对应 Excel 的「快速填充 Ctrl+E」
  4. 同义值归一化    3/8  —— 对应视频里 SYD / Sydney 那个坑
  5. 清洗后自检      2/8  —— 对应视频收尾的「证明它奏效了」

统一原则：**检测默认不改**。这五项都可能误伤真实数据，
一律先进报告，由人决定要不要执行。
"""

import re
import sys
import os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dirty_rules import parse_number, parse_date

# ---------------------------------------------------------------- 3. 模式提取

EXTRACT_PATTERNS = [
    ("手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("邮箱", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("身份证", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("URL", re.compile(r"https?://[\w./?%&=~+-]+")),
    ("日期串", re.compile(r"(?<!\d)(\d{4})[-/.年]?(\d{1,2})[-/.月]?(\d{1,2})")),
    ("纯数字", re.compile(r"-?\d+(?:[,.]\d+)?")),
]

# 常见分隔符，按"在中文表格里真实出现"的频率排序
SPLIT_DELIMS = [
    ("顿号", "、"), ("斜杠", "/"), ("竖线", "|"), ("分号", ";"),
    ("逗号", ","), ("空格", " "), ("连字符", "-"), ("下划线", "_"),
    ("冒号", ":"), ("中文逗号", "，"),
]


def extract_pattern(text, kind):
    """从单个文本里按模式提取。返回 (值 or None, 匹配数)。"""
    if not isinstance(text, str):
        return None, 0
    for name, rx in EXTRACT_PATTERNS:
        if name == kind:
            m = rx.search(text)
            if not m:
                return None, 0
            if kind == "日期串":
                # 拼回 ISO，否则会截出 "2026年1月5" 这种半个日期
                y, mo, d = m.groups()
                try:
                    v = "%04d-%02d-%02d" % (int(y), int(mo), int(d))
                except (ValueError, TypeError):
                    return None, 0
                if not (1 <= int(mo) <= 12 and 1 <= int(d) <= 31):
                    return None, 0
            else:
                v = m.group(0)
            return v, len(rx.findall(text))
    return None, 0


def detect_extractable(header, rows, min_ratio=0.6):
    """
    找出「整列都藏着同一种结构化信息」的列——这正是 Excel 快速填充的用武之地。
    比如"张三 13812345678"整列都能提取出手机号。
    """
    out = []
    for ci, name in enumerate(header):
        vals = [r[ci] for r in rows if ci < len(r)
                and isinstance(r[ci], str) and r[ci].strip()]
        if len(vals) < 3:
            continue
        n = len(vals)
        best = None
        for kind, rx in EXTRACT_PATTERNS:
            if kind == "纯数字":
                continue  # 太宽泛，整列本来就是数字时没意义
            if kind == "日期串":
                # 只统计"常规日期解析认不出来"的那些——纯日期列清洗时就会被转 ISO，
                # 再推荐提取一遍是噪音。这里要抓的是"订单号2026年3月5日A01"这类混合文本。
                hits = sum(1 for v in vals if rx.search(v) and not parse_date(v))
            else:
                hits = sum(1 for v in vals if rx.search(v))
            ratio = hits / n
            if ratio >= min_ratio and (best is None or ratio > best["ratio"]):
                sample = vals[0]
                m = rx.search(sample)
                ex = m.group(0) if m else ""
                # 只有当"提取出来比原值短"才算有价值，否则等于没提取
                if ex and len(ex) < len(sample):
                    best = {"kind": kind, "ratio": round(ratio, 2),
                            "sample": sample[:30], "extracted": ex}
        if best:
            best["column"] = name
            best["suggest"] = '--extract "%s:%s"' % (name, best["kind"])
            out.append(best)
    return out


# ---------------------------------------------------------------- 2. 复合列拆分

def detect_composite(header, rows, min_ratio=0.7):
    """
    检测「一列里挤了多个字段」——对应 Excel 的「分列」。
    判据：整列大多数值都能被同一分隔符切成相同段数，且每段长度稳定。
    """
    out = []
    for ci, name in enumerate(header):
        vals = [r[ci] for r in rows if ci < len(r)
                and isinstance(r[ci], str) and r[ci].strip()]
        if len(vals) < 3:
            continue
        n = len(vals)
        for dname, d in SPLIT_DELIMS:
            segs = [v.split(d) for v in vals if d in v]
            if len(segs) < n * min_ratio:
                continue
            counts = Counter(len(s) for s in segs)
            top_count, top_n = counts.most_common(1)[0]
            if top_count < 2 or top_n < n * min_ratio:
                continue
            # 段数必须稳定，否则是自由文本不是结构化数据
            if top_n / len(segs) < min_ratio:
                continue
            sample = next(v for v in vals if d in v)
            parts = sample.split(d)
            # 空段太多说明分隔符选错了
            if sum(1 for p in parts if not p.strip()) > len(parts) // 2:
                continue
            # 每段都是纯数字 → 多半是日期(2026-01-05)或编号，不是复合字段。
            # 少了这条，清洗后的 ISO 日期会被误判成"可以拆开"。
            solid = [p.strip() for p in parts if p.strip()]
            if solid and all(re.fullmatch(r"\d+", p) for p in solid):
                continue
            out.append({
                "column": name,
                "delimiter": d,
                "delimiter_name": dname,
                "segments": top_count,
                "ratio": round(len(segs) / n, 2),
                "sample": sample[:30],
                "preview": [p.strip()[:16] for p in parts[:4]],
                "suggest": '--split-col "%s" --delim "%s"' % (name, d),
            })
            break  # 一列只推荐一种拆法
    return out


def split_column(header, rows, col_name, delim, names=None):
    """执行拆分。返回 (新表头, 新行)。原列保留，拆出的列追加在后面。"""
    if col_name not in header:
        raise ValueError("没有这一列: %s" % col_name)
    ci = header.index(col_name)
    seg_max = 1
    for r in rows:
        if ci < len(r) and isinstance(r[ci], str) and delim in r[ci]:
            seg_max = max(seg_max, len(r[ci].split(delim)))

    new_names = names or ["%s_%d" % (col_name, i + 1) for i in range(seg_max)]
    if len(new_names) < seg_max:
        new_names = new_names + ["%s_%d" % (col_name, i + 1)
                                 for i in range(len(new_names), seg_max)]

    nh = list(header) + new_names
    nr = []
    for r in rows:
        base = list(r) + [None] * (len(nh) - len(r))
        v = r[ci] if ci < len(r) else None
        parts = v.split(delim) if isinstance(v, str) and delim in v else (
            [v] + [None] * (seg_max - 1) if v is not None else [None] * seg_max)
        for i in range(seg_max):
            base[len(header) + i] = parts[i].strip() if i < len(parts) and parts[i] is not None else None
        nr.append(base[:len(nh)])
    return nh, nr


# ---------------------------------------------------------------- 1. 重复值

def find_duplicates(header, rows, subset=None):
    """
    重复值检测。**默认绝不删**——视频里明确警告过：
    一张发票可能有多个明细行，看起来像重复其实是合法数据。

    分两类报告：
      - 整行完全重复：删掉几乎总是安全的
      - 部分列重复：必须人看，可能是合法的多行明细
    """
    n = len(rows)
    key_all = {}
    for i, r in enumerate(rows):
        k = tuple(("" if v is None else str(v)) for v in r)
        key_all.setdefault(k, []).append(i + 2)  # +2 = 表头 + 1 基

    full = [(v[0], v[1:]) for v in key_all.values() if len(v) > 1]
    full_dup_rows = sorted({i for keep, dups in full for i in dups})

    by_col = {}
    idxs = [header.index(c) for c in subset] if subset else range(len(header))
    for ci in idxs:
        if ci >= len(header):
            continue
        m = defaultdict(list)
        for i, r in enumerate(rows):
            v = r[ci] if ci < len(r) else None
            if v is None or (isinstance(v, str) and not v.strip()):
                continue
            # 数字也要转成字符串当键，否则整列数字会挤在同一个空字符串键下
            k = v.strip() if isinstance(v, str) else str(v)
            m[k].append(i + 2)
        dups = {k: v for k, v in m.items() if len(v) > 1}
        if dups:
            by_col[header[ci]] = {
                "dup_values": len(dups),
                "affected_rows": sum(len(v) for v in dups.values()),
                "examples": [{"value": k[:28], "rows": v[:6]}
                             for k, v in list(dups.items())[:5]],
            }

    return {
        "full_row_dup_groups": len(full),
        "full_row_removable": len(full_dup_rows),
        "full_row_examples": [
            {"keep_row": keep, "dup_rows": dups[:6],
             "preview": " | ".join(str(x)[:14] for x in rows[keep - 2][:5])}
            for keep, dups in full[:5]
        ],
        "by_column": by_col,
        "total_rows": n,
    }


def dedupe_rows(header, rows, subset=None, keep="first"):
    """实际删除重复行。只有用户显式 --dedupe 才调用。"""
    seen = set()
    out, removed = [], []
    idxs = [header.index(c) for c in subset] if subset else None
    for i, r in enumerate(rows):
        if idxs:
            k = tuple(("" if r[c] is None else str(r[c]).strip()) for c in idxs if c < len(r))
        else:
            k = tuple(("" if v is None else str(v)) for v in r)
        if k in seen:
            removed.append(i + 2)
            continue
        seen.add(k)
        out.append(r)
    return out, removed


# ---------------------------------------------------------------- 4. 同义值归一化

def _norm_key(s):
    """归一化比较用的键：去空格、去全角、统一大小写和括号。"""
    if not isinstance(s, str):
        return str(s)
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"\s+", "", s)
    return s.lower()


def detect_synonyms(header, rows, max_pairs=12):
    """
    找出「同一列里疑似同一个东西却写成不同样子」的值。
    这是分组统计的头号杀手：北京分公司 / 北京分公司(总部) 会被算成两家。

    三档置信度：
      - 高：仅大小写/空格/全角/括号不同，归一化后完全相同 → 建议直接合并
      - 中：一个是另一个的前缀，且差异部分是括号或常见后缀 → 建议人工确认
      - 低：编辑距离很近 → 只提示
    """
    from difflib import SequenceMatcher
    out = []
    for ci, name in enumerate(header):
        vals = [r[ci] for r in rows if ci < len(r)
                and isinstance(r[ci], str) and r[ci].strip()]
        freq = Counter(vals)
        uniq = list(freq.keys())
        if len(uniq) < 2 or len(uniq) > 300:
            continue

        # 高置信度：归一化后撞在一起
        groups = defaultdict(set)
        for v in uniq:
            groups[_norm_key(v)].add(v)
        high = [sorted(g, key=lambda x: -freq[x]) for g in groups.values() if len(g) > 1]

        # 中置信度：前缀包含关系，且差异只是尾缀
        mid = []
        short = [u for u in uniq if len(u) <= 24]
        for a in short:
            for b in short:
                if a >= b or not b.startswith(a):
                    continue
                tail = b[len(a):]
                if re.fullmatch(r"[（(【\[].{1,8}[)）】\]]|分公司|公司|有限|责任|总部|分部|\(\d+\)", tail):
                    mid.append((a, b))
                if len(mid) >= max_pairs:
                    break
            if len(mid) >= max_pairs:
                break

        # 低置信度：疑似缩写。SYD vs Sydney、BJ vs Beijing 这类。
        # 只提示不合并——缩写是否等价取决于业务，猜错代价高。
        low = []
        for a in uniq:
            if not (2 <= len(a) <= 5 and a.isalpha() and a.isupper()):
                continue
            for b in uniq:
                if b == a or len(b) <= len(a):
                    continue
                if not re.fullmatch(r"[A-Za-z][A-Za-z\s\-_]{1,23}", b or ""):
                    continue
                hit = b.lower().startswith(a.lower())
                if not hit:
                    words = [w for w in re.split(r"[\s\-_]+", b) if w]
                    hit = bool(words) and len(words) == len(a) and \
                        "".join(w[0] for w in words).upper() == a
                if hit:
                    low.append((a, b))
                    break
            if len(low) >= max_pairs:
                break

        pairs = []
        for g in high[:max_pairs]:
            pairs.append({"level": "高", "values": g, "counts": [freq[x] for x in g],
                          "reason": "只是空格/全角/括号/大小写不同"})
        for a, b in mid[:max_pairs]:
            pairs.append({"level": "中", "values": [a, b], "counts": [freq[a], freq[b]],
                          "reason": "一个是另一个加了个尾缀，可能是同一实体也可能不是"})
        for a, b in low[:max_pairs]:
            pairs.append({"level": "低", "values": [a, b], "counts": [freq[a], freq[b]],
                          "reason": "疑似缩写，是否等价取决于业务，不建议自动合并"})

        if pairs:
            out.append({"column": name, "unique_values": len(uniq), "pairs": pairs})
    return out


# ---------------------------------------------------------------- 5. 清洗后自检

ISO_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
PLACEHOLDER_RE = re.compile(
    r"^\s*(-{1,3}|－|—|/{1,2}|N/?A|na|null|none|无|暂无|待定|待补|未知|不需|不适用|\?{1,3}|待填|尚未)\s*$",
    re.I)


def _infer_target(values):
    """猜这一列"应该"是什么类型：数字 / 日期 / 文本。样本太少就不猜。"""
    nonempty = [v for v in values if v is not None and (not isinstance(v, str) or v.strip())]
    if len(nonempty) < 2:
        return "未知", 0.0
    n = len(nonempty)
    nums = sum(1 for v in nonempty if isinstance(v, (int, float)) and not isinstance(v, bool))
    isos = sum(1 for v in nonempty if isinstance(v, str) and ISO_RE.match(v))
    if nums / n >= 0.7:
        return "数字", nums / n
    if isos / n >= 0.7:
        return "日期", isos / n
    return "文本", max(nums / n, isos / n)


def self_check(header, rows):
    """
    清洗完「证明它奏效了」。对应视频收尾那步——
    用 ISNUMBER 验证数字列到底是不是真数字，而不是看起来像。

    返回每列的达标率 + 残留问题，以及一个总完成度。
    """
    cols = []
    for ci, name in enumerate(header):
        vals = [r[ci] if ci < len(r) else None for r in rows]
        nonempty = [v for v in vals if v is not None and (not isinstance(v, str) or v.strip())]
        if not nonempty:
            continue
        target, conf = _infer_target(nonempty)
        n = len(nonempty)

        bad, residual = [], []
        if target == "数字":
            bad = [(i + 2, v) for i, v in enumerate(vals)
                   if v is not None and not (isinstance(v, (int, float)) and not isinstance(v, bool))]
        elif target == "日期":
            bad = [(i + 2, v) for i, v in enumerate(vals)
                   if v is not None and not (isinstance(v, str) and ISO_RE.match(v))]
        residual = [(i + 2, v) for i, v in enumerate(vals)
                    if isinstance(v, str) and PLACEHOLDER_RE.match(v)]

        # 判断"还有没有清洗空间"——文本列里其实藏着数字或日期。
        # 少了这一步，一张没洗过的表会因为"全是文本且类型一致"而显示 100% 达标，
        # 那是假达标。
        hidden = {"number": 0, "date": 0}
        if target == "文本":
            for v in nonempty:
                if not isinstance(v, str):
                    continue
                if parse_number(v)[0] is not None:
                    hidden["number"] += 1
                elif parse_date(v):
                    hidden["date"] += 1
        max_hidden = max(hidden.values())
        potential = round(max_hidden / n, 3) if n else 0.0
        hidden_kind = "数字" if hidden["number"] >= hidden["date"] else "日期"

        ok = n - len(bad)
        cols.append({
            "column": name,
            "target": target,
            "nonempty": n,
            "conforming": ok,
            "rate": round(ok / n, 3) if n else 1.0,
            "violations": [{"row": r, "value": str(v)[:24]} for r, v in bad[:5]],
            "violation_count": len(bad),
            "placeholders": len(residual),
            "placeholder_examples": [str(v) for _, v in residual[:3]],
            "hidden_potential": potential,
            "hidden_kind": hidden_kind if potential >= 0.6 else None,
        })

    total = sum(c["nonempty"] for c in cols)
    good = sum(c["conforming"] for c in cols)
    score = round(good / total, 3) if total else 1.0
    failing = [c for c in cols if c["rate"] < 1.0]
    # 类型达标 ≠ 洗干净了。一张没洗过的表类型也一致，这里单独标出还有空间的列
    uncleaned = [c for c in cols if c.get("hidden_potential", 0) >= 0.6]

    if uncleaned:
        verdict = "类型一致，但有 %d 列还藏着可解析的%s，建议先清洗再分析" % (
            len(uncleaned), "数字/日期")
    elif score >= 0.999:
        verdict = "全部达标，可以直接进分析"
    elif score >= 0.95:
        verdict = "基本可用，但还有残留，见下方清单"
    else:
        verdict = "达标率偏低，建议先看报告里的待确认项"

    return {
        "score": score,
        "total_cells": total,
        "conforming_cells": good,
        "columns_checked": len(cols),
        "columns_failing": len(failing),
        "columns_uncleaned": len(uncleaned),
        "uncleaned_columns": [{"column": c["column"], "hidden_kind": c["hidden_kind"],
                               "ratio": c["hidden_potential"]} for c in uncleaned],
        "verdict": verdict,
        "columns": cols,
    }
