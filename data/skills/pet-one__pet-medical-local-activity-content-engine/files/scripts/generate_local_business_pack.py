#!/usr/bin/env python3
"""Generate a 7-day local-business customer acquisition content pack."""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from textwrap import dedent


DEFAULT_BRIEF = {
    "business_name": "样板门店",
    "city": "本地城市",
    "business_type": "本地生活门店",
    "target_customer": "附近有明确需求的人群",
    "main_pain": "不知道为什么现在要来店",
    "core_offer": "低门槛体验套餐",
    "average_order_value": "99-299元",
    "differentiators": ["位置方便", "服务稳定", "环境舒服"],
    "nearby_scenes": ["下班后", "周末", "临时需要", "朋友推荐"],
    "campaign_theme": "7天体验计划",
    "activity_object": "可变活动对象（以本次 brief 为准）",
    "service_scene": "自定义服务场景",
    "service_scenes": ["疫苗", "体检", "驱虫", "绝育评估", "老年宠"],
    "channels": ["抖音本地推", "美团", "高德", "朋友圈", "私域"],
    "journey_stages": ["触达", "咨询", "预约", "到店", "服务/核销", "真实评价", "复诊"],
    "review_gates": ["医疗表达", "病例隐私/脱敏", "价格与库存", "服务范围与承诺", "预约条款"],
    "tone": "真实、克制、可信",
    "cta": "私信发送关键词，领取体验名额",
    "constraints": ["不夸大承诺", "不使用虚假评价"],
}


DAY_THEMES = [
    ("痛点共鸣", "把目标客户的真实困扰说清楚"),
    ("场景展示", "展示门店环境和使用场景"),
    ("老板视角", "用经营者口吻解释为什么做这个活动"),
    ("客户决策", "回答客户下单前最常见的顾虑"),
    ("细节证明", "用具体细节证明门店靠谱"),
    ("限时体验", "给出低门槛行动理由"),
    ("复盘召回", "总结一周反馈并召回犹豫客户"),
]


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.replace("；", ";").split(";") if part.strip()]
    return []


def load_brief(path: Path | None) -> dict:
    brief = dict(DEFAULT_BRIEF)
    if path and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        brief.update(data)
    for key in ("differentiators", "nearby_scenes", "constraints", "service_scenes", "channels", "journey_stages", "review_gates"):
        brief[key] = as_list(brief.get(key)) or list(DEFAULT_BRIEF[key])
    if not brief.get("activity_object"):
        brief["activity_object"] = DEFAULT_BRIEF["activity_object"]
    if not brief.get("service_scene"):
        brief["service_scene"] = brief["service_scenes"][0]
    return brief


def s(brief: dict, key: str) -> str:
    return str(brief.get(key) or DEFAULT_BRIEF.get(key) or "").strip()


def activity_object_label(brief: dict) -> str:
    """Render a variable activity object without assuming one fixed offer."""
    value = brief.get("activity_object")
    if isinstance(value, dict):
        parts = [f"{key}：{str(item).strip()}" for key, item in value.items() if str(item).strip()]
        return "；".join(parts) or "由本次 brief 决定"
    return str(value or "由本次 brief 决定").strip()


def pet_medical_mode(brief: dict) -> bool:
    text = " ".join(str(value) for value in brief.values()).lower()
    return any(term in text for term in ("宠物医院", "宠物医疗", "动物医院", "兽医", "疫苗", "驱虫", "绝育", "老年宠"))


def joined(brief: dict, key: str) -> str:
    return "、".join(brief.get(key, []))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def calendar(brief: dict) -> str:
    start = date.today()
    rows = []
    for idx, (theme, goal) in enumerate(DAY_THEMES):
        day = start + timedelta(days=idx)
        scene = brief["nearby_scenes"][idx % len(brief["nearby_scenes"])]
        stage = brief["journey_stages"][idx % len(brief["journey_stages"])]
        rows.append(
            f"| Day {idx + 1} | {day.isoformat()} | {theme} | {scene} | "
            f"{joined(brief, 'channels')} | {stage} | {s(brief, 'cta')} | {goal} |"
        )
    return dedent(
        f"""
        # 7天内容日历

        门店：{s(brief, "business_name")}  
        城市：{s(brief, "city")}  
        活动对象：{activity_object_label(brief)}  
        当前服务场景：{s(brief, "service_scene")}  
        活动主题：{s(brief, "campaign_theme")}

        | 天数 | 日期 | 主题 | 场景 | 联动平台 | 当前链路阶段 | CTA | 目标 |
        | --- | --- | --- | --- | --- | --- | --- | --- |
        {chr(10).join(rows)}
        """
    )


