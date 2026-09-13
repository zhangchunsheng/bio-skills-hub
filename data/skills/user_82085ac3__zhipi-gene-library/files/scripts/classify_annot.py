#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脂批位置分类与版本断代 · 代码化引擎  (zhipi-gene-library / 模式 C)
================================================================

将《红楼梦》脂批按"批注位置"分类，跨版本提取为结构化数据，
执行脂批-正文剥离、三向一致性校验、反向归因与版本断代。

纯标准库实现（json / dataclasses / enum），无第三方依赖。
可作为实际批注工程的起点：把你的批注条目替换 demo 数据即可。

用法：
    python classify_annot.py --demo                 # 跑内置示例（触发全部归因标签）
    python classify_annot.py --axis-check           # 五轴对齐断伪校验示例（修正锚点版）
    python classify_annot.py --input entries.json --outdir out/   # 处理真实数据

输入条目格式（每条 = 某版本某回某位置的一条批语，同 annot_id 跨版本共享）：
    {
      "annot_id": "ZP-001",
      "chapter": 13,
      "version": "JIAXU",          # 见 VersionCode
      "position": "MEIPIAN",       # 见 Position
      "text": "批语原文",
      "selector": "p3-top",        # 与正文绑定的锚点（剥离后用于还原）
      "l2": "叙事引导", "l3": "痛惜"
    }
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


# --------------------------------------------------------------------------
# 一、本体枚举
# --------------------------------------------------------------------------
class Position(str, Enum):
    MEIPIAN = "MEIPIAN"            # 眉批
    XINGPI = "XINGPI"              # 行批（行间批）
    JIABI = "JIABI"               # 夹批
    CEBI = "CEBI"                 # 侧批
    HUISHOUBIPI = "HUISHOUBIPI"    # 回首批
    ZONGBI = "ZONGBI"             # 总批
    HUIMOBIPI = "HUIMOBIPI"       # 回末批


class VersionCode(str, Enum):
    YUXI = "YUXI"        # 余西盐课司本（1775 雅化，重构）
    KULUN = "KULUN"      # 库伦本（重构）
    JIAXU = "JIAXU"      # 甲戌本
    GENGCHEN = "GENGCHEN"  # 庚辰本
    QIXU = "QIXU"        # 戚序本
    MENGFU = "MENGFU"    # 蒙府本
    LIEZANG = "LIEZANG"  # 列藏本
    MENGAO = "MENGAO"    # 梦稿本（杨藏）
    # 靖藏本（JINGZANG）：其传世的"150 条批语"经版本/文献溯源层判定为
    # 定向作伪产物——系与俞平伯《脂砚斋红楼梦辑评》逐字重合（现代辑评本）而来，
    # 时代错置（anachronism），故整批定义为 FORGED（伪批）并予以隔离（quarantine）。
    # 注意：此判定的理由在"版本/文献溯源层"（辑评源），
    # 绝不在"小说文本层"（不得以"无正文载体/皮之不存"作为判伪理由）。
    JINGZANG = "JINGZANG"  # 靖藏本（150 条：定向作伪·定义伪批·隔离）
    # 程甲/程乙本：通本白文本，不载脂批（程高整理时删尽脂批）。
    # 故程高本不进入"脂批版本"范畴，仅作"脂批被白文本化/清洗出主流流传"的基线。
    CHENGJIA = "CHENGJIA"  # 程甲本（1791，白文本）
    CHENGBI = "CHENGBI"    # 程乙本（1792，白文本）
    # 脂本系统之外的后世评点/托名本（如三家评本王希廉等，道光后）。
    # 其上"脂批"自称脂批原生者，默认为 FORGED / 后世加批。
    POSTLOU = "POSTLOU"    # 后世评点/托名本（非脂本系统）


