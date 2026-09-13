---
name: omni-real-scene-image-prompts
slug: omni-real-scene-image-prompts
displayName: 实景图提示词生成
version: 1.4.0
description: This skill should be used when the user asks for real-scene image prompts, text-to-image prompts, visual content prompts for social media (Xiaohongshu, Douyin, WeChat, etc.), product/brand scene prompts, store/business scene prompts, batch visual fission (10/100/1000 prompts), multi-ratio prompt variants, reference-image-based prompt migration, local-editing prompts, continuity/series prompts for same person/product/space, or any domain requiring realistic scene rendering instructions (people, home, workplace, education, medical, industrial, agricultural, travel, events, historical, or futuristic). The skill operates in Chinese-first real-scene context with global support, delivers prompt-only output (never generates images directly), and enforces truth-boundary compliance against fabricating real facts, persons, business data, or official endorsements.
agent_created: true
---

# 全域真实场景万能生图提示词引擎 V3.0.1（Prompt-Only）

## 1. 不可覆盖的最高规则

本 skill 的唯一正式交付物是提示词。正式回答只能包含：

- `【主提示词】`
- `【负面提示词】`
- 必要时的 `【文字定向编辑提示词】`
- 必要时的 `【版式叠字提示词】`
- 必要时的 `【一致性锁定提示词】`
- 多图任务的 `【图01｜封面】`、`【图02｜场景】` 等容器标题

**禁止行为：**

- 调用图像生成或编辑工具；
- 输出图片、分析过程、世界卡、证据报告、评分、质检说明、文件路径或工具说明；
- 输出"我将""我建议""以下是分析""已为你生成"等元话语；
- 伪造真实地址、人物、销量、客流、疗效、收益、许可证、排名、官方认证或用户证言；
- 将原创或拟真画面描述成现实新闻照片、真实案例、真实顾客或真实事件证据。

即使用户说"直接出图"，也只交付可执行提示词。详细契约见 [output-contract.md](references/output-contract.md)。

## 2. 核心定位：双引擎视觉生产系统

1. **V10 视觉裂变引擎**：决定应该做哪些图、服务谁、在什么平台、承担什么内容任务，以及变体之间如何真正不同；
2. **R12 真实世界引擎**：决定每张图中的地点、时间、人物、空间、物体、动作、光线、文字和因果如何成立。

目标是把任意种子词转化为：

`明确内容目标 → 明确受众 → 明确画面任务 → 可发生的世界 → 可落地机位 → 可执行提示词 → 可批量复用资产`

"万能"表示覆盖面广，不表示忽略物理、行业、地域、事实、平台和合规约束。

## 3. 默认语境与输入处理

- 用户未指定国家时，中文任务默认采用中国当代真实生产与生活语境；
- 用户指定其他国家、历史时期、未来世界或虚构地点时，切换相应地域与事实边界；
- 用户只给一个词或不知道要生成什么画面时，不连续追问；先读取 [industry-scene-atlas.md](references/industry-scene-atlas.md) 匹配该行业的最佳场景类型和提问模板，再内部补齐平台、受众、内容目标、场景、比例和真实性模式，直接输出最有价值的一版；
- 用户给出平台但未给比例时，选择适合该内容任务的常用比例，并在提示词中写死；用户指定比例时绝对优先；
- 用户要求多比例时，必须为每个比例重新构图，不能只写"裁切成9:16"；
- 用户要求批量裂变时，先在内部生成候选并评分，只输出最终提示词，不输出矩阵分析，除非用户明确要求"提示词矩阵"（此时仍只交付提示词表）。

## 4. 真实性模式（A/B/C/D）

"100%真实"只表示证据边界、物理因果、行为逻辑和视觉光学内部一致，不表示资料不足时仍能精确还原现实。

**A 级：精确复现** — 需要用户有权使用的近期现场照片/视频/测量/产品资料/平面图/人物授权，并有足以支持目标细节的证据。仅 A 级允许写"同一真实地点""同一真实产品"或"同一授权人物"。未知区域保持不可辨或原创。

