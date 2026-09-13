# -*- coding: utf-8 -*-
"""
gen_data.py —— 通用备考题库生成脚本（模板，内置公务员考试示例数据）
遵循 skill 铁律 P5：JSON 必须脚本生成，禁止手写/流式输出。
复用方式：把本文件底部的 `db = {...}` 整体替换为你自己考试的数据即可，其它题型函数可照搬。

产出 data/questions.json，结构：
  subjects[] -> chapters[] -> questions[] / knowledgePoints[]
  外加 mockPapers[] / realPapers[]（试卷用 questionIds 引用题目）

题型覆盖：single(单选) / multiple(多选) / judge(判断) / blank(填空) / short(简答·主观) / essay(申论写作·主观)
客观题带 answer + analysis；主观题带 scoringPoints + referenceAnswer（不判分）。

用法：
  python3 scripts/gen_data.py
  node scripts/build-shards.js   # 再跑分片构建
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT = os.path.join(DATA_DIR, "questions.json")


def single(qid, question, options, answer, analysis):
    return {
        "id": qid, "type": "single", "question": question,
        "options": [{"label": l, "text": t} for l, t in options],
        "answer": answer, "analysis": analysis,
    }


def multiple(qid, question, options, answer, analysis):
    return {
        "id": qid, "type": "multiple", "question": question,
        "options": [{"label": l, "text": t} for l, t in options],
        "answer": answer, "analysis": analysis,
    }


def judge(qid, question, answer, analysis):
    return {
        "id": qid, "type": "judge", "question": question,
        "options": [{"label": "A", "text": "正确"}, {"label": "B", "text": "错误"}],
        "answer": answer, "analysis": analysis,
    }


def blank(qid, question, answer, analysis):
    return {
        "id": qid, "type": "blank", "question": question,
        "options": [], "answer": answer, "analysis": analysis,
    }


def short(qid, question, scoring_points, reference):
    return {
        "id": qid, "type": "short", "question": question, "options": [],
        "scoringPoints": [{"score": s, "point": p} for s, p in scoring_points],
        "referenceAnswer": reference,
    }


def essay(qid, question, scoring_points, reference):
    return {
        "id": qid, "type": "essay", "question": question, "options": [],
        "scoringPoints": [{"score": s, "point": p} for s, p in scoring_points],
        "referenceAnswer": reference,
    }


def kp(kid, sid, cid, title, body):
    return {"id": kid, "subjectId": sid, "chapterId": cid, "title": title, "body": body}


# ============ 科目一：行政职业能力测验（行测）—— 客观题为主 ============
xingce = {
    "id": "xingce",
    "name": "行政职业能力测验",
    "icon": "📊",
    "chapters": [
        {
            "id": "changshi", "name": "常识判断",
            "questions": [
                single("xc-cs-01",
                       "我国现行宪法是哪一年通过的？",
                       [("A", "1954 年"), ("B", "1975 年"), ("C", "1982 年"), ("D", "1988 年")],
                       "C",
                       "现行宪法即 1982 年宪法，由第五届全国人大第五次会议于 1982 年 12 月 4 日通过，后经多次修正。"),
                single("xc-cs-02",
                       "下列关于二十四节气的说法，正确的是：",
                       [("A", "惊蛰是一年中最热的节气"), ("B", "冬至这天北半球白昼最短"),
                        ("C", "立春标志着夏季开始"), ("D", "秋分时北极出现极夜")],
                       "B",
                       "冬至太阳直射南回归线，北半球白昼最短、黑夜最长；夏至则相反。"),
                multiple("xc-cs-03",
                         "下列属于我国民法典规定的基本原则的有：",
                         [("A", "平等原则"), ("B", "自愿原则"),
                          ("C", "公平原则"), ("D", "诚信原则")],
                         "ABCD",
                         "民法典总则编明确规定了平等、自愿、公平、诚信、守法与公序良俗、绿色等基本原则，四项均正确。"),
                judge("xc-cs-04",
                      "长江是我国第一大河，也是世界第三长河。",
                      "A",
                      "长江全长约 6300 公里，为我国第一长河、世界第三长河（次于尼罗河、亚马孙河），表述正确。"),
            ],
            "knowledgePoints": [
                kp("kp-cs-01", "xingce", "changshi", "现行宪法的时间节点",
                   "现行宪法是 <mark>1982 年宪法</mark>，此后有 <mark>1988、1993、1999、2004、2018</mark> 五次修正。备考只需牢记「82 年通过 + 五次修正」。"),
                kp("kp-cs-02", "xingce", "changshi", "二至二分的地理意义",
                   "<mark>夏至</mark>北半球昼最长，<mark>冬至</mark>昼最短，<mark>春分/秋分</mark>昼夜平分。抓住「太阳直射点位置」即可推断。"),
            ],
        },
        {
            "id": "yanyu", "name": "言语理解与表达",
            "questions": [
                single("xc-yy-01",
                       "填入划横线处最恰当的一项：科学研究需要____的态度，来不得半点虚假。",
                       [("A", "小心翼翼"), ("B", "实事求是"), ("C", "按部就班"), ("D", "锲而不舍")],
                       "B",
                       "「来不得半点虚假」提示应填与「真实/求真」相关的词，「实事求是」最契合语境。"),
                single("xc-yy-02",
                       "下列句子没有语病的一项是：",
                       [("A", "能否做好防疫工作，是保障师生健康的关键"),
                        ("B", "通过这次学习，使我提高了认识"),
                        ("C", "他大约十点钟左右到达"),
                        ("D", "我们要发扬艰苦奋斗的优良传统")],
                       "D",
                       "A 两面对一面搭配不当；B 缺主语（滥用「通过…使…」）；C「大约」与「左右」语义重复；D 无语病。"),
                blank("xc-yy-03",
                      "「不积跬步，无以至千里」出自《劝学》，其作者是战国时期的思想家____。",
                      "荀子",
                      "《劝学》为荀子代表作，强调学习贵在积累。答案：荀子（荀况）。"),
            ],
            "knowledgePoints": [
                kp("kp-yy-01", "xingce", "yanyu", "语病六大类型",
                   "常考语病：<mark>成分残缺、搭配不当、语序不当、两面对一面、语义重复、句式杂糅</mark>。「通过…使…」缺主语是高频陷阱。"),
            ],
        },
        {
            "id": "ziliao", "name": "资料分析",
            "questions": [
                single("xc-zl-01",
                       "某市 2023 年 GDP 为 5000 亿元，同比增长 8%，则 2022 年 GDP 约为：",
                       [("A", "4600 亿元"), ("B", "4630 亿元"), ("C", "4700 亿元"), ("D", "5400 亿元")],
                       "B",
                       "现期 / (1+增长率) = 5000 / 1.08 ≈ 4629.6 亿元，最接近 B。"),
                single("xc-zl-02",
                       "已知某产品去年销量 200 万件，今年增长 15%，今年销量为：",
                       [("A", "215 万件"), ("B", "230 万件"), ("C", "260 万件"), ("D", "300 万件")],
                       "B",
                       "基期 × (1+增长率) = 200 × 1.15 = 230 万件。"),
                judge("xc-zl-03",
                      "增长率为正时，现期值一定大于基期值。",
                      "A",
                      "增长量 = 基期 × 增长率，增长率为正则增长量为正，现期值必大于基期值，表述正确。"),
            ],
            "knowledgePoints": [
                kp("kp-zl-01", "xingce", "ziliao", "基期与现期互求",
                   "现期 = 基期 ×(1+r)；基期 = <mark>现期 /(1+r)</mark>。资料分析最核心的两个公式，务必区分「求谁」。"),
            ],
        },
    ],
}

# ============ 科目二：申论 —— 主观题为主（不判分，只给采分点） ============
shenlun = {
    "id": "shenlun",
    "name": "申论",
    "icon": "✍️",
    "chapters": [
        {
            "id": "guina", "name": "归纳概括",
            "questions": [
                short("sl-gn-01",
                      "根据「给定资料 1」，请概括当前基层治理面临的主要问题。（本题 15 分，要求：全面、准确、有条理，不超过 200 字）",
                      [(3, "人手不足：基层工作人员编制少、任务重，存在「小马拉大车」现象"),
                       (3, "权责不匹配：责任层层下压但相应权限与资源未同步下放"),
                       (3, "形式主义：填表报数、迎检留痕过多，挤占服务群众时间"),
                       (3, "数字负担：政务 APP、工作群过多，增加基层负担"),
                       (3, "群众参与不足：治理主体单一，社会力量与居民参与度低")],
                      "参考答案：一是人手不足，编制少任务重；二是权责不匹配，责大权小；三是形式主义突出，留痕迎检挤占服务；四是数字负担重，App 与工作群泛滥；五是群众参与不足，共治格局尚未形成。（要点齐全、分条作答即可）"),
                short("sl-gn-02",
                      "请概括「给定资料 2」中某地推进乡村振兴的主要做法。（10 分，不超过 150 字）",
                      [(3, "产业带动：发展特色种植 + 电商销售，延长产业链"),
                       (3, "人才回引：出台优惠政策吸引青年返乡创业"),
                       (2, "文化赋能：挖掘乡土文化打造文旅品牌"),
                       (2, "组织保障：党建引领，村集体统筹推进")],
                      "参考答案：一是产业带动，发展特色种植并借力电商；二是人才回引，政策吸引青年返乡；三是文化赋能，打造文旅品牌；四是组织保障，党建引领村集体统筹。"),
            ],
            "knowledgePoints": [
                kp("kp-gn-01", "shenlun", "guina", "归纳概括答题结构",
                   "标准结构：<mark>总括句 + 分条要点</mark>。要点来自材料，做到「一个要点一句话、动宾结构、前置关键词」，切忌照抄大段原文。"),
            ],
        },
        {
            "id": "duice", "name": "提出对策",
            "questions": [
                short("sl-dc-01",
                      "针对「给定资料 3」反映的城市内涝问题，请提出解决对策。（15 分，要求：切实可行，不超过 300 字）",
                      [(4, "工程治理：改造老旧管网、建设雨水调蓄设施、推进海绵城市"),
                       (4, "预警响应：完善气象监测与应急预案，建立联动机制"),
                       (3, "长效管理：明确排水管养责任主体，定期清淤维护"),
                       (2, "公众参与：加强防灾宣传，提升居民自救互救能力"),
                       (2, "资金保障：多渠道筹措资金，保障基础设施投入")],
                      "参考答案：一是工程治理，改造管网、建海绵城市；二是健全预警响应与应急联动；三是落实长效管养责任；四是加强公众防灾教育；五是保障资金投入。对策需针对问题、主体明确、可操作。"),
            ],
            "knowledgePoints": [
                kp("kp-dc-01", "shenlun", "duice", "对策的可行性来源",
                   "对策三来源：<mark>问题反推、材料借鉴、经验补充</mark>。书写做到「主体 + 手段 + 目的」，避免空喊口号。"),
            ],
        },
        {
            "id": "xiezuo", "name": "文章写作",
            "questions": [
                essay("sl-xz-01",
                      "请以「基层治理现代化」为主题，自拟题目，写一篇议论文。（40 分，要求：观点明确，论证充分，1000～1200 字）",
                      [(8, "立意准确：紧扣「基层治理现代化」，中心论点鲜明"),
                       (10, "结构完整：总分总，分论点清晰（如制度、科技、人本三维度）"),
                       (10, "论证充分：论据丰富（案例 + 道理），论证有逻辑"),
                       (7, "语言表达：文风端正、行文流畅、无明显语病"),
                       (5, "字数与卷面：符合字数要求，书写工整")],
                      "参考思路：开头由基层治理痛点引出中心论点「以现代化手段激活基层治理效能」。主体三段——分论点一「制度为纲，理顺权责」；分论点二「科技为翼，赋能减负」；分论点三「以人为本，共建共治共享」。每段「分论点句 + 案例 + 分析」。结尾升华，呼应主题。"),
            ],
            "knowledgePoints": [
                kp("kp-xz-01", "shenlun", "xiezuo", "议论文分论点拟定",
                   "分论点常用维度：<mark>是什么/为什么/怎么办</mark> 或 <mark>制度—科技—人本</mark>、<mark>政府—社会—个人</mark>。三个分论点需并列、不交叉、共同支撑总论点。"),
            ],
        },
    ],
}

db = {
    "subjects": [xingce, shenlun],
    # 模拟卷：引用已有题目 id（客观题为主）
    "mockPapers": [
        {
            "id": "mock-xc-01", "name": "行测全真模拟卷（一）",
            "subjectId": "xingce", "duration": 7200, "totalScore": 100,
            "questionIds": ["xc-cs-01", "xc-cs-02", "xc-cs-03", "xc-yy-01",
                            "xc-yy-02", "xc-zl-01", "xc-zl-02"],
        },
    ],
    # 真题卷：混合客观 + 主观
    "realPapers": [
        {
            "id": "real-2023-xc", "name": "2023 国考行测真题（节选）",
            "subjectId": "xingce", "duration": 7200, "totalScore": 100,
            "questionIds": ["xc-cs-04", "xc-yy-03", "xc-zl-03"],
        },
        {
            "id": "real-2023-sl", "name": "2023 国考申论真题（节选）",
            "subjectId": "shenlun", "duration": 10800, "totalScore": 100,
            "questionIds": ["sl-gn-01", "sl-dc-01", "sl-xz-01"],
        },
    ],
}


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    # 写完立即 JSON.parse 校验（P5 要求）
    with open(OUT, "r", encoding="utf-8") as f:
        json.load(f)
    n_sub = len(db["subjects"])
    n_q = sum(len(c["questions"]) for s in db["subjects"] for c in s["chapters"])
    n_kp = sum(len(c.get("knowledgePoints", [])) for s in db["subjects"] for c in s["chapters"])
    n_paper = len(db["mockPapers"]) + len(db["realPapers"])
    print("[gen_data] 生成成功:", OUT)
    print("  科目:", n_sub, "| 题目:", n_q, "| 知识点:", n_kp, "| 试卷:", n_paper)


if __name__ == "__main__":
    main()