# 重构本：需与脂批原生层分别计数，避免污染原生统计
RECONSTRUCTED = {VersionCode.YUXI, VersionCode.KULUN}
# 早期脂本原生层（乾嘉旧本，非重构）——断代时的"原生锚"
NATIVE_EARLY = {
    VersionCode.JIAXU, VersionCode.GENGCHEN, VersionCode.QIXU,
    VersionCode.MENGFU, VersionCode.LIEZANG, VersionCode.MENGAO,
}
# 载脂批的版本系统全集 = 早期原生层 ∪ 重构层
# （注意：LIPO_NATIVE 表示"该版本系统载脂批"，不等于"该批语是原生批"；
#   判定"原生 vs 重构层"须用 NATIVE_EARLY，勿用 LIPO_NATIVE。）
LIPO_NATIVE = NATIVE_EARLY | RECONSTRUCTED
# 定向作伪批次（隔离集）：靖藏本 150 条批语，系与俞平伯《脂砚斋红楼梦辑评》逐字重合
# 之定向作伪产物（版本/文献溯源层判定：后世现代辑评时代错置=anachronism）。
# 整批定义为 FORGED（伪批）并隔离（quarantine），不进入真批集合、不做逐条去污染。
# 判定理由在"版本/文献溯源层"，绝不在"小说文本层"（不得以无正文载体/皮之不存为据）。
FORGED_QUARANTINE = {VersionCode.JINGZANG}
# 白文本系统：程高本（程甲/程乙）通本无脂批，仅作"脂批被白文本化"的历史基线。
# 其上若出现"脂批"标注，属数据录入异常（或指后世读者眉批），非脂批原生品类。
WHITE_TEXT = {VersionCode.CHENGJIA, VersionCode.CHENGBI}
# 脂本系统之外的后世评点/托名本（三家评本、坊间冒称脂批本等）。
# 自称脂批原生者，默认为 FORGED / 后世加批。
POST_LIPING = {VersionCode.POSTLOU}


# --------------------------------------------------------------------------
# 二、数据结构
# --------------------------------------------------------------------------
@dataclass
class Annotation:
    annot_id: str
    chapter: int
    position: str
    text: str
    version: str
    selector: str = ""
    l2: str = ""
    l3: str = ""
    is_reconstructed: bool = False
    absent_in: list = field(default_factory=list)   # 该批语在哪些脂本中被删/缺失
    has_carrier: bool = True                         # 是否有被批的正文载体（靖藏残本类置 False）
    consistency: dict = field(default_factory=dict)
    attribution: dict = field(default_factory=dict)
    dating: dict = field(default_factory=dict)

    def to_jsonld(self) -> dict:
        return {
            # 占位命名空间（project-local URN），当前不对外解析；
            # 若需公开发布，替换为你实际托管的 JSON-LD context 地址。
            "@context": "https://redology.io/annotation/v1",
            "@id": f"urn:redology:annot:{self.version}:{self.chapter}:{self.annot_id}",
            "type": "ZhiPiAnnotation",
            "position": {"category": self.position, "selector": self.selector},
            "body": {"text": self.text, "L2_semantic": self.l2, "L3_emotion": self.l3},
            "version": {
                "code": self.version,
                "isReconstructed": self.is_reconstructed,
            },
            "absentIn": self.absent_in,
            "hasCarrier": self.has_carrier,
            "consistency": self.consistency,
            "attribution": self.attribution,
            "dating": self.dating,
        }


def normalize(entry: dict) -> Annotation:
    """将原始条目标准化为 Annotation，并补齐 is_reconstructed / absent_in / has_carrier 标记。"""
    ver = VersionCode(entry["version"])
    return Annotation(
        annot_id=str(entry["annot_id"]),
        chapter=int(entry["chapter"]),
        position=Position(entry["position"]).value,
        text=entry.get("text", ""),
        version=ver.value,
        selector=entry.get("selector", ""),
        l2=entry.get("l2", ""),
        l3=entry.get("l3", ""),
        is_reconstructed=ver in RECONSTRUCTED,
        absent_in=entry.get("absent_in", []),
        has_carrier=entry.get("has_carrier", True),
    )


# --------------------------------------------------------------------------
# 三、三向一致性校验（伪造识别核心）
# --------------------------------------------------------------------------
def consistency_check(group: list[Annotation]) -> dict:
    """
    对同一 annot_id 的跨版本批语组执行三向校验。
    返回 {positionMatch, textMatch, versionMatch}。
    """
    versions = [VersionCode(a.version) for a in group]
    positions = {a.position for a in group}
    texts = {a.text for a in group}

    # 位置一致性：多版本时多数一致即视为对齐（单版本默认 True）
    position_match = len(positions) <= 1
    # 文本一致性：跨版本逐字相同
    text_match = len(texts) <= 1
    # 版本一致性：脂批须落在"载脂批"的脂本系统或重构本；
    # 若混入白文本系统（程高本，本无脂批）或脂本系统之外的后世评点/托名本，
    # 则该批语版本归属存疑 → versionMatch=False。
    version_match = not any(
        (v in WHITE_TEXT) or (v in POST_LIPING) for v in versions
    )

    return {
        "positionMatch": position_match,
        "textMatch": text_match,
        "versionMatch": version_match,
    }


