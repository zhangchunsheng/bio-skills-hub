#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seed_registry.py — 写入仿制药调研成长库基线（首次运行或重置用）
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
    "products": {
        "仿制药立项优先级评估要素": {
            "name": "仿制药立项优先级评估要素",
            "last_checked": TODAY,
            "source": "seed-baseline(待regulatory-monitor/NMPA核验)",
            "content": "评估某仿制品种优先级需综合：①参比制剂（RLD/官方目录）可得性与可替代性；②原研专利到期与壁垒（化合物/制剂/工艺/用途）；③国内上市与申报状态（已上市/在审/未进口）；④市场容量与患者基数；⑤技术难度（剂型/无菌/复杂制剂）；⑥集采风险与利润空间。眼科/耳科局部制剂另加 BE 路径可行性。",
            "note": "通用评估框架，具体品种数据须以 CDE/企业年报核实"
        }
    },
    "patents": {
        "美国橙皮书与PIV专利挑战": {
            "name": "美国橙皮书与PIV专利挑战",
            "last_checked": TODAY,
            "source": "seed-baseline(待USPTO/Orange Book核验)",
            "content": "美国橙皮书（Orange Book）列明原研药品相关专利与 exclusivity。仿制药申请人提交 PIV 声明（专利无效或不予执行）可发起专利挑战，首个挑战成功者获 180 天市场独占期（first-filer exclusivity）。中国对应为专利声明（一类至四类）与专利链接制度，以 CNIPA 为准。",
            "note": "首访/首仿机会的核心制度基础"
        }
    },
    "be_registry": {
        "局部作用制剂BE豁免与质量一致替代证据": {
            "name": "局部作用制剂BE豁免与质量一致替代证据",
            "last_checked": TODAY,
            "source": "seed-baseline(待FDA/CDE guidance核验)",
            "content": "滴眼剂、滴耳剂等局部作用制剂通常不要求全身 BA/BE，而以质量一致作为等效证据：溶出/释放（IVRT/IVPT）、粒度（PSD）、流变、pH/渗透压、无菌/抑菌效力、含量均匀度等。FDA 有 ophthalmic 与 topical 的 BA/BE 替代证据指南（Q&A）。具体以 regulatory-monitor 拉取最新版为准。",
            "note": "区别于全身作用口服固体制剂的 BE 要求"
        }
    },
    "market": {
        "国家集采对仿制药的影响": {
            "name": "国家集采对仿制药的影响",
            "last_checked": TODAY,
            "source": "seed-baseline(待官方集采结果核验)",
            "content": "仿制药通过一致性评价后可参与国家/省级带量采购，中选价格通常大幅下降。立项须关注：同品种过评家数、竞争格局、中选价格与降幅、剩余量市场。眼科/耳科部分品种亦已纳入集采视野，需提前评估利润空间。",
            "note": "集采常态化下，仿制利润依赖成本与过评速度"
        }
    },
    "ocular_otic": {
        "眼科仿制核心难点": {
            "name": "眼科仿制核心难点",
            "last_checked": TODAY,
            "source": "seed-baseline(待ChP/CDE核验)",
            "content": "眼科局部用药难点：角膜前滞留<5min、眼底生物利用度常<5%、防腐剂（BAK）累积毒性、单剂量无防腐（BFS）趋势。眼用混悬/凝胶以 IVRT/流变/粒度等质量一致证据替代 BE。仿制须重现原研的递送表现与安全性特征。",
            "note": "联动 formulation-dev-assistant 与 RL009 单剂量瓶专题"
        },
        "耳科局部仿制特征": {
            "name": "耳科局部仿制特征",
            "last_checked": TODAY,
            "source": "seed-baseline(待ChP 0112核验)",
            "content": "滴耳剂多为溶液或混悬，耳用制剂可含抗真菌/抗细菌成分，局部作用同样倾向质量一致证据。耳道容积有限、黏度需适中利于铺展与滞留。仿制重点在处方重现、无菌与抑菌效力、局部耐受性。",
            "note": "参照中国药典 0112 耳用制剂"
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