**B 级：证据型同类原创** — 有区域、行业、产品、流程、空间或人群证据，但缺少完整现场资料。必须声明：`基于真实区域、行业与行为证据构建的同类原创场景，不对应具体已存在地点、人物或事件。`

**C 级：一般真实概念场景** — 只有主题、行业、平台或概念要求。必须声明：`符合目标地域、行业与人群逻辑的原创真实感场景，不复刻具体地址、人物或事件。`

**D 级：拟真虚构/历史/未来场景** — 目标本身不存在、不可直接拍摄或处于历史/未来设定。必须声明：`这是基于已知规律构建的拟真虚构或重建场景，不是现实影像证据。`

资料不足时自动降级，不伪造精度。证据规则见 [evidence-stack-and-provenance.md](references/evidence-stack-and-provenance.md)。

## 5. 任务路由表

先读取 [routing-and-modes.md](references/routing-and-modes.md)，再按模式进入对应子引擎。

| 模式 | 常见需求 | 关键要求 |
|---|---|---|
| 单张真实场景 | 任意主题的一张成片 | 一个核心叙事、可落地机位、最少充分锚点 |
| 小红书/自媒体封面 | 种草、教程、探店、职场、生活方式 | 停留点、主体占比、文字安全区、非硬广真实感 |
| 图文轮播/系列 | 5—20张内容图 | 每张承担不同信息任务，同世界连续，不重复换皮 |
| 产品与品牌场景 | 主图、种草、使用、细节、包装 | 产品几何与材质锁、使用因果、品牌文字策略 |
| 人物与生活方式 | 个人IP、家庭、职场、教育、运动 | 人物身份、关系、动作、服装、空间与光线统一 |
| 空间与建筑 | 室内、住宅、办公、公共空间、施工 | 尺寸、结构、动线、材料、光源和使用状态成立 |
| 工业/农业/基础设施 | 工厂、物流、能源、工地、农田、渔业 | 工艺流程、设备、PPE、物流、安全距离和环境成立 |
| 旅行/自然/城市 | 地方生活、景观、户外、交通 | 地理、季节、天气、活动、机位和客流匹配 |
| 活动/纪实 | 市集、会议、体育、节庆、社区活动 | 事件流程、角色分工、时间线、不冒充新闻证据 |
| 知识/教育/医疗科普 | 课程、步骤、科普、流程 | 信息边界、非诊疗承诺、场景化解释、文字分层 |
| 历史/未来/虚构 | 历史重建、未来生活、概念世界 | D级事实边界、时代物证、物理自洽、避免伪纪实 |
| 参考图迁移/局部编辑 | 换背景、换人群、修文字、扩图 | change-only、keep-unchanged、视觉DNA与身份锁 |
| 多比例重构 | 1:1、3:4、9:16、16:9等 | 每个比例独立构图，锁身份，不机械裁切 |
| 批量视觉裂变 | 10、100、1000条提示词 | V10候选评分、两两差异、覆盖率、重复率与质量门禁 |

## 6. V10 视觉裂变引擎

读取 [n10-visual-fission-engine.md](references/n10-visual-fission-engine.md) 与 [visual-opportunity-scoring.md](references/visual-opportunity-scoring.md)。内部至少处理十轴：

1. 行业/主题世界；2. 目标人群；3. 内容目标；4. 平台与版式；5. 场景与关键时刻；6. 主体与道具；7. 行为与叙事；8. 情绪与证据；9. 摄影/视觉机制；10. 交付变体与系列角色。

裂变不是机械排列。候选必须回答：谁看、为什么停留、画面证明什么、什么动作正在发生、为何适合该平台、能否真实生成、是否可复用。

批量任务可用：

```bash
python scripts/build_visual_fission_matrix.py --seed "职场妈妈晚餐" --audience "25-40岁城市家庭" --platform "小红书"
python scripts/score_visual_candidates.py tests/sample_visual_candidates.csv --out scored.csv
```

## 7. R12 通用真实世界模型

读取 [universal-scene-world-schema.md](references/universal-scene-world-schema.md)。内部锁定十二层：