# --------------------------------------------------------------------------
# 四、反向归因（批注者分析）
# --------------------------------------------------------------------------
def attribute(group: list[Annotation], consistency: dict) -> dict:
    """
    基于三向校验结果打归因标签（list 形式，供 run() 全局追加 CLEANED）：
    LAYERED / TAMPERED / CLEANED / FORGED / COPYIST_ERROR / AUTHENTIC
    """
    pm, tm, vm = (
        consistency["positionMatch"],
        consistency["textMatch"],
        consistency["versionMatch"],
    )
    versions = [VersionCode(a.version) for a in group]
    labels = set()

    # —— 定向作伪批次（隔离集）：靖藏本 150 条 ——
    # 理由在"版本/文献溯源层"：批语文本与俞平伯《脂砚斋红楼梦辑评》重合，
    # 而该辑评为  年现代出版物 → 时代错置（anachronism）= 定向作伪。
    # 整批定义为 FORGED（伪批）并隔离，不进入真批集合、不做逐条去污染。
    # 严禁以"无正文载体 / 皮之不存"等"小说文本层"理由作为此批次判伪依据。
    if any(v in FORGED_QUARANTINE for v in versions):
        return {
            "labels": ["FORGED"],
            "confidence": 0.0,
            "annotator": "定向作伪(与俞平伯《脂砚斋红楼梦辑评》逐字重合)·整批隔离",
        }

    # 受污染参照系（无正文载体，真/伪混杂，须逐条去污染）：
    # 注——此分支不适用于靖藏本 150 条（已在上文整批隔离为 FORGED）。
    # 这里的 CONTAMINATED_REF 仅用于其他"无载体、需逐条甄别真/伪"的混合样本。
    if all(not a.has_carrier for a in group) and not any(v in FORGED_QUARANTINE for v in versions):
        labels.add("CONTAMINATED_REF")

    if not vm:
        # 版本一致性失败：混入白文本系统（程高本，本无脂批）或后世评点/托名本。
        # 凡自称脂批原生却仅见于此二类 → 伪造/后世加批（无脂本系统承袭）。
        labels.add("FORGED" if not tm else "LATER_ADDITION")
    # 白文本异常标记：程高本通本无脂批，其上出现"脂批"属数据录入异常，
    # 提示应核查是否误将后世读者眉批/整理者注当作脂批。
    if any(v in WHITE_TEXT for v in versions):
        labels.add("WHITE_TEXT_ANOMALY")
    if not pm and tm:
        labels.add("COPYIST_ERROR")      # 文本真、位置错位
    if not tm and vm:
        labels.add("TAMPERED")            # 文本变异（早期有、晚期改）
    if len(group) >= 2 and len({a.position for a in group}) == 1:
        labels.add("LAYERED")             # 同位置同回跨多版本累积

    if not labels:
        labels.add("AUTHENTIC")

    # 置信度：三向全一致最高；每多一项失败递减
    fails = sum(1 for x in (pm, tm, vm) if not x)
    confidence = round(max(0.0, 1.0 - 0.28 * fails), 2)

    # 批注者候选（仅示例推断，最终须版本学+物证+笔迹三系互证）
    if "CONTAMINATED_REF" in labels:
        annotator = "待去污染（污染标本参照，逐条甄别真/伪）"
    elif labels & {"FORGED", "LATER_ADDITION"}:
        annotator = "后世（伪托/加批）"
    elif "COPYIST_ERROR" in labels:
        annotator = "过录者（误植）"
    else:
        annotator = "脂砚斋/畸笏叟（脂批原生层）"

    return {
        "labels": sorted(labels),
        "confidence": confidence,
        "annotator": annotator,
    }


