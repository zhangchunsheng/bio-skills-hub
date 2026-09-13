---
name: anes-case-generator
description: |
  Automated anaesthesia case report generator. Accepts structured patient data (demographics, clinical presentation, diagnostic workup, surgical details, anaesthetic management, outcomes) and produces (1) a standardized terminology and collocation summary, (2) a CARE/ACRE-compliant case report draft. Trigger scenarios: writing an anaesthesia case report, converting clinical case notes into an academic manuscript draft, or requiring terminology standardisation assistance. Users may optionally provide a domain-specific terminology checklist for translation accuracy; if absent, the built-in general anaesthesia terminology library is used. Suitable for users who have complete case data but need academic writing support.
  麻醉科病例报告自动生成器。输入患者病历资料（基本信息、临床表现、诊疗经过、手术资料、麻醉资料、结局），输出(1)专业术语与高频搭配汇总表，(2)符合CARE/ACRE指南的病例报告初稿。触发场景：撰写麻醉科case report、将临床病例转化为学术论文初稿、需要术语标准化辅助。需要用户提供对应领域的"专业名词核对清单"以确保翻译准确——若未提供则使用内置通用麻醉术语库。适用于：已有完整病例数据但需要学术写作支持的用户。
metadata:
  version: "1.0"
  tags:
    - anaesthesia
    - case-report
    - CARE-checklist
    - ACRE-checklist
    - terminology
    - academic-writing
    - medical
compatibility:
  - platform: claude
    min_version: "3.5"
  - platform: chatgpt
    min_version: "4o"
  - platform: domestic-llm
    note: "基于国产大语言模型开发，兼容DeepSeek/文心一言/通义千问等主流国产模型"
---

# AnesCaseGenerator — 麻醉病例报告生成器

## 概述

本技能将结构化患者病历资料转化为符合CARE/ACRE指南的麻醉学病例报告初稿，同时输出该病例覆盖的专业术语与高频搭配汇总表。核心价值：术语标准化 + 文献证据表驱动Discussion + 结构化写作三输出。

## 输入要求

### 必填：结构化病例数据

用户需提供以下六部分信息（支持任意格式：自由文本、表格、结构化JSON）：

| 模块 | 内容 | 对应CARE条目 |
|:---|:---|:---|
| 1. 基本信息 | 年龄、性别、既往病史、家族史、社会心理史、相关遗传信息 | 5a-5d |
| 2. 临床表现 | 主诉、主要症状、重要体征、症状时间线 | 5b, 6, 7 |
| 3. 诊疗经过 | 诊断性检查（实验室/影像/电生理）、诊断过程（含鉴别诊断与诊断挑战）、预后评估 | 8a-8d |
| 4. 手术资料 | 手术指征、术式、手术时长、术中出血量 | 9a |
| 5. 麻醉资料 | 麻醉方案（诱导/维持/苏醒）、药物及剂量、监测手段、术中事件 | 9a-9c |
| 6. 结局 | 术后恢复、并发症、随访结果、患者评估 | 10a-10d |

### 可选：参考资料

- **专业名词核对清单（xx领域）**：用户提供的领域术语表（如 `assets/sps_terminology.md`），确保翻译准确。路径通过参数传入。
- **参考文献库**：支持以下格式/来源：
  - **ima知识库**：腾讯ima知识库文件夹（推荐，支持批量导出）
  - **学术平台导出表**：PubMed/Embase/Cochrane/Web of Science检索结果导出为Excel/CSV
  - **文献管理软件**：EndNote批量导出HTML/XML，Zotero/Mendeley导出RIS/BibTeX
  - **论文文件**：PDF（需含DOI或完整引用信息）、Word文档中的参考文献列表
  - **在线数据库**：通过API接入的PubMed、CNKI、万方等（需配合检索skill）
  
  **提供参考文献库将触发文献增强Discussion流程（Step 4-6）。**

### 推荐配套技能

- **MedExtract**（知识库文献筛选与结构化数据提取）：
  - 对ima知识库执行PRISMA流程的文献筛选，输出标准化Table 1提取表格
  - **MedExtract的输出可直接作为本技能的参考文献库输入**，实现无缝衔接：
    - MedExtract Table 1 → 本技能 Step 4 参考文献库
    - MedExtract 溯源注释 → 本技能 `[n]` 引用标注
  - 推荐工作流：先用MedExtract完成文献筛选和数据提取，再用本技能生成病例报告
  - 适用场景：需要对知识库中的多篇文献进行系统化筛选后生成病例报告

