#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 V1.1 schema 的 data.json 转换为 V1.1.1 schema（用于迁移旧报告）。"""
import json
import sys


def derive_phase(progress):
    p = (progress or "").replace(" ", "")
    for key in ["已上市", "III期", "注册性临床", "II期", "I/II期", "I期", "IND", "临床前"]:
        if key in p:
            return key
    return "其他"


def norm(s):
    return "".join(str(s).split()).lower()


def main():
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, "r", encoding="utf-8") as f:
        d = json.load(f)

    meta = d.get("meta", {})
    new_meta = {
        "topic": meta.get("topic", ""),
        "target": meta.get("target", ""),
        "search_date": meta.get("search_date", ""),
        "search_scope": "；".join(meta.get("search_scope", [])) if isinstance(meta.get("search_scope"), list) else meta.get("search_scope", ""),
        "date_range": meta.get("date_range", ""),
        "tools": "；".join(meta.get("tools", [])) if isinstance(meta.get("tools"), list) else meta.get("tools", ""),
        "keywords": "；".join(meta.get("keywords", [])) if isinstance(meta.get("keywords"), list) else meta.get("keywords", ""),
    }

    background = (
        "KRAS G12D 是胰腺癌（PDAC）中最常见的驱动突变，约 40% 的 PDAC 携带该突变，"
        "在结直肠癌、胆道癌、非小细胞肺癌等实体瘤中亦有分布。G12D 突变导致 KRAS 蛋白持续处于 GTP 结合（激活）态，"
        " constitutively 激活下游 RAF-MEK-ERK 与 PI3K 通路，驱动肿瘤增殖与存活。\n\n"
        "PDAC 整体预后极差，五年生存率不足 13%；后线治疗客观缓解率（ORR）常低于 10%、中位总生存（mOS）约 6 个月，"
        "存在巨大的未满足临床需求。长期以来 KRAS 被视为\"不可成药\"靶点，直至 KRAS G12C 抑制剂获批才被打破；"
        "而占比更高、临床需求更迫切的 G12D 亚型，其靶向药物直到近年才集中进入临床，当前尚无任何 KRAS G12D 选择性抑制剂获批上市。"
    )

    # 综合汇总表（小分子），补充 phase 字段，统一 tumor 字段名
    sm = d.get("summary_small_molecule", [])
    rows = []
    phase_by_drug = {}
    for r in sm:
        ph = derive_phase(r.get("progress", ""))
        drug = r.get("drug", "")
        rows.append({
            "drug": drug,
            "company": r.get("company", ""),
            "progress": r.get("progress", ""),
            "phase": ph,
            "tumor": r.get("tumors", r.get("tumor", "")),
            "efficacy": r.get("efficacy", ""),
            "safety": r.get("safety", ""),
        })
        # 建立 名称->phase 映射，供重点药物排序
        base = norm(drug).split("(")[0]
        phase_by_drug[base] = ph

    # 重点药物详情：补充 phase
    details = []
    for dt in d.get("drug_details", []):
        name = dt.get("name", "")
        ph = "其他"
        nname = norm(name)
        for base, p in phase_by_drug.items():
            if nname.startswith(base) or base.startswith(nname[:6]):
                ph = p
                break
        new_dt = dict(dt)
        new_dt["phase"] = ph
        details.append(new_dt)

    # 非主流开发方向：非小分子模态
    nsm = d.get("summary_non_small_molecule", [])
    nm_rows = [{
        "drug": r.get("drug", ""),
        "company": r.get("company", ""),
        "progress": r.get("progress", ""),
        "phase": derive_phase(r.get("progress", "")),
        "tumor": r.get("tumors", r.get("tumor", "")),
        "efficacy": r.get("efficacy", ""),
        "safety": r.get("safety", ""),
    } for r in nsm]
    non_mainstream = {
        "analysis": (
            "非小分子模态（TCR-T / siRNA / 疫苗 / 外泌体 / 抗体等）多聚焦于辅助、维持或免疫联合场景，"
            "机制与给药路径与小分子抑制剂差异显著，不作本次重点。其在术后辅助治疗、ctDNA 阴性转化、"
            "以及联合免疫检查点抑制剂等方向具备差异化价值，是 G12D 综合治疗图景的重要补充。"
        ),
        "rows": nm_rows,
    }

    # 结论：重构为 {title: points}
    concl = d.get("conclusion", [])
    conclusion = [
        {"title": "临床进展与阶段梯队", "points": concl[0:6]},
        {"title": "联合治疗方向", "points": [concl[6]] if len(concl) > 6 else []},
        {"title": "耐药机制", "points": [concl[7]] if len(concl) > 7 else []},
        {"title": "非主流模态", "points": [concl[8]] if len(concl) > 8 else []},
        {"title": "核心适应症", "points": [concl[9]] if len(concl) > 9 else []},
        {"title": "中国市场与获批预期", "points": [concl[10]] if len(concl) > 10 else []},
    ]
    conclusion = [c for c in conclusion if c["points"]]

    out = {
        "meta": new_meta,
        "background": background,
        "summary_table": {"rows": rows},
        "drug_details": details,
        "non_mainstream": non_mainstream,
        "conference_data": d.get("conference_data", []),
        "resistance_mechanisms": d.get("resistance_mechanisms", []),
        "pubmed_refs": d.get("pubmed_refs", []),
        "conclusion": conclusion,
    }
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[OK] V1.1 -> V1.1.1 转换完成: {outp}")
    print(f"  summary rows={len(rows)} drug_details={len(details)} "
          f"non_mainstream={len(nm_rows)} pubmed={len(out['pubmed_refs'])}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: transform_v11_to_v111.py <in.json> <out.json>", file=sys.stderr)
        sys.exit(2)
    main()
