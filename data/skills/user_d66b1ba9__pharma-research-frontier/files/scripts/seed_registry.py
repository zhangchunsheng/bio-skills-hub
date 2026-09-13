#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seed_registry.py — 写入医药前沿研究成长库基线（首次运行或重置用）
依赖：同目录 registry_cli.py 的 DB 路径约定。
用法：python3 seed_registry.py
"""
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "registry.json")
TODAY = date.today().isoformat()

BASELINE = {
    "meta": {"last_full_refresh": TODAY, "version": 1, "freshness_months": 6},
    "trends": {
        "医药前沿治疗模态概览": {
            "name": "医药前沿治疗模态概览",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献核验)",
            "content": "当前前沿模态：基因治疗（AAV/CRISPR）、RNA 药物（siRNA/ASO）、细胞治疗、核酸与新型递送、AI 驱动药物设计、微生物组疗法。成熟度差异大，立项须按 TRL 分层。眼科/耳科因未满足需求大、专科药少、局部/靶向递送价值高，是前沿转化高潜力区。",
            "note": "TRL 分层避免把论文当产品"
        }
    },
    "papers": {
        "顶刊与会议信号源": {
            "name": "顶刊与会议信号源",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献核验)",
            "content": "高价值信号源：NEJM/Nature/Science/Cell 及子刊、Ophthalmology、JARO 等；会议：ARVO、AAO、TRIO。关注重磅临床读出、机制突破与监管信号（突破性疗法/孤儿药）。须标注期刊/会议、年份与阶段，区分已发表与摘要。",
            "note": "信号源质量决定研判可靠性"
        }
    },
    "platforms": {
        "眼/耳递送技术平台": {
            "name": "眼/耳递送技术平台",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献核验)",
            "content": "眼部：玻璃体腔、结膜下、角膜前、视网膜下给药；技术含纳米粒、原位凝胶、基因载体（AAV）、植入缓释。耳部：鼓室、耳蜗给药；技术含纳米递送、基因/细胞递送、缓释。内耳靶向与屏障穿透是耳科核心难点。",
            "note": "递送平台决定局部新药可行性"
        },
        "基因递送载体(AAV/脂质体)": {
            "name": "基因递送载体(AAV/脂质体)",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献核验)",
            "content": "AAV 具组织趋向性（不同血清型靶向视网膜/耳蜗等），是体内基因治疗主流载体；LNP 用于 siRNA/mRNA 递送。眼科视网膜下/玻璃体给药路径成熟（已有获批产品佐证赛道）。耳蜗基因递送仍处攻坚期。",
            "note": "载体选择直接决定靶向与安全性"
        }
    },
    "ocular_otic": {
        "眼科前沿方向": {
            "name": "眼科前沿方向",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献/监管核验)",
            "content": "基因治疗（RPE65 介导视网膜营养不良已有获批产品佐证赛道）、抗 VEGF 更长间隔/新机制、视网膜色素变性/AMD 的基因与细胞治疗、人工视觉/光遗传、干眼机制新靶点、青光眼神经保护。眼科是基因治疗在体验证最成熟的专科之一。",
            "note": "联动 new-drug-intel 与 new-drug-research-expert"
        },
        "耳科前沿方向": {
            "name": "耳科前沿方向",
            "last_checked": TODAY,
            "source": "seed-baseline(待文献核验)",
            "content": "感音神经性聋毛细胞再生（Notch 抑制、Atoh1）、耳蜗基因/细胞治疗、人工耳蜗之外的药物干预、眩晕（梅尼埃病）机制与新靶点、中耳炎局部新疗法。耳科在研药物显著少于眼科，差异化前沿窗口明显，但转化不确定性更高。",
            "note": "与 new-drug-intel / 立项联动"
        }
    }
}


def main():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(BASELINE, f, ensure_ascii=False, indent=2)
    print("SEED_OK", DB, TODAY)


if __name__ == "__main__":
    main()