### 参考文献库缺失提醒

若用户未提供参考文献库，必须在输出首行打印以下提醒：

> ⚠️ **由于您未指定参考文献库，大语言模型自由检索可能引入幻觉，请审慎采纳。** 建议提供参考文献来源（ima知识库/检索结果导出表/EndNote导出/论文文件），或接入专业检索skill进行文献补充。

## 工作流

---

### Step 1: 解析病例数据

1. 接受用户输入，识别结构化病例数据的六个模块内容
2. 若输入不完整，列出缺失模块并提示补充
3. 若提供了专业名词核对清单路径，读取该文件载入领域术语库

---

### Step 2: 术语提取与匹配

1. **加载通用术语库（Part A）**：读取 `references/general_terminology.md`（内置通用麻醉/医学/统计学术语库，~220条），此为内置资源，无需用户提供
2. **加载领域术语库（Part B）**（可选）：若用户提供了领域专业名词核对清单（如 `assets/sps_terminology.md`），读取该文件作为 Part B 领域专属术语
3. 扫描病例数据，从术语库中匹配出现术语，生成两份初筛表：
   - 已匹配术语（术语库中存在）
   - 候选术语（病例中出现但术语库中未收录）
4. 补充提取病例中出现的高频固定学术搭配

---

### Step 3: 生成术语汇总表

输出 **专业术语与高频搭配汇总表**，格式与结构：

```
# 专业术语与高频搭配汇总表（[疾病/术式名称]）

## I. 麻醉/医学通用术语
[English | 中文 | Abbreviation | 出现上下文]

## II. 领域专属术语
[English | 中文 | Abbreviation | 出现上下文]

## III. 高频学术固定搭配
[English Expression | 中文表达 | 使用场景]
```

---

### Step 4: 参考文献库检索与病例匹配（仅在用户提供参考文献库时执行）

**目标**：从用户提供的文献库中检索与本病例最相关的病例报告，为Discussion中的数据提取表提供素材。

**检索策略**：

1. **提取检索锚点**：从病例数据中抽取3个核心检索维度——
   - 疾病锚点：诊断名称（如"Stiff Person Syndrome"）及其变体
   - 麻醉锚点：麻醉方式（如"TIVA"、"general anesthesia"）、关键药物（如"propofol"、"rocuronium"）
   - 手术锚点：术式关键词（如"thyroidectomy"、"abdominal surgery"）

2. **多策略检索**（根据文献库格式选择）：
   - **ima知识库**：使用 `search(source="kb", kb_id=xxx)` 以"疾病名 + anesthesia/case report"为查询词检索；随后用 `fetch(type="media_id")` 逐篇阅读
   - **Excel/CSV导出表格**：读取表格，在标题/摘要列中匹配疾病锚点+麻醉锚点
   - **EndNote HTML**：解析文献条目，在Title和Abstract字段中检索
   - **PDF/Word文件**：逐篇使用 `fetch` 提取病例信息

3. **相关性排序**：按以下优先级排序检索结果——
   - 优先级1：同疾病 + 同麻醉技术
   - 优先级2：同疾病 + 不同麻醉技术（对照价值高）
   - 优先级3：同疾病 + 同手术类型
   - 优先级4：仅疾病相同

---

### Step 5: 文献数据提取表生成（仅在用户提供参考文献库时执行）

**目标**：从匹配到的病例报告中提取关键数据，生成结构化对比表。

**表格规范**（参考 `references/extraction_table_spec.md`）：

#### 标准列结构（11列，4大分组）

| 分组 | 列名 | 提取内容 |
|:---|:---|:---|
| **A. 文献信息** | 年份 | 发表年份 |
| | 参考文档标题 | 论文标题（缩写） |
| | 作者 | 第一作者 et al. |
| | 期刊 | 期刊名缩写 |
| **B. 患者** | 病例数/基本资料 | 例数，年龄，性别，BMI（如有） |
| | 合并症 | 相关合并症 + 术前SPS用药 |
| **C. 麻醉方案** | 手术 | 术式名称 |
| | 麻醉方式 | TIVA / GA+Inhalation / Regional / CSE等 |
| | 吸入药 | 药物名 + 浓度 |
| | 静脉药 | 诱导+维持药物及剂量 |
| | 阿片类/区域麻醉药 | 阿片类 + 局麻药详情 |
| | 肌松药及拮抗 | NMBA种类+剂量 / 拮抗剂种类+剂量 / 未使用 |
| **D. 结局** | 并发症/结局 | 并发症类型 + 处理 + 转归 |

#### 提取规则

