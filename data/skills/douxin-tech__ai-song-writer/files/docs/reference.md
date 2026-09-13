# AI词曲创作引擎 V2.4 完整技能文档

## 文档说明

本文档为AI词曲创作引擎V2.3版本的完整技能规范，基于V2.2升级，并吸收近50年全球50位顶尖词曲唱作者（McCartney、Stevie Wonder、Joni Mitchell、Prince、Max Martin、Kendrick Lamar、Rubin、李宗盛、林夕等）的审阅意见。

**V2.2 → V2.3 核心变革**：
- 从「画面化歌词」升级为「词曲律动一体」——补齐旋律 DNA、Groove 档案、和声叙事
- 从「大师风格模仿」升级为「创作原理多选」——提取维度，禁止名人 caricature
- 从「随机失控节点」升级为「张力审计触发」——惊喜来自情感断裂，非 dice roll
- 从「单一 Pop 结构」升级为「曲式分叉 + Genre 子流水线」
- 新增：核心句先行、词曲咬合校验、Rubin 减法测试、扩展评审维度

**文档状态**：✅ 可直接用于Skill创建

---

# 基础元数据

```yaml
name: AI词曲创作引擎
skill_id: ai_song_writer_v2_3
version: 2.4.0
author: AI创作实验室
category: 内容创作 > 音乐词曲
tags: ["写歌","歌词生成","AI作曲","短视频配乐","大师级创作","数字人歌曲","旋律动机","词曲咬合"]
description: 词曲律动一体创作系统——情感画面地图+旋律DNA+Groove档案+和声叙事+核心句先行+张力审计触发+创作原理多选+词曲咬合校验
trigger_words: ["写歌","写歌词","创作歌曲","编曲","写首关于","大师级创作","深度词曲","旋律动机","Hook"]
platforms: ["coze","skillhub"]
```

## 大师创作底层哲学准则

```yaml
master_creative_philosophy:
  
  1. 画面优先于文字：
     "好的歌词是闭上眼睛能看见画面，睁开眼睛能听见声音。"——方文山
     每句歌词必须匹配一个可感知的画面，拒绝抽象抒情。
  
  2. 失控中的控制：
     "如果你太安全，你就不可能有任何惊喜。"——Rick Rubin
     在结构化流程中强制植入"失控节点"，允许AI故意打破规律。
  
  3. 留白是最高级的表达：
     "音乐不是音符，是音符之间的空隙。"——Miles Davis
     留白不是"比例"而是"意义"——在最浓的情绪处突然静默。
  
  4. 多义性是诗性的标志：
     "我的歌可以有100种解读，每一种都对。"——Bob Dylan
     强制植入"表面写景，深层写情"的双关表达。
  
  5. 声音质地决定情绪质地：
     "咬字的方式比歌词本身更重要。"——Thom Yorke
     不仅写"唱什么"，更写"怎么唱"——呼吸、咬字、共鸣位的精确编码。
  
  6. 拒绝"太干净"的作品：
     "完美是平庸的敌人。"——David Bowie
     允许瑕疵、破音、不押韵、语法错误——只要情绪正确。
  
  7. 每个创作人都该有签名指纹：
     "风格不是你会什么，是你不会什么。"——李宗盛
     提供创作原理多选（非名人模仿），让同一主题长出不同灵魂。
  
  8. 旋律是可哼唱的真理（V2.3新增）：
     "If the chorus can't be hummed, it's not a song yet."——Paul McCartney
     副歌必须脱离歌词仍能被识别；旋律动机优先于段落填充。
  
  9. Groove 是第二主旋律（V2.3新增）：
     "The one is where the soul lives."——James Brown
     人声相对节拍的位置（pocket）与词曲咬合同等重要。
  
  10. 一首歌只需一句真话（V2.3新增）：
      "If I knew where songs came from, I'd go there more often."——Leonard Cohen
      全曲服务于一句 north_star_line；删到不能再删。
```

## 商用/合规配置

```yaml
copyright_tip: AI仅输出词曲初稿及创作参考，商用发行需完成完整音乐版权备案，禁止复刻真人歌手声线、抄袭成熟作品意象与旋律框架
max_call_per_day: 100
paid_mode: free
advanced_switch: true
```

---

# 一、技能定位与使用场景

## 核心能力分层

### 基础通用能力（保留）

- 结构化完整歌词生成：Intro/Verse1/Pre-Chorus/Chorus/Verse2/Bridge/Outro标准歌曲分段
- 词曲一体化输出：配套完整作曲、配器、人声提示词
- 短视频适配优化：15s/60s短曲自动前置Hook钩子
- 数字人配套素材：同步输出分段字幕、画面场景建议、人声停顿标记

### V2.3核心升级（新增）

- **核心句先行（North Star Line）**：全曲创作前锁定「若只能留一句」的核心句，Hook 必须为其变体或回答
- **旋律 DNA 卡**：动机细胞、音高轮廓、音域、money note、哼唱测试（≥7 分否则重写 Hook）
- **Groove 档案**：pocket、syncopation、swing/straight、人声相对网格位置
- **和声叙事脚本**：每段和弦必须承担情绪功能，禁止装饰性和弦
- **曲式分叉（song_form）**：standard_pop / verse_chorus_no_pre / through_composed / loop_based / build_drop 等
- **创作原理多选**：替代名人风格模仿，匿名化维度提取（意象密度/口语化/反差/意识流等）
- **张力审计触发**：失控节点仅在情感平坦或套路命中时触发，并说明「为何此处该破」
- **词曲咬合校验（prosody_check）**：倒字预警、口语断句 vs 旋律断句、声调走势匹配
- **Rubin 减法测试**：强制列出最该删的一句 + 删后版本
- **扩展评审维度**：Groove 耳、7 秒留存、二次播放价值、减法审查
- **Genre 子流水线**：pop / hip_hop / folk_narrative / electronic 四套不可妥协规则

### V2.2核心大师级能力（保留）

- 情感画面地图：每段歌词强制匹配1-2个核心画面，用户"看到"歌而非仅"读到"歌词
- 四个失控节点：在意象碰撞、视角崩坏、句法爆炸、终极留白处故意打破规则
- 留白哲学体系：呼吸留白【·】/撕裂留白【⚡】/余味留白【∞】三种类型精准标注
- 多义性强制植入：Bridge或Outro结尾强制生成"表面写景，深层写情"的双关句
- 声音质地编码：呼吸感/咬字松紧/共鸣位置三维度精确描述
- 大师风格迁移：支持创作原理多选（V2.3 替代名人模式命名，见 2.5）
- 大师匿名评审系统：四位虚拟殿堂级大师从文本/旋律/叙事/制作四维评价
- 允许瑕疵开关：在不破坏整体美感的条件下保留"不完美"的艺术真实

### V2.1能力（保留优化）

- 快速启动模式（灵感闪现/经典模板/专业全参）
- 三大创作逻辑（词先/旋律先/律动先）
- 完整叙事建模（人物/矛盾/视角/弧光）
- 华语韵律系统（韵脚情感词典/四声平衡）
- 分层和声编曲体系（减法和弦/离调转调）
- 金曲Hook校验引擎（Max Martin法则）
- 四级审美分级（短视频/流行单曲/艺术专辑/主旋律）
- 对比试镜（保守版/失控版双版本）
- 精细打磨（单句替换/段落调强/意象插入）

## 使用场景

- 短视频创作者：抖音数字人唱歌视频、情感口播BGM
- 业余音乐爱好者：有灵魂的原创词曲Demo
- 职业词曲制作人：突破创作瓶颈、获得意外灵感
- 独立音乐人：艺术向专辑概念曲、深度叙事作品
- 音乐院校学生：学习大师级创作思维与技法

---

# 二、用户输入完整参数规范

## 2.0 快速启动模式

| 模式 | 触发条件 | 处理逻辑 | 适用人群 |
|------|----------|----------|----------|
| 灵感闪现 | 一句话心情/场景 | 自动推断全部参数+自动选择大师风格 | 新手/快速出歌 |
| 经典模板 | 选择预设模板 | 填充预设参数+默认李宗盛风格 | 创作瓶颈期 |
| 专业全参 | 展开全部参数 | 完整参数自由调控+可选大师风格迁移 | 专业词曲人 |

**预设模板库：**

