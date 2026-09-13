# pharmcube MCP 工具参数速查

> 本文件为所有 Skill 共享参考，列出每个工具的真实参数、枚举值和使用要点。**以下内容已对照 MCP 工具的实际 schema 逐字段核实**（2026-07-14 核实）。

---

## ⚠️ drugUID 获取方式（全局重要说明，所有涉及 drugUID 的 Skill 必读）

**drugUID 只能通过 `drugBaseCN`（详细版，成本高）获取，`drugBaseLiteCN`（概要版，成本低）不返回 drugUID。**

- `drugBaseLiteCN` 返回字段中只有内部字段 `_id`（形如 `"kBRoEwhSwvo="`），这个值**不能**当作 drugUID 传给 `drugApprDisease`/`drugClinicalPaper`/`drugNonClinicalPaper`/`drugDisease`——传入会静默返回 0 条结果（不报错），容易被误判为"该品种无数据"。
- 真正的 drugUID 是 `drugBaseCN` 返回结果中的 `uid` 字段（形如 `"DR050301"`）。
- **因此**："先用 drugBaseLiteCN 便宜地拿到 drugUID，再按需对少数品种调用昂贵的 drugBaseCN" 这种两段式成本控制策略不成立。正确流程是：
  1. 用 `drugBaseLiteCN` 做筛选、列表展示、计数统计——这些场景不需要 drugUID。
  2. 当确实需要 drugUID（用于 drugApprDisease / drugClinicalPaper / drugNonClinicalPaper / drugDisease）时，对锁定的少数重点品种（用 `drugName` 精确匹配）调用 `drugBaseCN`，从返回结果的 `uid` 字段取值。
  3. 成本控制仍然重要，但控制的手段是"限制调用 drugBaseCN 的品种数量"，而不是"用 drugBaseLiteCN 代替 drugBaseCN 去拿 drugUID"。

**⚠️ `drugName` 不是精确匹配——用 drugName 调用 drugBaseCN/drugBaseLiteCN 取 uid 前必须核对 total。** 实测发现：许多通用名会同时匹配原研药、生物类似药、复方制剂、剂型变体等多条记录（如"帕博利珠单抗"匹配38条，包含无关的膀胱内灌注剂型、其他企业的生物类似药）。仅取返回结果的第一条会**静默拿到错误品种的 uid**（不报错，看起来正常，但数据是错的）。正确做法：
1. 调用后检查 `total` 字段。若 `total=1`，直接使用。
2. 若 `total>1`，必须用 `companyName`（原研/目标企业名）、`phase`/`phaseCN`（如筛选"批准上市"聚焦原研上市品种）等参数进一步收窄，或在多条候选中核对 `name_short`/`company_names_originator` 等字段确认匹配到目标品种后再取其 `uid`，禁止默认取第一条。

**⚠️ 成本模型：按返回记录数计费，不是按调用次数计费。** 实测 `drugBaseLiteCN`/`drugBaseCN` 按每条返回记录计费（drugBaseCN 单条记录costs显著高于 drugBaseLiteCN），因此一次 `pageSize=20` 的"轻量"调用实际成本可能远高于预期。控制成本的关键是**同时控制调用次数和 pageSize/返回记录数**，尤其 `drugBaseCN` 应尽量用精确 `drugName` + `pageSize=1`，避免宽泛条件下的大 pageSize 调用。若某工具调用返回 `errorCode":"2002"`（账户状态异常/冻结），说明账户额度已耗尽，应立即停止后续调用，在报告中如实说明"因数据服务额度限制，以下部分数据未能获取"，不得跳过此错误继续静默重试。

**⚠️ 大记录可能超出单次返回的 token 上限。** `drugBaseCN`（尤其适应症/试验/专利记录很多的品种）、`clinicalTrialTopic` 的响应有时会超过工具输出上限而被重定向到本地文件。遇到这种情况，优先用更小的 `pageSize`（`drugBaseCN` 建议从 `pageSize=1` 开始）和更精确的检索条件减少返回记录数，而不是尝试读取超大文件。

---

## drugBaseCountCN — 管线数量统计（最轻量，优先用于快速计数）

**用途**：快速了解某疾病/靶点/企业的管线总数和阶段分布，成本最低。**无分页参数**（一次性返回统计结果）。

**至少选择一个作为检索条件**（不能全为空）：drugName、companyName、target、disease、diseaseArea、phase、phaseCN、regnOriginator

