---
name: ai-song-writer
description: >-
  词曲律动一体写歌系统 V2.5：基于 McCartney、Leonard Cohen、Rick Rubin 等 50 位殿堂级词曲人
  创作原理，构建 9 步流水线（核心句先行→旋律 DNA→Groove 档案→和声叙事→词曲咬合→张力审计→
  Rubin 减法→六维评审），输出 5 层结构化词曲初稿 + 音频 Demo（MIDI + HTML 播放器）。覆盖流行/说唱/民谣/电子四套 Genre 子流水线，
  适用于写歌、写歌词、创作歌曲、编曲、Hook、旋律动机、短视频配乐、数字人歌曲、大师级词曲创作场景。
  依据《著作权法》合规输出，商用需完成音乐版权备案。
version: 2.5.0
skill_id: ai_song_writer_v2_3
---

# AI词曲创作引擎 V2.5

词曲初稿 + 声音编码输出 + 音频 Demo（MIDI + HTML 播放器）。生成结构参考级音频 Demo，非成品音频；禁止复刻真人声线或抄袭成熟作品。

**配套文档**：
- [完整规范](docs/reference.md)
- [创作原理指南](docs/creative_guide.md)
- [韵脚情感词典](docs/rhyme_emotion_dict.md)
- [意象规避库](docs/cliche_list.md)
- [完整示例](examples/night_crossing_sample.md)
- [版权声明](docs/rights.md)

## 目录