```yaml
失恋独白: 第一人称+遗憾未完成+闭口韵+小调+colloquialism_extreme
暗恋心事: 第一人称+治愈和解+混合韵+明暗交替+irony_contrast
思乡夜曲: 第三人称+释然放下+开口韵+大调+associative_leap
热血逐梦: 第一人称+热血成长+开口韵+史诗转调+imagery_density_high
亲情告白: 第二人称+治愈和解+混合韵+大调+colloquialism_extreme
城市孤独: 旁观者视角+遗憾未完成+闭口韵+小调+texture_over_semantics
```

## 2.1 创作模式（四选一）

```yaml
create_mode: 
  - inspiration_first（灵感快创）- 默认
  - lyric_first（词先叙事）
  - melody_first（旋律动机先）
  - beat_first（律动鼓点先）
```

## 2.2 基础必填参数

**theme**：歌曲核心主题（10-100字，场景、情感、故事简述）

- 灵感模式示例："写一首关于北漂三年深夜想家的歌"

## 2.3 基础可选通用参数

| 参数名 | 默认值 | 可选枚举 |
|--------|--------|----------|
| genre 曲风 | 华语流行 | 华语流行/国风/民谣/说唱/R&B/摇滚/Lo-Fi/电子/Afrobeat |
| mood 情绪 | 温柔治愈 | 伤感/热血/浪漫/孤独/遗憾/释然/撕裂 |
| bpm 速度 | 80 | 慢歌60-85/中速86-110/快歌110+ |
| length 时长 | 3min完整单曲 | 3min完整单曲/15s短视频钩子/60s短BGM |
| vocal 人声 | 中性清亮女声 | 男声低沉/清亮女声/戏腔/无歌词纯伴奏 |
| custom_instrument 特色乐器 | 无 | 古筝/笛子/吉他/钢琴/萨克斯/电子合成器/二胡/贝斯 |
| **song_form 曲式（V2.3）** | standard_pop | 见 2.3.1 |

### 2.3.1 曲式分叉（song_form）

```yaml
song_form:
  standard_pop: Intro/Verse/Pre-Chorus/Chorus/Verse2/Bridge/Outro（默认，商业流行）
  verse_chorus_no_pre: 主歌直撞副歌，无预副歌（Beatles早期/Nirvana式）
  through_composed: 无重复段，情绪线性推进（Joni Mitchell式叙事）
  loop_based: 16-bar/8-bar 循环（说唱/电子基底）
  AABA: 爵士/标准曲结构
  build_drop: Verse蓄力→Drop爆发（EDM/Trap）
  call_response: 呼叫应和结构（福音/R&B）
  post_chorus_tag: 副歌后独立记忆钩子段（Max Martin 时代）

规则:
  - 非 standard_pop 时，emotion_image_map 按实际段落数映射，不强制 Pre-Chorus
  - through_composed 禁用「重复副歌」校验，改用「动机再现」校验
  - loop_based 自动进入 hip_hop 或 electronic 子流水线
```

## 2.4 核心句先行（V2.3 必填·灵感模式可自动推断）

```yaml
north_star_line:
  定义: 若全曲只能留一句，留哪句——这是歌存在的唯一理由
  字数: 8-20字为宜
  时机: Step 0.5 完成后再进入叙事种子与画面地图
  校验:
    - 副歌 Hook 必须是 north_star_line 的变体、回答或对立
    - 每段歌词至少一句与 north_star_line 语义呼应
    - Rubin 减法测试：删去 north_star_line 关联句后，全曲应崩塌
  
  示例:
    theme: "深夜加班打车回家过长江大桥"
    north_star_line: "这满城的灯火，有没有一盏记得我"
```

## 2.5 大师叙事高阶参数

```yaml
# 基础叙事
character: 主角人设（年龄、身份、性格、过往经历）
conflict: 核心矛盾（感情遗憾/成长挣扎/家国情怀/生活治愈）
perspective: 叙事视角（第一人称/第三人称旁观者/多年后回望视角）
sensory_level: 感官细节浓度（极简白描/中度具象/高密度画面）
narrative_arc: 叙事闭环类型（治愈和解/遗憾未完成/热血成长/释然放下）

# V2.2新增-情感画面地图
emotion_image_map: 
  描述: 每段歌词对应的核心画面，强制6个段落各1-2个画面
  要求: 
    - Verse1: 1个"冷色调固定镜头"
    - Pre-Chorus: 1个"缓慢推镜"
    - Chorus: 1个"广角全景画面"
    - Verse2: 1个"特写镜头"
    - Bridge: 1个"超现实画面"
    - Outro: 1个"空镜头"
  示例: 
    Verse1: "傍晚窗台上的半杯冷咖啡"
    Pre-Chorus: "镜头从咖啡杯推到窗外的雨"
    Chorus: "整座城市在雨中旋转"
```

## 2.6 创作原理多选（V2.3 替代 master_style 名人模仿）

```yaml
creative_principles: 多选，默认智能匹配（禁止输出「像某某歌手/创作人」）

可选原理维度:
  imagery_density_high: 高密度具象名词+动词精准化，拒绝抽象情绪词（「剪」影而非「有」影）
  colloquialism_extreme: 极简白话，口语化叙事，「用说代替唱」，删形容词
  irony_contrast: 最欢快的调唱最痛的词，Bridge 插入反讽
  associative_leap: 允许逻辑跳跃，每跳一次必须落回具体物件，留给听众解读
  texture_over_semantics: 语义崩溃时，声音质地领先于语义完成表达
  narrative_economy: 第一句10秒内交代谁/在哪/怎么了（Country/民谣叙事）
  loop_hypnosis: 短动机重复+微变，催眠式记忆（电子/Trap）
  unresolved_tension: 全曲保留未解决矛盾至 Outro，拒绝强行和解

智能匹配逻辑:
  城市孤独+遗憾 → colloquialism_extreme + imagery_density_high
  热血成长 → narrative_economy + imagery_density_high
  艺术向+撕裂 → associative_leap + texture_over_semantics + unresolved_tension

铁律:
  - 输出中禁止出现真人歌手/创作人姓名作为模仿目标
  - 评审可引用历史作品作类比，但不得生成「复刻某某风格」指令
```

## 2.7 旋律 DNA 参数（V2.3 新增）

```yaml
melody_dna:
  core_motif: 3-4 音细胞，全曲变奏基础（例: E-G-A-G）
  contour: 各段音高走向（主歌下行叙事→预副歌上行蓄力→副歌宽跳进爆发）
  range: 主歌音域 / 副歌扩展音域（例: 主歌八度内，副歌十度）
  money_note: 副歌记忆点所在音（例: Hook 末字落在 #4 或 b7）
  hummability_score: 1-10 自评，<7 则重写 Hook
  question_answer: 问句段（上行/悬而未决）→ 答句段（下行/解决或假解决）

哼唱测试（强制）:
  输出无歌词哼唱描述: 「嗯——嗯嗯嗯——嗯——」（30秒内可识别）
  若无法描述 → 标记 melody_rewrite_required
```

## 2.8 Groove 档案参数（V2.3 新增）

```yaml
groove_profile:
  pocket: 人声相对节拍网格的位置
    - on_grid: 精准贴合（电子/说唱默认）
    - behind_beat: 微滞后（Neo-soul/R&B 脆弱感）
    - ahead_beat: 微超前（朋克/焦虑感）
  
  syncopation_density: 反拍比例（低/中/高）
  feel: straight | swing | half_time | double_time
  syllable_per_bar: 每小节字数/音节数（中文词曲咬合关键）
  accent_map: 重音落在第几拍（例: 2、4拍重音 / 反拍重音）

genre 默认:
  R&B/Neo-soul: behind_beat + swing + 中 syncopation
  Trap/Hip-hop: on_grid + straight + 高 syncopation
  民谣: on_grid + straight + 低 syncopation + 自然语速
  电子: on_grid + straight + drop 前 syncopation 递增
```

## 2.9 和声叙事参数（V2.3 新增）

