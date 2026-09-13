#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从既有 v2 docx 抽取结构化数据，重构为 gen_drug_target_report.py 的 data.json。
演示「检索 -> 填充 data.json -> 生成固定格式报告」工作流。"""
import json, sys
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

SRC = sys.argv[1] if len(sys.argv) > 1 else "D:/WorkBuddy/肿瘤临床开发/KRAS_G12D_临床最新进展_检索报告_20260717_v2.docx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data_kras_g12d.json"

def iter_blocks(doc):
    body = doc.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)

doc = Document(SRC)

data = {
    "meta": {
        "topic": "KRAS G12D 靶点药物在胰腺癌的临床数据",
        "target": "KRAS G12D",
        "search_date": "2026-07-17",
        "search_scope": ["PubMed", "ASCO 2026", "AACR 2026", "ESMO 2025", "CSCO 2025", "WebSearch"],
        "keywords": ["KRAS G12D", "pancreatic cancer", "inhibitor", "clinical trial", "胰腺癌", "临床试验"],
        "date_range": "2023-01-01 至 2026-07-17",
        "pubmed_count": 390,
        "conference_count": 22,
        "tools": ["PubMed E-utilities API", "WebSearch", "WebFetch"]
    },
    "summary_small_molecule": [],
    "summary_non_small_molecule": [],
    "drug_details": [],
    "conference_data": [],
    "resistance_mechanisms": [],
    "pubmed_refs": [],
    "conclusion": []
}

cur_h1 = cur_h2 = None
drug = None
cur_block = None

for blk in iter_blocks(doc):
    if isinstance(blk, Paragraph):
        txt = blk.text.strip()
        if not txt:
            continue
        style = blk.style.name if blk.style else ""
        if style == "Heading 1":
            cur_h1, cur_h2 = txt, None
            drug, cur_block = None, None
            continue
        if style == "Heading 2":
            cur_h2 = txt
            if cur_h1 and cur_h1.startswith("二"):
                name = txt.split(" — ")[0] if " — " in txt else txt
                company = txt.split(" — ")[1] if " — " in txt else ""
                drug = {"name": name, "company": company, "content": []}
                data["drug_details"].append(drug)
                cur_block = None
            elif cur_h1 and cur_h1.startswith("三"):
                data["conference_data"].append({"conf": txt, "items": []})
            continue
        # Normal / List Bullet
        if cur_h1 and cur_h1.startswith("二") and drug is not None:
            is_bullet = (style == "List Bullet")
            if txt.startswith("机制") and "：" in txt and not drug.get("mechanism"):
                drug["mechanism"] = txt.split("：", 1)[1]
            elif ("主要研究者" in txt or "报告人" in txt or ("PI" in txt and "：" in txt)) and not drug.get("pi"):
                drug["pi"] = txt
            elif ("试验注册" in txt or "CTR" in txt or "NCT" in txt or "ChiCTR" in txt) and not drug.get("trial_reg"):
                drug["trial_reg"] = txt
            elif is_bullet:
                if cur_block is None or "p" in cur_block:
                    cur_block = {"h": "", "bullets": []}
                    drug["content"].append(cur_block)
                cur_block["bullets"].append(txt)
            elif txt.endswith("：") or txt.startswith(("ASCO", "AACR", "ESMO", "CSCO", "III 期", "I 期", "II 期")):
                cur_block = {"h": txt, "bullets": []}
                drug["content"].append(cur_block)
            elif txt.startswith("要点概括"):
                drug["content"].append({"p": txt})
                cur_block = None
            else:
                if drug.get("mechanism") is None and cur_block is None:
                    drug["mechanism"] = txt
                else:
                    cur_block = {"h": txt, "bullets": []}
                    drug["content"].append(cur_block)
        elif cur_h1 and (cur_h1.startswith("四") or cur_h1.startswith("六")):
            if style == "List Bullet":
                data["resistance_mechanisms" if cur_h1.startswith("四") else "conclusion"].append(txt)
    else:  # Table
        hdr = [c.text.strip() for c in blk.rows[0].cells]
        if hdr[:1] == ["品种"] and cur_h1 and cur_h1.startswith("一"):
            target = data["summary_small_molecule"] if hdr[1] == "开发企业" else data["summary_non_small_molecule"]
            for r in blk.rows[1:]:
                c = [x.text.strip() for x in r.cells]
                target.append({"drug": c[0], "company": c[1], "progress": c[2],
                               "tumors": c[3], "efficacy": c[4], "safety": c[5]})
        elif hdr[:1] in (["摘要号"], ["专场"]) and data["conference_data"]:
            conf = data["conference_data"][-1]
            for r in blk.rows[1:]:
                c = [x.text.strip() for x in r.cells]
                if hdr[0] == "专场":
                    conf["items"].append({"abstract": "", "drug": c[1], "tumor": c[2], "key_data": c[3], "session": c[0]})
                else:
                    conf["items"].append({"abstract": c[0], "drug": c[1], "tumor": c[2], "key_data": c[3], "session": ""})
        elif hdr[:1] == ["耐药机制"]:
            for r in blk.rows[1:]:
                c = [x.text.strip() for x in r.cells]
                data["resistance_mechanisms"].append(f"{c[0]}：{c[1]}（来源：{c[2]}）")
        elif hdr[:1] == ["#"]:
            for r in blk.rows[1:]:
                c = [x.text.strip() for x in r.cells]
                data["pubmed_refs"].append({"pmid": c[1], "type": c[2], "doi": c[3],
                                            "title": c[4], "first_author": c[5], "journal": c[6], "year": c[7]})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] 写出 {OUT}")
print(f"  综合汇总表(小分子): {len(data['summary_small_molecule'])} 行")
print(f"  综合汇总表(非小分子): {len(data['summary_non_small_molecule'])} 行")
print(f"  重点药物详情: {len(data['drug_details'])} 个")
for d in data["drug_details"]:
    print(f"    - {d['name']} (content blocks={len(d['content'])})")
print(f"  会议分组: {len(data['conference_data'])} 个 -> " + ", ".join(c['conf'] for c in data['conference_data']))
print(f"  耐药机制: {len(data['resistance_mechanisms'])} 条")
print(f"  PubMed 文献: {len(data['pubmed_refs'])} 篇")
print(f"  总结条目: {len(data['conclusion'])} 条")