| 参数 | 说明 | 常用值 |
|------|------|------|
| drugName | 管线名/药品名 | |
| disease | 疾病名称 | "非小细胞肺癌"、"乳腺癌" |
| target | 靶点 | "PD-1"、"EGFR"、"HER2" |
| companyName | 研发机构 | |
| diseaseArea | 疾病领域 | "肿瘤领域"、"心脑血管领域" |
| phase | 全球最高研发阶段（多值） | 临床前/申报临床/I期临床/I·II期临床/II期临床/II·III期临床/III期临床/申请上市/批准上市 |
| phaseCN | 中国最高研发阶段（多值） | 同上 |
| status | 全球研发状态（多值） | Active（3年内有进展）/Unknown（3-6年无进展）/Inactive（放弃或6年以上无进展） |
| customGroupBy | 自定义分组维度（多值） | drug_type_1/drug_type_2/latest_phase/latest_phase_cn（默认按 status 分组） |
| withDeals | 是否有交易 | "Y"/"N" |
| regnOriginator | 原研机构国家地区 | "中国"、"美国" |

**⚠️ 不要传 pageNo/pageSize 给此接口——它没有这两个参数，传了会被忽略或报错。**

---

## drugBaseLiteCN — 管线概要列表（筛选/概览首选）

**用途**：列出品种清单，覆盖药品名、靶点、企业、研发阶段。成本低于详细版。**不返回 drugUID**（见上方全局说明）。必填：pageNo（从0开始）、pageSize。

**至少选择一个作为检索条件**：drugName、companyName、target、disease、diseaseArea、phase、phaseCN、regnOriginator

| 参数 | 说明 | 常用值/注意 |
|------|------|------|
| drugName | 管线名、药品名 | |
| disease | 疾病 | |
| target | 靶点 | |
| companyName | 研发机构 | |
| phase | 全球最高研发阶段（多值） | 同上 |
| phaseCN | 中国最高研发阶段（多值） | |
| status | 全球研发状态（多值） | Active/Unknown/Inactive |
| drugType1 | 创新类型（多值） | 创新药/微创新/生物仿制 |
| drugType2 | 药品类别（多值） | 中药/化药/生物/其他 |
| drugType3 | modality | 小分子/抗体偶联药物/双特异性抗体/CAR T细胞疗法/RNAi疗法 等 |
| withDeals | 是否有交易 | Y/N |
| customSort | 自定义排序 | 按 name_short/drug_type_1/drug_type_2/status 排序 |
| pageNo | 必填，从0开始 | |
| pageSize | 必填，同次检索保持一致 | 1/5/10/20/50 |

**关键返回字段**：`_id`（内部ID，不是drugUID，不可用于其他接口）、药品名、靶点、研发机构、全球/中国最高阶段。**无 approvalStatus 参数**——筛选已上市品种应传 `phase: ["批准上市"]`。

---

## drugBaseCN — 管线详细信息（唯一能拿到 drugUID 的接口，成本高）

**用途**：获取单个品种的完整信息，包含注册信息、专利到期、交易汇总等。仅当需要 drugUID 或详细字段时调用。必填：pageNo（从0开始）、pageSize。

**至少选择一个作为检索条件**：drugName、companyName、target、disease、diseaseArea、phase、phaseCN、latestPhaseDateFrom/To、latestPhaseCNDateFrom/To

额外参数：
- drugTag：品种标签（First-in-Class、Potential First-in-Class、差异化疾病、中国无申报、肿瘤免疫 等）
- withDeals：是否有交易（Y/N）
- latestPhaseDateFrom/To：全球最高阶段开始日期范围
- latestPhaseCNDateFrom/To：中国最高阶段开始日期范围

**关键返回字段**：`uid`（即 drugUID，形如 "DR050301"，供 drugApprDisease/drugClinicalPaper/drugNonClinicalPaper/drugDisease 使用）、专利到期日期（compound_sequence_patent_cn 等）、交易汇总（deal_num、total_upfront_payment、total_deal_value）、NCT登记号列表（nct_ids）。

---

## applicationCN — CDE/NMPA注册审评

**用途**：查询注册申报进度、审批状态、竞品申报数量。必填：pageNo（从0开始）。**至少选择一个作为检索条件**：appNO、drugName、target、moa、disease、diseaseType、applicant、appType、txnDateFrom/To、issueDateFrom/To。