# --------------------------------------------------------------------------
# 五、版本断代指纹
# --------------------------------------------------------------------------
def date_version(group: list[Annotation], attribution: dict) -> dict:
    vers = [VersionCode(a.version) for a in group]
    in_white = any(v in WHITE_TEXT for v in vers)
    in_post = any(v in POST_LIPING for v in vers)
    in_early = any(v in NATIVE_EARLY for v in vers)       # 见于早期脂本原生层
    in_recon = any(v in RECONSTRUCTED for v in vers)      # 见于重构本（余西/库伦）
    in_quar = any(v in FORGED_QUARANTINE for v in vers)   # 定向作伪隔离集（靖藏本150条）

    if in_white:
        # 程高本通本白文本，本不该有脂批；此数据属录入异常，须人工复核。
        era = "数据异常（程高本为白文本，不载脂批，需核查录入）"
        fp = ["程高本白文本", "脂批标注异常"]
    elif in_post:
        era = "1791 后（后世评点/托名本，非脂本系统）"
        fp = ["见于后世评点本/托名本", "脂本系统无承袭"]
    elif in_recon and not in_early:
        # 仅见于重构本、早期脂本原生层全无 → 重构层。
        # （若同时见于早期原生本，则属原生批被重构本承袭，不判重构层。）
        era = "1775 后（仅见于重构本带雅化特征 → 重构层）"
        fp = ["余西/库伦雅化标记", "早期脂批原生本无"]
    elif in_early:
        # authentic 硬上限 = 1775-11-25 曹𫖯泪笔（见五轴轴④），非 1791。
        # 1791 是程高刊印/白文本化节点，属"脂批退出主流流传"的传播史节点，不是批语纪年上限。
        era = "≤1775（脂批原生，脂本系统共有；1791 起程高白文本化未载）"
        fp = ["脂批原生版本共有", "未见于白文本/后世评点本"]
    else:
        era = "待定（需物证/版本学裁定）"
        fp = []

    if in_quar:
        # 定向作伪隔离集（靖藏本 150 条）：版本/文献溯源层判定——
        # 批语文本与俞平伯《脂砚斋红楼梦辑评》逐字重合，时代错置=anachronism。
        era = "后世（定向作伪：与俞平伯《脂砚斋红楼梦辑评》逐字重合·整批隔离）"
        fp = ["批语文本与俞平伯《脂砚斋红楼梦辑评》重合", "时代错置=anachronism", "判定层=版本/文献溯源层(非小说文本层)"]
    elif "FORGED" in attribution["labels"]:
        era = "1791 后（伪造）"
    elif "CONTAMINATED_REF" in attribution["labels"]:
        era = "待去污染（污染标本参照：逐条三向/五轴/语义甄别真/伪）"

    return {"era": era, "fingerprint": fp}


# --------------------------------------------------------------------------
# 五、五轴对齐断伪校验（用户修正锚点版 · 2026-08-04）
# --------------------------------------------------------------------------
# 修正锚点：
#   首条 authentic = 1703 墨琴始批
#   末条 authentic = 1775-11-25 曹𫖯泪笔
#   剔除程高本（程甲1791 / 程乙1792 不计入 authentic 脂批源）
#   版本轴：甲戌本 1754 → 余西本 1775-11-22 封箱
FIRST_ANNOT_YEAR = 1703
LAST_ANNOT_YEAR = 1775          # 1775-11-25 曹𫖯泪笔
YUXI_SEAL_YEAR = 1775           # 1775-11-22 余西封箱，硬上限
AUTHOR = ("曹雪芹", 1715, 1775)
ANNOTATOR_LIFE = {
    "脂砚斋": (1666, 1734),      # 曹墨琴（KB 内假说）
    "畸笏叟": (1687, 1779),      # 曹頫（KB 内假说；1773年86岁→1687生）
    "墨香": (1740, 1790),
}
# 程高本：白文本，整体系剔除出 authentic 脂批源（不载脂批，
# 故其上标注的"脂批"属录入异常，而非一个真实存在的"程高独有批"品类）。
EXCLUDED_AXIS = {VersionCode.CHENGJIA, VersionCode.CHENGBI}
EMPIRE = [("康熙", 1662, 1722), ("雍正", 1723, 1735), ("乾隆", 1736, 1795)]


