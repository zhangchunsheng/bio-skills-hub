---
name: biotech-pitch-deck-narrative
description: 适用于制作生物科技融资演示文稿、将科学数据转化为投资者语言、准备募资展示或撰写投资者问答的场景。将复杂的科学与临床数据转化为引人入胜的投资者叙事，助力生物科技融资。
allowed-tools: "Read Write Bash Edit"
license: MIT
metadata:
  skill-author: AIPOCH
version: "1.0.2"
displayName: "生物科技融资演示文稿叙事"
slug: biotech-pitch-deck-narrative
---

# 生物科技融资演示文稿叙事

## 概述

一款战略沟通工具，将复杂的生物科技创新转化为引人入胜的商业叙事，专为风险投资、制药合作及公开市场投资者优化。

**核心能力：**
- **科学转化**：将技术数据转化为商业价值语言
- **叙事架构**：构建“问题→解决方案→市场→业绩验证→愿景”的叙事流程
- **阶段优化**：针对种子轮至IPO各募资阶段定制信息内容
- **投资者校准**：适配通才型与专才型受众
- **风险缓释**：将科学与监管风险表述为可管理的挑战
- **问答准备**：预判投资者提问并准备应答

## 何时使用

**✅ 适用场景：**
- 为VC路演准备A轮/B轮融资演示文稿
- 为IPO路演制作管理层演示文稿
- 为制药合作洽谈准备BD材料
- 为资助申请撰写执行摘要
- 为业绩说明会排练投资者问答
- 将临床数据转化为商业叙事
- 将学术报告改编为面向商业受众的内容

**❌ 不适用场景：**
- 科学会议演示 → 使用技术性语言
- 监管申报文件 → 使用正式的FDA/EMA格式
- 内部研发团队沟通 → 使用完整的科学细节
- 专利申请 → 使用精确的法律/科学术语
- 面向患者的材料 → 使用 `lay-summary-gen`

**集成关系：**
- **上游**：`market-access-value`（商业评估）、`competitor-trial-monitor`（竞争格局分析）
- **下游**：`business-model-canvas`（战略制定）、`investor-relations-prep`（持续沟通）

## 核心能力

### 1. 科学到商业的转化

将技术概念转化为投资者友好的语言：

```python
from scripts.narrative_engine import BiotechNarrativeEngine

engine = BiotechNarrativeEngine()

# Translate technical description
translation = engine.translate_science(
    technical_description="""
    Our proprietary AAV9-based gene therapy utilizes a codon-optimized 
    transgene under control of a liver-specific promoter to restore 
    functional enzyme in patients with MPS I deficiency.
    """,
    audience="generalist_vc",
    preserve_accuracy=True
)

print(translation.business_narrative)
# "One-time gene therapy delivering a functional copy of the missing enzyme, 
#  potentially curing MPS I rather than managing symptoms"
```

**转化策略：**
| 技术概念 | 商业转化表述 | 为何有效 |
|-------------------|---------------------|--------------|
| "CRISPR-Cas9 gene editing" | "精准基因医疗平台" | 平台化意味着可扩展性 |
| "Phase II clinical data" | "已通过人体概念验证降低风险的资产" | 降低感知风险 |
| "Off-target effects" | "行业领先的特异性表现" | 竞争性表述 |
| "MOA via JAK-STAT pathway" | "针对病因的新型机制" | 价值主张 |

### 2. 叙事架构

构建融资演示文稿的叙事流程，实现最大化影响力：

```python
# Generate complete narrative arc
narrative = engine.build_narrative(
    company_stage="series_b",
    science_type="gene_therapy",
    clinical_stage="phase_2",
    target_market="rare_disease",
    key_differentiation="one_time_cure"
)

# 获取各组成部分
print(narrative.hook)           # 开场吸引点
print(narrative.problem)        # 市场痛点
print(narrative.solution)       # 你的解决方案
print(narrative.traction)       # 迄今的验证成果
print(narrative.ask)            # 融资请求
```