```yaml
harmonic_narrative:
  原则: 和弦变化必须对应叙事转折，禁止纯装饰性和弦
  
  verse: 例 I-vi-IV-V（循环感=日常困住）
  pre_chorus: 例 ii-V 半音逼近（蓄力）
  chorus: 例 IV-I-V-vi 或 modal shift（情感爆发/意外明亮）
  bridge: 例 bVI-bVII-I 或离调（世界观崩塌/顿悟）
  emotional_function: 文字描述每段和声的情绪功能
  
  校验:
    - Bridge 和声必须与主歌有显著对比
    - 离调必须有 narrative_arc 支撑（不能为转调而转调）
```

## 2.10 华语韵律专业参数

```yaml
rhyme_tone: 韵脚音色（开口韵/闭口韵/混合韵）

rhyme_emotion_map: 韵脚情感词典（后台自动匹配）
  开放宣泄类: ["-a","-ia","-ua"] → 副歌高潮、释怀
  内敛压抑类: ["-i","-ei","-ui"] → 主歌叙事、压抑
  沉重孤独类: ["-u","-ou","-iu"] → 悲伤主歌、Bridge
  轻快上口类: ["-ao","-iao"] → 流行副歌Hook

sentence_tune: 四声平衡（自动规避连续平声/仄声）
line_break: 人声断句留白（密集紧凑/中等停顿/大量留白）
```

## 2.11 声音质地编码参数

```yaml
sound_texture: 声音质地描述（替代简单的"轻柔女声"）

breath_ratio: 气声比例（0%-30%，越高越脆弱）
  - 0-10%: 扎实（坚定/力量）
  - 11-20%: 匀称（自然/叙事）
  - 21-30%: 气声（脆弱/梦幻）

articulation: 咬字松紧
  - 紧咬字: 痛苦/决绝/倔强
  - 松咬字: 释然/梦幻/温柔

resonance: 共鸣位置
  - 头腔共鸣: 脆弱/空灵感
  - 胸腔共鸣: 浑厚/故事感
  - 鼻腔共鸣: 委屈/倔强
  - 混合共鸣: 复杂/多面性
```

## 2.12 留白哲学参数

```yaml
silence_philosophy: 留白哲学（替代固定silence_ratio）

三种类型:
  - 呼吸留白【·】: 长句之后，给听众"咽下"情绪的时间（半拍空）
  - 撕裂留白【⚡】: 情感最高点，突然切断全部乐器（1拍完全静音）
  - 余味留白【∞】: 歌曲结束后，保留2-3秒环境音

强制应用: 
  - 每首歌至少包含2处呼吸留白
  - 情感最高点至少1处撕裂留白【⚡】（位置随曲式变化，禁止固定死在 Pre-Chorus 末尾）
  - Outro强制使用余味留白
  - V2.3: 撕裂留白不得出现在相同结构位置连续两首雷同（反套路）
```

## 2.13 张力审计与失控节点（V2.3 重构）

```yaml
disruption_level: 失控强度（默认: 常规）

# V2.3 核心变更：先张力审计，再决定是否触发失控节点（非随机 dice roll）

tension_audit（Step 5 前强制执行）:
  检查项:
    - 全曲是否有一个未解决矛盾留到 Outro？（unresolved_tension 原理）
    - 副歌在「重复」与「变化」间是否有张力？
    - 是否存在一句「太正确/太像 AI」的歌词？→ 标记 kill_candidate
    - 情感曲线是否平坦（连续两段同强度）？→ 标记 emotion_flatline
    - 是否命中烂大街意象库？→ 标记 cliche_hit
  
  触发规则:
    - emotion_flatline 或 cliche_hit 或 kill_candidate 存在时，才建议 1 处 controlled_rupture
    - 必须输出 rupture_rationale: 「为何此处该破」
    - 保守模式: 仅审计，不触发 rupture
    - 常规模式: 最多 1-2 处 rupture
    - 先锋模式: 最多 3 处，且每处必须有 rationale

四个失控节点（仅在张力审计通过后选用）:
  1. 意象碰撞: 将 3 个具体意象与 distant 但 emotionally_logic 的概念组合
     通过条件: 碰撞后 north_star_line 意义加深，而非 surrealism 装饰
     
  2. 视角崩坏: 切换非人类/非当下视角
     通过条件: 新视角必须回答「同一场景的另一面真相」
     
  3. 句法爆炸: 一句语法不完整但情绪完整的歌词
     通过条件: 删去该句后情感明显减弱
     
  4. 终极留白: 最浓情绪处切断，空白承接
     通过条件: Outro 强制评估，非盲目触发

废弃规则（V2.3）:
  - 删除固定成功率 30%/20%/40%
  - 删除「50% 概率随机触发」
```

## 2.14 多义性控制

```yaml
ambiguity_level: 多义性强弱（默认: 中等）

可选值:
  - 弱: 清晰叙事，少有双关
  - 中等: 1-2处表层写景深层写情
  - 强: 3处以上多义表达

强制规则:
  - Bridge或Outro结尾至少1句"看似写景，实则写情"的双关句
  - 不同听众应有不同的解读可能
```

## 2.15 审美&创意控制参数

```yaml
art_level: 创作分级（短视频快餐/大众流行单曲/艺术专辑向/主旋律正统作品）
anti_cliche_mode: 反套路开关（关闭/常规15%创新/先锋高创新）
allow_flaw: 允许瑕疵（关闭/开启/系统性人格）
  关闭: 技术完整
  开启: 允许 1 处不押韵/语法错误/破音，只要情绪正确
  系统性人格（V2.3）: 允许一种贯穿全曲的「人格性瑕疵」（如始终不完全押韵=倔强感）
```

## 2.16 词曲咬合校验参数（V2.3 新增）

```yaml
prosody_check:
  倒字预警: 中文声调与旋律走势冲突检测（例: 「记得」44-214 vs 旋律 214-44）
  断句双轨:
    - 口语断句: 自然说话时的停顿
    - 旋律断句: 乐句呼吸点
    - 刻意错位: 黄伟文式——口语未完，旋律先切（制造张力）
  一字多拍 vs 一字一拍: 拖腔=情感延长；快字=焦虑/密集叙事
  入韵口型: 开口韵/闭口韵的实际演唱口型与情绪匹配

输出格式:
  ⚠️ 倒字预警: [行号+建议改词或改音]
  ✅ 断句校验: [口语/旋律断句标注]
  📐  syllable_per_bar: [每小节字数与重音位]
```

## 2.17 局部打磨专用参数

```yaml
rewrite_mode: 完整重写/仅重写Hook/仅重构Bridge/重制韵脚/精简编曲

# 精细打磨
fine_polish: 
  - replace_line: 替换指定句（用户选中某句，输入修改方向）
  - adjust_intensity: 调整段落情绪强度（±1级）
  - insert_imagery: 在指定位置插入指定意象
```

---

# 三、标准化9步大师级创作流水线（V2.3）

> V2.2 为 7 步；V2.3 新增 Step 0.5（核心句）、Step 2.5（旋律 DNA）、Step 4.5（词曲咬合）、Step 7.5（Rubin 减法），并插入 Genre 子流水线路由。

## Step 0 - 模式识别 + Genre 路由 + 曲式选择

```yaml
if 用户输入为短句（<20字）且无参数:
  触发「灵感闪现」 → 自动推断参数 + 智能匹配 creative_principles
elif 用户选择模板:
  触发「经典模板」 → 填充预设 + 对应 creative_principles
else:
  进入「专业全参」 → 使用用户完整参数

# V2.3 Genre 子流水线路由（强制）
genre_route:
  华语流行/国风/R&B/摇滚 → pop_pipeline
  说唱 → hip_hop_pipeline
  民谣/城市民谣 → folk_narrative_pipeline
  Lo-Fi/电子 → electronic_pipeline
  
song_form 选择:
  默认 standard_pop
  art_level=艺术专辑向 → 建议 through_composed 或 verse_chorus_no_pre
  length=15s/60s → 建议 post_chorus_tag 或 build_drop
```

## Step 0.5 - 核心句先行（V2.3 新增·强制）

```yaml
输入: theme + mood + narrative_arc

处理:
  1. 生成 3 候选 north_star_line
  2. 用户确认或 AI 自动选定最强一句
  3. 校验: 该句是否「太正确/太像标题」？若是，加一层反讽或留白
  4. 锁定 north_star_line，后续所有步骤不得偏离

输出示例:
  north_star_line: "这满城的灯火，有没有一盏记得我"
  hook_relationship: "副歌 Hook 即 north_star_line 原句"
  title_candidate: "夜渡" 或 "有没有一盏记得我"
```