def axis_check(entry: dict) -> dict:
    """
    五轴对齐断伪：一条脂批须同时落进五轴窗口，任一违例即伪。
    entry: {year, version, annotator?, ref_year?, has_carrier?}
      year        —— 该批语声称纪年（公历）
      version     —— VersionCode
      annotator   —— 声称批注者（脂砚斋/畸笏叟/...），可选
      ref_year    —— 批语所指涉历史事件年，可选（轴②⑤互校）
      has_carrier —— 是否有正文载体（靖藏本类置 False → 轴①崩）
    """
    year = int(entry["year"])
    ver = VersionCode(entry["version"])
    annotator = entry.get("annotator", "")
    ref_year = entry.get("ref_year")
    has_carrier = entry.get("has_carrier", True)

    # 定向作伪批次（隔离集）：靖藏本 150 条批语。
    # 判伪理由在"版本/文献溯源层"——批语文本与俞平伯《脂砚斋红楼梦辑评》重合，
    # 而该辑评为  年现代出版物 → 时代错置（anachronism）= 定向作伪。
    # 整批定义为 FORGED（伪批）并隔离；严禁以 has_carrier（无正文载体/皮之不存）
    # 等"小说文本层"理由作为此批次判伪依据。
    if ver in FORGED_QUARANTINE:
        return {
            "year": year,
            "version": ver.value,
            "annotator": annotator or "未指明",
            "axes": {},
            "contaminated": False,
            "failed_axes": ["版本/文献溯源层：批语与俞平伯《脂砚斋红楼梦辑评》重合=时代错置(定向作伪)"],
            "verdict": "FORGED/伪批（定向作伪·与俞平伯《脂砚斋红楼梦辑评》重合·整批隔离）",
        }

    axes = {}
    # 轴①版本：非程高 + 纪年 ≤ 余西封箱。
    # 注：靖藏本类（JINGZANG）已在上方整批隔离为 FORGED，此处不再走 CONTAMINATED_REF 分支。
    axes["①版本轴"] = (ver not in EXCLUDED_AXIS) and (year <= YUXI_SEAL_YEAR)
    # 轴②作者：纪年及指涉事件均不晚于作者卒 1775
    a2 = year <= AUTHOR[2]
    if ref_year is not None:
        a2 = a2 and (ref_year <= AUTHOR[2])
    axes["②作者生卒"] = a2
    # 轴③批注者：若指明，其生卒须覆盖 year
    if annotator and annotator in ANNOTATOR_LIFE:
        b, d = ANNOTATOR_LIFE[annotator]
        axes["③批注者生卒"] = (b <= year <= d)
    else:
        axes["③批注者生卒"] = True
    # 轴④首末条：year ∈ [1703, 1775-11-25]
    axes["④首末条"] = (FIRST_ANNOT_YEAR <= year <= LAST_ANNOT_YEAR)
    # 轴⑤清代历史背景：落在康雍乾三朝（1662–1795）
    a5 = any(s <= year <= e for _, s, e in EMPIRE)
    if ref_year is not None:
        a5 = a5 and any(s <= ref_year <= e for _, s, e in EMPIRE)
    axes["⑤清代历史背景"] = a5

    failed = [k for k, v in axes.items() if not v]
    # 受污染参照系（无正文载体，真/伪混杂，须逐条去污染）：
    # 注——靖藏本 150 条（JINGZANG）已在上方整批隔离为 FORGED，不落此分支。
    # 此 CONTAMINATED_REF 仅用于其他"无载体、需逐条甄别真/伪"的混合样本。
    contaminated = not has_carrier
    if contaminated:
        verdict = "CONTAMINATED_REF/污染标本参照（需逐条去污染）"
    else:
        verdict = "FORGED/伪批" if failed else "AUTHENTIC/真批"
    return {
        "year": year,
        "version": ver.value,
        "annotator": annotator or "未指明",
        "axes": axes,
        "contaminated": contaminated,
        "failed_axes": failed,
        "verdict": verdict,
    }


def axis_demo_entries() -> list[dict]:
    return [
        {"year": 1703, "version": "JIAXU", "annotator": "脂砚斋"},                          # 真：首条
        {"year": 1775, "version": "YUXI", "annotator": "畸笏叟", "ref_year": 1775},         # 真：末条 曹𫖯泪笔
        {"year": 1840, "version": "POSTLOU", "annotator": "王希廉"},                        # 伪：三家评本（道光后，非脂本系统/轴①）
        {"year": 1740, "version": "GENGCHEN", "annotator": "脂砚斋"},                        # 伪：托名脂砚斋>1734（轴③）
        # 靖藏本 150 条：DEFINED FORGED（定向作伪）。判伪理由在"版本/文献溯源层"——
        # 批语文本与俞平伯《脂砚斋红楼梦辑评》逐字重合→ 时代错置(anachronism)。
        # 关键：即便 has_carrier=False（无正文载体），判伪理由也绝不取"小说文本层"（皮之不存），
        # 而是版本/文献溯源层的 辑评源重合。整批隔离（quarantine），不逐条去污染。
        {"year": 1959, "version": "JINGZANG", "annotator": "不明（毛国瑶1959转录）", "has_carrier": False},
    ]