**叙事结构：**
1. **开场钩子**（30秒）：为什么是这个、为什么是现在、为什么是你
2. **问题**（十亿美元级市场）：未满足的医疗需求、现有标准疗法的局限
3. **解决方案**：你的技术/平台、作用机制
4. **业绩验证**：临床数据、合作关系、验证成果
5. **市场**：规模、竞争、你的优势
6. **团队**：过往履历、成功的原因
7. **融资请求**：融资金额、资金用途、里程碑

### 3. 阶段专属优化

针对融资轮次校准信息深度：

```python
# 针对不同阶段进行优化
seed_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="seed",
    focus="team_and_vision"  # 种子轮关注团队与宏大构想
)

series_a_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="series_a",
    focus="proof_of_concept"  # A轮需要验证数据
)

ipo_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="ipo",
    focus="commercial_readiness"  # IPO要求近期收入前景
)
```

**阶段要求：**
| 阶段 | 关键问题 | 关注重点 |
|-------|---------------|-------------|
| **种子轮**（50万-200万美元） | 你能执行吗？ | 团队、愿景、早期验证 |
| **A轮**（1000万-3000万美元） | 有效吗？ | 概念验证数据、知识产权布局、市场进入 |
| **B轮**（3000万-7500万美元） | 能规模化吗？ | 二/三期数据、BD业绩、团队扩张 |
| **C轮/IPO**（1亿美元以上） | 商业化执行 | 注册性试验、上市准备、收入路径 |

### 4. 投资者受众校准

针对不同类型的投资者调整语气与深度：

```python
# 针对特定投资者进行校准
calibrated = engine.calibrate_for_audience(
    narrative=narrative,
    investor_type="healthcare_vc",  # 与 "generalist_vc" 或 "pharma_corp" 相对
    technical_depth="moderate",      # 科学细节的深度
    risk_tolerance="high"            # 早期与后期阶段的表述框架
)
```

**投资者类型：**
- **通才型VC**：关注市场规模、商业模式、团队背景
- **医疗健康VC**：平衡科学严谨性与商业潜力
- **药企BD**：强调战略契合度、验证数据、合作潜力
- **公开市场投资者**：突出近期催化剂、收入预测、风险缓释

## 常见模式

### 模式1：临床阶段治疗药物

**场景**：处于二期临床的生物科技公司正在进行B轮融资。

```bash
# 生成完整的融资叙事
python scripts/main.py \
  --science "Small molecule inhibitor targeting mutant KRAS G12C" \
  --stage "phase_2" \
  --indication "lung_cancer" \
  --data "ORR 45%, median PFS 6.5 months" \
  --competition "Mirati, J&J" \
  --output series_b_narrative.json
```

**叙事要素：**
- **问题**：KRAS突变存在于30%的癌症中，此前被认为“无法成药”
- **解决方案**：具有卓越选择性的同类首创共价抑制剂
- **业绩验证**：二期数据显示45%的应答率，且应答持久
- **市场**：覆盖多种肿瘤类型的150亿美元以上机遇
- **差异化优势**：同类最佳的药效强度、良好的安全性表现
- **融资请求**：7500万美元，用于完成三期临床并准备NDA申报

### 模式2：平台型公司

**场景**：一家新型递送平台公司正在进行种子轮融资。

```python
platform_narrative = engine.generate_platform_narrative(
    platform_technology="Lipid nanoparticle for CNS delivery",
    differentiator="Crosses BBB with 50x improvement over existing LNPs",
    applications=["Alzheimer's", "Parkinson's", "brain_cancer"],
    stage="seed",
    target="platform_value_creation"
)
```

**平台叙事脉络：**
- **平台论点**：解决递送难题可解锁多个适应症
- **验证**：在两个以上疾病模型中完成机制验证
- **广度**：覆盖中枢神经系统、肿瘤学、罕见病的产品管线
- **合作吸引力"：药企对获取CNS靶点的兴趣
- **可扩展性**：生产平台可支撑多个资产

### 模式3：医疗器械

**场景**：一家手术机器人公司正在进行A轮融资。

```python
device_narrative = engine.generate_device_narrative(
    device_type="surgical_robot",
    clinical_benefit="50% reduction in complications, 30% faster recovery",
    regulatory_path="510k_de_novo",
    reimbursement="CPT_code_established",
    stage="series_a"
)
```