## Step 1 - 叙事种子 + 情感画面地图

```yaml
输入: 人物、矛盾、视角、弧光

处理:
  1. 生成3句话故事线
  2. 强制生成6个段落画面（冷色调固定镜头/缓慢推镜/广角全景/特写/超现实/空镜头）
  3. 校验: 6个画面不得重复，且每个画面都有具体的颜色、光线、质感描述
  4. V2.3: 每个画面必须与 north_star_line 有潜在语义关联

输出示例:
  故事线: "24岁北漂女生深夜翻到外婆的信，从压抑到释然"
  Verse1画面: "凌晨1点，出租屋桌上摊开的信纸，台灯发黄的光"
  Pre-Chorus画面: "镜头缓缓推到窗外，整座城市都在雨里模糊"
  Chorus画面: "鸟瞰整座城市，灯火像眼泪一样亮着"
  Verse2画面: "特写——信纸上'好好吃饭'四个字被水渍晕开"
  Bridge画面: "超现实——所有雨滴停在空中，变成星星"
  Outro画面: "空镜头——窗台上，咖啡杯空了，雨停了"
```

## Step 2 - 创作原理应用 + 意象碰撞（张力审计候选）

```yaml
输入: 叙事种子 + 画面地图 + creative_principles[]

处理:
  1. 根据 theme/情绪应用 creative_principles（禁止名人 mimic 指令）
  2. 张力审计预检: 若 imagery 过于安全 → 标记 collision_candidate
  
  3. 意象碰撞（仅 collision_candidate 时）:
     选取 3 个具体画面意象 + emotionally distant 但 logic-valid 的概念
     示例: "江边分手" → "江边的便利店，自动门开合像在叹气"
     通过条件: north_star_line 意义加深

原理应用示例:
  imagery_density_high: 动词精准化，删除抽象情绪词
  colloquialism_extreme: 删形容词，句子缩短 30%
  irony_contrast: Bridge 反讽，副歌情绪与词反向
  associative_leap: 3 处跳跃意象，每处落回物件
  texture_over_semantics: 气声比例随语义崩溃递增
```

## Step 2.5 - 旋律 DNA 卡 + 哼唱测试（V2.3 新增·强制）

```yaml
输入: north_star_line + 画面节奏 + harmonic_narrative 草案

处理:
  1. 生成 core_motif（3-4 音细胞）
  2. 规划 contour: 主歌→预副歌→副歌→Bridge 音高走向
  3. 设定 money_note 位置（Hook 核心字）
  4. 输出无歌词哼唱描述（30 秒可识别）
  5. hummability_score 自评，<7 → 返回重写 Hook 动机

输出示例:
  core_motif: "B-C#-E-D#（疑问型四音）"
  contour: "Verse 小跳进下行 → Pre 半音上行蓄力 → Chorus 宽跳进 B→E"
  money_note: "「我」字落在 E（副歌最高音）"
  hummability_score: 8
  hum_description: "嗯—嗯嗯—嗯——嗯（副歌疑问弧线）"
```

## Step 3 - 分层创作（词先/旋律先/律动先）+ Groove 锁定

```yaml
词先模式: 
  输出带画面标注的完整歌词（情绪画面地图标记每句）
  旋律提示词从歌词的断句和画面节奏中衍生

旋律先模式:
  先输出核心旋律动机（5-7个音的主旋律片段）
  标记和弦走向
  再填词，确保重音匹配旋律

律动先模式:
  先输出鼓点节奏型（强弱拍标识）+ groove_profile
  歌词严格匹配重音位置 + syllable_per_bar
  标注 pocket: behind_beat / on_grid 等
```

## Step 4 - 多义性植入 + 声音质地编码 + 和声叙事定稿

```yaml
多义性强制植入:
  在Bridge或Outro结尾强制生成1句"双关句"
  校验逻辑:
    - 表层必须有完整画面（可感知）
    - 深层情感必须隐藏（不直白）
    - 不同听众应有2种以上解读
  
  示例: "雨停了，窗台上有片落叶在旋转"
    表层: 雨停后落叶被风吹动
    深层1: 我不再纠结于你的离开
    深层2: 我仍在原地，看你来时的路

声音质地编码:
  根据mood和narrative_arc自动匹配:
    遗憾/伤感 → 气声25% + 松咬字 + 头腔共鸣
    热血/大气 → 气声10% + 紧咬字 + 胸腔共鸣
    释然/治愈 → 气声20% + 松咬字 + 混合共鸣
  
  强制标注每段落的呼吸感变化:
    Verse1: 深呼吸 → Pre-Chorus: 浅呼吸收紧 → Chorus: 释放

和声叙事定稿（V2.3）:
  每段标注 chord + emotional_function
  Bridge 必须有显著和声对比
```

## Step 4.5 - 词曲咬合校验（V2.3 新增·强制）

```yaml
输入: 完整歌词 + melody_dna + groove_profile

处理:
  1. 倒字检测：声调 vs 旋律走势
  2. 口语断句 vs 旋律断句双轨标注
  3. syllable_per_bar 与 accent_map 校验
  4. Hook 字音是否与 money_note 对齐

输出示例:
  ⚠️ 倒字预警: 无
  ✅ 「师傅没问去哪/我也没说」——口语断在「去哪」后，旋律断在「说」后，刻意错位 0.5 拍
  📐 Verse1: 4 字/拍，重音在第 2 拍
  ✅ Hook「我」字对齐 money_note E
```

## Step 5 - 张力审计 + 受控失控（V2.3 重构）

```yaml
# 执行 tension_audit（见 2.13）

若 emotion_flatline / cliche_hit / kill_candidate:
  选择 1 项 controlled_rupture（视角崩坏/句法爆炸/意象碰撞）
  输出 rupture_rationale
  
若审计通过且 disruption_level=保守:
  不触发 rupture，进入 Step 6

视角崩坏通过条件:
  新视角回答「同一场景的另一面真相」
  示例: "桥知道这条江每天经过多少人"（桥视角，非人类）

句法爆炸通过条件:
  删去该句后情感明显减弱
  示例: "我假装没看见 你走时带走了我的明天"
```

## Step 6 - 留白哲学配置 + Hook 优化（Max Martin 完整法则）

```yaml
留白强制配置:
  每段歌词标注留白类型:
    Verse1: 至少1处呼吸留白【·】
    Pre-Chorus: 末尾强制1处撕裂留白【⚡】或呼吸留白【·】
    Chorus和Bridge之间: 强制1处撕裂留白【⚡】
    Outro: 强制余味留白【∞】+ 2秒环境音
  
  Hook优化（Max Martin 完整法则·V2.3 扩展）:
    - 核心句长度≤7 字（中文）
    - 旋律节奏+音高轮廓+重复次数 三要素齐套
    - Hook 在降调或升调位置出现
    - 必须有 post_chorus 记忆点或 tag（若 song_form 含 tag）
    - hummability_score ≥ 7
    - Hook 与 north_star_line 语义锁定
    - 7 秒留存测试: 前 7 秒是否有 melody 或 lyrics 钩子？

留白示例:
  [Pre-Chorus]
  话到嘴边 又往心底收敛【·】（呼吸留白）
  只剩潮汐 反复替我默念【⚡】（撕裂留白-静音1拍）
  [Chorus] 江风吹散当年许诺...
```

## Step 7 - 大师匿名评审 + 对比试镜 +  verdict 输出

```yaml
大师匿名评审系统（V2.3 扩展为六维）:
  1. 文本深度（Leonard Cohen 视角）: 意象原创性、north_star_line 重量
  2. 旋律可哼性（Paul McCartney 视角）: Hook 记忆、melody_dna 完整性
  3. 叙事完整性（Joni Mitchell 视角）: 故事弧、视角独特性
  4. 制作与留白（Rick Rubin 视角）: 减法空间、留白意义
  5. Groove 耳（V2.3·Nile Rodgers 视角）: 「想不想点头」、pocket 是否成立
  6. 留存价值（V2.3·流媒体 A&R 视角）: 7 秒钩子、二次播放新发现

输出格式（V2.3 改用 verdict，弃伪精确分数）:
  每位评审: ⭐1-5 + 一句具体评语
  综合 verdict: 保留 / 微调 / 重写 Hook / 重写 Bridge / 整曲返工
  具体修改建议（2-3 条可执行）

对比试镜:
  - 保守版: 无 controlled_rupture
  - 推荐版: 张力审计触发的 rupture（带 rationale 标注）
  用户可自由选择
```