1. 事实与真实性模式；2. 地理、文化与本地化；3. 时间、季节与天气；4. 空间几何与可供性；5. 主体身份与外观；6. 物体、设备、材料与状态；7. 动作、流程与因果；8. 人际关系、群体行为与交通；9. 机位、光学、构图与曝光；10. 文字、品牌、版式与UI边界；11. 同人物/产品/空间/系列连续性；12. 合规、隐私与事实边界。

所有画面遵循因果链：`地域与时代 → 空间与资源 → 主体身份 → 物体与设备 → 动作与流程 → 社会关系 → 光线与摄影 → 平台构图`。任何上游变量变化，下游必须重算。

## 8. 中国优先的真实本地化

中国场景继续使用 [china-morphology-engine.md](references/china-morphology-engine.md)、[people-mobility-behavior-engine.md](references/people-mobility-behavior-engine.md) 与 [satellite-ground-evidence-protocol.md](references/satellite-ground-evidence-protocol.md)。

不得把中国理解为红灯笼、仿古牌楼、CBD、密集中文招牌或"脏乱差"的单一风格。优先建模：省/市/区县/街道或镇；地形、气候、季节和城市形态；土地用途、建筑年代、物业和交通；当地人群、职业、家庭结构、出行目的和消费/工作动作；真实材料、维护水平、数字化设施和公共服务。

其他国家或地区读取 [global-localization-policy.md](references/global-localization-policy.md)，同样禁止视觉刻板印象。

## 9. 行业与场景子引擎

根据任务加载对应引擎。当用户输入行业名称但不确定要生成什么画面时，首先读取 [industry-scene-atlas.md](references/industry-scene-atlas.md) —— 涵盖67个行业的230+个视觉场景定义和最强提问模板，直接给出该行业应该生成什么图、在什么平台、服务什么人。

- 全行业场景与提问模板：[industry-scene-atlas.md](references/industry-scene-atlas.md)

- 全行业与流程证据：[domain-process-atlas.md](references/domain-process-atlas.md)
- 零售、餐饮、本地生活与门店：[commerce-operation-engine.md](references/commerce-operation-engine.md)、[store-world-schema.md](references/store-world-schema.md)
- 小红书与自媒体：[social-media-content-engine.md](references/social-media-content-engine.md)、[xiaohongshu-visual-engine.md](references/xiaohongshu-visual-engine.md)
- 产品、电商与品牌：[product-and-brand-scene-engine.md](references/product-and-brand-scene-engine.md)
- 人物、家庭、职场、教育与医疗生活：[people-home-work-education-health-engine.md](references/people-home-work-education-health-engine.md)
- 空间、建筑与室内：[space-architecture-interior-engine.md](references/space-architecture-interior-engine.md)
- 工业、农业、物流、能源与基础设施：[industrial-agriculture-infrastructure-engine.md](references/industrial-agriculture-infrastructure-engine.md)
- 户外、旅行、自然与城市生活：[outdoor-travel-nature-engine.md](references/outdoor-travel-nature-engine.md)
- 活动、体育与纪实：[events-documentary-engine.md](references/events-documentary-engine.md)
- 科普、教程与高风险行业边界：[knowledge-health-education-engine.md](references/knowledge-health-education-engine.md)

## 10. 物理、行为与摄影真实性

读取 [physical-causality-and-affordance.md](references/physical-causality-and-affordance.md) 与 [camera-and-visual-realism.md](references/camera-and-visual-realism.md)。

每张图必须回答：相机真正站在哪里；主体为何在这里；正在做什么，动作前后发生什么；物体从哪里来、如何被使用、将去哪里；空间是否容得下人物、设备、车辆和动线；光源在哪里，反射、阴影、景深和曝光是否一致；材料是否有不同粗糙度、磨损、重量和接触关系；画面中的"真实感"是否来自因果，而不是脏乱、噪点或电影滤镜。

## 11. 自媒体与平台内容结构

平台不是只决定比例，还决定信息层级。读取 [social-media-content-engine.md](references/social-media-content-engine.md)。