| 参数 | 说明 | 合法值 |
|------|------|------|
| appNO | 受理号 | |
| drugName | 药品名称 | |
| disease | 适应症 | |
| diseaseType | 疾病领域 | |
| applicant | 持证商/合作申报企业 | |
| target | 靶点 | |
| moa | 药理类型 | |
| appType | 申请事项 | 申请临床/申请上市/补充申请/申请再注册/申请复审/进口分包装申请/技术转移申请/一次性进口/原辅包备案 |
| innovationType | 创新类型 | **创新药/改良型新药/生物类似物/仿制药/未知**（不是"3类"/"4类"这种注册分类代码） |
| fastTrack | 审评通道 | 附条件批准/拟优先审评/优先审评/拟突破性治疗/突破性治疗/特殊审批/特别审批/重大专项 |
| milestone | 申报里程碑 | 首次申请临床/首次批准临床/首次申请上市/首次批准上市 |
| submissionType | 注册分类 | （中国3类/4类等具体分类信息在此字段，而非 innovationType） |
| txnDateFrom/To | CDE承办日期范围 | yyyy-MM-dd |
| issueDateFrom/To | 签发日期范围 | yyyy-MM-dd |

**注意**：要查"某品种的仿制药申报"，应传 `innovationType: "仿制药"` + `drugName`，若要进一步区分3类/4类，需查看返回结果中的 `submissionType` 字段或结合 `milestone`，不要把"3"/"4"当作 innovationType 的值传入。

---

## clinicalTrialTopic — 全球临床试验

**用途**：检索在研/完成的临床试验，获取试验设计、入排标准、终点指标等。必填：pageNo（从0开始）。**至少选择一个作为检索条件，且必须是以下四者之一**：nctId、associate_nctId、**primaryDrugName**（试验组药品，注意不是 drugName）、otherDrugName（对照组药品）。

⚠️ **disease、target 等字段是补充过滤条件，不能单独满足"检索条件"要求**——仅传 disease/phase/pivotal 而不传 nctId/primaryDrugName/otherDrugName/associate_nctId 中任意一个，可能不被接受为有效检索。若只知道疾病/靶点、不知道具体品种名，需先通过 drugBaseLiteCN 或 drugBaseCN 查到 primaryDrugName 再检索，或改用 primaryTarget 是否可行需结合实际返回结果判断（primaryTarget 存在于 schema 中，但不在"至少一个"的必需清单里，建议同时传 primaryDrugName 保证请求有效）。

| 参数 | 说明 | 常用值 |
|------|------|------|
| nctId | 试验登记号（精确） | NCT开头 |
| associate_nctId | 关联登记号 | |
| primaryDrugName | 试验组药品 | |
| otherDrugName | 对照组药品 | |
| primaryTarget | 试验组靶点 | |
| otherTarget | 对照组靶点 | |
| disease | 疾病 | |
| diseaseArea | 疾病领域 | |
| phase | 试验分期 | ⚠️ 输入schema未明确枚举值；实测传入"III期"/"III"均静默返回0条（不报错），而真实返回记录里的 phase 字段值是英文格式（如"Phase III"、"Phase II/III"）。**建议不要依赖此参数做筛选**，改为不传 phase、只用 `pivotal`/`disease`/`primaryDrugName` 检索，再对返回结果的 phase 字段做人工/程序过滤；若必须传参，先用小范围测试确认当前实际枚举格式，不要直接套用中文"X期"格式 |
| pivotal | 是否注册性临床 | Y/N（不是"是"/"否"） |
| positive_placebo | 对照类型 | 阳性对照/安慰剂·空白对照 |
| primaryCombo/otherCombo | 联用情况 | 单药治疗/联用治疗 |
| primaryDrugType1/2/3 | 试验组药品分类 | |
| result | 是否有结果 | |
| sponsor | 申办方、合作方 | |
| dataSource | 登记平台 | AUS-ANZCTR/BRA-REBEC/CN-CDE/CN-ChiCTR/EU-EudraCT/IN-CTRI/JP-JAPIC/JP-JRCT/JP-UMIN/KOR-CRIS/TW-DCTI/UK-ISRCTN/US-ClinicalTrial |

---

## trialResultTC — 临床试验结果

**用途**：获取关键有效性和安全性数据。必填：nctId、pageNo（从0开始）。

| 参数 | 说明 |
|------|------|
| nctId | 试验登记号（必填，精确匹配） |
| pageNo | 必填，从0开始 |
| keyEvidence | 是否为关键证据（"是"/"否"）——若该试验支持过获批，选取首次公布主要终点结果的证据；若未支持获批，选取最新一次重要结果（排除亚组/事后分析） |

**关键字段**：ORR、PFS、OS、mOS 等终点指标结果

---

## drugApprDisease — 已上市药品获批详情

**用途**：查询某品种在中/美/欧/日的获批情况。必填：drugUIDList（最多200个，**必须来自 drugBaseCN 的 `uid` 字段**，不可用 drugBaseLiteCN 的 `_id`）、pageNo（从0开始）。