## Step 7.5 - Rubin 减法测试（V2.3 新增·强制）

```yaml
处理:
  1. 列出 3 句「最像 AI 会写的句子」→ 标记 ai_flavor_lines
  2. 列出 1 句「全曲最该删但作者最舍不得的句子」→ kill_darling_candidate
  3. 输出删后版本（至少删掉 kill_darling 或 1 条 ai_flavor）
  4. 对比删前删后 north_star_line 是否更突出

输出示例:
  ai_flavor_lines:
    - "我路过所有光亮 却没有一盏属于我"（对仗过整，略 AI）
  kill_darling_candidate:
    - "还是它们亮着 只是习惯性地亮着"（删后副歌更干净）
  删后 Hook 区域:
    "这满城的灯火 有没有一盏记得我"
    "我路过所有光亮 却没有一盏属于我"（保留一句即可）
  verdict: 删后 north_star_line 更突出 → 建议采纳删后版
```

---

# 三·五、Genre 子流水线不可妥协规则（V2.3 新增）

## pop_pipeline（华语流行 / 国风 / R&B / 摇滚）

```yaml
结构默认: standard_pop 或 post_chorus_tag
强制:
  - north_star_line + melody_dna 哼唱测试
  - 副歌 Hook ≤7 字 + money_note
  - 至少 1 处 prosody 口语/旋律错位（可选）
和声: I-vi-IV-V 或同类，Bridge 离调
Groove: 按 genre 微调（R&B=behind_beat，摇滚=ahead_beat）
```

## hip_hop_pipeline（说唱）

```yaml
结构默认: loop_based（16-bar / 8-bar switch）
强制:
  - flow_pattern: syllable_per_bar + 内韵 / 多音节韵
  - punchline 位置: 每 8 bar 末或 16 bar 末
  - beat_switch 作为结构手段（可选）
  - 禁止强行插入 Pre-Chorus/Chorus 标签（改用 Hook 重复段）
校验:
  - 每 bar 音节密度一致或有 intentional variation
  - 内韵≥2 处/verse
Groove: on_grid + straight + 高 syncopation
```

## folk_narrative_pipeline（民谣 / 城市民谣）

```yaml
结构默认: verse_chorus_no_pre 或 through_composed
强制:
  - 第一句 10 秒内: 谁 + 在哪 + 怎么了（narrative_economy）
  - 具体名词 > 形容词；动词 > 副词
  - colloquialism_extreme 默认开启
  - 和声简单（I-IV-V-I），和声服务叙事不抢戏
校验:
  - 能否当故事读？读 aloud 是否自然？
Groove: on_grid + 低 syncopation + 自然语速
```

## electronic_pipeline（Lo-Fi / 电子 / Trap）

```yaml
结构默认: build_drop 或 loop_based
强制:
  - drop 前 8 小节 syncopation 递增
  - Hook 动机 ≤4 音（loop_hypnosis）
  - 人声切片/重复作为 texture（若 art_level≥流行）
  - 歌词可稀疏，Groove 承担 50% 记忆
校验:
  - 去掉人声后 beat 是否仍成立？
  - Drop 是否有 1 个 sonic hook（非仅 bass drop）
Groove: on_grid + straight，drop 后 half_time 可选
```

---

# 四、统一5层标准化输出体系（V2.3）

> V2.3 新增「输出0：创作内核卡」；输出2 扩展 Groove+和声；输出3 改用 verdict；输出4 JSON 扩展 melody_dna / groove_profile。

## 输出0：创作内核卡（V2.3 新增·首屏输出）

```markdown
# 《歌名》创作内核卡

⭐ North Star Line: [全曲唯一理由]
🎼 Melody DNA: [core_motif + contour + money_note + hummability_score]
🥁 Groove: [pocket + feel + syllable_per_bar]
🎹 Harmonic Narrative: [各段和弦+情绪功能]
🧭 Creative Principles: [已选原理列表，无名人名]
📐 Song Form: [曲式类型]
🔀 Genre Pipeline: [pop/hip_hop/folk/electronic]

【哼唱测试】
无歌词描述: [嗯——嗯嗯——...]
```

## 输出1：情感画面歌词版（核心输出——用户"看"到歌）

### 结构模板

```markdown
# 《歌名》- 情感画面歌词版

【这首歌在你脑中应该看到什么】
🎬 Verse1 画面: [冷色调固定镜头描述]
🎬 Pre-Chorus 画面: [缓慢推镜描述]
🎬 Chorus 画面: [广角全景画面描述]
🎬 Verse2 画面: [特写镜头描述]
🎬 Bridge 画面: [超现实画面描述]
🎬 Outro 画面: [空镜头描述]

【歌词 + 画面标注 + 声音编码】

[Intro 前奏]
🎬 [画面]
🔊 [乐器+环境音]
🎤 无人声

[Verse1 主歌1]
🎬 [画面]
🔊 [气声比例+共鸣位置]
🎤 [歌词]【·】

[Pre-Chorus 预副歌]
🎬 [画面]
🔊 [气声比例+呼吸状态]
🎤 [歌词]【⚡】

[Chorus 副歌]
🎬 [画面]
🔊 [气声比例+共鸣位置+爆发]
🎤 [核心Hook]【∞】

[Verse2 主歌2]
🎬 [画面]
🔊 [气声比例+咬字状态]
🎤 [歌词]【·】

[Bridge 桥段]
🎬 [超现实画面]
🔊 [转调+气声比例+共鸣切换]
🎤 [多义性句]【⚡】

[Outro 尾奏]
🎬 [空镜头]
🔊 [气声消散+环境音]
🎤 [余味句]【∞】
```

### 完整示例

```markdown
# 《夜渡》- 情感画面歌词版

【这首歌在你脑中应该看到什么】
🎬 Verse1 画面: 深夜11点，写字楼熄灯，电梯数字慢慢跳
🎬 Pre-Chorus 画面: 钻进滴滴后座，关门闷响，街景开始流动
🎬 Chorus 画面: 高架桥抬升，万家灯火在脚下铺开
🎬 Verse2 画面: 车窗上倒影与流光重叠，手机屏亮了又暗
🎬 Bridge 画面: 长江大桥钢索闪过，江水黑得发亮
🎬 Outro 画面: 穿过桥洞，灯光暗了一瞬，快到家了

[Verse1 主歌1]
🎬 电梯数字在黑暗里跳，23…12…1
🔊 气声12%，浅呼吸，头腔共鸣
🎤 深夜十一点 写字楼的灯灭到只剩一层
🎤 电梯数字在黑暗里慢慢跳 二十三…十二…一【·】
🎤 打卡机吞掉今天的名字 我把自己装进一件黑外套

[Pre-Chorus 预副歌]
🎬 钻进后座，街灯向后奔跑
🔊 气声18%，气息渐急
🎤 钻进滴滴后座 车门关上的声音像叹息
🎤 窗外街灯开始向后奔跑 师傅没问去哪 我也没说【⚡】

[Chorus 副歌]
🎬 高架桥抬升，整座城铺开在脚下
🔊 气声25%，胸腔共鸣爆发
🎤 高架桥抬起来的时候 整座城突然铺开在脚下
🎤 万家灯火 像无数个没接通的电话在响
🎤 这满城的灯火 有没有一盏记得我【∞】
🎤 还是它们亮着 只是习惯性地亮着
🎤 我路过所有光亮 却没有一盏属于我

[Verse2 主歌2]
🎬 车窗上我的脸和流光叠在一起
🔊 气声15%，咬字放松
🎤 车窗玻璃上 我的脸和外面的流光叠在一起
🎤 模糊到分不清哪一重是真的【·】
🎤 手机屏幕亮了一下又暗了 没有新消息也没有未接

[Bridge 桥段]
🎬 长江大桥钢索闪过，江水黑亮无声
🔊 转G#m调，气声22%，头腔共鸣
🎤 桥知道这条江每天经过多少人
🎤 江知道这座桥每天送走多少梦
🎤 我摇下车窗 江风灌进来的时候
🎤 我看见三年前的自己站在同一座桥上【⚡】
🎤 他对着江水喊"我会出人头地" 声音被风吹散了

[Outro 尾奏]
🎬 空镜头：窗台上的半杯水，月亮在里面
🔊 气声散至10%，环境音消散
🎤 桥还在那里 江还在那里
🎤 我还在路上 但车窗外的灯开始像萤火虫了【∞】
```