def video_scripts(brief: dict) -> str:
    scripts = []
    for idx, (theme, _) in enumerate(DAY_THEMES):
        scene = brief["nearby_scenes"][idx % len(brief["nearby_scenes"])]
        diff = brief["differentiators"][idx % len(brief["differentiators"])]
        service_scene = brief["service_scenes"][idx % len(brief["service_scenes"])]
        medical_note = (
            f"医疗表达只描述‘{service_scene}’的服务流程、适用范围和准备事项，不能诊断、承诺疗效或替代兽医判断。"
            if pet_medical_mode(brief)
            else "表达只讲真实服务流程和可验证细节，不做结果保证。"
        )
        scripts.append(
            dedent(
                f"""
                ## Day {idx + 1}：{theme}

                标题：{s(brief, "city")}{s(brief, "business_type")}｜{scene}的人，可以试试这个办法
                当前服务场景：{service_scene}

                镜头脚本：
                1. 0-3秒：拍一个真实场景，字幕写“{s(brief, "main_pain")}”
                2. 3-8秒：展示门店或服务细节：{diff}
                3. 8-15秒：解释本周活动：{s(brief, "core_offer")}
                4. 15-25秒：补一个信任点，不夸张，只讲具体细节。
                5. 25-30秒：口播 CTA：{s(brief, "cta")}

                口播稿：
                如果你也遇到“{s(brief, "main_pain")}”，可以先不用急着办长期套餐。
                我们这周做的是「{s(brief, "campaign_theme")}」，重点是让你先体验真实环境和服务。
                你最需要看的是这点：{diff}。
                想了解空位/价格，私信我发“{keyword(brief)}”。

                拍摄提示：用真实门店光线，避免过度滤镜；不要使用虚假排队、虚假评价或夸张承诺。
                {medical_note}
                """
            ).strip()
        )
    return "# 短视频脚本\n\n" + "\n\n".join(scripts)


def keyword(brief: dict) -> str:
    cta = s(brief, "cta")
    if "“" in cta and "”" in cta:
        return cta.split("“", 1)[1].split("”", 1)[0]
    if '"' in cta:
        parts = cta.split('"')
        if len(parts) >= 3:
            return parts[1]
    return "体验"


def xiaohongshu_notes(brief: dict) -> str:
    notes = []
    city = s(brief, "city")
    btype = s(brief, "business_type")
    for idx, (theme, goal) in enumerate(DAY_THEMES[:5]):
        diff = brief["differentiators"][idx % len(brief["differentiators"])]
        scene = brief["nearby_scenes"][idx % len(brief["nearby_scenes"])]
        notes.append(
            dedent(
                f"""
                ## 笔记 {idx + 1}：{city}{btype}怎么选？{scene}先看这3点

                开头：
                最近很多人问我，{scene}的时候，到底该不该找一个{btype}。我的建议是：先看你是不是被这个问题卡住了：{s(brief, "main_pain")}。

                正文：
                1. 先看场景是不是匹配：{scene}。
                2. 再看细节是不是稳定：{diff}。
                3. 最后看试错成本，本周可以先试「{s(brief, "core_offer")}」。

                结尾：
                我们在{city}，这周主题是「{s(brief, "campaign_theme")}」。想看价格和位置，私信“{keyword(brief)}”。

                关键词：
                #{city}{btype} #{city}探店 #{city}本地生活 #{s(brief, "campaign_theme")} #{theme}

                目标：{goal}
                """
            ).strip()
        )
    return "# 小红书笔记草稿\n\n" + "\n\n".join(notes)