def run_axis_demo() -> None:
    print("[AXIS-CHECK] 五轴对齐断伪（修正锚点版）")
    print("  首条=1703 墨琴始批 | 末条=1775-11-25 曹𫖯泪笔 | 程高本为白文本(不载脂批,剔出脂批版本轴) | 版本轴 甲戌1754→余西1775-11-22")
    print("  靖藏本150条=定向作伪(与俞平伯《脂砚斋红楼梦辑评》重合)·DEFINED FORGED·整批隔离：判伪理由在版本/文献溯源层，非小说文本层\n")
    for e in axis_demo_entries():
        r = axis_check(e)
        fa = "/".join(r["failed_axes"]) if r["failed_axes"] else ("载体缺失" if r["contaminated"] else "无")
        tag = " [污染标本]" if r["contaminated"] else ""
        print(f"  {r['version']:8} yr={r['year']:<5} {r['annotator']:6} -> 违例轴={fa:18} | {r['verdict']}{tag}")
    print("\n结论：任一轴违例即伪批必现；五轴全过且非定向作伪隔离批次，方入 authentic 脂批集合。")
    print("      靖藏本150条为定向作伪(抄《脂砚斋红楼梦辑评》)的隔离批次：DEFINED FORGED、整批隔离，不逐条去污染。\n")


# --------------------------------------------------------------------------
# 六、主流程
# --------------------------------------------------------------------------
def run(entries: list[dict]) -> dict:
    annots = [normalize(e) for e in entries]

    # 按 annot_id 分组
    groups: dict[str, list[Annotation]] = {}
    for a in annots:
        groups.setdefault(a.annot_id, []).append(a)

    # 全局：出现在白文本系统 / 后世评点本 / 脂批原生系的批语 id
    white_ids = {
        a.annot_id for a in annots if VersionCode(a.version) in WHITE_TEXT
    }
    post_ids = {
        a.annot_id for a in annots if VersionCode(a.version) in POST_LIPING
    }
    native_ids = {
        a.annot_id for a in annots if VersionCode(a.version) in LIPO_NATIVE
    }

    for gid, grp in groups.items():
        cons = consistency_check(grp)
        attr = attribute(grp, cons)
        # —— 全局归因修正（先于断代，保证年代结论一致）——
        if gid in post_ids and gid not in native_ids:
            # 仅见于后世评点/托名本、脂本系统无承袭 → 伪造（对称于 CLEANED）
            attr["labels"] = sorted((set(attr["labels"]) - {"LATER_ADDITION"}) | {"FORGED"})
        elif gid not in white_ids:
            # 脂本内部清洗：某批语在脂本系统部分为共有、却缺失于另一脂本
            # （早有晚无 / 某脂本删批），且文本与位置无变异 → 清洗痕迹。
            # 注意：程高本"白文本化"是系统级事实，不逐条标 CLEANED，
            # 仅作五轴/版本背景的硬知识（脂批自 1791 退出主流流传）。
            present_vers = [VersionCode(a.version) for a in grp
                            if VersionCode(a.version) in LIPO_NATIVE]
            absent = []
            for a in grp:
                absent += [VersionCode(x) for x in a.absent_in]
            if (present_vers
                    and len({a.text for a in grp}) <= 1
                    and len({a.position for a in grp}) == 1
                    and any(v in LIPO_NATIVE for v in absent)):
                attr["labels"] = sorted(set(attr["labels"]) | {"CLEANED"})
        dat = date_version(grp, attr)
        for a in grp:
            a.consistency = cons
            a.attribution = {
                "label": "/".join(attr["labels"]),
                "confidence": attr["confidence"],
                "annotator": attr["annotator"],
            }
            a.dating = dat

    nodes = [a.to_jsonld() for a in annots]
    # 脂批-正文剥离：批语独立成库，正文锚点留 selector
    annotations_db = [
        {
            "annot_id": a.annot_id,
            "chapter": a.chapter,
            "position": a.position,
            "text": a.text,
            "version": a.version,
            "selector": a.selector,
            "consistency": a.consistency,
            "attribution": a.attribution,
            "dating": a.dating,
        }
        for a in annots
    ]
    # 真批集合（剔除伪造/后世加批/定向作伪隔离批次/篡改/误植/待去污染）。
    # 注①：靖藏本 150 条（JINGZANG）属定向作伪隔离批次 → 整批 FORGED，不计入 authentic_set。
    # 注②：CONTAMINATED_REF（其他无载体混合样本）既非真批亦非定伪，需逐条去污染后重新归类。
    # 注③：TAMPERED/COPYIST_ERROR 虽可能源出真批，但当前形态已失真（文本变异/位置错置），
    #      须先复原再入库，故一律排除；LAYERED 与 CLEANED 属真批的正常流传形态，可纳入。
    BLOCKING = {
        "FORGED", "LATER_ADDITION", "CONTAMINATED_REF",
        "TAMPERED", "COPYIST_ERROR", "WHITE_TEXT_ANOMALY",
    }
    # 分层：原生真批 vs 重构层——重构本（余西/库伦）批语须与脂批原生层分别计数，
    # 避免"重构层雅化批"污染原生统计（见 position-taxonomy.md 七、执行边界）。
    authentic_ids: list[str] = []
    recon_ids: list[str] = []
    for n in annotations_db:
        labels = set(n["attribution"]["label"].split("/"))
        if labels & BLOCKING:
            continue
        if not (labels & {"AUTHENTIC", "LAYERED", "CLEANED"}):
            continue
        bucket = recon_ids if n["dating"]["era"].startswith("1775 后") else authentic_ids
        if n["annot_id"] not in bucket:
            bucket.append(n["annot_id"])

    return {
        "annotations_db": annotations_db,     # 独立批语数据集（脂批-正文剥离结果）
        "authentic_set": authentic_ids,       # 脂批原生真批（去重，已剔伪/篡改/误植/隔离批次）
        "reconstructed_set": recon_ids,       # 重构层（余西/库伦雅化，单列不混入原生统计）
        "nodes_jsonld": nodes,
    }