- **本病例独占首行**，加粗或 `*` 标注
- 文献病例按年份降序排列
- 缺失值标注为 `—`（区别于"未使用"）
- "未使用"指临床决策不使用某类药物，标注为"未使用"
- 剂量保留原文献单位，不进行换算
- 同一文献涉及多次麻醉的，分拆为独立行（如"病例X-第1次"、"病例X-第2次"）

---

### Step 6: 文献增强Discussion生成

**目标**：将数据提取表嵌入Discussion，完成定性分析 + 定量分析建议，形成完整Discussion。

#### 6.1 Discussion结构（文献增强版）

```
Discussion
├── 6.1.1 本病例核心发现概述（1段）
├── 6.1.2 文献数据提取表（完整表格）
├── 6.1.3 定性分析（逐维度讨论）
│   ├── 麻醉方式选择的证据对比
│   ├── 肌松药使用的安全性分析
│   ├── 吸入药 vs TIVA的结局差异
│   ├── 拮抗策略比较
│   └── 并发症模式归纳
├── 6.1.4 定量分析建议
│   ├── 可量化的结局指标识别
│   ├── 建议的统计方法
│   └── 样本量需求估算
├── 6.1.5 本病例在文献图谱中的定位
├── 6.1.6 局限性
└── 6.1.7 临床实践建议
```

#### 6.1.1 本病例核心发现概述

用2-3句话概括本病例的麻醉决策亮点、与文献的差异点、学术贡献。

#### 6.1.2 文献数据提取表

将Step 5生成的表格嵌入此处。表格标题格式：`**Table 1. Summary of Published Case Reports of Anesthetic Management in Patients with [Disease]**`

#### 6.1.3 定性分析

逐维度进行系统性对比分析。每条分析必须引用表格中的具体数据。核心分析维度：

| 分析维度 | 引导问题 | 输出要求 |
|:---|:---|:---|
| 麻醉方式 | TIVA vs 吸入 vs 区域麻醉的病例分布如何？本病例选择在哪一端？ | 统计各类麻醉方式的例数，指出主流方案和本病例的位置 |
| 肌松药策略 | 使用/未使用NMBA的病例各多少？使用后并发症率？ | 列出每例的NMBA种类、剂量、是否使用拮抗剂、是否出现并发症 |
| 吸入药风险 | 使用吸入药的病例中术后低张力发生率？与TIVA对比？ | 制作2×2对比（吸入药± × 并发症±），描述趋势 |
| 拮抗策略 | Sugammadex vs Neostigmine的使用频率和逆转效果？ | 对比两种拮抗剂的成功率 |
| 并发症模式 | 各类并发症的发生条件和处理方式？是否有可预防的模式？ | 归纳并发症类型→发生条件→处理→转归的因果链 |

**定性分析写作要求**：
- 每段以主题句开头（如"Regarding the choice of anesthetic technique, the literature reveals..."）
- 引用表格数据时使用"如表1所示，在N例使用XX的患者中，M例出现了YY"
- 避免"所有病例均无并发症"等绝对化表述，改为"在已报告的N例中未观察到XX"
- 对比本病例与文献的异同时，明确指出差异的可能原因

#### 6.1.4 定量分析建议

基于表格数据的局限性，提出定量分析方向：

1. **可量化的结局指标**：从表格中识别可用于统计的变量——
   - 二分类：并发症（有/无）、拔管延迟（是/否）、使用NMBA（是/否）
   - 连续变量：住院天数、拔管时间（如有数据）

2. **建议的统计方法**：
   - Fisher精确检验（样本量<30时）：比较不同麻醉方式的并发症率
   - Mann-Whitney U检验：比较住院天数在不同麻醉方式间的差异
   - 多变量逻辑回归（若数据充足）：识别术后并发症的独立预测因子

3. **样本量需求估算**：基于当前表格中的效应量趋势，估算达到统计显著性所需的最小样本量

4. **明确标注**："由于当前文献仅有N例报告，以下定量分析仅为方向性建议，不具备统计推断效力。"

#### 6.1.5 本病例在文献图谱中的定位

明确指出本病例在已有文献中的独特贡献（如：首例使用XX药物、首次报告YY结局、填补ZZ手术类型的空白）。

#### 6.1.6 局限性

- 文献报告的发表偏倚（阳性结果更可能被发表）
- 样本量限制
- 回顾性数据的固有局限
- 缺乏标准化结局指标

#### 6.1.7 临床实践建议

以3-5条可操作建议收束Discussion，每条建议需有表格数据支撑。