常见内容任务：封面停留（一眼理解主题，保留标题安全区）；场景建立（交代地点、人物和问题）；过程证明（显示动作、工具和步骤）；细节证据（材质、手部、局部、结果前兆）；结果展示（不伪造收益、疗效或用户评价）；对比解释（同机位、同光线或明确差异来源）；结尾承接（保留文案区，但不模拟平台按钮和虚假互动数据）。

小红书专用规则见 [xiaohongshu-visual-engine.md](references/xiaohongshu-visual-engine.md)。

## 12. 文字、品牌与版式 / 参考图、编辑、连续性与多比例

读取 [text-signage-policy.md](references/text-signage-policy.md)、[reference-visual-dna.md](references/reference-visual-dna.md)、[continuity-series-and-multiratio.md](references/continuity-series-and-multiratio.md)。

**文字策略：** 重要中文、品牌名和标题必须逐字准确；文字较多时默认采用"两阶段"（先生成无乱码真实背景，再输出【版式叠字提示词】）；不让图像模型在远处价签、屏幕和包装上承担大量可读文字；不生成可扫描二维码、真实电话、真实订单、许可证号、虚假星级、销量或评论；不仿造平台原生UI或官方文件。

**参考图与编辑：** 区分参考图（迁移抽象构图/光线/节奏/材质/空间层级，不复制可识别地点/人物/品牌）与编辑目标图（只改指定区域，其他锁定）。同人物/同产品/同空间使用结构化身份签名；多比例要求主体身份和世界不变，构图/留白/景深/前景重新布局；系列图每张承担不同叙事角色但时间线/空间/主体状态连续。

## 13. 批量裂变与差异门禁

读取 [batch-diversity-ledger.md](references/batch-diversity-ledger.md)。不同场景至少比较18轴：行业/主题、人群、内容目标、平台、地域、空间、时间天气、主体、道具、动作、情绪证据、机位、构图、焦段、光线、材料色彩、文字策略、系列角色。任意两条独立提示词默认至少有8个轴明显不同。可用：

```bash
python scripts/audit_visual_plan.py tests/sample_batch_plan.json --strict
python scripts/audit_visual_plan.py tests/sample_series_plan.json --strict
python scripts/audit_visual_plan.py tests/sample_multiratio_plan.json --strict
```

## 14. 提示词编排

读取 [prompt-composer.md](references/prompt-composer.md)。主提示词按以下顺序：Use case/平台/内容目标/真实性模式 → 画幅/图位/系列角色/主体占比 → 地域/时间/环境/空间几何 → 主体身份/外观/产品/设备/道具 → 主动作/次动作/过程/关系 → 机位/焦段/构图/景深/曝光/光源 → 材料/使用状态/细节/真实瑕疵 → 文字/品牌/留白/安全区 → 连续性锁/允许变化项/事实边界 → 任务特定负面约束。

删除"8K、杰作、史诗、震撼"等空泛词。提示词必须可独立使用，不得写"同上"。不同模型适配见 [model-adapters.md](references/model-adapters.md)，未指定模型时输出模型无关版本。

## 15. 内部质量门禁

读取 [quality-gate-and-repair.md](references/quality-gate-and-repair.md)。出现任一 P0 错误不得输出原版本：

- 内容目标与画面不匹配；事实模式或证据尺度越界；地域/时代/季节/行业/人物/设备/流程串场；
- 空间放不下动作，物体/手部/人物/车辆穿模；光源/阴影/反射/镜头/透视冲突；
- 只换背景/脸/颜色/比例的伪裂变；同人物/同产品/同空间/同系列身份漂移；
- 中文关键文字错误或清晰乱码；未授权真实人物/品牌/车牌/住址/隐私；
- 伪造销量/客流/疗效/收益/证言/媒体报道/官方背书；海外模板/中国刻板印象/过度豪华/过度脏旧/3D效果图/无理由电影化；
- 批量提示词重复率高或两两差异不足。

最终输出可用：

```bash
python scripts/lint_prompt_output.py tests/sample_prompt_output.txt --strict
python scripts/validate_scene_world.py tests/sample_scene_world.json --strict
```

## 16. 合规与最终输出格式

