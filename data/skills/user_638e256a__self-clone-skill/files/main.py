"""
自我风格数字分身 - 十维人格DNA建模引擎
纯Python零依赖 | 10维人格模型 | 本地存储
"""

import json
import os
import sys
import re
import io
from datetime import datetime
from collections import Counter

# Windows 编码兼容
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
DNA_FILE = os.path.join(DATA_DIR, "self_dna.json")


# ─── DNA结构 ───

def init_dna():
    return {
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "sample_count": 0,
        "total_chars": 0,
        "dna": {
            "thinking_mode": {},      # 思维模式
            "value_order": {},        # 价值排序
            "emotion_tone": {},       # 情绪基调
            "expression_style": {},   # 表达风格
            "decision_pref": {},      # 决策偏好
            "social_mode": {},        # 社交模式
            "risk_attitude": {},      # 风险态度
            "time_orientation": {},   # 时间取向
            "cognitive_complexity": {}, # 认知复杂度
            "self_perception": {},    # 自我认知
        }
    }


# ─── 十维分析 ───

def analyze_thinking_mode(texts):
    """思维模式：线性/发散/批判/系统性"""
    keywords = {
        "linear": ["首先", "其次", "然后", "最后", "第一步", "第二步", "按照", "依次", "顺序"],
        "divergent": ["换个角度", "另一方面", "不过", "但是", "或者", "也许", "可能", "除此之外"],
        "critical": ["问题", "不对", "但是", "然而", "矛盾", "漏洞", "不成立", "质疑", "未必"],
        "systematic": ["整体", "系统", "框架", "结构", "层次", "维度", "全局", "体系", "生态"]
    }
    scores = {}
    all_text = " ".join(texts)
    for mode, kws in keywords.items():
        scores[mode] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_value_order(texts):
    """价值排序：效率/公平/创新/稳定/关系"""
    keywords = {
        "efficiency": ["效率", "快", "速度", "优化", "提升", "自动化", "节省", "产出"],
        "fairness": ["公平", "合理", "应该", "对等", "平衡", "公正", "平等"],
        "innovation": ["创新", "突破", "尝试", "新", "探索", "实验", "不一样"],
        "stability": ["稳定", "可靠", "安全", "保证", "确定", "风险", "可控"],
        "relationship": ["关系", "人", "团队", "合作", "信任", "沟通", "理解"]
    }
    scores = {}
    all_text = " ".join(texts)
    for val, kws in keywords.items():
        scores[val] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_emotion_tone(texts):
    """情绪基调：乐观/务实/悲观/中性"""
    keywords = {
        "optimistic": ["好", "棒", "不错", "可以", "没问题", "机会", "希望", "期待", "加油", "冲"],
        "pragmatic": ["先做", "试试", "看情况", "具体", "实际", "落地", "执行", "推进"],
        "pessimistic": ["难", "不行", "麻烦", "问题", "风险", "担心", "可能不行", "悬"],
        "neutral": ["收到", "了解", "明白", "OK", "好的", "知道了"]
    }
    scores = {}
    all_text = " ".join(texts)
    for tone, kws in keywords.items():
        scores[tone] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_expression_style(texts):
    """表达风格：简洁/详细/幽默/严肃"""
    avg_len = sum(len(t) for t in texts) / max(len(texts), 1)

    keywords = {
        "concise": [],  # 用句长判断
        "detailed": ["具体", "详细", "举例", "比如", "例如", "包括", "分为"],
        "humorous": ["哈哈", "笑死", "搞笑", "逗", "梗", "😂", "hhh", "xswl"],
        "serious": ["必须", "严肃", "认真", "重要", "关键", "核心", "原则"]
    }
    scores = {}
    all_text = " ".join(texts)
    for style, kws in keywords.items():
        if style == "concise":
            scores[style] = max(0, 10 - avg_len / 10)
        else:
            scores[style] = sum(all_text.count(kw) for kw in kws)

    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_decision_pref(texts):
    """决策偏好：数据/直觉/共识/权威"""
    keywords = {
        "data": ["数据", "数字", "指标", "分析", "统计", "证据", "事实"],
        "intuition": ["感觉", "直觉", "经验", "判断", "我觉得", "看起来"],
        "consensus": ["讨论", "大家", "商量", "共识", "对齐", "评审"],
        "authority": ["规定", "制度", "流程", "标准", "要求", "规范"]
    }
    scores = {}
    all_text = " ".join(texts)
    for pref, kws in keywords.items():
        scores[pref] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_social_mode(texts):
    """社交模式：外向/内向/主导/随和"""
    keywords = {
        "extrovert": ["一起", "我们", "大家", "约", "聚", "聊", "分享", "交流"],
        "introvert": ["我", "自己", "一个人", "安静", "独处", "思考"],
        "dominant": ["应该", "必须", "听我的", "我决定", "按我说的", "就这样"],
        "agreeable": ["好的", "行", "没问题", "听你的", "你定", "都行", "随意"]
    }
    scores = {}
    all_text = " ".join(texts)
    for mode, kws in keywords.items():
        scores[mode] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_risk_attitude(texts):
    """风险态度：冒险/稳健/保守"""
    keywords = {
        "adventurous": ["赌", "冲", "试试", "大不了", "万一成功", "博一把", "拼"],
        "moderate": ["平衡", "控制", "分步", "试点", "渐进", "灰度", "小范围"],
        "conservative": ["安全第一", "稳妥", "确定", "有把握", "保险", "兜底", "备份"]
    }
    scores = {}
    all_text = " ".join(texts)
    for att, kws in keywords.items():
        scores[att] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_time_orientation(texts):
    """时间取向：过去/现在/未来"""
    keywords = {
        "past": ["之前", "上次", "以前", "曾经", "历史", "过去", "原来"],
        "present": ["现在", "当前", "目前", "正在", "此刻", "眼下"],
        "future": ["未来", "以后", "将", "计划", "打算", "目标", "愿景", "下一步"]
    }
    scores = {}
    all_text = " ".join(texts)
    for orient, kws in keywords.items():
        scores[orient] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