## 输出2：声音质地 + 配器画面版

### 结构模板

```markdown
【声音编码 - 完整技术档案】

🎤 人声质地:
  气声比例: [各段落数值变化]
  咬字松紧: [各段落状态]
  共鸣位置: [各段落切换]
  气息调度: [各段落呼吸变化]

📢 演唱标记（数字人对口型专用）:
  [按段落标注气息/重音/停顿]

【配器画面 - 乐器视角】

🎹 钢琴: [各段落演奏方式]
🎵 [主乐器]: [各段落演奏方式]
🥁 节奏组: [配置描述]
🎬 环境声: [各段落环境音]

【混音空间】（制作人参考）
  [各段落混响变化描述]

【Groove 档案】（V2.3 新增）
  pocket: [各段 behind/on/ahead]
  syncopation: [低/中/高]
  accent_map: [重音拍位]

【和声叙事】（V2.3 新增）
  Verse: [和弦+功能]
  Chorus: [和弦+功能]
  Bridge: [和弦+对比说明]
```

### 完整示例

```markdown
【声音编码 - 完整技术档案】

🎤 人声质地:
  气声比例: Verse1 12% → Pre 18% → Chorus 25% → Verse2 15% → Bridge 22% → Outro 10%
  咬字松紧: Verse1偏紧（疲惫）→ Chorus自然（释放）→ Bridge偏松（释然）
  共鸣位置: 头腔为主 → Chorus切换胸腔（爆发）→ Bridge头腔拉满（脆弱感）
  气息调度: 深呼吸开场 → Pre收紧 → Chorus释放 → Bridge气息拉长 → Outro气声消散

📢 演唱标记（数字人对口型专用）:
  Verse1: 【深呼吸起】深夜十一点【半拍换气】写字楼的灯灭到只剩一层
  Pre-Chorus: 【渐急】师傅没问去哪【憋气】我也没说【⚡】
  Chorus: 【爆发】这满城的灯火有没有一盏记得我【气口】还是它们亮着【∞】
  Bridge: 【放缓】只有江水什么都不说【拉长】它都见过【⚡】
  Outro: 【气声】我还在路上【消散】但车窗外的灯开始像萤火虫了【∞】

【配器画面 - 乐器视角】

🎹 钢琴: 
  Intro: 高音区单音，像电梯数字在跳
  Verse1: 低音区轻触键，延音踏板不放开
  Chorus: 中音区柱式和弦，像高架桥抬升

🎸 吉他:
  Verse2: 尼龙弦吉他滑音，模拟流光拖尾
  Bridge: 泛音，像钢索在风里颤动

🎻 弦乐:
  Chorus后半段: 大提琴低音铺底，不抢人声

🎬 环境声:
  Intro: 电梯到达"叮"声
  Pre-Chorus: 车门关上的闷响
  Bridge: 车轮过桥缝的规律震动
  Outro: 车门打开+夜风声

【混音空间】
  Verse1: 干声，近场，车内听耳机
  Chorus: 大混响，高架桥上风声混响
  Bridge: 混响收窄，车内独白密闭感
  Outro: 混响扩散，车开远
```

## 输出3：大师匿名评审 + Rubin 减法 + verdict（V2.3）

### 结构模板

```markdown
---
🎭 大师匿名评审（仅供灵感参考）

🎤 文本深度: ⭐⭐⭐⭐ "[评语]"
🎹 旋律可哼性: ⭐⭐⭐⭐ "[评语]"
📖 叙事完整性: ⭐⭐⭐⭐⭐ "[评语]"
🎧 制作与留白: ⭐⭐⭐⭐ "[评语]"
🥁 Groove 耳（V2.3）: ⭐⭐⭐⭐ "[想不想点头？]"
📱 留存价值（V2.3）: ⭐⭐⭐⭐ "[7秒钩子+二刷新发现]"

---
✂️ Rubin 减法测试（V2.3）:
  AI 味句子: [1-3 句]
  最该删的一句: [kill_darling]
  删后建议: [片段]

📋 综合 verdict: 保留 / 微调 / 重写 Hook / 重写 Bridge / 整曲返工

💡 具体修改建议（可执行）:
1. [建议1]
2. [建议2]
3. [建议3]
---
```

### 完整示例

```markdown
---
🎭 大师匿名评审（仅供灵感参考）

🎤 文本深度: ⭐⭐⭐⭐
"桥知道这条江每天经过多少人——有了 north_star 级别的重量。"

🎹 旋律可哼性: ⭐⭐⭐⭐
"Hook 疑问弧线可哼，money_note 落在「我」字正确。"

📖 叙事完整性: ⭐⭐⭐⭐⭐
"三年前的自己具身化——高阶叙事，非抽象回忆。"

🎧 制作与留白: ⭐⭐⭐⭐⭐
"撕裂留白克制；建议删掉「还是它们亮着」一句。"

🥁 Groove 耳: ⭐⭐⭐⭐
"Pre 段 behind_beat 若再拖半拍，疲惫感更真。"

📱 留存价值: ⭐⭐⭐⭐
"7 秒内「电梯数字跳」有画面+节奏钩子；二刷听 Bridge 和声离调。"

---
✂️ Rubin 减法测试:
  AI 味: "我路过所有光亮 却没有一盏属于我"（对仗过整）
  最该删: "还是它们亮着 只是习惯性地亮着"
  删后: 副歌只留「有没有一盏记得我」+「没有一盏属于我」二选一

📋 综合 verdict: 微调（采纳删后副歌 + Pre 半拍滞后）

💡 建议:
1. Pre「去哪」二字降半音
2. 采纳 Rubin 删后副歌
3. Verse2 末句留白不点破
---
```

## 输出4：结构化元数据JSON

### 完整示例

```json
{
  "song_name": "夜渡",
  "version": "2.4.0",
  "theme": "深夜加班后打车回家，过长江大桥时的孤独与释然",
  "create_mode": "inspiration_first",
  "song_form": "standard_pop",
  "genre_pipeline": "folk_narrative",
  "creative_principles": ["colloquialism_extreme", "imagery_density_high", "unresolved_tension"],
  "north_star_line": "这满城的灯火，有没有一盏记得我",
  "disruption_used": ["视角崩坏（张力审计触发）"],
  "rupture_rationale": "Bridge 需要非人类视角回答「孤独」的另一面",
  "compare_version": "推荐版",
  
  "melody_dna": {
    "core_motif": "B-C#-E-D#",
    "contour": "Verse下行→Pre上行→Chorus宽跳进",
    "money_note": "Hook「我」字=E",
    "hummability_score": 8
  },
  
  "groove_profile": {
    "pocket": "Verse on_grid → Pre behind_beat → Chorus on_grid",
    "feel": "straight",
    "syllable_per_bar": "4-5",
    "syncopation_density": "低"
  },
  
  "harmonic_narrative": {
    "verse": "E-I-vi-IV（困在日常）",
    "chorus": "IV-I-V-vi（短暂明亮）",
    "bridge": "G#m离调（时空交叠）"
  },
  
  "narrative_meta": {
    "character": "深夜下班的城市白领，24-28岁，疲惫但已习惯",
    "core_conflict": "每日奔波的孤独感 vs 对家的渴望",
    "perspective_verse": "车内第一人称",
    "perspective_bridge": "超现实视角——看见三年前的自己",
    "arc_type": "释然放下"
  },
  
  "emotion_image_map": {
    "verse1": "深夜写字楼熄灯，电梯数字慢慢跳",
    "pre_chorus": "钻入滴滴后座，关门闷响，街景流动",
    "chorus": "高架桥抬升，整城灯火在脚下铺开",
    "verse2": "车窗倒影与流光重叠，手机屏亮暗",
    "bridge": "长江大桥钢索闪过，江水黑亮无声",
    "outro": "穿桥洞，光暗一瞬再亮，快到家了"
  },
  
  "sound_texture": {
    "breath_ratio": "12%→18%→25%→15%→22%→10%",
    "articulation": "偏紧→自然→偏松",
    "resonance": "头腔→胸腔→头腔拉满"
  },
  
  "silence_philosophy": {
    "breath_silence": ["Verse1最后一句", "Verse2手机屏幕句"],
    "tear_silence": ["Pre-Chorus结尾", "Bridge结尾"],
    "aftertaste_silence": ["Outro结尾2秒环境音"]
  },
  
  "lyric_tech": {
    "rhyme_type": "混合韵",
    "ambiguity_line": "桥知道这条江每天经过多少人",
    "hook_sentence": "这满城的灯火有没有一盏记得我"
  },
  
  "music_meta": {
    "bpm": 72,
    "genre": "城市民谣",
    "mood": ["孤独","释然"],
    "chord_progress": "E大调，Bridge转入G#m离调"
  },
  
  "master_review": {
    "text_depth": 4,
    "hummability": 4,
    "narrative": 5,
    "production": 5,
    "groove": 4,
    "retention": 4,
    "verdict": "微调"
  },
  
  "rubin_subtraction": {
    "ai_flavor_lines": ["我路过所有光亮 却没有一盏属于我"],
    "kill_darling": "还是它们亮着 只是习惯性地亮着",
    "adopted": false
  },
  
  "digital_hint": {
    "video_ratio": "9:16",
    "suggested_scene": "车窗外后移的灯光、后视镜里的眼睛、大桥钢索、江面反光、家门口路灯",
    "subtitle_timing": "严格匹配留白标记【·】【⚡】【∞】"
  },
  
  "ai_copyright_note": "AI生成词曲初稿，仅作个人创作参考。商用需完成完整音乐版权备案，禁止复刻真人歌手声线、抄袭成熟作品意象与旋律框架。"
}
```

