"""
一稿通：全平台爆款文案智能适配器
One Draft, All Platforms: Full-Platform Viral Copy Generator

核心引擎：平台适配 + 爆款学习 + AI去痕 + SEO优化
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class Platform(Enum):
    """内容平台"""
    XIAOHONGSHU = "小红书"
    WEIBO = "微博"
    DOUYIN = "抖音"
    WECHAT = "公众号"


@dataclass
class PlatformProfile:
    """平台画像"""
    name: str
    style: str
    word_count_range: Tuple[int, int]
    tone: str
    emoji_density: str  # 低/中/高
    hashtag_strategy: str
    opening_style: str
    closing_style: str


# 平台画像定义
PLATFORM_PROFILES = {
    Platform.XIAOHONGSHU: PlatformProfile(
        name="小红书",
        style="种草风、真实分享、亲切",
        word_count_range=(300, 800),
        tone="亲切随和，像朋友推荐好物。多用'我'开头，强调真实体验感。",
        emoji_density="高",
        hashtag_strategy="5-8个标签，包括类目标签+场景标签+人群标签",
        opening_style="用个人体验或痛点切入，制造共鸣",
        closing_style="互动引导（点赞收藏评论）"
    ),
    Platform.WEIBO: PlatformProfile(
        name="微博",
        style="短快狠、互动性强、有梗",
        word_count_range=(140, 280),
        tone="短小精悍，自带话题性。多用设问、反讽、对比制造讨论。",
        emoji_density="中",
        hashtag_strategy="1-2个核心话题词，用#话题词#格式",
        opening_style="直接抛出争议点或数据，制造话题",
        closing_style="互动引导（你怎么看？转发讨论）"
    ),
    Platform.DOUYIN: PlatformProfile(
        name="抖音",
        style="口语化、情绪强烈、节奏快",
        word_count_range=(50, 200),
        tone="高度口语化，像和朋友说话。黄金3秒抓住注意，多用感叹和疑问。",
        emoji_density="中",
        hashtag_strategy="3-5个热门话题标签",
        opening_style="黄金3秒：数字/反问/夸张观点",
        closing_style="明确行动指令（点赞关注、评论区见）"
    ),
    Platform.WECHAT: PlatformProfile(
        name="公众号",
        style="深度干货、人格化、有观点",
        word_count_range=(800, 2000),
        tone="专业但有温度，像领域专家娓娓道来。用故事开头，结构清晰。",
        emoji_density="低",
        hashtag_strategy="不使用标签，使用引导关注语",
        opening_style="用故事、数据或场景引入，建立信任感",
        closing_style="金句收尾+关注引导"
    ),
}


@dataclass
class HitDNA:
    """爆款DNA"""
    opening_type: str  # 开头类型
    emotional_curve: List[str]  # 情绪曲线
    structure_template: str  # 结构模板
    keywords_density: Dict[str, float]  # 关键词密度
    style_fingerprint: Dict[str, float]  # 风格指纹
    viral_score: float  # 传播潜力评分


@dataclass
class PlatformCopy:
    """平台文案"""
    platform: Platform
    title: str
    body: str
    hashtags: List[str]
    word_count: int
    engagement_hook: str  # 互动引导
    visual_suggestion: str  # 配图建议


class AITraceRemover:
    """AI痕迹消除引擎"""

    # AI写作六大特征及替换策略
    AI_PATTERNS = {
        "夸大象征意义": {
            "patterns": [
                r"是一种(?:精神|理念|态度|生活方式)",
                r"不仅仅[是]?(.+?)，更[是]?(.+?)",
                r"标志着(.+?)的重大(?:突破|变革|升级)",
            ],
            "replace_strategy": "用具体的功能、数据或使用场景替代抽象象征"
        },
        "宣传性语言": {
            "patterns": [
                r"(?:精心|匠心|用心)(?:打造|设计|制作)",
                r"为(?:您|用户|消费者)(?:打造|带来|呈现)",
                r"堪称(?:完美|极致|一流|顶级)",
            ],
            "replace_strategy": "用客观描述替代宣传语，让读者自己得出结论"
        },
        "三段式机械结构": {
            "patterns": [
                r"首先.+其次.+最后",
                r"第一[点]?.+第二[点]?.+第三[点]?",
                r"从(.+?)来看.+从(.+?)来看.+从(.+?)来看",
            ],
            "replace_strategy": "用自然段落过渡、故事串接替代机械式并列"
        },
        "AI万能词汇": {
            "vocabulary": [
                "值得注意的是", "不可否认", "众所周知",
                "换言之", "总体而言", "归根结底",
                "在当今时代", "随着...的发展"
            ],
            "replace_strategy": "直接删除或用口语化表达替代"
        },
        "破折号过度": {
            "patterns": [r"——.{5,50}——"],
            "replace_strategy": "限制破折号使用频率，用句号或其他标点替代"
        },
        "否定式排比": {
            "patterns": [r"不是(.+?)，而是(.+?)(?:，更不是(.+?))?"],
            "replace_strategy": "用正面陈述替代否定式排比"
        }
    }

    def detect_ai_traces(self, text: str) -> List[Dict]:
        """检测AI痕迹"""
        traces = []
        for category, info in self.AI_PATTERNS.items():
            if "patterns" in info:
                for pattern in info["patterns"]:
                    matches = re.findall(pattern, text)
                    if matches:
                        traces.append({
                            "category": category,
                            "count": len(matches),
                            "examples": matches[:3],
                            "suggestion": info["replace_strategy"]
                        })
            if "vocabulary" in info:
                found = [w for w in info["vocabulary"] if w in text]
                if found:
                    traces.append({
                        "category": category,
                        "count": len(found),
                        "examples": found[:3],
                        "suggestion": info["replace_strategy"]
                    })
        return traces

    def humanize(self, text: str, platform: Platform) -> str:
        """人性化改写"""
        profile = PLATFORM_PROFILES[platform]

        # 1. 移除AI万能词汇
        for word in self.AI_PATTERNS["AI万能词汇"]["vocabulary"]:
            text = text.replace(word, "")

        # 2. 限制破折号
        text = re.sub(r'——', '，', text)

        # 3. 添加口语化表达
        if platform == Platform.XIAOHONGSHU:
            text = text.replace("。", "~。") if "~" not in text else text
            coloquial_addons = ["姐妹们谁懂啊", "真的绝了", "良心推荐", "入股不亏"]
            if not any(c in text for c in coloquial_addons):
                text = coloquial_addons[0] + "！" + text

        elif platform == Platform.DOUYIN:
            coloquial_addons = ["你绝对想不到", "姐妹们快冲", "这个真的可以"]
            if not any(c in text for c in coloquial_addons):
                text = coloquial_addons[0] + "！" + text

        return text


class HitDNAExtractor:
    """爆款DNA提取器"""

    def analyze(self, text: str) -> HitDNA:
        """分析爆款文案DNA"""
        # 分析开头类型
        opening = text[:100]
        if "?" in opening or "？" in opening:
            opening_type = "疑问钩子"
        elif any(d in opening for d in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
            opening_type = "数字钩子"
        elif "你" in opening:
            opening_type = "对话钩子"
        else:
            opening_type = "故事钩子"

        # 分析情绪曲线
        emotional_curve = self._analyze_emotional_curve(text)

        # 提取结构模板
        structure = self._extract_structure(text)

        # 关键词密度分析
        keywords = self._keyword_density(text)

        # 风格指纹
        fingerprint = self._style_fingerprint(text)

        # 传播潜力评分
        viral_score = self._calc_viral_score(text)

        return HitDNA(
            opening_type=opening_type,
            emotional_curve=emotional_curve,
            structure_template=structure,
            keywords_density=keywords,
            style_fingerprint=fingerprint,
            viral_score=viral_score
        )

    def _analyze_emotional_curve(self, text: str) -> List[str]:
        """分析情绪曲线"""
        curve = ["开篇：制造共鸣/好奇"]
        if "!" in text or "！" in text:
            curve.append("中段：制造情绪高点")
        if "?" in text or "？" in text:
            curve.append("互动：引发思考/讨论")
        curve.append("结尾：行动引导")
        return curve

    def _extract_structure(self, text: str) -> str:
        """提取结构模板"""
        if "场景" in text or "那天" in text or "昨天" in text:
            return "场景代入式：真实场景 → 问题描述 → 解决方案 → 效果对比"
        elif "?" in text or "？" in text:
            return "问题驱动式：抛问题 → 讲述痛点 → 给答案 → 驱动行动"
        elif any(w in text[:50] for w in ["1", "2", "3", "首先"]):
            return "清单列举式：结论先行 → 分点论证 → 总结提炼 → 收藏引导"
        else:
            return "故事叙事式：人物/事件 → 冲突 → 转折 → 感悟 → 引导"

    def _keyword_density(self, text: str) -> Dict[str, float]:
        """关键词密度分析"""
        words = text.replace("\n", " ").replace("。", " ").split()
        total = max(len(words), 1)
        # 提取高频词TOP10
        word_freq = {}
        for w in words:
            if len(w) >= 2:
                word_freq[w] = word_freq.get(w, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return {w: c/total for w, c in top_words}

    def _style_fingerprint(self, text: str) -> Dict[str, float]:
        """风格指纹分析"""
        return {
            "口语化程度": min(1.0, text.count("！") / max(len(text)*0.001, 1)),
            "专业度": min(1.0, len([w for w in text.split() if len(w) > 4]) / max(len(text.split()), 1)),
            "互动性": min(1.0, (text.count("?") + text.count("？")) / max(len(text)*0.001, 1)),
            "感召力": min(1.0, (text.count("!") + text.count("！")) / max(len(text)*0.001, 1)),
            "亲和力": min(1.0, text.count("你") / max(len(text.split()), 1) * 2),
        }

    def _calc_viral_score(self, text: str) -> float:
        """计算传播潜力评分"""
        score = 5.0  # 基础分

        # 标题优化
        if any(d in text[:50] for d in "123456789"):
            score += 1
        if "?" in text[:50] or "？" in text[:50]:
            score += 0.5
        if "!" in text[:50] or "！" in text[:50]:
            score += 0.5

        # 互动元素
        interactive_words = ["点赞", "收藏", "关注", "评论", "转发", "你怎么看", "你觉得"]
        score += sum(0.2 for w in interactive_words if w in text)

        return min(10, score)


class PlatformAdapter:
    """平台适配引擎"""

    def adapt(self, core_idea: str, platform: Platform, hit_dna: Optional[HitDNA] = None) -> PlatformCopy:
        """将核心idea适配到指定平台"""
        profile = PLATFORM_PROFILES[platform]

        # 生成标题
        title = self._generate_title(core_idea, platform, hit_dna)

        # 生成正文
        body = self._generate_body(core_idea, platform, profile, hit_dna)

        # 生成标签
        hashtags = self._generate_hashtags(core_idea, platform)

        # 生成互动引导
        engagement = self._generate_engagement(platform)

        # 配图建议
        visual = self._generate_visual_suggestion(core_idea, platform)

        return PlatformCopy(
            platform=platform,
            title=title,
            body=body,
            hashtags=hashtags,
            word_count=len(body),
            engagement_hook=engagement,
            visual_suggestion=visual
        )

    def _generate_title(self, idea: str, platform: Platform, hit_dna=None) -> str:
        """生成平台适配标题"""
        if platform == Platform.XIAOHONGSHU:
            patterns = [
                f"终于找到{idea.split('的')[0] if '的' in idea else idea[:10]}了！谁懂啊😭✨",
                f"用了30天，{idea[:15]}真的绝了！",
                f"真诚分享 | {idea[:20]}📝",
            ]
        elif platform == Platform.WEIBO:
            patterns = [
                f"说实话，{idea[:20]}这件事...#{idea[:10]}#",
                f"{idea[:25]}是来整顿行业的吗？",
                f"爆料：{idea[:20]}你绝对不知道的真相",
            ]
        elif platform == Platform.DOUYIN:
            patterns = [
                f"换过3次才找到！{idea[:15]}真的太香了",
                f"别再被割韭菜了！{idea[:15]}我帮你们试了",
                f"9成人不知道的{idea[:15]}秘密",
            ]
        else:
            patterns = [
                f"{idea[:20]}：一个被忽略的真相",
                f"深度解析 | {idea[:25]}背后的逻辑",
                f"关于{idea[:15]}，我想说点不一样的",
            ]
        return patterns[0]

    def _generate_body(self, idea: str, platform: Platform, profile: PlatformProfile, hit_dna=None) -> str:
        """生成平台适配正文"""
        if platform == Platform.XIAOHONGSHU:
            return f"""{idea[:30]}的经历有没有姐妹跟我一样的😭

