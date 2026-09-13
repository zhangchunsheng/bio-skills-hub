"""
基金经理蒸馏引擎模块
两级 fallback：对话 LLM（零安装，由 agent 执行）-> 规则引擎（无依赖）
支持季报转人话（icbc式）+ 思维 DNA 提炼（女娲式）。
"""

import os
import re
import json
from datetime import datetime

import _common
from _common import http_get, read_json, write_json, log, load_manager, save_manager, REFERENCES_DIR

# 蒸馏 prompt 文件路径
PROMPTS_PATH = os.path.join(REFERENCES_DIR, "distill-prompts.md")

# 行业关键词映射（用于规则引擎）
INDUSTRY_KEYWORDS = {
    "科技": ["腾讯", "阿里巴巴", "中芯国际", "东山精密", "宁德时代", "立讯精密", "中际旭创", "科大讯飞", "海康威视", "紫光国微", "北方华创"],
    "消费": ["贵州茅台", "五粮液", "泸州老窖", "山西汾酒", "百胜中国", "美的集团", "格力电器", "伊利股份", "古井贡酒", "今世缘"],
    "金融": ["中国平安", "招商银行", "兴业银行", "工商银行", "中信证券", "东方财富", "宁波银行"],
    "能源": ["中国海洋石油", "紫金矿业", "中国石油", "中国石化", "陕西煤业", "兖矿能源"],
    "医药": ["恒瑞医药", "药明康德", "迈瑞医疗", "爱尔眼科", "通策医疗", "泰格医药"],
    "制造": ["三一重工", "汇川技术", "隆基绿能", "通威股份", "福斯特"],
}

# 投资风格关键词
STYLE_KEYWORDS = {
    "价值": ["估值", "安全边际", "低估值", "价值投资", "现金流", "分红", "ROE", "PB"],
    "成长": ["成长性", "增速", "赛道", "创新", "渗透率", "空间", "景气度", "高增长"],
    "均衡": ["均衡", "平衡", "分散", "多策略", "灵活配置", "核心卫星"],
    "量化": ["量化", "因子", "指数增强", "alpha", "beta", "多因子"],
}


def prepare_distill_materials(manager_id):
    """
    准备蒸馏素材：收集经理的投资策略、重仓、业绩等数据。
    如果数据不完整，返回已有部分并标注缺失。
    返回: {manager_id, name, company, strategy_texts, top_holdings, performance, ...}
    """
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在，请先添加到名单并抓取数据"}

    materials = {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        "company": mgr.get("company", ""),
        "products": mgr.get("fund_names", []) or [p.get("name", "") for p in mgr.get("products", [])],
        "tenure_return": mgr.get("tenure_return", ""),
        "strategy_texts": mgr.get("strategy_texts", []),
        "top_holdings": mgr.get("top_holdings", []),
        "holdings_report_date": mgr.get("holdings_report_date", ""),
        "performance": mgr.get("performance", {}),
        "invest_idea": mgr.get("invest_idea", ""),
    }

    # 检查数据完整性
    missing = []
    if not materials["strategy_texts"]:
        missing.append("投资策略")
    if not materials["top_holdings"]:
        missing.append("十大重仓")
    if not materials["performance"]:
        missing.append("业绩数据")
    materials["missing"] = missing

    if missing:
        log.warning(f"经理 {manager_id} 缺少数据：{', '.join(missing)}，建议先运行数据抓取")

    return materials


def detect_distill_engine():
    """
    检测可用的蒸馏引擎。
    返回: "rules"
    注意："对话LLM"模式不在此检测，因为它由 agent 直接执行（distill_manager.py 生成任务）。
    """
    log.info("使用规则引擎（对话 LLM 模式由 agent 通过 task 命令触发）")
    return "rules"