def write_outputs(result: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(result["annotations_db"], f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "text_clean_anchors.json"), "w", encoding="utf-8") as f:
        # 正文剥离概念：仅保留 selector 锚点，正文回归纯净文本（此处示意）
        json.dump(
            [{"annot_id": n["annot_id"], "selector": n["selector"]} for n in result["annotations_db"]],
            f, ensure_ascii=False, indent=2,
        )
    with open(os.path.join(outdir, "authentic_set.json"), "w", encoding="utf-8") as f:
        json.dump(result["authentic_set"], f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "reconstructed_set.json"), "w", encoding="utf-8") as f:
        json.dump(result["reconstructed_set"], f, ensure_ascii=False, indent=2)
    print(f"[OK] 输出已写入：{outdir}")
    print(f"     批语条目总数：{len(result['annotations_db'])}（含同批语跨版本重复条目）")
    print(f"     原生真批：{len(result['authentic_set'])} 条"
          f"（已剔除伪造/后世加批/篡改/误植/定向作伪隔离批次）")
    print(f"     重构层  ：{len(result['reconstructed_set'])} 条（余西/库伦雅化，单列不混入原生）")


# --------------------------------------------------------------------------
# 七、Demo 数据（覆盖全部归因标签）
# --------------------------------------------------------------------------
def demo_entries() -> list[dict]:
    return [
        # ZP-001：脂批原生、跨甲戌/庚辰一致 → AUTHENTIC（真批）
        {"annot_id": "ZP-001", "chapter": 13, "version": "JIAXU",
         "position": "MEIPIAN", "text": "秦可卿淫丧天香楼，作者用史笔也。", "selector": "p1-top", "l2": "叙事引导", "l3": "痛惜"},
        {"annot_id": "ZP-001", "chapter": 13, "version": "GENGCHEN",
         "position": "MEIPIAN", "text": "秦可卿淫丧天香楼，作者用史笔也。", "selector": "p1-top", "l2": "叙事引导", "l3": "痛惜"},

        # ZP-002：甲戌眉批，庚辰变夹批（位置漂移但文本同）→ COPYIST_ERROR 误植
        {"annot_id": "ZP-002", "chapter": 27, "version": "JIAXU",
         "position": "MEIPIAN", "text": "玉兄若见此批，必长叹。", "selector": "p5-top", "l2": "情感评价", "l3": "悲悯"},
        {"annot_id": "ZP-002", "chapter": 27, "version": "GENGCHEN",
         "position": "JIABI", "text": "玉兄若见此批，必长叹。", "selector": "p5-inline", "l2": "情感评价", "l3": "悲悯"},

        # ZP-003：甲戌/庚辰同位置、文本微异（梯度变异）→ TAMPERED 篡改
        {"annot_id": "ZP-003", "chapter": 42, "version": "JIAXU",
         "position": "HUIMOBIPI", "text": "此回借画园，暗讽盐政奢靡。", "selector": "p9-end", "l2": "制度评析", "l3": "讽刺"},
        {"annot_id": "ZP-003", "chapter": 42, "version": "GENGCHEN",
         "position": "HUIMOBIPI", "text": "此回借画园，暗讽盐政之奢靡。", "selector": "p9-end", "l2": "制度评析", "l3": "讽刺"},

        # ZP-004：靖藏本 150 条之一 → DEFINED FORGED（定向作伪）·整批隔离。
        # 判伪理由在"版本/文献溯源层"：批语文本与俞平伯《脂砚斋红楼梦辑评》逐字重合
        # → 时代错置(anachronism)。绝不以"无正文载体/皮之不存"等小说文本层理由判伪。
        {"annot_id": "ZP-004", "chapter": 56, "version": "JINGZANG",
         "position": "ZONGBI", "text": "雪香囊十二对，此乃后人所补。", "selector": "",
         "l2": "元叙事", "l3": "中性", "has_carrier": False},

        # ZP-005：余西重构本独有带雅化 → 重构层（1775后）
        {"annot_id": "ZP-005", "chapter": 81, "version": "YUXI",
         "position": "HUISHOUBIPI", "text": "余西盐课司本：自八十一回，盐案渐起。", "selector": "p1-head", "l2": "制度评析", "l3": "敬畏"},

        # ZP-006：同位置同回甲戌+庚辰+戚序累积 → LAYERED 层积
        {"annot_id": "ZP-006", "chapter": 5, "version": "JIAXU",
         "position": "CEBI", "text": "判词早定，千红一哭。", "selector": "p3-side", "l2": "叙事引导", "l3": "极悲"},
        {"annot_id": "ZP-006", "chapter": 5, "version": "GENGCHEN",
         "position": "CEBI", "text": "判词早定，千红一哭。", "selector": "p3-side", "l2": "叙事引导", "l3": "极悲"},
        {"annot_id": "ZP-006", "chapter": 5, "version": "QIXU",
         "position": "CEBI", "text": "判词早定，千红一哭。", "selector": "p3-side", "l2": "叙事引导", "l3": "极悲"},

        # ZP-007：甲戌+庚辰同文本同位置，梦稿本（MENGAO）删此批 → CLEANED 清洗痕迹
        {"annot_id": "ZP-007", "chapter": 8, "version": "JIAXU",
         "position": "CEBI", "text": "此处旧有极警醒语，后被删。", "selector": "p2-side",
         "l2": "叙事引导", "l3": "隐忍"},
        {"annot_id": "ZP-007", "chapter": 8, "version": "GENGCHEN",
         "position": "CEBI", "text": "此处旧有极警醒语，后被删。", "selector": "p2-side",
         "l2": "叙事引导", "l3": "隐忍", "absent_in": ["MENGAO"]},
    ]