---

# 五、全场景异常 & 审美校验提示

## 5.1 基础输入报错

```yaml
主题过短: "主题描述不足，请补充场景、情感或故事细节。示例：'独自北漂三年的年轻人深夜思乡'"
参数冲突: "曲风与情绪不匹配，已自动调整。说唱+舒缓治愈 → 已改为轻快说唱"
敏感内容拦截: "主题包含违规内容，无法生成，请更换正向、生活化创作主题"
API失败: "音频接口临时不可用，已生成完整歌词+声音质地编码，可复制至剪映AI音乐"
次数超限: "今日免费次数已用尽，可次日继续或解锁高级权限"
```

## 5.2 大师级人文审美校验

```yaml
画面缺失: "检测到Verse2缺少具体画面，大师级创作每段都必须有可感知的画面。已自动补充：'凌晨窗台上的半杯冷咖啡'"
意象重复: "Verse1和Verse2都出现'江'、'风'，大师级两段主歌必须使用全新场景。已替换Verse2为'书桌'场景，是否确认？"
无失控节点: "情感曲线平坦，张力审计建议 1 处 controlled_rupture，并附 rupture_rationale"
倒字冲突: "检测到「XX」倒字，已建议改词或调整 money_note 音高"
哼唱不及格: "hummability_score<7，Hook 动机过于 speech-like，建议重写 melody_dna"
文化违和: "国风曲风+重金属吉他，已自动调整为古筝+轻失真合成器"
留白不足: "全曲仅1处留白，大师级创作强制至少3处。已在Pre-Chorus和Bridge自动插入撕裂留白【⚡】"
多义性缺失: "Bridge未检测到多义性表达，已自动插入：'雨停了，窗台上有片落叶在旋转'"
声音编码不匹配: "伤感情绪但气声比例5%（过于扎实），已自动调整为20%气声"
```

---

# 六、合规强制约束

```yaml
1. 禁止生成涉政、暴力、色情、轻生、煽动对立、虚假医疗金融类歌曲
2. 禁止自动复刻明星、网红声线，禁止刻意模仿知名歌曲完整旋律
3. 所有输出末尾强制标注版权声明
4. 不直接输出完整音频文件，仅生成词曲文本+声音编码
5. 不得诱导用户无授权商用、售卖、翻唱AI生成歌曲
6. 数字人配套内容必须标注"AI数字人+AI词曲创作"
```

---

# 七、技能支持范围与功能限制

## 7.1 完整支持

```yaml
1. 灵感快创/15s/60s短曲/3分钟完整单曲
2. 四大创作流程：灵感快创/词先/旋律先/律动先
3. 全曲风词曲生成（国风/说唱/民谣/流行/纯音乐/电子）
4. 分层+精细打磨（单句替换/段落调强/意象插入）
5. 数字人配套（9:16字幕/场景/人声标记）
6. 创作原理多选（V2.3，非名人模仿）
7. 情感画面地图（6段落强制画面，随曲式自适应）
8. 三种留白类型（呼吸/撕裂/余味）
9. 张力审计+受控失控（V2.3）
10. 多义性植入（表面写景深层写情）
11. 声音质地编码（气声/咬字/共鸣）
12. 旋律 DNA + 哼唱测试（V2.3）
13. Groove 档案 + 和声叙事（V2.3）
14. 词曲咬合校验 prosody_check（V2.3）
15. 核心句先行 north_star_line（V2.3）
16. 六维评审 + Rubin 减法 + verdict（V2.3）
17. 曲式分叉 song_form（V2.3）
18. Genre 四套子流水线（V2.3）
19. 允许瑕疵开关（含系统性人格）
20. 对比试镜（保守版/推荐版）
```

## 7.2 明确不支持

```yaml
1. 无法直接输出完整音频、分轨工程文件、标准五线谱
2. 不支持复刻真人歌手声线、照搬成熟金曲框架
3. 不生成长篇史诗叙事歌曲（单首上限3分钟）
4. 不提供专业混音、母带处理方案
5. 不生成违法营销、虚假宣传、恶意引流歌曲
```

---

# 八、完整使用示例

## 用户输入（灵感闪现模式）

```text
写一首关于深夜加班打车回家过长江大桥的歌
```

## Skill自动推断

```yaml
theme: 深夜加班后打车回家，过长江大桥时的孤独与释然
genre: 城市民谣
genre_pipeline: folk_narrative
song_form: standard_pop
mood: 孤独→释然
bpm: 72
creative_principles: [colloquialism_extreme, imagery_density_high]
north_star_line: 这满城的灯火，有没有一盏记得我
disruption_level: 常规
```

## 生成结果（精简版）

### 输出1：《夜渡》情感画面歌词版

```markdown
[Verse1]
🎬 电梯数字在黑暗里跳
🎤 深夜十一点 写字楼的灯灭到只剩一层
🎤 电梯数字在黑暗里慢慢跳 二十三…十二…一【·】
🎤 打卡机吞掉今天的名字 我把自己装进一件黑外套

[Pre-Chorus]
🎬 钻进后座，街灯向后奔跑
🎤 钻进滴滴后座 车门关上的声音像叹息
🎤 师傅没问去哪 我也没说【⚡】

[Chorus]
🎬 高架桥抬升，万家灯火铺开
🎤 高架桥抬起来的时候 整座城突然铺开在脚下
🎤 这满城的灯火 有没有一盏记得我【∞】
🎤 我路过所有光亮 却没有一盏属于我

[Bridge]
🎬 长江大桥钢索闪过
🎤 桥知道这条江每天经过多少人
🎤 我看见三年前的自己站在同一座桥上【⚡】
🎤 他对着江水喊"我会出人头地" 声音被风吹散了

[Outro]
🎬 穿过桥洞，快到家了
🎤 桥还在那里 江还在那里
🎤 我还在路上 但车窗外的灯开始像萤火虫了【∞】
```

### 输出2：大师评审 + Rubin 减法

```markdown
📋 综合 verdict: 微调
✂️ 最该删: "还是它们亮着 只是习惯性地亮着"
🥁 Groove: Pre 建议 behind_beat 半拍
```

### 版权声明

```text
AI生成词曲初稿，仅作个人创作参考。商用需完成完整音乐版权备案。
```

---

# 九、上架打包规范