def _detect_top_industries(holdings, strategy_text=""):
    """
    从重仓股名称和策略文本中识别行业偏好（规则方式）。
    返回: (top_industries[(行业, 得分), ...] 最多3个, industry_scores dict)
    """
    industry_scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = 0.0
        for h in holdings:
            for kw in keywords:
                if kw in h.get("name", ""):
                    # 使用持仓占比加权（total_ratio 是聚合后的总占比，为 float）
                    score += h.get("total_ratio", 0) or 0
        # 也从策略文本中检测（策略文本中的提及给予少量加分）
        for kw in keywords:
            if kw in strategy_text:
                score += 0.5
        if score > 0:
            industry_scores[industry] = round(score, 2)

    top_industries = sorted(industry_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return top_industries, industry_scores


def _generate_viewpoint_from_holdings(holdings, top_industries, concentration, conc_desc, strategy_texts, manager_name=""):
    """
    从持仓数据生成投资观点摘要（替代从法律模板文本中提取"观点"）。
    规则引擎无法读取 PDF 季报中的真实投资观点，因此基于持仓分析生成有意义的摘要。
    """
    if not holdings:
        return "暂无足够数据生成投资观点。"

    # 1. 从持仓推断核心投资方向
    top3 = holdings[:3]
    top3_names = [h.get("name", "") for h in top3 if h.get("name")]
    top3_str = "、".join(top3_names) if top3_names else ""

    # 2. 行业偏好
    industry_str = ""
    if top_industries:
        industry_str = "、".join([i[0] for i in top_industries[:3]])

    # 3. 持仓特征
    total_top10 = sum(h.get("total_ratio", 0) for h in holdings[:10])
    if concentration == "SECTOR_CONCENTRATED" or total_top10 > 60:
        position_style = "高度集中"
    elif total_top10 > 35:
        position_style = "适度分散"
    else:
        position_style = "广泛分散"

    # 4. 市场覆盖判断（v2.1 修复：跳过空代码，避免空 code 被误判为海外）
    has_hk = any(h.get("code", "").startswith("0") and len(h.get("code", "")) == 5 for h in holdings)
    has_us = any(
        (h.get("code", "") and not h.get("code", "").isdigit())
        or (h.get("code", "") and len(h.get("code", "")) <= 4 and h.get("code", "").isalpha())
        for h in holdings
    )
    market_desc = ""
    if has_hk and has_us:
        market_desc = "涵盖A股、港股和海外市场"
    elif has_hk:
        market_desc = "重点关注A股和港股市场"
    elif has_us:
        market_desc = "涵盖A股和海外市场"
    else:
        market_desc = "主要聚焦A股市场"

    # 5. 生成第一人称观点
    parts = []
    if top3_str:
        parts.append(f"我当前重仓持有{top3_str}")
    if industry_str:
        parts.append(f"重点关注{industry_str}板块的投资机会")
    if position_style:
        parts.append(f"持仓风格{position_style}")
    parts.append(f"投资视野{market_desc}")

    viewpoint = "。".join(parts) + "。"
    # 长度控制
    if len(viewpoint) > 200:
        viewpoint = viewpoint[:197] + "..."

    return viewpoint


def distill_with_rules(materials):
    """
    规则引擎蒸馏：用关键词/持仓规则生成风格标签和摘要。
    零 LLM 依赖，质量有限但保证可用。
    返回: {style_tags, industry_preference, style_code, bio, viewpoint_human}
    """
    holdings = materials.get("top_holdings", [])
    strategy_texts = materials.get("strategy_texts", [])
    all_strategy = " ".join(strategy_texts)

    # 1. 行业偏好分析
    top_industries, industry_scores = _detect_top_industries(holdings, all_strategy)

    # 2. 投资风格分析
    style_scores = {}
    for style, keywords in STYLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in all_strategy)
        if score > 0:
            style_scores[style] = score

    if style_scores:
        top_style = max(style_scores, key=style_scores.get)
    else:
        top_style = "均衡"  # 默认

    # 3. 持仓集中度
    if holdings:
        total_ratio = sum(h.get("total_ratio", 0) for h in holdings[:10])
        if total_ratio > 70:
            concentration = "SECTOR_CONCENTRATED"
            conc_desc = "高度集中"
        elif total_ratio > 40:
            concentration = "SECTOR_BALANCED"
            conc_desc = "适度集中"
        else:
            concentration = "SECTOR_DIVERSED"
            conc_desc = "分散配置"
    else:
        concentration = "UNKNOWN"
        conc_desc = "未知"

    # 4. 市场覆盖
    has_hk = any(h.get("code", "").startswith("0") and len(h.get("code", "")) == 5 for h in holdings)
    market = "HK_STOCK" if has_hk else "A_SHARE"

    # 5. 风格标签码
    style_map = {"价值": "VALUE", "成长": "GROWTH", "均衡": "BALANCED", "量化": "QUANT"}
    style_code = f"{style_map.get(top_style, 'BALANCED')}-MED_POS-{concentration}-LOW_TURNOVER-{market}"

    # 6. 生成 bio（第一人称简介）
    name = materials.get("name", "该经理")
    company = materials.get("company", "")
    industry_str = "、".join([i[0] for i in top_industries]) if top_industries else "多领域"

    bio = f"我是{name}，现任{company}基金经理。我的投资风格偏向{top_style}，" \
          f"重点配置{industry_str}板块，持仓{conc_desc}。"
    if materials.get("tenure_return"):
        bio += f"任职以来累计回报{materials['tenure_return']}。"

    # 7. 生成 viewpoint_human
    # 注意：策略文本来自基金招募说明书（jbgk），是法律模板文本，不是季度报告的投资观点。
    # 规则引擎无法读取 PDF 季报中的真实观点，因此仅基于持仓数据生成摘要。
    viewpoint_human = _generate_viewpoint_from_holdings(
        holdings, top_industries, concentration, conc_desc, strategy_texts, name
    )

    return {
        "style_tags": [top_style, conc_desc],
        "industry_preference": [i[0] for i in top_industries],
        "industry_scores": industry_scores,
        "specialty": "、".join([i[0] for i in top_industries]),
        "style_code": style_code,
        "bio": bio,
        "viewpoint_human": viewpoint_human,
        "engine": "rules",
        "note": "由规则引擎生成，质量有限。建议在有 LLM 的环境下重新蒸馏以获得更深入的风格分析。",
    }