| 参数 | 说明 |
|------|------|
| drugUIDList | 必填，药品UID列表（来自 drugBaseCN 的 uid 字段） |
| disease | 疾病（模糊匹配） |
| appDateFrom/To | 获批日期范围 |
| pageNo | 必填，从0开始 |

**返回字段**：drug_uid、drug_name、disease_name、appr_time、appr_type（如"常规批准"/"附条件批准(中国)"）、country、is_first_appr、label_indication_cn/en 等。

---

## drugDeal — 交易信息

**用途**：查询 License-in/out、并购、合作等交易。必填：dateFrom、dateTo、pageNo（从0开始）。**没有 `company`（双向匹配）参数，也没有 `dealType` 枚举参数**——按公司检索必须明确传 `transferor`（转让方/License-out方）或 `transferee`（受让方/License-in方），按交易类型筛选需要结合 `phaseDealing`（交易时研发阶段）或从返回结果中人工判断交易性质，工具本身不提供 License-in/License-out/并购/合作开发 这样的分类过滤参数。

| 参数 | 说明 | 常用值 |
|------|------|------|
| dateFrom/dateTo | 交易日期范围（必填） | yyyy-MM-dd |
| pageNo | 必填，从0开始 | |
| drugName | 交易药品名 | |
| disease | 疾病 | |
| target | 靶点 | |
| transferor | 转让方（License-out方） | |
| transferee | 受让方（License-in方） | |
| phaseDealing | 交易时药品全球最高研发阶段 | 临床前/申报临床/I期临床/I·II期临床/II期临床/II·III期临床/III期临床/申请上市/批准上市 |

**若要"只看某企业的对外授权"**：传 `transferor=企业名`（不要传 transferee，也没有 dealType 可用）。**若要按 License-in/License-out/并购/合作开发 分类**：分别用 transferor/transferee 定位企业角色作为方向依据，具体交易性质（并购 vs 合作）需结合返回结果中的描述字段人工判断，不能靠传参过滤。

---

## investEvent — 投融资事件

**用途**：查询企业融资历史。必填：dateFrom、dateTo、pageNo（从0开始）。企业名参数是 **`companyName`**（不是 `company`），且为可选参数（不是必填）。

| 参数 | 说明 | 常用值 |
|------|------|------|
| dateFrom/dateTo | 融资日期范围（必填） | yyyy-MM-dd |
| pageNo | 必填，从0开始 | |
| companyName | 企业名称（可选） | |
| round | 融资轮次 | 种子轮/天使轮/Pre-A轮/A轮/A+轮/…/IPO/增发/战略投资/并购 等（传"A"会模糊匹配到含"A"的轮次如Pre-A、A、A+） |
| isNewDrugCompany | 是否创新药企 | 是/否 |
| registeredType | 资本状态 | 上市公司/非上市公司 |
| registeredCountry | 企业注册国家/地区 | 中国/香港/台湾/澳门 等 |
| companyMarket | 企业上市地 | 上交所/深交所/科创板/北交所/港交所/纽交所/纳斯达克 |
| province | 企业所在地省份 | |
| foundYear | 企业成立年份 | |
| capitalName | 投资机构名称 | |
| amountCNFrom/To | 融资金额范围（万元人民币） | |

---

## medicalMeeting — 医学会议摘要

**用途**：查询 ASCO/ESMO/ASH/AACR/EHA 等会议数据。必填：pageNo（从0开始）。**至少选择一个作为检索条件**：drugName、target、disease、company、abstractId、conference、dateFrom。

| 参数 | 说明 | 常用值 |
|------|------|------|
| drugName | 药品名（模糊匹配） | |
| disease | 疾病（模糊匹配） | |
| target | 靶点（模糊匹配） | |
| company | 研发机构（模糊匹配） | |
| diseaseArea | 疾病领域（模糊匹配） | |
| drugType1/2 | 创新类型/药品类别（模糊匹配） | |
| abstractId | 摘要号（模糊匹配） | |
| conference | 会议名称（模糊匹配，查特定届次建议用"会议名+年份"精确格式，如 "ASCO 2026"） | |
| theme | 主题类型（多值） | 遗传学/靶点·标志物/结构/药物发现/非临床/临床/耐药/技术 等 |
| dateFrom/dateTo | 会议日期范围 | yyyy-MM-dd |
| pageNo | 必填，从0开始 | |

---

## newsSearch — 医药舆情新闻（全文检索）