---

### Step 7: 生成病例报告初稿（双语独立输出）

**核心要求**：
1. **双语独立稿件**：分别生成完整的英文版初稿和中文版初稿
2. **禁止中英文混用**：同一稿件内不得出现中英夹杂（术语首次出现时可标注英文原文，如"僵人综合征（Stiff-person syndrome, SPS）"，之后仅用中文）
3. **全句引用标注**：初稿中任何非用户病例数据的语句均需标注参考文献（详见 `references/citation_standards.md`）

**参考文献标注规范**（必读 `references/citation_standards.md`）：
- `[1], [2]` — 来自用户提供的参考文献库
- `[L1], [L2]` — LLM补充来源：
  - 实时检索的外源文献（需说明检索策略和置信度）
  - 训练数据中的高置信度医学常识（基础概念、机制等，见 `citation_standards.md` 2.2.1）
- `[T1], [T2]` — 术语库/指南/标准引用
- `[需验证]` — 无法找到匹配来源的陈述

**关于模型记忆知识的使用限制**（详见 `references/citation_standards.md` 2.2.1）：
- ✅ **允许**：基础医学常识（药物分类、作用机制、解剖结构等）可标注 `[Ln]`（置信度：高）
- ❌ **禁止**：具体统计数据、数值、研究结论等不得直接使用模型记忆，必须检索确认
- 示例：❌ "SPS发病率约1/100万"（模型记忆，可能过时）→ ✅ 检索确认后标注 `[Ln]`

**诚实性原则**：
- 若使用了LLM检索补充的文献，必须在文末主动说明
- 若使用了模型记忆中的高置信度常识，标注 `[Ln]` 并注明"来源：模型知识，置信度：高"
- 若无法找到某陈述的文献支持，标注`[需验证]`而非编造
- 区分"有文献支持的事实"与"基于病例的临床推断"

---

#### 7.1 英文版初稿（English Draft）

**术语核对**：参照术语汇总表，确保英文术语与名词汇总表一致

**结构**（遵循CARE/ACRE Checklist）：
1. **Title**：Diagnosis/Intervention + "Case Report"
2. **Keywords**：2-5 keywords, including "case report"
3. **Abstract**（structured）：
   - Introduction：Unique features and academic contribution
   - Main symptoms/clinical findings
   - Main diagnoses, interventions, outcomes
   - Conclusion — take-away lesson
4. **Introduction**：Why this case is worth reporting
5. **Case Presentation**：Patient Information → Clinical Findings → Timeline → Diagnostic Assessment → Therapeutic Intervention
6. **Discussion**：
   - 若执行了Step 4-6 → 使用文献增强版结构（6.1.1-6.1.7）
   - 若未提供参考文献库 → 使用基础版（本病例优势/局限，所有非病例数据陈述标注`[L]`或`[需验证]`）
7. **Conclusion**：Single-paragraph take-away lesson
8. **Patient Perspective**（if available）
9. **Declarations**：Informed consent, conflicts of interest, funding

**引用标注要求**：
- 所有非用户病例数据的陈述必须标注`[n]`、`[Ln]`、`[Tn]`或`[需验证]`
- 文末列出References（分三类：References / LLM-Supplemented References / Terminology & Standards）

---

#### 7.2 中文版初稿（Chinese Draft）

**术语核对**：参照术语汇总表，确保中文翻译严谨专业

**结构**（与英文版对应，遵循CARE/ACRE Checklist）：
1. **标题**：诊断/干预 + "病例报告"
2. **关键词**：2-5个关键词，含"病例报告"
3. **摘要**（结构化）：
   - 引言：本病例独特之处及学术贡献
   - 主要症状/临床发现
   - 主要诊断、干预措施、结局
   - 结论 — 核心启示
4. **引言**：为何本病例值得报告
5. **病例介绍**：患者信息 → 临床表现 → 时间线 → 诊断评估 → 治疗干预
6. **讨论**：
   - 若执行了Step 4-6 → 使用文献增强版结构
   - 若未提供参考文献库 → 使用基础版
7. **结论**：单段核心启示
8. **患者视角**（如有）
9. **声明**：知情同意、利益冲突、资助

**引用标注要求**：
- 使用与英文版**同一套引用编号**`[n]`、`[Ln]`、`[Tn]`
- 文末列出参考文献列表（与英文版相同）

---

#### 7.3 参考文献列表格式（两版本共用）