def wechat_posts(brief: dict) -> str:
    posts = []
    for idx, (theme, _) in enumerate(DAY_THEMES):
        scene = brief["nearby_scenes"][idx % len(brief["nearby_scenes"])]
        diff = brief["differentiators"][idx % len(brief["differentiators"])]
        posts.append(
            dedent(
                f"""
                ## Day {idx + 1} 朋友圈：{theme}

                今天想认真说一个很小但很真实的需求：{scene}。

                很多人不是不想解决问题，而是卡在「{s(brief, "main_pain")}」。

                所以这周我们做了「{s(brief, "campaign_theme")}」：{s(brief, "core_offer")}。

                我们不会承诺夸张结果，只把体验做扎实：{diff}。

                想了解的朋友，私信我发“{keyword(brief)}”，我把价格和安排发你。
                """
            ).strip()
        )
    return "# 微信朋友圈/社群文案\n\n" + "\n\n".join(posts)


def private_chat_sop(brief: dict) -> str:
    first_scene = brief["nearby_scenes"][0] if brief["nearby_scenes"] else "下班后"
    return dedent(
        f"""
        # 私域成交话术 SOP

        ## 1. 用户私信关键词

        用户：{keyword(brief)}

        回复：
        你好，我把「{s(brief, "campaign_theme")}」的说明发你。这个活动适合{s(brief, "target_customer")}，主要解决的是：{s(brief, "main_pain")}。

        ## 2. 发活动说明

        当前活动对象：{activity_object_label(brief)}  
        当前服务场景：{s(brief, "service_scene")}  
        本周体验：{s(brief, "core_offer")}  
        适合场景：{", ".join(brief["nearby_scenes"])}  
        体验重点：{", ".join(brief["differentiators"][:4])}

        你可以先告诉我：你更偏向工作日、周末，还是临时体验？

        ## 3. 常见顾虑处理

        觉得贵：
        理解，你可以先不用办长期。这个活动本来就是低门槛体验，先确认环境/服务适不适合你。

        怕没效果：
        我们不承诺夸张结果，只保证把门店能做到的服务和环境讲清楚。你可以先体验一次，再决定是否继续。

        没时间：
        可以先选一个最容易坚持的时间段。比如{first_scene}。

        ## 4. 预约—到店—核销—评价—复诊

        - 预约：确认服务场景、宠物基本信息、期望时间、地址、价格/取消规则；医疗问题交由兽医判断。
        - 到店：发送路线和到店提醒，记录实际到店，不把预约当成到店。
        - 核销：只在服务真实发生后由门店核销，记录服务项目和时间，不补录虚假核销。
        - 评价：服务完成后邀请客户基于真实体验评价，不代写、不返现换好评、不暗示必须五星。
        - 复诊：按门店/兽医确认的建议提醒复诊，不承诺疗效，不把提醒写成医疗结论。

        ## 5. 成交确认

        我先帮你登记预约意向。你发我：称呼/宠物基本信息/服务场景/期望到店时间，我再以门店确认的价格、库存和时段回复。

        ## 6. 未成交跟进

        第一次跟进：我把这周可选时间发你，你看哪个方便。  
        第二次跟进：体验价到本周结束，过期就恢复原价。这里必须是真实政策，不能虚假倒计时。  
        第三次跟进：如果暂时不来，也可以先收藏，下次需要安静环境/服务时再联系。
        """
    )


def offer_design(brief: dict) -> str:
    return dedent(
        f"""
        # 活动与套餐设计

        ## 可变活动对象

        活动对象：{activity_object_label(brief)}  
        当前服务场景：{s(brief, "service_scene")}  
        可选服务场景：{joined(brief, "service_scenes")}  
        本次目标：{brief["journey_stages"][0]} → {brief["journey_stages"][-1]}

        ## 主推活动

        名称：{s(brief, "campaign_theme")}  
        内容：{s(brief, "core_offer")}  
        客单价参考：{s(brief, "average_order_value")}  
        CTA：{s(brief, "cta")}

        ## 三层转化

        | 层级 | 目标 | 设计 |
        | --- | --- | --- |
        | 低门槛体验 | 让陌生客户愿意问 | 一次体验/7天体验/小额套餐 |
        | 首单成交 | 让客户到店或付款 | 预约确认、时间选择、权益说明 |
        | 复购升级 | 把体验客户变长期客户 | 次卡、月卡、会员、转介绍 |

        ## 五平台联动

        | 平台 | 主要任务 | 下一步动作 |
        | --- | --- | --- |
        | 抖音本地推 | 本地触达、内容放大、POI/团购入口 | 咨询/预约 |
        | 美团 | 搜索决策、门店页、团购与核销 | 预约/到店 |
        | 高德 | POI、路线和附近到店意图 | 到店 |
        | 朋友圈 | 院长/医生/门店真实场景与提醒 | 私信 |
        | 私域 | 咨询、预约、提醒、评价、复诊 | 记录下一步 |

        ## 活动链路

        `触达 → 咨询 → 预约 → 到店 → 服务/核销 → 真实评价 → 复诊`

        ## 安全边界

        {bullet(brief["constraints"])}

        发布前人工审核：{joined(brief, "review_gates")}。
        所有优惠、库存、名额、价格、服务承诺都需要门店确认后再发布；宠物医疗内容还需完成病例脱敏和兽医/负责人审核。
        禁止虚假评价、虚假名额、虚构病例或数据、疗效/治愈承诺、诱导消费和平台规则规避。
        """
    )