def generate_distill_task(manager_id):
    """
    生成蒸馏任务（供对话 LLM 执行）。
    返回一个结构化的蒸馏任务描述，包含素材和 prompt。
    agent 读取此任务后，用自身 LLM 能力执行蒸馏，再调用 apply_distill_result 写回结果。
    """
    materials = prepare_distill_materials(manager_id)
    if materials.get("error"):
        return materials

    # 格式化素材供 prompt 使用
    strategy_text = "\n---\n".join(materials.get("strategy_texts", [])) or "（暂无投资策略文本）"

    holdings_str = ""
    for h in materials.get("top_holdings", [])[:15]:
        ratio = h.get("total_ratio", h.get("ratio", ""))
        holdings_str += f"  {h.get('name','')} ({h.get('code','')}) - 占比{ratio}%, 出现{h.get('appear_count',1)}次\n"

    perf = materials.get("performance", {})
    perf_str = ""
    if perf:
        summary = perf.get("summary", {})
        for label, val in summary.get("avg_returns", {}).items():
            perf_str += f"  {label}: {val}%\n"

    # 加载 prompt 模板
    prompt_path = PROMPTS_PATH
    prompt_text = ""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()

    task = {
        "task_type": "distill_manager",
        "manager_id": manager_id,
        "manager_name": materials["name"],
        "company": materials["company"],
        "engine": "llm",
        "instruction": (
            f"请对基金经理 {materials['name']}（{materials['company']}）执行投资风格蒸馏。\n"
            f"1. 用「季报转人话 Prompt」把投资策略文本转为第一人称口吻（viewpoint_human）\n"
            f"2. 用「思维 DNA 提炼 Prompt」提炼投资思维 DNA（style_dna）\n"
            f"3. 完成后调用 apply_distill_result 写回结果\n\n"
            f"Prompt 模板见 references/distill-prompts.md\n"
        ),
        "materials": {
            "name": materials["name"],
            "company": materials["company"],
            "products": materials["products"],
            "tenure_return": materials["tenure_return"],
            "strategy_text": strategy_text,
            "top_holdings": holdings_str,
            "performance": perf_str,
            "missing": materials.get("missing", []),
        },
        "prompt_file": "references/distill-prompts.md",
        "output_fields": [
            "bio (第一人称投资风格简介, 80-150字)",
            "viewpoint_human (季报转人话, 80-200字)",
            "style_dna (思维DNA, 含决策框架/风格DNA/表达方式/能力边界/反模式)",
            "specialty (擅长领域标签)",
        ],
    }

    return task