```
References
[1] Author A, Author B. Title. Journal. Year;Vol:Pages.
[2] ...

LLM-Supplemented References
[L1] Author. Title. Journal. Year. (检索策略：PubMed检索词"XXX"，置信度：高/中/低)
[L2] ...

Terminology & Standards
[T1] Gagnier JJ, et al. The CARE Guidelines. J Clin Epidemiol. 2013;67(1).
[T2] Shelton CL, et al. The ACRE Checklist. Anaesthesia Reports. 2021.
[T3] AnesCaseGenerator内置术语库，Part A/Part B.
```

**写作约束**：
- 所有事实性陈述需基于用户提供的病例数据或标注参考文献
- 术语使用：优先匹配术语库标准翻译
- 参考 `references/writing_patterns.md` 中的高频句式和论证逻辑
- 若使用了LLM检索补充的文献，必须在"LLM-Supplemented References"部分主动说明

---

### Step 8: 自查与交付

#### 8.1 CARE/ACRE 结构完整性核查

1. 对照 **CARE Checklist** 和 **ACRE Checklist** 逐项核验完整性（两项核验标准均参见 `references/care_checklist.md`）
2. 标注未覆盖项及原因（如"患者视角未提供"）

#### 8.2 文献增强Discussion核查（如适用）

- 表格中本病例数据与正文Case Presentation一致
- 每条定性分析均有表格数据支撑
- 定量分析建议标注了"方向性建议"限定

#### 8.3 参考文献标注核查（关键）

逐句检查英文版和中文版初稿：
- [ ] 所有非用户病例数据的陈述均有引用标注（`[n]`/`[Ln]`/`[Tn]`/`[需验证]`）
- [ ] 用户文献 `[n]`、LLM补充 `[Ln]`、术语 `[Tn]` 分类正确
- [ ] LLM补充文献有检索策略和置信度说明
- [ ] 文末参考文献列表完整，编号连续
- [ ] 无 `[需验证]` 遗漏（或已明确告知用户）
- [ ] 中英文版本引用编号一致

#### 8.4 双语稿件格式核查

- [ ] 英文版初稿：全文英文，无中文混用（术语首次出现可标注中文）
- [ ] 中文版初稿：全文中文，无英文混用（术语首次出现可标注英文）
- [ ] 两版本结构对应，内容一致
- [ ] 术语翻译参照术语汇总表，确保严谨专业

#### 8.5 诚实性声明核查

- [ ] 若使用了LLM检索补充的文献，已在文末主动说明
- [ ] 若存在`[需验证]`标注，已告知用户需人工核实
- [ ] 无编造文献或虚假引用

#### 8.6 输出格式

按以下顺序输出最终产物：

```
# 专业术语与高频搭配汇总表
...

---

# 病例报告初稿（英文版）
## English Draft
...

---

# 病例报告初稿（中文版）
## Chinese Draft
...

---

# 参考文献列表（References）
## References
...

## LLM-Supplemented References
...（如有，需说明检索策略和置信度）

## Terminology & Standards
...

---

# 自查报告
## 完整性核查
...

## 引用标注核查
...

## 需用户人工核实项
...（列出所有[需验证]标注处）
```

---

## 接口扩展点

本技能保留以下接口供与其他专业检索skill对接：

- `reference_search_hook`：当用户提供参考文献库时，优先调用对应格式解析器检索
- `terminology_hook`：当用户提供领域核对清单（如 `assets/sps_terminology.md`）时，使用该清单作为 Part B 术语基准
- 若用户接入外部检索skill（如PubMed系统检索、多数据库文献检索），Step 4的检索策略可替换为该skill的标准检索流程，检索结果直接输入Step 5

---

## 资源文件

### references/

| 文件 | 用途 |
|:---|:---|
| `general_terminology.md` | 内置通用术语库（Part A，~220条），涵盖麻醉/医学/统计学通用术语，无需用户提供即可使用 |
| `care_checklist.md` | CARE 指南 + ACRE 麻醉扩展检查清单，用于病例报告结构核验 |
| `writing_patterns.md` | 学术写作模式库——高频句式、5种Discussion论证路径、术语使用原则 |
| `extraction_table_spec.md` | 文献数据提取表规范——11列标准结构、提取规则、缺失值处理协议 |
| `citation_standards.md` | **参考文献标注规范**——引用类型定义、标注格式、诚实性原则、操作流程 |

### assets/

| 文件 | 用途 |
|:---|:---|
| `case_report_template.md` | CARE/ACRE 标准病例报告空白模板（含文献数据提取表占位） |
| `sps_terminology.md` | SPS 领域专属术语（Part B，可选），用户按需提供 |