def review_table(brief: dict) -> str:
    rows = []
    for idx, (theme, _) in enumerate(DAY_THEMES):
        stage = brief["journey_stages"][idx % len(brief["journey_stages"])]
        rows.append(f"| Day {idx + 1} | {theme} | {stage} |  |  |  |  |  |  |  |  |  |")
    return dedent(
        f"""
        # 7天全链路复盘表

        活动对象：{activity_object_label(brief)}  
        联动平台：{joined(brief, "channels")}

        | 天数 | 内容主题 | 当前阶段 | 平台 | 播放/曝光 | 私信/咨询 | 预约 | 到店 | 核销 | 真实评价 | 复诊 | 收入/备注 |
        | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
        {chr(10).join(rows)}

        ## 复盘问题

        - 哪个平台带来的有效咨询、预约和到店最多？
        - 哪个服务场景最容易引发真实咨询，而不是泛流量？
        - 预约到店、到店到核销、核销到评价、评价到复诊分别掉在哪里？
        - 哪个顾虑最常出现，是否需要改页面、话术或服务说明？
        - 下周继续当前活动对象，还是切换到另一个服务场景？切换前先更新 brief 并重新审核。
        """
    )


def delivery_note(brief: dict) -> str:
    return dedent(
        f"""
        # 给客户的交付说明

        你好，这是「{s(brief, "business_name")} - {s(brief, "campaign_theme")}」7天内容包。

        请先确认：

        - 当前活动对象、服务场景和目标是否是本次真实要推广的内容，而不是沿用旧活动。
        - 活动价格、时间、名额是否真实有效。
        - 门店地址、联系方式、营业时间是否准确。
        - 若为宠物医疗：服务范围、适用对象、准备事项和医疗表达是否经负责人/兽医审核。
        - 病例图片、聊天记录和宠物信息是否已获授权并完成脱敏。
        - 文案里是否有你不想公开的信息。
        - 视频脚本中的镜头是否能真实拍到。
        - 私域话术是否符合你平时的沟通语气。
        - 预约、到店、核销、评价、复诊的负责人和记录位置是否明确。
        - 是否已删除虚假评价、虚假名额、疗效承诺和诱导消费表达。

        使用建议：

        1. 每天至少发布 1 条短视频或图文。
        2. 朋友圈当天同步发，社群不要刷屏。
        3. 所有咨询都记录到复盘表。
        4. 第 3 天和第 7 天各复盘一次，及时调整标题、封面和 CTA。

        注意：本内容包用于提升内容组织和转化沟通效率，不承诺固定流量、收入或医疗结果；外部发布、价格与医疗判断均需人工确认。
        """
    )