**器械专属要素：**
- **临床证据**：相较于标准治疗方案的更优结果
- **经济价值**：为医疗系统节省成本
- **监管明确性**：清晰的FDA路径、报销策略
- **推广策略**：培训、支持、关键意见领袖合作

### 模式4：药企合作洽谈

**场景**：将资产对外授权给大型制药公司。

```bash
# 生成BD材料
python scripts/main.py \
  --mode partnership \
  --asset "Phase 2 ready asset" \
  --indication "NASH" \
  --data_package "Phase 1b complete, biomarker validated" \
  --partner_profile "novo_nordisk" \
  --output bd_presentation.json
```

**合作框架：**
- **战略契合度**：与合作方的代谢领域业务形成互补
- **验证**：已通过人体机制验证降低风险
- **价值创造**：峰值销售潜力超过5亿美元
- **交易结构**：提出灵活的合作条款

## 完整工作流示例

**构建全面的融资材料：**

```python
from scripts.narrative_engine import BiotechNarrativeEngine
from scripts.slide_generator import SlideGenerator
from scripts.qa_prep import QAPreparation

# 初始化
engine = BiotechNarrativeEngine()
slides = SlideGenerator()
qa = QAPreparation()

# 第1步：生成核心叙事
narrative = engine.build_narrative(
    company_stage="series_a",
    therapeutic_area="oncology",
    modality="cell_therapy",
    clinical_stage="phase_1",
    key_differentiation="allogeneic_off_the_shelf"
)

# 第2步：创建逐页幻灯片指南
slide_guide = slides.generate_guide(
    narrative=narrative,
    n_slides=12,
    include_visual_suggestions=True
)

# 第3步：准备问答
qa_prep = qa.generate_qa(
    narrative=narrative,
    investor_type="healthcare_vc",
    depth="comprehensive"
)

# 第4步：导出完整材料包
engine.export_package(
    narrative=narrative,
    slides=slide_guide,
    qa=qa_prep,
    output_dir="series_a_pitch_package/"
)
```

## 质量检查清单

**叙事质量：**
- [ ] 开场钩子能在30秒内抓住注意力
- [ ] 问题对应十亿美元级市场且未满足需求明确
- [ ] 解决方案相较于竞品具有差异化优势
- [ ] 业绩验证支持技术与商业假设
- [ ] 团队具有相关履历
- [ ] 融资请求具体且里程碑清晰

**转化准确性：**
- [ ] 科学主张在简化后仍保持准确
- [ ] 无误导性陈述或夸大宣称
- [ ] 风险因素得到适当披露
- [ ] 监管路径切实可行
- [ ] 市场规模假设有依据支撑

**投资者契合度：**
- [ ] 与阶段和投资者类型相匹配
- [ ] 主动应对投资者可能关切的问题
- [ ] 财务预测合理
- [ ] 退出策略可信

**演示前：**
- [ ] **关键**：对所有宣称内容进行法律审核
- [ ] **关键**：由领域专家进行科学准确性核查
- [ ] 已获经验丰富的生物科技投资者反馈并排练
- [ ] 已为详细提问准备备用幻灯片

## 常见误区

**转化错误：**
- ❌ **过度简化** → “我们的药物能治愈癌症”（具有误导性）
  - ✅ “我们的药物使40%的患者出现肿瘤缩小”

- ❌ **术语堆砌** → 使用技术术语却不加解释
  - ✅ 使用类比：“如同分子GPS引导药物精准到达肿瘤”

- ❌ **隐藏风险** → 不提及副作用或竞争
  - ✅ 承认风险并说明缓释策略

**叙事失误：**
- ❌ **为技术找问题** → 科学很酷，却没有市场
  - ✅ 从问题出发，解决方案自然呈现

- ❌ **忽视竞争** → “我们没有竞争对手”
  - ✅ 承认竞争，说明差异化优势

- ❌ **不切实际的预测** → 第三年营收达100亿美元
  - ✅ 采用保守估算并给出清晰假设

**阶段不匹配：**
- ❌ **种子轮演示文稿却使用三期临床预测** → 过于超前
  - ✅ 使里程碑与阶段相匹配

- ❌ **向种子轮投资者展示IPO级演示文稿** → 重点错位
  - ✅ 根据投资者的成熟度调整深度与重点

## 参考资料