**用途**：按关键词+实体搜索新闻。**没有 `channel` 参数**，正确的分类过滤字段是 **`primary_type`**（枚举：药品、公司、疾病、人、政策），不做实体标准化、直接精确匹配。以下参数均在 schema 的 required 列表中，调用时须全部显式传值（无需过滤的用 `[]`/`""`）。

| 参数 | 说明 | 常用值 |
|------|------|------|
| query | 全文检索关键词（默认空字符串=不按关键词过滤） | |
| diseases | 疾病列表（会做实体标准化） | [] |
| targets | 靶点列表（会做实体标准化） | [] |
| drugs | 药品列表（会做实体标准化） | [] |
| companies | 公司列表（会做实体标准化） | [] |
| primary_type | 新闻类型（不做实体标准化，直接匹配） | ["药品"]、["公司"]、["疾病"]、["人"]、["政策"]，不限则传 [] |
| published_after/before | 发布时间范围 | 推荐 "2026/05/01" 格式，也兼容 "2026-05-01" |
| max_results | 单次返回上限（1-100，默认10） | 10 |
| offset | 分页偏移（从0开始，无 pageNo 参数） | 0 |
| entity_match_mode | 实体匹配模式 | "any_per_field"（同字段任一命中）/"all_per_field"（同字段全部命中） |

---

## epidemiology — 流行病学数据

**用途**：查询疾病患者人群规模（2018-2030年覆盖，含预测）。必填：pageNo（从0开始）。**至少选择一个作为检索条件**：patientPopulation、disease、targets、area、statisticalDimension。

| 参数 | 说明 | 常用值 |
|------|------|------|
| disease | 疾病名称（模糊匹配） | "肺癌"、"乳腺癌"（注意字段名是 `disease`，不是 `diseaseName`） |
| patientPopulation | 患者人群描述（模糊匹配） | "HER2阳性乳腺癌"、"非小细胞肺癌" |
| area | 地区列表（数组） | ["中国"]、["中国","美国"]，不指定默认查所有地区 |
| statisticalDimension | 统计维度列表（数组） | ["新发病例"]、["患者总数"]、["死亡病例"] |
| targets | 靶点（**竖线分隔的单个字符串**，不是数组） | "EGFR\|ALK" |
| pageNo | 必填，从0开始 | |

**is_real 字段**：标注该条数值是否为实测统计值；is_real=false 表示预测值，报告中需注明"（预测）"。

---

## drugPatent — 药品专利

**用途**：查询专利布局、到期时间。必填：pageNo（从0开始）。**至少选择一个作为检索条件**：drugName、companyName、target、disease、appNumber、pubNumber。**没有 drugUID 参数**——按品种查专利必须用 `drugName`。

| 参数 | 说明 | 常用值 |
|------|------|------|
| drugName | 药品名/管线名 | |
| companyName | 研发机构 | |
| target | 靶点 | |
| disease | 疾病 | |
| diseaseArea | 疾病领域 | |
| moa | 药理类型 | |
| legalStatus | 法律状态（多值） | 失效/授权/申请/待确认 |
| patentAuthority | 专利受理局（多值） | WO/CN/US/EP/JP/GB/KR 等 |
| patentType | 专利类型（竖线分隔字符串） | "化合物\|序列\|组合物\|晶型\|医药用途\|制剂\|制备方法\|给药装置" 等 |
| phase/phaseCN | 全球/中国最高研发阶段（多值） | |
| appNumber | 专利申请号（数组，最多100个） | |
| pubNumber | 专利公开号（数组，最多100个） | |
| expDateFrom/To | 专利到期日期范围 | yyyy-MM-dd |
| pageNo | 必填，从0开始 | |

---

## drugClinicalPaper / drugNonClinicalPaper — 研究论文

**用途**：查询某品种的临床/非临床研究论文。必填：drugUID（**必须来自 drugBaseCN 的 `uid` 字段**）、pageNo（从0开始）。

参数：drugUID（必填，单个字符串，不是列表）、pageNo（必填）

---

## drugDisease — 药品单疾病研发进展

**用途**：查询某品种在某适应症的全球研发进展详情（各地区阶段、开始日期、特殊资格认定等）。必填：drugUIDList（**必须来自 drugBaseCN 的 `uid` 字段**，最多200个）、pageNo（从0开始）。

参数：drugUIDList（必填，数组）、disease（可选，模糊匹配）、diseaseStatus（可选：Active/Unknown/Inactive）、pageNo（必填）

---

## byDrugNews — 按日期查询新闻

**用途**：按发布日期范围批量拉取新闻。必填：startDate、endDate、pageNo（从0开始，每页10条）。