def apply_distill_result(manager_id, result):
    """
    将蒸馏结果写回经理档案。
    result 可以来自对话 LLM 或规则引擎。
    """
    mgr = load_manager(manager_id)
    if not mgr:
        mgr = {"id": manager_id}

    # 应用各字段
    if result.get("bio"):
        mgr["bio"] = result["bio"]
    if result.get("viewpoint_human"):
        mgr["viewpoint_human"] = result["viewpoint_human"]
    if result.get("style_dna"):
        mgr["style_dna"] = result["style_dna"]
    if result.get("specialty"):
        mgr["specialty"] = result["specialty"]
    if result.get("style_tags"):
        mgr["style_tags"] = result["style_tags"]
    if result.get("industry_preference"):
        mgr["industry_preference"] = result["industry_preference"]
    if result.get("style_code"):
        mgr["style_code"] = result["style_code"]

    mgr["distill_engine"] = result.get("engine", "llm")
    mgr["distill_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 蒸馏结果已写入档案（引擎: {mgr['distill_engine']}）")

    # 更新名单状态（单次保存）
    try:
        import roster_manager
        roster_manager.mark_distilled(manager_id)
    except Exception:
        pass

    return {"success": True, "message": f"✅ {mgr.get('name','')} 蒸馏完成（引擎: {mgr['distill_engine']}）"}


def distill_manager(manager_id, engine="auto"):
    """
    主蒸馏函数。
    engine:
      - "auto": 检测可用引擎（-> rules）
      - "llm": 生成蒸馏任务供对话 LLM 执行（返回任务描述）
      - "rules": 用规则引擎蒸馏
    """
    log.info(f"开始蒸馏经理 {manager_id}（引擎: {engine}）")

    # 准备素材
    materials = prepare_distill_materials(manager_id)
    if materials.get("error"):
        return materials

    if engine == "llm":
        return generate_distill_task(manager_id)

    if engine == "auto":
        engine = detect_distill_engine()

    if engine == "rules":
        result = distill_with_rules(materials)
        return apply_distill_result(manager_id, result)

    return {"error": f"未知引擎: {engine}"}


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python distill_manager.py detect               # 检测可用引擎")
        print("  python distill_manager.py task <经理ID>        # 生成蒸馏任务(供LLM执行)")
        print("  python distill_manager.py distill <经理ID> [auto/rules]  # 执行蒸馏")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "detect":
        engine = detect_distill_engine()
        print(f"可用蒸馏引擎: {engine}")

    elif cmd == "task":
        mgr_id = sys.argv[2]
        task = generate_distill_task(mgr_id)
        if task.get("error"):
            print(task["error"])
        else:
            print(f"\n蒸馏任务：{task['manager_name']}（{task['company']}）")
            print(f"引擎: {task['engine']}")
            print(f"\n指令: {task['instruction']}")
            print(f"\n素材:")
            for k, v in task["materials"].items():
                print(f"  {k}: {str(v)[:200]}")
            print(f"\nPrompt文件: {task['prompt_file']}")
            print(f"输出字段: {', '.join(task['output_fields'])}")

    elif cmd == "distill":
        mgr_id = sys.argv[2]
        engine = sys.argv[3] if len(sys.argv) > 3 else "auto"
        result = distill_manager(mgr_id, engine)
        if result.get("success"):
            print(result["message"])
        elif result.get("task_type"):
            print(f"已生成蒸馏任务，请用对话LLM执行（引擎: llm）")
        else:
            print(f"蒸馏失败: {result}")