之前一直用的XX，感觉也还行但总觉得差点意思。直到最近换了{idea[:20]}，才明白什么叫做真香！🔥

用了大概两周，最大的感受就是——{idea[:15]}真的太方便了！！
具体说说我的使用体验：

1️⃣ 第一点：{idea[:15]}的体验远超预期，每天用起来都觉得很舒服
2️⃣ 第二点：之前担心的xxx问题完全没有出现
3️⃣ 第三点：性价比真的绝了，同价位完全找不到对手

如果是跟我一样有xxx需求的朋友，真的可以冲！不踩雷！！！💯

推荐指数：⭐⭐⭐⭐⭐

#好物分享 #干货推荐 #生活小技巧 #{idea[:10]}"""

        elif platform == Platform.WEIBO:
            return f"""说实话，{idea[:20]}这件事比你想象的要有意思多了。

你可能会问为什么？其实很简单——{idea[:15]}改变的不是一个点，是一整套体验。

用过都说好，没用过都在观望。你觉得呢？#行业观察#"""

        elif platform == Platform.DOUYIN:
            return f"""你绝对想不到！{idea[:15]}居然这么好用！

作为一个用过不下10款同类产品的人，我敢说{idea[:20]}是目前最强的！

记住这三点就够了：
① 核心卖点
② 核心卖点
③ 核心卖点

快去试试，不好用来找我！#推荐 #干货"""

        else:  # WECHAT
            return f"""你有没有遇到过这种情况：想找一个{idea[:10]}的产品，翻遍了所有推荐，要么太贵，要么不好用？

我之前就是这样。

直到我遇到了{idea[:20]}。

今天这篇文章，我就从一个普通用户的角度，聊聊{idea[:15]}到底值不值得，以及它改变了我哪些习惯。

---

## 一、为什么{idea[:10]}这么重要？

说到底，{idea[:15]}解决的是一个最基础但最容易被忽略的问题——xxx。

## 二、实际体验如何？

用了两周后，我发现...

## 三、它适合谁？

如果你符合以下任何一种情况，{idea[:10]}大概率适合你：
- 每天需要xxx的人
- 对xxx有要求的人
- 追求xxx体验的人

---

**最后说一句**

{idea[:10]}不是万能的，但它确实解决了我的一个核心痛点。如果你也在纠结要不要入手，我的建议是：试一下。

如果你喜欢这篇文章，欢迎点赞在看，我们下期见。"""

    def _generate_hashtags(self, idea: str, platform: Platform) -> List[str]:
        """生成平台标签"""
        base_tags = [idea[:10], "好物推荐", "干货分享"]

        if platform == Platform.XIAOHONGSHU:
            return base_tags + ["种草", "生活中那些小美好", "提升幸福感", "分享日常", "好物分享"]
        elif platform == Platform.WEIBO:
            return [f"#{idea[:10]}#", "#来聊聊#"]
        elif platform == Platform.DOUYIN:
            return base_tags + ["推荐", "干货", "种草"]
        else:
            return []

    def _generate_engagement(self, platform: Platform) -> str:
        """生成互动引导"""
        hooks = {
            Platform.XIAOHONGSHU: "如果觉得有用就点赞收藏吧~还有什么想知道的评论区告诉我！💕",
            Platform.WEIBO: "你怎么看？转发说说你的看法👇",
            Platform.DOUYIN: "你觉得呢？评论区见！别忘了点赞关注！🔥",
            Platform.WECHAT: "如果你觉得有收获，欢迎点赞在看，转发给需要的朋友。"
        }
        return hooks[platform]

    def _generate_visual_suggestion(self, idea: str, platform: Platform) -> str:
        """生成配图建议"""
        suggestions = {
            Platform.XIAOHONGSHU: "建议配图：使用场景图（3-4张）+ 对比图 + 干货信息图（封面需带有吸引人的标题文字）",
            Platform.WEIBO: "建议配图：信息长图/九宫格对比图/投票卡片",
            Platform.DOUYIN: "建议配图：产品特写+使用过程+效果对比，封面需有吸引人的文字",
            Platform.WECHAT: "建议配图：头图（品牌调性）+ 文中插图（数据图/场景图）+ 尾图（引导关注）"
        }
        return suggestions[platform]