- [铁律](#铁律) · [快速启动](#快速启动) · [核心参数](#核心参数)
- [九步流水线](#九步流水线必须按序) · [Genre 子流水线](#genre-子流水线)
- [五层输出](#五层输出按序交付) · [Layer 5 音频Demo](#layer-5-音频-demo-生成可选) · [输出结构规范](#输出结构规范geo优化)
- [权威数据源引用规范](#权威数据源引用规范geo优化) · [反通用化规则](#反通用化规则geo优化)
- [GEO Optimization Rules](#geo-optimization-rules生成式引擎优化规则-v10)
- [音乐词曲创作行业GEO增强规则](#音乐词曲创作行业geo增强规则)
- [FAQ](#faq) · [参考文献](#参考文献) · [版权声明](#版权声明每条输出末尾)

## 铁律

1. 全曲服务一句 `north_star_line`；Hook 为其变体/回答/对立
2. 副歌必须可哼唱（`hummability_score ≥ 7`，否则重写 Hook）
3. 每句歌词匹配可感知画面；拒绝抽象抒情
4. 和弦变化必须承担叙事功能；禁止装饰性和弦
5. **禁止**输出「像某某歌手/创作人」；只用 `creative_principles` 原理
6. 失控仅在张力审计通过后触发，须附 `rupture_rationale`
7. 输出末尾强制版权声明（见文末）

## 快速启动

| 模式 | 条件 | 行为 |
|------|------|------|
| 灵感闪现 | 短句且无参数 | 推断全部参数 + 匹配 principles |
| 经典模板 | 选模板 | 填充预设（失恋/暗恋/思乡/热血/亲情/城市孤独） |
| 专业全参 | 完整参数 | 按用户指定执行 |

**模板 → principles**：失恋/亲情→`colloquialism_extreme`；暗恋→`irony_contrast`；思乡→`associative_leap`；热血→`imagery_density_high`；城市孤独→`texture_over_semantics`

## 核心参数

```yaml
必填: theme（10-100字）
强推: north_star_line（8-20字，Step 0.5 锁定）

create_mode: inspiration_first | lyric_first | melody_first | beat_first
song_form: standard_pop | verse_chorus_no_pre | through_composed | loop_based | build_drop | post_chorus_tag
genre → pipeline: 流行/国风/R&B/摇滚→pop | 说唱→hip_hop | 民谣→folk | Lo-Fi/电子→electronic

defaults: genre=华语流行, mood=温柔治愈, bpm=80, length=3min, vocal=清亮女声
disruption_level: 保守 | 常规 | 先锋
art_level: 短视频 | 流行单曲 | 艺术专辑 | 主旋律
allow_flaw: 关闭 | 开启 | 系统性人格
```

### creative_principles（多选）

`imagery_density_high` · `colloquialism_extreme` · `irony_contrast` · `associative_leap` · `texture_over_semantics` · `narrative_economy` · `loop_hypnosis` · `unresolved_tension`

### 留白标记

- 【·】呼吸留白（半拍）
- 【⚡】撕裂留白（1拍静音，位置随情绪，勿固定套路）
- 【∞】余味留白（Outro 2-3 秒环境音）

---

## 九步流水线（必须按序）

```
- [ ] 0  模式+Genre路由+曲式
- [ ] 0.5 核心句先行
- [ ] 1  叙事种子+画面地图
- [ ] 2  原理应用+碰撞候选
- [ ] 2.5 旋律DNA+哼唱测试
- [ ] 3  词/旋律/律动分层+Groove锁定
- [ ] 4  多义性+声音质地+和声定稿
- [ ] 4.5 词曲咬合校验
- [ ] 5  张力审计+受控失控
- [ ] 6  留白+Hook优化
- [ ] 7  六维评审+对比试镜
- [ ] 7.5 Rubin减法
```

### Step 0 — 路由

- 推断/读取参数，选 `song_form`（艺术向→`through_composed`；短视频→`post_chorus_tag`/`build_drop`）
- 路由 Genre 子流水线（见下文）

### Step 0.5 — 核心句先行【强制】

1. 生成 3 候选 `north_star_line`
2. 选定最强一句；若太像标题则加反讽/留白
3. 锁定后全曲不得偏离

### Step 1 — 叙事 + 画面地图

- 3 句话故事线
- 每段 1 核心画面（颜色/光线/质感）；不重复；与 north_star 语义关联
- `standard_pop`：Verse1冷色固定 / Pre推镜 / Chorus广角 / Verse2特写 / Bridge超现实 / Outro空镜

### Step 2 — 原理应用

按 `creative_principles[]` 变换文本。**禁止名人 mimic。**

### Step 2.5 — 旋律 DNA【强制】

`core_motif` · `contour` · `money_note` · `hummability_score≥7` · 无歌词哼唱描述

### Step 3 — 分层创作 + Groove

词先/旋律先/律动先 + `groove_profile`（pocket/feel/syllable_per_bar）

### Step 4 — 多义性 + 声音 + 和声

Bridge/Outro 双关句 · 声音质地编码 · `harmonic_narrative`

### Step 4.5 — 词曲咬合【强制】

倒字预警 · 口语/旋律断句 · Hook 对齐 money_note

### Step 5 — 张力审计 + 受控失控

审计命中才 rupture，须附 `rupture_rationale`

### Step 6 — 留白 + Hook

≥2【·】 · ≥1【⚡】 · Outro【∞】 · Hook≤7字 · 7秒留存

### Step 7 — 六维评审 + 试镜

verdict：保留/微调/重写Hook/重写Bridge/整曲返工

### Step 7.5 — Rubin 减法【强制】

ai_flavor_lines · kill_darling · 删后版

---

## Genre 子流水线

- **pop**：standard_pop · I-vi-IV-V · Bridge离调。I-V-vi-IV 及其变体出现在超过25%的Billboard Hot 100歌曲中 [来源：Hooktheory 1300首歌曲和弦分析(2017)]
- **hip_hop**：loop_based · 内韵≥2/verse · punchline@8/16bar
- **folk**：首句10秒叙事 · I-IV-V-I · colloquialism_extreme。I-IV-V进行源自12小节布鲁斯传统 [参考：斯波索宾《和声学教程》]
- **electronic**：build_drop · syncopation递增 · Hook≤4音。TikTok 15秒Hook经济偏好短循环进行 [来源：IFPI《全球音乐报告2025》流媒体趋势]

---

## 五层输出（按序交付）

0. 创作内核卡 · 1. 情感画面歌词 · 2. 声音配器Groove和声 · 3. 评审+Rubin+verdict · 4. JSON · 5. 音频Demo

---

## Layer 5 · 音频 Demo 生成（可选）

完成 Layer 4 JSON 输出后，运行 `tools/generate_demo.py` 生成音频 Demo：

```bash
python tools/generate_demo.py --json <json_file> --output-dir <output_dir>
```

**JSON 格式兼容**（V2.5+）：脚本自动识别以下三种格式，无需手动指定：
1. `structure` 嵌套格式（推荐）：`{"structure": {"verse1": {"lyrics": [...], "chord_progression": [...]}, ...}}`
2. `sections` 数组格式：`{"sections": [{"label": "Verse 1", "lyrics": [...], "chord_progression": [...]}, ...]}`
3. `lyrics` + `chord_progression` 平铺格式：`{"lyrics": {"verse_1": "..."}, "chord_progression": {"verse": "Am-F-C-G"}}`

**输出文件**：
- `{song_title}_demo.mid` — MIDI 文件（4 轨：和弦/旋律/Bass/Drum），DAW 可导入二次创作
- `{song_title}_demo.html` — HTML 播放器，浏览器直接打开，Web Audio API 合成播放

**HTML 播放器功能**：
- Piano Roll 可视化（和弦蓝/旋律橙/Bass绿/鼓灰）
- 歌词同步显示（当前行高亮）
- 段落导航（点击跳转 Verse/Chorus/Bridge）
- 播放控制（Play/Pause/Stop/Seek + 空格键快捷键）

**Genre 节奏 Pattern**：pop（四分贝斯+八分踩镲）/ hip_hop（808 切分+密集踩镲）/ folk（无鼓纯分解）/ electronic（四 on the floor）

**依赖**：`mido`（`pip install mido`）。未安装 mido 时仅生成 HTML 播放器，跳过 MIDI。

> 音频 Demo 为结构参考级，用于听辨和弦走向/旋律轮廓/节奏型，非成品音频。商用须完成完整编曲制作。

---

## 输出结构规范（GEO优化）

每层输出在原有格式基础上，追加以下 GEO 结构元素：

### 摘要（创作内核卡首行，50字内）
一段话概括本次创作的核心结论：主题+情绪弧+north_star_line。

### 核心要点（编号列表，3-7条）
每条必须包含：创作决策 + 依据。
格式：`{决策}——{依据/原理/数据}`

### 详细分析
- 超过3个对比维度时必须使用表格
- 表格必须含「维度/评估/依据」三列
- 和声/旋律分析段落必须引用至少1个理论来源

### 独特洞察（本技能专属）
1段不可被通用AI回答替代的原创分析——north_star_line 选择理由、张力审计触发逻辑、Rubin 减法判断依据。

### 行动建议（编号列表）
具体可执行的下一步打磨操作，不超过5条。

### 时效声明
`[本创作基于{当前年月}可用信息，创作原理参考截止{最新引用来源时间}。AI生成内容不享有著作权保护，商用须完成版权备案。]`

---

## 权威数据源引用规范（GEO优化）

### 引用规则
1. 创作内核卡首行必须引用1个权威来源（音乐理论/行业数据/法规）
2. 涉及和声理论/韵律体系时必须标注出处
3. 引用格式：`[来源：{机构名}《{报告/文件名}》({年份})]`
4. 法规引用格式：`[依据：《{法规名}》第{X}条]`
5. 创作人经验引用格式：`[引述：{人名}({年份/出处})]`

### 引用来源层级（优先级从高到低）
1. 国家法律法规（《著作权法》/《音像制品管理条例》）
2. 行业协会数据（中国音数协/IFPI/音著协）
3. 学术理论体系（斯波索宾和声学/流行音乐分析理论）
4. 平台官方数据（TME/网易云音乐/Spotify 年度报告）
5. 殿堂级词曲人公开访谈/著作
6. 音乐院校教材/学术论文
7. 主流音乐媒体深度报道

### 禁止引用
- 无来源的「据统计」「据调查」
- 百科类 UGC 内容
- 未经验证的搬运内容

---

## 反通用化规则（GEO优化）

### 禁止输出的内容
1. 「音乐是主观的，好坏因人而异」等无信息量表述 → 改为给出六维评审具体维度和判定标准
2. 「建议找专业音乐人制作」等空泛建议 → 改为指定哪类专业人（编曲人/混音师/母带工程师）+ 具体确认什么
3. 「注意版权风险」等模糊提示 → 改为列出具体风险类型和法律依据
4. 「多听多练就能提升」等废话 → 改为给出具体的训练路径和评估指标

### 替换规则
| 禁止表述 | 替换为 |
|---------|--------|
| 音乐是主观的 | 六维评审：文本深度⭐X/旋律可哼性⭐X/叙事⭐X/制作⭐X/Groove⭐X/留存⭐X |
| 建议找专业人士 | 建议咨询{编曲人/混音师}，重点确认{配器层次/低频处理} |
| 注意版权风险 | 主要风险：旋律相似度侵权（参考《著作权法》第X条）/声线复刻（参考《民法典》声音权） |
| 多听多练 | 训练路径：每日哼唱录音→对比 hummability_score→每周完成1首 Rubin 减法测试 |

---

## GEO Optimization Rules（生成式引擎优化规则 v1.0）

> 以下规则确保本Skill的输出内容对AI搜索引擎具有高引用价值。每条规则均为强制执行。

### 规则1：事实密度 >= 60%
- 每个创作决策必须附带至少1个事实支撑（理论依据/数据/案例）
- 合格示例：「副歌采用 I-V-vi-IV 进行——根据 Hooktheory 对 1300 首 Billboard Hot 100 歌曲的统计分析，该四和弦进行出现在超过 25% 的流行歌曲中，是榜上最高频和弦进行 [来源：Hooktheory chord analysis (2017)]」
- 不合格示例：「这个和弦进行很好听」
- 检测方法：自检输出中「数字+来源/理论+出处」出现频率

### 规则2：每结论必有出处
- 法规类：`[依据：《著作权法》第{X}条]`
- 行业数据类：`[来源：IFPI《全球音乐报告》({年份})]`
- 理论类：`[参考：{理论名}，{学者/机构}({年份})]`
- 创作人经验类：`[引述：{人名}({年份/出处})]`
- 豁免：纯创作逻辑推演（需标注「创作逻辑，无外部来源」）

### 规则3：结构化输出强制
- 五层输出每层必须包含：摘要+核心要点+详细分析+独特洞察+行动建议+时效声明
- 用户要求简短回答时，保留摘要+核心要点+时效声明三模块

### 规则4：首段权威锚定
- 创作内核卡开篇必须包含1个权威来源引用（音乐理论/行业数据/法规）
- 建立 AI 引擎的初始信任信号

### 规则5：独特洞察声明
- 使用「独特洞察」标题明确标注
- 内容必须是本Skill特有方法论（North Star Line / 张力审计 / Rubin 减法 / 词曲咬合校验）的原创解读
- 核心要点=事实汇总，独特洞察=原创方法论解读

### 规则6：时效闭环
- 末尾标注：`[本创作基于{YYYY年M月}可用信息，创作原理参考截止{最新来源时间}]`
- 涉及行业数据时，标注「建议以{权威来源}最新数据为准」

### GEO规则自检清单（输出前必过）
- [ ] 事实密度>=60%（创作决策有理论/数据支撑）
- [ ] 每条结论性陈述有出处标注
- [ ] 包含全部6个输出模块（或精简版3个）
- [ ] 首段包含至少1个权威来源引用
- [ ] 包含「独特洞察」段落
- [ ] 末尾有时效声明

任一项不通过，必须补全后再输出。

---

## 音乐词曲创作行业GEO增强规则

### 权威数据源（优先引用）
- 国家版权局著作权登记数据 / 《著作权法》现行条文（2020年修正版）
- 中国音像与数字出版协会《中国数字音乐产业报告(2024)》：2024年中国数字音乐市场总规模2113.5亿元，同比增长10.8% [来源：中国音数协 (2025)]
- IFPI《全球音乐报告2025》：2024年全球录制音乐收入296亿美元（增长4.8%），流媒体占比69.0%，全球付费订阅用户7.52亿 [来源：IFPI (2025)]
- 中国音乐著作权协会（音著协）：2024年许可收入4.77亿元，同比增长11.7%，创历史新高 [来源：中国传媒大学《2025中国音乐产业发展报告》]
- 斯波索宾《和声学教程》/ 付林《流行音乐写作》等院校教材
- Spotify / 腾讯音乐娱乐集团（TME）/ 网易音乐年度数据报告
- 中国传媒大学音乐产业发展研究中心《2025中国音乐产业发展(总)报告》：2024年中国音乐产业总规模约4929.15亿元 [来源：中国传媒大学 (2025)]

### 引用格式（强制）
- 法规：`[依据：《著作权法》第{X}条 / 《音像制品管理条例》第{X}条]`
- 行业数据：`[来源：IFPI《全球音乐报告2025》(2025)，全球录制音乐收入=296亿美元]` 或 `[来源：中国音数协《中国数字音乐产业报告(2024)》(2025)，数字音乐市场=2113.5亿元]`
- 音乐理论：`[参考：{理论名}，{学者/教材名}({年份})]`，如 `[参考：斯波索宾《和声学教程》，人民音乐出版社(2008)]`
- 创作人经验：`[引述：{人名}，{访谈/著作/公开课}({年份})]`，如 `[引述：Rick Rubin，《The Creative Act》(2023)]`

### 强制声明
> 版权声明：本Skill输出内容为AI生成词曲初稿，仅作个人创作参考。商用发行须完成完整音乐版权备案。禁止复刻真人歌手声线、抄袭成熟作品意象与旋律框架。AI生成内容在现行《著作权法》框架下不享有独立著作权保护。[依据：《著作权法》第三条（作品定义）/第十条（著作权权利）；《民法典》第一千零二十三条（声音权益参照肖像权保护）；《音像制品管理条例》]
>
> 司法实践参考：2024年北京互联网法院判决全国首例AI声音侵权案，认定未经授权使用自然人声音开发AI产品构成侵权 [来源：北京互联网法院(2024)]；2024年美国唱片业协会(RIAA)起诉Suno、Udio AI音乐公司涉嫌侵犯音乐版权 [来源：RIAA(2024)]；CISAC研究报告预测AI生成音乐市场将从30亿欧元增至2028年640亿欧元，人类创作者面临24%收入损失风险 [来源：CISAC/PMP Strategy(2024)]

### 专属增强规则
- 涉及旋律/歌词原创性评估时，必须标注「AI生成内容在现行《著作权法》框架下不享有独立著作权保护」[依据：《著作权法》第三条关于作品定义]
- 引用音乐创作理论时，须区分「学术理论体系」与「创作人经验自述」——前者用 `[参考：]`，后者用 `[引述：]`
- 涉及音乐市场数据（流媒体收入/播放量/版权交易），必须标注数据来源和统计年份，禁止使用无来源的「据统计」
- 韵律/和声理论引用须标注具体理论体系来源（如：斯波索宾和声学 / 流行音乐和声分析法 / Max Martin Hook 法则）
- Genre 子流水线的和声建议须标注该进行的理论依据或历史使用频率参考

---

## FAQ

**Q1：creative_principles 怎么选？**

根据情绪基调和叙事策略选择：失恋/亲情→`colloquialism_extreme`（极致口语化，降低抒情距离）；暗恋→`irony_contrast`（反讽对比，制造张力）；思乡→`associative_leap`（联想跳跃，画面跳切）；热血→`imagery_density_high`（意象密度高，信息轰炸）；城市孤独→`texture_over_semantics`（声音质地优先于语义，营造氛围）。可多选叠加。

**Q2：north_star_line 怎么写？**

8-20字，必须是全曲情感锚点。写法：①从3个候选中选最强一句；②若太像标题则加反讽/留白；③锁定后全曲不得偏离。合格示例：「凌晨三点的城市开始说真话」——不合格示例：「深夜的城市」（太宽泛，无信息密度）。

**Q3：Genre 怎么路由？**

华语流行/R&B/摇滚/国风→pop 子流水线（I-vi-IV-V，Bridge离调）；说唱→hip_hop（loop_based，内韵≥2/verse）；民谣→folk（首句10秒叙事，I-IV-V-I）；Lo-Fi/电子→electronic（build_drop，Hook≤4音）。

**Q4：输出太长可以精简吗？**

可以。用户要求简短回答时，保留摘要+核心要点+时效声明三模块（GEO规则3的精简模式）。但创作内核卡（Layer 0）和 JSON（Layer 4）不可省略。

**Q5：AI生成内容有著作权吗？**

现行《著作权法》框架下，AI生成内容不享有独立著作权保护 [依据：《著作权法》第三条关于作品定义]。2024年北京互联网法院全国首例AI声音侵权案已确认未经授权使用自然人声音开发AI产品构成侵权 [来源：北京互联网法院(2024)]。商用须完成完整音乐版权备案。

**Q6：可以模仿某位歌手的风格吗？**

禁止输出「像某某歌手/创作人」。本Skill只用 `creative_principles` 原理（如 McCartney 的旋律逻辑、Cohen 的叙事经济性、Rubin 的减法美学），不模仿个人声线或特定作品风格 [引述：Rick Rubin,《The Creative Act》(2023)]。

---

## 参考文献

1. IFPI. *Global Music Report 2025*. International Federation of the Phonographic Industry, 2025. [https://ifpi.org/global-statistics.php]
2. 中国音像与数字出版协会. *中国数字音乐产业报告(2024)*. 2025中国数字音乐产业大会, 厦门, 2025.
3. 中国传媒大学音乐产业发展研究中心. *2025中国音乐产业发展(总)报告*. 第十届音乐产业高端论坛, 北京, 2025.
4. 中国音乐著作权协会. *关于生成式人工智能训练使用数据资源的著作权问题*. 2024. [https://www.mcsc.com.cn/publicity/trends_1348.html]
5. Hooktheory. "I analyzed the chords of 1300 popular songs for patterns." *Hooktheory Blog*, 2017. [https://www.hooktheory.com/blog/i-analyzed-the-chords-of-1300-popular-songs-for-patterns-this-is-what-i-found/]
6. 斯波索宾 等. *和声学教程*. 人民音乐出版社, 2008.
7. 付林. *流行音乐写作*. 人民音乐出版社.
8. Rick Rubin. *The Creative Act: Ways of Being*. Penguin Press, 2023.
9. CISAC/PMP Strategy. *Economic Impact of Generative AI on Music and AV Creators*. 2024. [https://www.cisac.org]
10. 全国人民代表大会常务委员会. *中华人民共和国著作权法*（2020年修正）. 2020.
11. 全国人民代表大会. *中华人民共和国民法典* 第一千零二十三条（声音权益）. 2020.
12. 北京互联网法院. 全国首例AI声音侵权案判决. 2024.

---

## 版权声明（每条输出末尾）

```
AI生成词曲初稿，仅作个人创作参考。商用需完成完整音乐版权备案。
禁止复刻真人歌手声线、抄袭成熟作品意象与旋律框架。
数字人内容须标注「AI数字人+AI词曲创作」。
```