位于 `references/` 目录下：

- `vc_presentation_best_practices.md` - 风险投资路演指南
- `biotech_valuation_models.md` - 各阶段估值方法
- `regulatory_pathway_guides.md` - FDA/EMA审批时间线
- `market_sizing_methodologies.md` - TAM/SAM/SOM计算方法
- `investor_question_bank.md` - 各类投资者常见问答
- `competitive_landscape_templates.md` - 定位框架

## 脚本

位于 `scripts/` 目录下：

- `main.py` - 叙事生成的CLI接口
- `narrative_engine.py` - 核心故事架构
- `science_translator.py` - 技术到商业的转化
- `slide_generator.py` - 演示文稿结构与视觉指导
- `qa_preparation.py` - 投资者问答准备
- `competitive_analyzer.py` - 市场定位分析
- `risk_framer.py` - 风险缓释表述
- `stage_optimizer.py` - 融资轮次校准

## 局限性

- **非财务建议**：不能提供投资建议
- **监管合规**：不能确保符合SEC或其他监管要求
- **市场特异性**：可能无法捕捉小众投资者的偏好
- **实时适应**：无法根据投资者的现场反应实时调整
- **保密性**：不处理重大非公开信息保护事宜
- **法律审核**：所有材料在使用前均需法律顾问审核

## 参数

| 参数 | 类型 | 默认值 | 是否必需 | 说明 |
|-----------|------|---------|----------|-------------|
| `--science` | string | - | 是* | 技术的科学描述 |
| `--stage` | string | - | 是* | 融资阶段（pre-seed、seed、series-a等） |
| `--audience` | string | - | 是* | 目标受众类型（generalist-vc、healthcare-vc等） |
| `--section` | string | - | 否 | 待改写的部分（hook、problem、solution等） |
| `--content` | string | - | 否 | 待改写的内容 |
| `--input` | string | - | 否 | 输入文件路径 |
| `--output`, `-o` | string | - | 否 | 输出文件路径 |

*是否必需取决于子命令

## 用法

### 基本用法

```bash
# 根据科学描述生成叙事
python scripts/main.py generate --science "CRISPR gene therapy for sickle cell" --stage series-a --audience healthcare-vc

# 改写指定部分
python scripts/main.py rewrite --section technology --content "We use AAV vectors..." --audience generalist-vc

# 分析现有的融资演示文稿
python scripts/main.py analyze --input pitch.pptx --stage series-a
```

## 风险评估

| 风险指标 | 评估 | 等级 |
|----------------|------------|-------|
| 代码执行 | Python脚本在本地执行 | 低 |
| 网络访问 | 无外部API调用 | 低 |
| 文件系统访问 | 读写文件 | 低 |
| 数据暴露 | 可能处理机密商业信息 | 中 |
| 监管 | 不能确保符合SEC合规要求 | 中 |

## 安全检查清单

- [x] 无硬编码凭证或API密钥
- [x] 无未授权的文件系统访问
- [x] 输出不暴露敏感信息
- [x] 已设置提示注入防护
- [x] 错误信息已做净化处理
- [x] 脚本在沙盒环境中执行

## 前提条件

```bash
# Python 3.7+
# 无需额外安装包（使用标准库）
```

## 评估标准

### 成功指标
- [x] 成功生成融资叙事
- [x] 能针对不同投资者类型调整内容
- [x] 能将技术内容改写为面向商业受众的版本
- [x] 能提供与阶段相符的信息表述

### 测试用例
1. **生成叙事**：科学描述 → 完整的融资叙事
2. **改写部分**：技术内容 → 面向商业受众的版本
3. **受众适配**：同一内容适配不同类型的VC

## 生命周期状态

- **当前阶段**：草案
- **下次审阅日期**：2026-03-06
- **已知问题**：帮助文本为中文
- **改进计划**：
  - 将所有界面文本翻译为英文
  - 增加更多投资者画像
  - 完善叙事模板

---

**💼 商业提示：成功的生物科技融资需要在科学可信度与商业吸引力之间取得平衡。本工具有助于构建叙事结构，但最终成功仍取决于底层科学与团队执行力。请始终保持诚信——过度承诺会摧毁在成熟投资者面前的可信度。**