# SEO优化引擎
class SEOOptimizer:
    """SEO优化引擎"""

    TITLE_PATTERNS = [
        "数字型": "{数字}个{主题}，{结果}",
        "疑问型": "{问题}？答案在这里",
        "对比型": "用了{产品A}才知道{产品B}差在哪",
        "命令型": "别再{错误行为}了！试试{正确方案}",
        "揭秘型": "9成人不知道的{主题}秘密",
        "清单型": "{主题}必看的{N}个建议",
        "故事型": "从{困境}到{成果}，我做了什么",
    ]

    def optimize_title(self, title: str, platform: Platform) -> List[str]:
        """标题优化，生成多个候选"""
        results = []
        for pattern_name, pattern in self.TITLE_PATTERNS.items():
            new_title = pattern.format(
                数字="5",
                主题=title[:15] if len(title) > 15 else title,
                结果="太香了",
                问题=title[:15] + "到底值不值得",
                产品A=title[:8] if len(title) > 8 else title,
                产品B="之前的",
                错误行为=title[:10] + "了" if len(title) > 10 else title,
                正确方案=title[:10] if len(title) > 10 else title,
                N="3",
                困境="踩坑",
                成果="真香"
            )
            results.append(f"[{pattern_name}] {new_title}")
        return results


# 全平台生成引擎
class OneDraftEngine:
    """一稿通主引擎"""

    def __init__(self):
        self.adapter = PlatformAdapter()
        self.seo = SEOOptimizer()
        self.trace_remover = AITraceRemover()
        self.dna_extractor = HitDNAExtractor()

    def generate_all_platforms(self, core_idea: str) -> Dict[Platform, PlatformCopy]:
        """一键生成全平台文案"""
        results = {}
        for platform in Platform:
            copy = self.adapter.adapt(core_idea, platform)
            # AI去痕
            copy.body = self.trace_remover.humanize(copy.body, platform)
            results[platform] = copy
        return results

    def analyze_hit(self, text: str) -> HitDNA:
        """分析爆款DNA"""
        return self.dna_extractor.analyze(text)

    def remove_ai_traces(self, text: str, platform: str = "公众号") -> Dict:
        """消除AI痕迹"""
        platform_enum = getattr(Platform, platform.upper(), Platform.WECHAT)
        traces = self.trace_remover.detect_ai_traces(text)
        humanized = self.trace_remover.humanize(text, platform_enum)
        return {
            "traces": traces,
            "humanized": humanized
        }

    def optimize_titles(self, idea: str, platform: str = "公众号") -> List[str]:
        """优化标题"""
        platform_enum = getattr(Platform, platform.upper(), Platform.WECHAT)
        return self.seo.optimize_title(idea, platform_enum)


# 示例
if __name__ == "__main__":
    engine = OneDraftEngine()

    # 示例1：生成全平台文案
    idea = "智能手环，续航14天，监测心率血氧睡眠"
    results = engine.generate_all_platforms(idea)

    for platform, copy in results.items():
        print(f"\n{'='*50}")
        print(f"📱 {platform.value}")
        print(f"📝 标题：{copy.title}")
        print(f"📊 字数：{copy.word_count}")
        print(f"🏷️ 标签：{', '.join(copy.hashtags)}")
        print(f"💬 互动：{copy.engagement_hook}")
        print(f"🎨 配图：{copy.visual_suggestion}")
        print(f"\n{copy.body[:200]}...")

    # 示例2：SEO优化
    print("\n\n🔍 SEO标题优化：")
    for title in engine.optimize_titles("智能手环", "公众号"):
        print(f"  {title}")