def pet_medical_workflow(brief: dict) -> str:
    return dedent(
        f"""
        # 宠物医疗活动工作流与审核清单

        > 本文件适用于宠物医院/动物医院活动；非医疗门店可把服务场景替换为自己的可变活动对象。

        ## 本次活动对象

        活动对象：{activity_object_label(brief)}  
        当前服务场景：{s(brief, "service_scene")}  
        可选场景：{joined(brief, "service_scenes")}

        五个基础服务场景必须能被单独切换，而不是写死在模板里：疫苗、体检、驱虫、绝育评估、老年宠。每次切换活动对象时，重新填写适用对象、服务范围、价格、时段、容量、负责人和 CTA。

        ## 平台联动

        | 渠道 | 角色 | 交接字段 |
        | --- | --- | --- |
        | 抖音本地推 | 本地触达、内容放大、POI/团购入口 | 素材、定向、预算、咨询/预约 |
        | 美团 | 搜索决策、门店页、团购、核销 | 项目、价格、预约、核销状态 |
        | 高德 | POI、路线、附近到店意图 | 地址、电话、营业时间、路线 |
        | 朋友圈 | 院长/医生/门店真实场景与提醒 | 真实素材、服务说明、私信口令 |
        | 私域 | 咨询、预约、提醒、评价、复诊 | 宠物基本信息、时间、状态、下一步 |

        ## 用户状态流

        | 阶段 | 必须完成 | 禁止越界 |
        | --- | --- | --- |
        | 触达 | 说明场景、适用对象和真实入口 | 不用虚假名额/排队/病例 |
        | 咨询 | 记录问题和基础信息，必要时转人工 | 不在线诊断、处方或承诺疗效 |
        | 预约 | 确认项目、价格、时段、地址、取消规则 | 不把意向写成已预约 |
        | 到店 | 发路线/提醒并记录实际到店 | 不把预约或曝光算到店 |
        | 服务/核销 | 真实服务后核销并留记录 | 不补录虚假核销 |
        | 真实评价 | 邀请基于体验评价 | 不代写、买好评、诱导五星 |
        | 复诊 | 按负责人/兽医确认的安排提醒 | 不把提醒写成治疗结论 |

        ## 发布前人工审核

        - 医疗表达：只写服务流程、适用范围、准备事项和可验证细节。
        - 病例隐私：取得授权；姓名、电话、订单号、病历、影像和可识别信息脱敏。
        - 价格与服务承诺：价格、库存、时段、取消规则和赠送权益逐项确认。
        - 真实性：禁止虚假评价、虚假名额、虚构病例/数据、疗效或治愈承诺。
        - 交易边界：禁止诱导消费、强迫加购、夸大风险和平台规则规避。

        审核人：________  日期：________  发布渠道：{joined(brief, "channels")}
        """
    )


def summary(brief: dict) -> str:
    return dedent(
        f"""
        # 内容包总览

        | 项目 | 内容 |
        | --- | --- |
        | 门店 | {s(brief, "business_name")} |
        | 城市 | {s(brief, "city")} |
        | 行业 | {s(brief, "business_type")} |
        | 活动对象 | {activity_object_label(brief)} |
        | 当前服务场景 | {s(brief, "service_scene")} |
        | 目标客户 | {s(brief, "target_customer")} |
        | 核心痛点 | {s(brief, "main_pain")} |
        | 主推活动 | {s(brief, "core_offer")} |
        | 活动主题 | {s(brief, "campaign_theme")} |
        | 行动口令 | {keyword(brief)} |

        ## 文件说明

        - `01-calendar.md`：7天内容日历。
        - `02-short-video-scripts.md`：短视频脚本。
        - `03-xiaohongshu-notes.md`：小红书笔记。
        - `04-wechat-posts.md`：朋友圈/社群文案。
        - `05-private-chat-sop.md`：私域成交话术。
        - `06-offer-design.md`：活动和套餐设计。
        - `07-review-table.md`：7天复盘表。
        - `08-delivery-note.md`：给客户的交付说明。
        - `09-pet-medical-workflow.md`：宠物医疗服务场景、五平台联动、预约到复诊和审核清单。
        """
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", type=Path, help="Path to merchant JSON brief.")
    parser.add_argument("--out", type=Path, default=Path("local-business-content-pack"))
    args = parser.parse_args()

    brief = load_brief(args.brief)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    write(out / "00-summary.md", summary(brief))
    write(out / "01-calendar.md", calendar(brief))
    write(out / "02-short-video-scripts.md", video_scripts(brief))
    write(out / "03-xiaohongshu-notes.md", xiaohongshu_notes(brief))
    write(out / "04-wechat-posts.md", wechat_posts(brief))
    write(out / "05-private-chat-sop.md", private_chat_sop(brief))
    write(out / "06-offer-design.md", offer_design(brief))
    write(out / "07-review-table.md", review_table(brief))
    write(out / "08-delivery-note.md", delivery_note(brief))
    write(out / "09-pet-medical-workflow.md", pet_medical_workflow(brief))
    write(out / "brief.used.json", json.dumps(brief, ensure_ascii=False, indent=2))

    print(f"Generated local business content pack: {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