def main():
    ap = argparse.ArgumentParser(description="脂批位置分类与版本断代代码化引擎")
    ap.add_argument("--input", help="批注条目 JSON 路径")
    ap.add_argument("--outdir", default="out", help="输出目录")
    ap.add_argument("--demo", action="store_true", help="运行内置示例（三向校验/反向归因）")
    ap.add_argument("--axis-check", action="store_true", help="运行五轴对齐断伪校验示例")
    args = ap.parse_args()

    if args.axis_check:
        run_axis_demo()
        return

    if args.demo or not args.input:
        entries = demo_entries()
        print("[DEMO] 运行内置示例（触发 AUTHENTIC/COPYIST_ERROR/TAMPERED/CLEANED/FORGED(靖藏定向作伪·隔离)/重构层/LAYERED；CONTAMINATED_REF 仅用于其他无载体混合样本）\n")
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            entries = json.load(f)

    result = run(entries)
    if args.demo or not args.input:
        print("=== 归因汇总 ===")
        for n in result["annotations_db"]:
            a = n["attribution"]
            d = n["dating"]
            print(f"  {n['annot_id']:8} [{n['version']:8}] {n['position']:12} -> "
                  f"{a['label']:22} conf={a['confidence']} | {d['era']}")
        print(f"\n原生真批集合（剔伪造/后世加批/篡改/误植/隔离批次）：{result['authentic_set']}")
        print(f"重构层集合（余西/库伦，单列不混入原生统计）：{result['reconstructed_set']}\n")
    else:
        write_outputs(result, args.outdir)


if __name__ == "__main__":
    main()