读取 [compliance-production-gate.md](references/compliance-production-gate.md) 与 [output-contract.md](references/output-contract.md)。

**合规：** 真实人物/未成年人/医疗/金融/法律/政治/灾难/公共事件执行额外事实和隐私门禁；不生成可误导为真实新闻/监控证据/官方通知/病历/证书/账单/聊天记录或交易凭证的画面；公开传播保留适用的AI生成标识；不以"真实感"制造歧视/贫困猎奇/身体羞辱/身份刻板印象。

**输出格式（单图）：**

```text
【主提示词】
[完整、可独立使用的生产级提示词]

【负面提示词】
[当前任务最可能发生的错误]

```

文字较多或需精确标题时追加 `【版式叠字提示词】`；局部文字修复时追加 `【文字定向编辑提示词】`；同人物/同产品/同空间/系列/多比例时追加 `【一致性锁定提示词】`。

多图任务每张必须完整、可脱离其他图片独立使用。提示词之后不得增加解释或结语。

## 17. 文件路由总表

- 所有任务：[output-contract.md](references/output-contract.md)、[routing-and-modes.md](references/routing-and-modes.md)、[universal-scene-world-schema.md](references/universal-scene-world-schema.md)、[prompt-composer.md](references/prompt-composer.md)、[quality-gate-and-repair.md](references/quality-gate-and-repair.md)
- 行业场景提问模板：[industry-scene-atlas.md](references/industry-scene-atlas.md)（67行业230+提问模板，用户不知道生成什么时优先读取）
- 裂变：[n10-visual-fission-engine.md](references/n10-visual-fission-engine.md)、[visual-opportunity-scoring.md](references/visual-opportunity-scoring.md)、[batch-diversity-ledger.md](references/batch-diversity-ledger.md)
- 真实资料与地点：[evidence-stack-and-provenance.md](references/evidence-stack-and-provenance.md)、[satellite-ground-evidence-protocol.md](references/satellite-ground-evidence-protocol.md)、[compliance-production-gate.md](references/compliance-production-gate.md)
- 中国地域：[china-morphology-engine.md](references/china-morphology-engine.md)；全球地域：[global-localization-policy.md](references/global-localization-policy.md)
- 人物行为：[people-mobility-behavior-engine.md](references/people-mobility-behavior-engine.md)、[people-home-work-education-health-engine.md](references/people-home-work-education-health-engine.md)
- 行业流程：[domain-process-atlas.md](references/domain-process-atlas.md)
- 商业门店：[commerce-operation-engine.md](references/commerce-operation-engine.md)、[store-world-schema.md](references/store-world-schema.md)
- 自媒体：[social-media-content-engine.md](references/social-media-content-engine.md)、[xiaohongshu-visual-engine.md](references/xiaohongshu-visual-engine.md)
- 产品品牌：[product-and-brand-scene-engine.md](references/product-and-brand-scene-engine.md)
- 空间建筑：[space-architecture-interior-engine.md](references/space-architecture-interior-engine.md)
- 工农基建：[industrial-agriculture-infrastructure-engine.md](references/industrial-agriculture-infrastructure-engine.md)
- 户外旅行自然：[outdoor-travel-nature-engine.md](references/outdoor-travel-nature-engine.md)
- 活动纪实：[events-documentary-engine.md](references/events-documentary-engine.md)
- 科普与高风险行业：[knowledge-health-education-engine.md](references/knowledge-health-education-engine.md)
- 摄影物理：[physical-causality-and-affordance.md](references/physical-causality-and-affordance.md)、[camera-and-visual-realism.md](references/camera-and-visual-realism.md)
- 文字版式：[text-signage-policy.md](references/text-signage-policy.md)
- 参考图/连续/多比例：[reference-visual-dna.md](references/reference-visual-dna.md)、[continuity-series-and-multiratio.md](references/continuity-series-and-multiratio.md)
- 模型适配：[model-adapters.md](references/model-adapters.md)
- 官方资料基线：[source-baseline.md](references/source-baseline.md)
- 样例：[example-prompts.md](references/example-prompts.md)

---

## 版本信息

**版本**：v1.4.0
**作者**：亿达老师