def analyze_cognitive_complexity(texts):
    """认知复杂度：简单/中等/复杂"""
    all_text = " ".join(texts)
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', all_text)
    unique_words = set(words)

    # 词汇丰富度（TTR）
    ttr = len(unique_words) / max(len(words), 1)

    # 平均句长
    sentences = re.split(r'[。！？.!?\n]', all_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_len = sum(len(s) for s in sentences) / max(len(sentences), 1)

    # 复杂度词
    complex_keywords = ["辩证", "辩证地", "相对", "取决于", "一方面", "另一方面", "权衡", "综合", "本质上"]
    complex_count = sum(all_text.count(kw) for kw in complex_keywords)

    simple_score = max(0, 10 - ttr * 20 - avg_sentence_len / 5)
    medium_score = 5 + ttr * 5
    complex_score = ttr * 10 + avg_sentence_len / 5 + complex_count

    total = simple_score + medium_score + complex_score or 1
    return {
        "simple": round(simple_score / total, 3),
        "medium": round(medium_score / total, 3),
        "complex": round(complex_score / total, 3)
    }


def analyze_self_perception(texts):
    """自我认知：自信/谦虚/自我批评"""
    keywords = {
        "confident": ["我确定", "我懂", "我擅长", "没问题", "肯定", "绝对", "一定"],
        "modest": ["可能", "也许", "大概", "不太确定", "不一定", "仅供参考"],
        "self_critical": ["我错了", "是我的问题", "没做好", "抱歉", "不足", "改进"]
    }
    scores = {}
    all_text = " ".join(texts)
    for perc, kws in keywords.items():
        scores[perc] = sum(all_text.count(kw) for kw in kws)
    total = sum(scores.values()) or 1
    return {k: round(v / total, 3) for k, v in scores.items()}


# ─── 采集 ───

def collect(texts):
    """采集自我文本，建立人格DNA"""
    valid_texts = [t.strip() for t in texts if len(t.strip()) >= 30]

    if len(valid_texts) < 10:
        print(f"⚠️ 有效文本不足10段（每段需≥30字）。当前有效：{len(valid_texts)}段")
        print("建议至少10段，覆盖：工作沟通3段 + 日常聊天3段 + 观点表达2段 + 决策记录2段")
        return None

    dna = init_dna()
    dna["sample_count"] = len(valid_texts)
    dna["total_chars"] = sum(len(t) for t in valid_texts)

    d = dna["dna"]
    d["thinking_mode"] = analyze_thinking_mode(valid_texts)
    d["value_order"] = analyze_value_order(valid_texts)
    d["emotion_tone"] = analyze_emotion_tone(valid_texts)
    d["expression_style"] = analyze_expression_style(valid_texts)
    d["decision_pref"] = analyze_decision_pref(valid_texts)
    d["social_mode"] = analyze_social_mode(valid_texts)
    d["risk_attitude"] = analyze_risk_attitude(valid_texts)
    d["time_orientation"] = analyze_time_orientation(valid_texts)
    d["cognitive_complexity"] = analyze_cognitive_complexity(valid_texts)
    d["self_perception"] = analyze_self_perception(valid_texts)

    with open(DNA_FILE, "w", encoding="utf-8") as f:
        json.dump(dna, f, ensure_ascii=False, indent=2)

    print(f"✅ 人格DNA采集完成")
    print(f"   样本数：{len(valid_texts)} 段")
    print(f"   总字数：{dna['total_chars']} 字")
    print(f"   DNA已保存至：{DNA_FILE}")
    print(f"\n💡 运行 python main.py report 查看你的十维人格报告")
    return dna


# ─── 报告 ───

def show_report():
    """展示十维人格报告"""
    if not os.path.exists(DNA_FILE):
        print("❌ 尚未采集人格数据，请先运行：python main.py collect --samples ...")
        return

    with open(DNA_FILE, "r", encoding="utf-8") as f:
        dna = json.load(f)

    d = dna["dna"]
    print(f"\n{'='*65}")
    print(f"  🪞 十维人格DNA报告")
    print(f"{'='*65}")
    print(f"  采集时间：{dna['created_at'][:19]}")
    print(f"  样本数：{dna['sample_count']} 段 | 总字数：{dna['total_chars']}")
    print()

    dims = [
        ("思维模式", d["thinking_mode"], {"linear": "线性", "divergent": "发散", "critical": "批判", "systematic": "系统"}),
        ("价值排序", d["value_order"], {"efficiency": "效率", "fairness": "公平", "innovation": "创新", "stability": "稳定", "relationship": "关系"}),
        ("情绪基调", d["emotion_tone"], {"optimistic": "乐观", "pragmatic": "务实", "pessimistic": "悲观", "neutral": "中性"}),
        ("表达风格", d["expression_style"], {"concise": "简洁", "detailed": "详细", "humorous": "幽默", "serious": "严肃"}),
        ("决策偏好", d["decision_pref"], {"data": "数据", "intuition": "直觉", "consensus": "共识", "authority": "权威"}),
        ("社交模式", d["social_mode"], {"extrovert": "外向", "introvert": "内向", "dominant": "主导", "agreeable": "随和"}),
        ("风险态度", d["risk_attitude"], {"adventurous": "冒险", "moderate": "稳健", "conservative": "保守"}),
        ("时间取向", d["time_orientation"], {"past": "过去", "present": "现在", "future": "未来"}),
        ("认知复杂度", d["cognitive_complexity"], {"simple": "简单", "medium": "中等", "complex": "复杂"}),
        ("自我认知", d["self_perception"], {"confident": "自信", "modest": "谦虚", "self_critical": "自省"}),
    ]

    for name, data, labels in dims:
        if not data:
            continue
        top_key = max(data, key=data.get)
        top_label = labels.get(top_key, top_key)
        print(f"  【{name}】→ {top_label}")
        items = sorted(data.items(), key=lambda x: -x[1])
        for k, v in items:
            bar = "█" * int(v * 20)
            label = labels.get(k, k)
            print(f"    {label:<8} {bar} {v:.1%}")
        print()

    print(f"{'='*65}")

    # 人格总结
    print(f"\n  📝 人格速写：")
    traits = []
    for name, data, labels in dims:
        if not data:
            continue
        top_key = max(data, key=data.get)
        traits.append(f"{labels.get(top_key, top_key)}")
    print(f"  {' · '.join(traits)}")

    print(f"\n{'='*65}\n")


# ─── 人格对话模拟 ───

def chat(intent):
    """以自我人格风格对话"""
    if not os.path.exists(DNA_FILE):
        print("❌ 尚未采集人格数据")
        return

    with open(DNA_FILE, "r", encoding="utf-8") as f:
        dna = json.load(f)
    d = dna["dna"]

    print(f"\n{'='*60}")
    print(f"  🪞 人格对话（基于你的DNA）")
    print(f"{'='*60}")
    print(f"  你的问题：{intent[:80]}...")

    # 提取关键人格特征
    tm = max(d["thinking_mode"], key=d["thinking_mode"].get)
    vo = max(d["value_order"], key=d["value_order"].get)
    et = max(d["emotion_tone"], key=d["emotion_tone"].get)
    es = max(d["expression_style"], key=d["expression_style"].get)
    dp = max(d["decision_pref"], key=d["decision_pref"].get)
    sm = max(d["social_mode"], key=d["social_mode"].get)
    ra = max(d["risk_attitude"], key=d["risk_attitude"].get)
    sp = max(d["self_perception"], key=d["self_perception"].get)

    print(f"\n  【当前激活的人格特征】")
    tm_map = {"linear": "你会按逻辑顺序思考", "divergent": "你会从多角度发散思考", "critical": "你会先质疑再接受", "systematic": "你会从全局系统看问题"}
    vo_map = {"efficiency": "你优先考虑效率", "fairness": "你重视公平合理", "innovation": "你追求创新突破", "stability": "你看重稳定可靠", "relationship": "你关注人际关系"}
    et_map = {"optimistic": "你倾向于看到积极面", "pragmatic": "你务实落地", "pessimistic": "你会先想最坏情况", "neutral": "你保持中立客观"}
    es_map = {"concise": "你说话简洁直接", "detailed": "你喜欢详细说明", "humorous": "你自带幽默感", "serious": "你态度认真严肃"}

    print(f"  {tm_map.get(tm, '')}")
    print(f"  {vo_map.get(vo, '')}")
    print(f"  {et_map.get(et, '')}")
    print(f"  {es_map.get(es, '')}")

    print(f"\n  【人格驱动的回答框架】")
    print(f"  你的思考方式：{tm} → 先用{tm}方式理解问题")
    print(f"  你的价值判断：{vo} → 从{vo}角度评估")
    print(f"  你的情绪反应：{et} → 带着{et}情绪回应")
    print(f"  你的表达方式：{es} → 用{es}风格输出")
    print(f"  你的决策方式：{dp} → 基于{dp}做判断")
    print(f"  你的社交姿态：{sm} → 以{sm}姿态互动")
    print(f"  你的风险态度：{ra} → 采取{ra}策略")
    print(f"  你的自我定位：{sp} → {sp}地表达")

    print(f"\n  💡 以上是人格框架。具体回答内容需AI模型结合你的DNA特征生成。")
    print(f"  提示词：用{es}风格、{tm}思维、{vo}优先的价值观来回答以下问题...")

    print(f"\n{'='*60}\n")


def decide(scenario):
    """决策模拟"""
    if not os.path.exists(DNA_FILE):
        print("❌ 尚未采集人格数据")
        return

    with open(DNA_FILE, "r", encoding="utf-8") as f:
        dna = json.load(f)
    d = dna["dna"]

    dp = max(d["decision_pref"], key=d["decision_pref"].get)
    ra = max(d["risk_attitude"], key=d["risk_attitude"].get)
    vo = max(d["value_order"], key=d["value_order"].get)
    tm = max(d["thinking_mode"], key=d["thinking_mode"].get)

    print(f"\n{'='*60}")
    print(f"  🎯 决策模拟（基于你的DNA）")
    print(f"{'='*60}")
    print(f"  场景：{scenario[:80]}...")

    print(f"\n  【你的决策框架】")
    dp_map = {"data": "先看数据 → 量化对比 → 选最优", "intuition": "凭感觉 → 快速判断 → 相信直觉", "consensus": "找人商量 → 收集意见 → 达成共识", "authority": "查规定 → 按流程 → 照标准"}
    print(f"  决策偏好：{dp} → {dp_map.get(dp, '')}")

    ra_map = {"adventurous": "愿意冒风险搏收益", "moderate": "平衡风险与收益", "conservative": "优先规避风险"}
    print(f"  风险态度：{ra} → {ra_map.get(ra, '')}")

    vo_map = {"efficiency": "效率优先：哪个方案更快更省", "fairness": "公平优先：哪个方案更合理", "innovation": "创新优先：哪个方案更有突破性", "stability": "稳定优先：哪个方案更安全可靠", "relationship": "关系优先：哪个方案更利于人际关系"}
    print(f"  价值排序：{vo} → {vo_map.get(vo, '')}")

    print(f"\n  【你的决策链路】")
    print(f"  1. 用{tm}思维分析问题")
    print(f"  2. 以{vo}为第一优先级评估选项")
    print(f"  3. 基于{dp}方式做最终判断")
    print(f"  4. 采取{ra}策略执行")

    print(f"\n{'='*60}\n")


def rehearse(scene, context):
    """场景预演"""
    if not os.path.exists(DNA_FILE):
        print("❌ 尚未采集人格数据")
        return

    with open(DNA_FILE, "r", encoding="utf-8") as f:
        dna = json.load(f)
    d = dna["dna"]

    sm = max(d["social_mode"], key=d["social_mode"].get)
    es = max(d["expression_style"], key=d["expression_style"].get)
    et = max(d["emotion_tone"], key=d["emotion_tone"].get)
    sp = max(d["self_perception"], key=d["self_perception"].get)

    print(f"\n{'='*60}")
    print(f"  🎬 场景预演：{scene}")
    print(f"{'='*60}")
    print(f"  场景描述：{context[:80]}...")

    print(f"\n  【你在{scene}场景中的表现预测】")
    sm_map = {"extrovert": "你会主动互动，积极参与", "introvert": "你会先观察再发言，保持适度距离", "dominant": "你会主导对话节奏", "agreeable": "你会配合对方节奏，保持友好"}
    print(f"  社交姿态：{sm_map.get(sm, '')}")

    es_map = {"concise": "言简意赅，直击要点", "detailed": "会展开详细说明，举例论证", "humorous": "会用幽默化解紧张", "serious": "态度认真，保持专业"}
    print(f"  表达方式：{es_map.get(es, '')}")

    et_map = {"optimistic": "保持积极乐观的态度", "pragmatic": "实事求是，不夸大不贬低", "pessimistic": "会提前想好最坏情况的应对", "neutral": "保持客观中立"}
    print(f"  情绪状态：{et_map.get(et, '')}")

    sp_map = {"confident": "自信地表达自己的观点", "modest": "谦虚但坚定地表达", "self_critical": "会主动承认不足并说明改进方向"}
    print(f"  自我呈现：{sp_map.get(sp, '')}")

    print(f"\n  【预演要点】")
    print(f"  1. 开场姿态：{'主动出击' if sm == 'dominant' else '顺势而为'}")
    print(f"  2. 核心表达：{es_map.get(es, '')}")
    print(f"  3. 情绪管理：{et_map.get(et, '')}")
    print(f"  4. 收尾方式：{'留有余地' if sp == 'modest' else '明确结论'}")

    print(f"\n{'='*60}\n")


# ─── CLI ───

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法：python main.py <command> [options]")
        print("命令：collect | report | chat | decide | rehearse | reset")
        return

    cmd = sys.argv[1]

    if cmd == "collect":
        texts = []
        samples = []
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--text" and i + 1 < len(args):
                texts.append(args[i + 1]); i += 2
            elif args[i] == "--samples":
                i += 1
                while i < len(args) and not args[i].startswith("--"):
                    samples.append(args[i]); i += 1
            else:
                i += 1
        for sp in samples:
            try:
                with open(sp, "r", encoding="utf-8") as f:
                    texts.append(f.read())
            except Exception as e:
                print(f"⚠️ 无法读取 {sp}: {e}")
        if not texts:
            print("❌ 请提供文本：--samples file1.txt file2.txt ...（至少10个文件）")
            return
        collect(texts)

    elif cmd == "report":
        show_report()

    elif cmd == "chat":
        intent = None
        args = sys.argv[2:]; i = 0
        while i < len(args):
            if args[i] == "--intent" and i + 1 < len(args):
                intent = args[i + 1]; i += 2
            else:
                i += 1
        if not intent:
            print("❌ 用法：python main.py chat --intent \"...\"")
            return
        chat(intent)

    elif cmd == "decide":
        scenario = None
        args = sys.argv[2:]; i = 0
        while i < len(args):
            if args[i] == "--scenario" and i + 1 < len(args):
                scenario = args[i + 1]; i += 2
            else:
                i += 1
        if not scenario:
            print("❌ 用法：python main.py decide --scenario \"...\"")
            return
        decide(scenario)

    elif cmd == "rehearse":
        scene = None; context = None
        args = sys.argv[2:]; i = 0
        while i < len(args):
            if args[i] == "--scene" and i + 1 < len(args):
                scene = args[i + 1]; i += 2
            elif args[i] == "--context" and i + 1 < len(args):
                context = args[i + 1]; i += 2
            else:
                i += 1
        if not scene or not context:
            print("❌ 用法：python main.py rehearse --scene \"面试\" --context \"...\"")
            return
        rehearse(scene, context)

    elif cmd == "reset":
        if os.path.exists(DNA_FILE):
            os.remove(DNA_FILE)
        # 清理 data 目录
        for f in os.listdir(DATA_DIR):
            os.remove(os.path.join(DATA_DIR, f))
        print("🗑️ 所有人格数据已清除")

    else:
        print(f"❌ 未知命令：{cmd}")
        print("可用命令：collect | report | chat | decide | rehearse | reset")


if __name__ == "__main__":
    main()