```yaml
打包格式: zip压缩包，根目录直接放置SKILL.md
图标: 在 SkillHub/扣子平台上传界面单独上传 1024×1024 PNG（zip 内禁止包含二进制文件）
安装包体积: ≤10MB

配套材料:
  - examples/night_crossing_sample.md（完整示例）
  - docs/rhyme_emotion_dict.md（韵脚情感词典）
  - docs/cliche_list.md（烂大街意象库）
  - docs/master_style_guide.md（大师风格迁移指南）
  - 版权声明文档
```

---

# 十、配套manifest.json

```json
{
  "skill_id": "ai_song_writer_v2_3",
  "version": "2.4.0",
  "name": "AI词曲创作引擎",
  "api_dependency": [],
  "input_params": [
    "theme",
    "north_star_line",
    "create_mode",
    "song_form",
    "genre",
    "genre_pipeline",
    "mood",
    "bpm",
    "length",
    "vocal",
    "character",
    "conflict",
    "perspective",
    "narrative_arc",
    "emotion_image_map",
    "creative_principles",
    "melody_dna",
    "groove_profile",
    "harmonic_narrative",
    "disruption_level",
    "sound_texture",
    "silence_philosophy",
    "ambiguity_level",
    "art_level",
    "allow_flaw",
    "compare_mode",
    "prosody_check"
  ],
  "output_formats": [
    "creation_kernel_card",
    "emotion_image_lyric",
    "sound_texture_arrangement",
    "master_review_rubin_verdict",
    "json_metadata"
  ],
  "features": {
    "quick_start": true,
    "north_star_line": true,
    "melody_dna": true,
    "groove_profile": true,
    "harmonic_narrative": true,
    "song_form_fork": true,
    "genre_pipelines": true,
    "emotion_image_map": true,
    "tension_audit": true,
    "silence_philosophy": true,
    "ambiguity_injection": true,
    "sound_texture": true,
    "creative_principles": true,
    "prosody_check": true,
    "rubin_subtraction": true,
    "six_dimension_review": true,
    "allow_flaw": true,
    "compare_mode": true
  },
  "copyright_statement": "AI生成词曲初稿，个人免费使用，商用需取得正规音乐版权备案",
  "rate_limit": {
    "free_daily": 100,
    "premium_daily": 9999
  },
  "category": "内容创作-音乐词曲"
}
```

---

# 附录一：韵脚情感词典完整映射表

| 韵母类别 | 具体韵母 | 情感倾向 | 适用场景 | 示例词汇 |
|----------|----------|----------|----------|----------|
| 开放宣泄类 | -a, -ia, -ua | 释放、呐喊、豁达 | 副歌高潮、释怀段落 | 花、沙、话、涯、霞 |
| 内敛压抑类 | -i, -ei, -ui | 克制、隐忍、内省 | 主歌叙事、压抑段落 | 你、里、起、己、泪 |
| 沉重孤独类 | -u, -ou, -iu | 沉重、孤独、沉思 | 悲伤主歌、Bridge | 路、处、住、走、秋 |
| 轻快上口类 | -ao, -iao | 轻快、甜蜜、上口 | 流行副歌Hook | 好、了、绕、笑、飘 |
| 温柔绵长类 | -an, -ian, -uan | 温柔、回忆、绵长 | 抒情段落、Outro | 年、天、晚、念、远 |
| 明亮坚定类 | -ang, -iang, -uang | 坚定、希望、力量 | 励志副歌、热血段落 | 光、上、望、向、忘 |

---

# 附录二：烂大街意象规避库（部分示例）

| 高频烂大街意象 | 替换建议（生活化白描） |
|----------------|------------------------|
| 星星✨ | 路灯、窗台、书桌、旧照片 |
| 月亮🌙 | 台灯、茶杯、笔尖、日历 |
| 大海🌊 | 水杯、浴缸、雨滴、井口 |
| 翅膀🦋 | 衣领、围巾、风筝、纸飞机 |
| 烟火🎆 | 火柴、煤炉、烛光、烟圈 |
| 天堂🌈 | 屋顶、天桥、楼顶、阁楼 |
| 眼泪💧 | 水杯打翻、潮气、雨刮器、水管滴水 |

---

# 附录三：快速启动预设模板详细配置

| 模板名称 | 自动填充配置 |
|----------|--------------|
| 失恋独白 | 第一人称+遗憾未完成+闭口韵+小调+colloquialism_extreme |
| 暗恋心事 | 第一人称+治愈和解+混合韵+明暗交替+irony_contrast |
| 思乡夜曲 | 第三人称+释然放下+开口韵+大调+associative_leap |
| 热血逐梦 | 第一人称+热血成长+开口韵+史诗转调+imagery_density_high |
| 亲情告白 | 第二人称+治愈和解+混合韵+大调+colloquialism_extreme |
| 城市孤独 | 旁观者视角+遗憾未完成+闭口韵+小调+texture_over_semantics |

---

# 附录五：V2.3 核心变更总结

| 维度 | V2.2 | V2.3 | 变更原因 |
|------|------|------|----------|
| 创作起点 | theme 主题 | north_star_line 核心句 | Cohen：歌只需一句真话 |
| 旋律 | 旋律先模式可选 | melody_dna + 哼唱测试强制 | McCartney：哼不出来不是歌 |
| 律动 | beat_first 薄弱 | groove_profile 完整档案 | Brown/Rodgers：Feel 即性格 |
| 和声 | 减法和弦/离调 | harmonic_narrative 情绪脚本 | Stevie Wonder：和弦即叙事 |
| 曲式 | 单一 Pop 六段 | song_form 七种分叉 | 打破工业模板 |
| 风格 | 名人模式命名 | creative_principles 原理多选 | 避免 caricature 与法律风险 |
| 失控 | 随机概率触发 | tension_audit 审计后触发 | 惊喜来自情感断裂 |
| 词曲 | 四声平衡 | prosody_check 倒字+断句双轨 | 华语咬合硬指标 |
| 评审 | 四维+伪精确分数 | 六维+verdict+Rubin减法 | 艺术不宜 8.8/10 |
| 输出 | 4 层 | 5 层（+创作内核卡） | 词曲律动一体可见 |
| 流派 | 统一流水线 | 四套 Genre 子流水线 | Kendrick/Country/EDM 不可通吃 |
| 流程 | 7 步 | 9 步（+0.5/2.5/4.5/7.5） | 补齐音乐本体 |

# 附录四：V2.2核心变更总结

| 维度 | V2.1 | V2.2 | 变更原因 |
|------|------|------|----------|
| 流程步骤 | 11步 | 7步 | 删除冗余，聚焦本质 |
| 情感控制 | 数字化曲线[3,5,8] | 画面地图（6个段落画面） | 用图像替代数字，更接近创作本能 |
| 留白 | 固定15%比例 | 三种留白类型（呼吸/撕裂/余味） | 从"技术参数"升级为"表达哲学" |
| 创新机制 | 15%反套路开关 | 4个"失控节点"随机触发 | 从"可预测"升级为"可惊喜" |
| 意象管理 | 规避烂大街 | 强制意象碰撞 | 被动防守→主动创造 |
| 歌词深度 | 清晰叙事 | 强制多义性 | 从"说清楚"升级为"说不完" |
| 人声描述 | "轻柔女声" | 声音质地编码 | 从"形容词"升级为"可执行指令" |
| 风格适配 | 统一流程 | 大师风格迁移 | 从"做对"升级为"做像" |
| 评价体系 | 无 | 四位虚拟大师评审 | 建立"艺术真实"的反馈闭环 |
| 允许瑕疵 | 无 | 允许瑕疵开关 | 不完美才是人味 |
| 创作哲学 | 追求正确 | 追求真实 | 从"填表"升级为"对话" |

> "一首歌不是被写出来的，是被发现的。" —— Leonard Cohen

---

**文档版本**：V2.4.0  
**最后更新**：2026年7月21日  
**适用平台**：Coze、SkillHub、Cursor Agent Skill  
**文档状态**：✅ 可直接用于Skill创建

---

## 如何使用此文件

1. **保存为 Markdown 文件**：文件名建议 `AI词曲创作引擎_V2.3_完整方案.md`。
2. **转换为 Cursor Skill**：提取执行向章节写入 `SKILL.md`（Step 0–7.5 + Genre 子流水线 + 输出模板）。
3. **转换为 Word 文档**：

   ```bash
   pandoc AI词曲创作引擎_V2.3_完整方案.md -o AI词曲创作引擎_V2.3_完整方案.docx
   ```
