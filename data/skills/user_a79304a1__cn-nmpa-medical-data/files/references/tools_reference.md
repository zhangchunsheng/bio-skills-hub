# medmcp 工具参考

medmcp 连接器暴露 35 个工具，全部为只读查询。以下为完整参数定义、返回字段与调用示例。

> **响应格式**：所有工具返回 JSON，结构为 `{"data": [...], "count": N, "hint": ""}`（hint 字段保留但为空，便于后续扩展）。医院搜索最多返回 50 条，其余工具最多 20 条。医疗器械三类工具（equipment/productor/seller）亦最多 20 条。

## 1. search_hospitals — 搜索医院

按关键词和/或城市搜索医保定点医院。结果按等级排序（三级 > 二级 > 其他），同级按床位降序，主要医院优先返回。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 医院名称模糊匹配（匹配 medinsName/medinsName2/addr） |
| city | string | 否 | "" | 城市名（如"北京""上海"），模糊匹配 cityName/privence 字段，带不带"市"后缀等价 |
| limit | int | 否 | 20 | 返回条数，1–50 |

**返回**：医院摘要数组，每条字段：

| 字段 | 说明 | 示例 |
|---|---|---|---|---|
| id | 医院记录 ID（数字，get_hospital_detail 用此值） | 96664 |
| code | 机构编码（medinsCode） | "H31010600037" |
| name | 医院名称 | "复旦大学附属华山医院" |
| address | 地址 | "上海市乌鲁木齐中路12号…" |
| province | 省份（privence 字段） | "上海市" |
| city | 城市（cityName 字段） | "上海市" |
| district | 区县 | "静安区" |
| level | 机构类别（medinsLvName） | "综合医院" |
| type | 等级（medinsTypeName） | "三级" / "二级" / "未定级" |
| beds | 床位数（bed_num，可能为 null） | 40 |

示例调用：`search_hospitals(keyword="协和", city="北京")`

## 2. get_hospital_detail — 医院详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| hospital_id | string | 是 | search_hospitals 返回的数字 id（如 "96664"）；也支持 medinsCode/uuid |

**返回**：单条医院完整字段，含 id/name/code/level/type/address/province/city/district/beds/lat/lng/phone 等。空值字段会保留但可能为 null。

## 3. search_pharmacies — 搜索药店

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 药店名称模糊匹配（如"国大药房"） |
| city | string | 否 | "" | 城市/省份名（如"上海""广东"），匹配 privence 与 addr 字段，带不带"市/省"后缀等价 |
| limit | int | 否 | 20 | 返回条数，1–20 |

> 城市过滤时按 privence 精确匹配优先排序：真正的本市药店排前，地址中偶含关键词的外省店排后。

**返回**：药店摘要数组，字段：

| id | 药店记录 ID（get_pharmacy_detail 用此值） | 103667 |
| code | 定点零售药店编码（rtalPhacCode） | "P31010100003" |
| name | 药店名称（medinsName） | "国药控股国大药房上海连锁有限公司龙华东路店" |
| address | 地址（addr） | "龙华东路385号一层102室、103室" |
| phone | 电话（tel） | "13482299173" |
| province | 省份（privence 字段） | "上海市" |
| open_elec | 是否开通医保电子凭证（openElec，0/1） | 1 |
| biz_scope | 经营范围（drugBizScp） | "中成药；化学药制剂；抗生素…" |

## 4. get_pharmacy_detail — 药店详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| pharmacy_id | string | 是 | search_pharmacies 返回的数字 id；也支持 rtalPhacCode/uuid |

**返回**：单条药店完整字段，含 id/name/code/address/phone/province/open_elec/biz_scope/lnt/lat 等。

## 5. search_drugs — 搜索药品

按关键词搜索药品**说明书要点**（匹配药品名/通用名/分类/生产厂家），返回药品列表。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 是 | — | 药品名称关键词（如"布洛芬""阿莫西林"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：药品说明书摘要数组：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 id | "D001" |
| name | 药品名称 | "布洛芬缓释胶囊" |
| generic_name | 通用名 | "布洛芬" |
| category | 分类 | "解热镇痛药" |
| manufacturer | 生产厂家 | "示例制药有限公司" |
| approval_number | 批准文号 | "国药准字H00000001" |
| indications | 适应症 | "缓解轻至中度疼痛如头痛、关节痛…" |
| dosage | 用法用量 | "成人一次1粒，一日2次…" |
| contraindications | 禁忌 | "对布洛芬过敏者禁用；孕妇及哺乳期妇女慎用" |
| side_effects | 不良反应 | "偶见恶心、胃部不适、头晕" |
| price | 价格（当前恒为 null） | null |

> **数据性质**：本工具与 `get_drug_detail` 现返回说明书要点，但**当前底层为示例/种子数据**——manufacturer 均为"示例制药有限公司"、approval_number 为占位号、price 恒为 null，**并非真实生产数据**。调用结果只能作示意，不能用于实际用药决策。字段结构同 §6。

## 6. get_drug_detail — 药品说明书详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| drug_name | string | 是 | 药品名称（**精确匹配**完整品名，如"布洛芬缓释胶囊"；"布洛芬片"等不完整/不匹配名称会返回空） |

**返回**：匹配的药品说明书要点（单条），字段与 `search_drugs` 一致：id/name/generic_name/category/manufacturer/approval_number/indications/dosage/contraindications/side_effects/price。

> 注意：返回的是**说明书要点**（适应症/用法用量/禁忌/不良反应/价格），**非** NMPA 注册基础信息（原剂型/规格/审核日期等字段已不再返回）。数据为示例/种子数据，详见 SKILL.md 数据局限 #1。

## 7. search_doctors — 搜索医生

按姓名/擅长/城市/医院/科室搜索医生（数据源 `hdf_doctor_20250110`，93.7 万条，覆盖全国 31 省级）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 医生姓名 / 擅长疾病 / 医院名（模糊匹配 docname/telents/hosname） |
| city | string | 否 | "" | 省份/城市名（如"上海""北京"），匹配 privence 字段 |
| hospital | string | 否 | "" | 医院名（如"中日医院"），匹配 hosname/hospital 字段 |
| department | string | 否 | "" | 科室名（如"呼吸内科"），匹配 dep1/dep2 字段 |
| limit | int | 否 | 20 | 返回条数，1–20 |

> 排序：主任/副主任医师优先，其次问诊量（wenzhen）降序。
> 姓名/擅长为全表模糊扫描，单次约 1-5 秒，属正常；建议同时传 city/hospital 缩小范围。

**返回**：医生摘要数组，字段：

| id | 医生记录 ID（get_doctor_detail 用此值） | 1 |
| uuid | 记录 UUID（也可用于查详情） | "2290" |
| name | 医生姓名（docname） | "王辰" |
| province / region | 省份 / 地市 | "北京市" / "朝阳" |
| hospital | 医院（hosname） | "中日医院" |
| dep1 / dep2 | 一级 / 二级科室 | "内科" / "呼吸与危重症医学科" |
| title | 职称 | "主任医师" |
| specialty | 擅长（telents） | "肺栓塞，肺动脉高压…" |
| consultations | 问诊量（wenzhen） | 0 |

示例调用：`search_doctors(keyword="肺栓塞", city="北京", limit=20)`

## 8. get_doctor_detail — 医生详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| doctor_id | string | 是 | search_doctors 返回的数字 id 或 uuid |

**返回**：单条医生完整字段，含 id/name/province/region/hospital/dep1/dep2/title/specialty/direction/achievements/social/about/consultations 等。成就/社会任职/简介多为空（数据稀疏）。

## 9. search_doctor_registration — 医师执业注册查询

按姓名/执业机构/执业类别查询医师执业注册信息（数据源 `credit_jdzx_net_cn_doctor`，451.1 万条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| name | string | 否 | "" | 医生姓名（如"王辰"） |
| hospital | string | 否 | "" | 执业机构（医院）名（如"北京大学第一医院"） |
| category | string | 否 | "" | 执业类别（如"临床""中医""口腔""公共卫生"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：执业注册摘要数组，字段：

| doc_id | 医师执业证书编号 | "110110000044387" |
| name | 医生姓名 | "王辰" |
| sex | 性别 | "女" |
| hospital | 执业机构（hos） | "北京大学第一医院" |
| category | 执业类别（type） | "临床" |
| level | 执业级别（type2） | "执业医师" / "执业助理医师" |
| reg_date | 注册日期（reg） | "2019/04/19" |

> 与 `search_doctors` 的区别：本工具是官方执业注册信息（证书编号/机构/类别）；search_doctors 是出诊简介（职称/擅长/科室）。同姓名医生多，建议加 hospital 过滤。注册日期为信用中国快照（多为 2019 年前后），不代表最新执业状态。

## 10. search_drg — DRG 分组标杆查询

查询 DRG 分组标杆数据（数据源 `drg_biaogan_info`，1608 条：CN 国家版 1017 + CHS 591）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| code | string | 否 | "" | DRG 编码，支持前缀模糊（如"OZ"命中 OZ15 等） |
| keyword | string | 否 | "" | DRG 名称关键词（如"妊娠"） |
| drg_type | string | 否 | "" | 分组版本：`CN` 国家版 / `CHS` CHS-DRG（大小写敏感） |
| category | string | 否 | "" | 专业类别（如"骨科专业""产科专业"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：DRG 标杆数组，字段：

| code | DRG 编码 | "OZ15" |
| name | DRG 名称 | "其他与妊娠相关的诊断，不伴合并症与伴随病" |
| type | 版本（CN/CHS） | "CN" |
| category | 专业类别 | "产科专业" |
| weight | 权重（weight） | 0.3 |
| weight_ratio | 权重比（weightRatio） | 0.028 |
| avg_days | 平均住院日（averageTimes） | 4.05 |
| avg_expense | 平均费用（averageExpense，元） | 2679.0 |
| risk_level | 风险等级（fxdj） | "低风险" |
| expense_p50 / expense_p75 | 费用分位数（元） | 2333 / 1797 |
| time_p50 / time_p75 | 住院日分位数（天） | 3.94 / 3.42 |
| low_risk_death_ratio | 低风险死亡率（部分为空） | "" |

示例调用：`search_drg(code="OZ15")` 或 `search_drg(keyword="妊娠", drg_type="CHS")`

## 11. search_icd_diagnosis — 诊断名词 / ICD 编码查询

查询临床医学诊断名词及 ICD 编码映射（数据源 `drg_words_info`，2.2 万条，来源《常用临床医学名词》2019 版等）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 是 | — | 诊断名 / 别名 / ICD 编码 / 英文名关键词（如"糖尿病""E10"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：名词映射数组，字段：

| name | 诊断名词 | "1型糖尿病伴有眼的并发症" |
| name_en | 英文名 | "type 1 diabetes associated with eye complication" |
| alias | 别名 | "" |
| icd_code | ICD 编码 | "E10.300" |
| icd_type | ICD 版本 | "ICD10" |
| icd_name | ICD 字典名 | "国家临床版ICD-10 2.0" |
| department | 关联科室 | "眼科" |
| category | 词典类别 | "疾病诊断名词" |
| label | 词典来源 | "《常用临床医学名词》（2019版）" |

示例调用：`search_icd_diagnosis(keyword="糖尿病")`

## 12. count_hospitals_by_region — 医院区域统计

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| scope | string | 是 | — | "province" 按省统计；"city" 下钻到市级 |
| province | string | scope=city 时必填 | — | 省份简称（如"广东""四川"），无需"省"后缀 |
| limit | int | 否 | 20 | 返回区域数，1–100 |

**返回**：

```json
[{
  "kind": "hospitals",
  "scope": "province",
  "total": 600582,
  "rows": [
    {"region": "河南省", "count": 62819, "percent": 10.46},
    {"region": "山东省", "count": 57271, "percent": 9.54}
  ]
}]
```

底层按 `privence` 字段（省级）或 `cityName`（市级）GROUP BY。

## 13. count_pharmacies_by_region — 药店区域统计

参数同上（scope/province/limit）。

**返回结构同上**，kind 为 "pharmacies"。

底层逻辑（数据源为 `fuwu_nhsa_gov_cn_yibiaoyaodian` 医保药店表，46.2 万行，覆盖全国 31 省级）：
- **按省**：直接按 `privence` 字段 GROUP BY（准确）
- **按市**：取该省 `privence + addr` 在 Python 侧提取城市名——直辖市直接用省名，其他匹配地址中的"XX市"；地址未含市名的记录归并为该省名（数据质量兜底）

示例：`count_pharmacies_by_region(scope="city", province="广东")` → total=36012，广州 6464、深圳 5249、佛山 4205…

## 14. search_equipment — 搜索医疗器械产品

按关键词搜索 NMPA 医疗器械注册/备案信息（数据源 `nmpa_e_equipment_info`，9.6 万条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 产品名/生产企业/管理类别/产品类型/注册证号关键词（如"血糖仪""迈瑞""三类"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：器械产品摘要数组，字段：

| id | 记录 ID（get_equipment_detail 用此值） | 15 |
| uuid | 记录 UUID（也可查详情） | "54523ab5…" |
| code | 注册证编号 / 备案号（code2） | "浙食药监械(准)字2013第240089" |
| company | 注册人 / 生产企业（company） | "艾康生物技术(杭州)有限公司" |
| product | 产品名称（product） | "血糖测试条" |
| category | 管理类别（category，一类/二类/三类） | "第二类" |
| type | 产品类型（type） | "包装：1人份/袋…" |
| compose | 结构及组成（compose） | "每根血糖测试条包含…" |
| useage | 适用范围（useage） | "本测试条与对应的测试仪配套使用…" |
| audit_office | 审批部门（aduit，部分为空） | "" |
| begin_date / end_date | 有效期起 / 止 | "2015.02.13" / "2020.02.12" |

示例调用：`search_equipment(keyword="血糖仪")` / `search_equipment(keyword="三类")`

## 15. get_equipment_detail — 医疗器械详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| equipment_id | string | 是 | search_equipment 返回的数字 id 或 uuid |

**返回**：单条器械完整字段（同 search 字段集，含 compose/useage/有效期等）。

## 16. search_productor — 搜索医疗器械生产企业

按关键词搜索医疗器械生产企业（数据源 `nmpa_e_productor_info`，1.8 万条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 企业名/法人/负责人/住所/生产地址/生产范围/许可证号关键词（如"迈瑞""无菌器械"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：生产企业摘要数组，字段：

| id | 记录 ID（get_productor_detail 用此值） | 1450 |
| uuid | 记录 UUID | "f6b68932…" |
| code | 许可证编号（code2） | "苏食药监械生产许20080046号" |
| name | 企业名称（name） | "南京迈瑞生物医疗电子有限公司" |
| legal_person | 法定代表人（legal_person） | "LI XITING" |
| host_person | 企业负责人（host_person） | "韩乐" |
| address | 住所（address） | "南京市江宁经济技术开发区…" |
| product_address | 生产地址（product_address） | "南京市江宁经济技术开发区…" |
| scope | 生产范围（fanwei） | "III类:01-07手术导航…" |
| license_office | 发证部门（license_office） | "江苏省药品监督管理局" |
| record | 备案/许可证号（record） | "苏食药监械生产许20080046号" |
| begin_date / end_date | 有效期起 / 止 | "2022-02-17" / "2023-04-09" |

示例调用：`search_productor(keyword="迈瑞")`

## 17. get_productor_detail — 生产企业详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| productor_id | string | 是 | search_productor 返回的数字 id 或 uuid |

**返回**：单条生产企业完整字段（同 search 字段集）。

## 18. search_seller — 搜索医疗器械经营企业/销售商

按关键词搜索医疗器械经营企业（数据源 `nmpa_e_seller_info`，28.3 万条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 企业名/法人/负责人/地址/经营方式/经营范围/许可证号关键词（如"九州通""批发""体外诊断试剂"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：经营企业摘要数组，字段：

| id | 记录 ID（get_seller_detail 用此值） | 865 |
| uuid | 记录 UUID | "0dc1c20c…" |
| code | 许可证编号（code2） | "京海食药监械经营许20180099号" |
| name | 企业名称（name） | "北京计尔康爱的阁生殖保健用品配送有限公司" |
| legal_person | 法定代表人（legal_person） | "李光一" |
| host_person | 企业负责人（host_person） | "李光一" |
| address1 / address2 / address3 | 注册/经营/仓库地址 | "北京市朝阳区康家沟145号…" |
| model | 经营方式（model） | "批发" / "零售" / "批零兼营" |
| scope | 经营范围（limited） | "Ⅲ类：6801基础外科手术器械…" |
| license_office | 发证部门（license_office） | "北京市朝阳区市场监督管理局" |
| begin_date / end_date | 有效期起 / 止 | "2022-04-18" / "2023-05-02" |

示例调用：`search_seller(keyword="九州通")` / `search_seller(keyword="批发")`

## 19. get_seller_detail — 经营企业详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| seller_id | string | 是 | search_seller 返回的数字 id 或 uuid |

**返回**：单条经营企业完整字段（同 search 字段集，含地址/经营方式/经营范围/许可证等）。

## 20. search_equipment_import — 搜索进口医疗器械产品

按关键词搜索**进口**医疗器械注册/备案信息（数据源 `nmpa_e_equipment_f_info`，1.9 万条）。与国产基表 `nmpa_e_equipment_info` 字段不兼容，故为独立工具；两者 uuid 重叠为 0（国产 vs 进口互补）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 产品名/注册人/代理人/管理类别/注册证号关键词（如"碎石器""奥林巴斯""三类"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：进口器械产品摘要数组，字段：

| id | 记录 ID（get_equipment_import_detail 用此值） | 2 |
| uuid | 记录 UUID | "a2168973…" |
| code | 注册证编号 / 备案号（code2） | "国械注进20142225238" |
| name | 产品名称（name） | "一次性碎石器ディスポーザブル砕石具" |
| registrant | 注册人名称（reg_name，多为境外企业） | "奥林巴斯医疗株式会社" |
| registrant_address | 注册人住所（reg_address） | "日本国东京都涩谷区…" |
| product_address | 生产地址（product_address） | "日本国青森县黑石市…" |
| agent | 代理人名称（agent_name，进口特有） | "奥林巴斯贸易(上海)有限公司" |
| agent_address | 代理人住所（agent_address） | "中国(上海)自由贸易试验区…" |
| category | 管理类别（type，一类/二类/三类） | "第二类" |
| spec | 规格型号（size） | 0.0 |
| compose | 结构及组成（struct） | "该产品由一次性碎石器和BML手柄组成…" |
| useage | 适用范围（fangwei） | "该产品与奥林巴斯指定内镜配套使用，用于粉碎胆管内结石" |
| store | 储存条件（store） | "" |
| audit_office | 审批部门（audit_office） | "国家食品药品监督管理总局" |
| change | 变更情况（change） | "1. 变更产品技术要求…" |
| begin_date / end_date | 有效期起 / 止 | "2018-05-28" / "2023-05-27" |

示例调用：`search_equipment_import(keyword="碎石器")` / `search_equipment_import(keyword="三类")`

## 21. get_equipment_import_detail — 进口医疗器械详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| equipment_id | string | 是 | search_equipment_import 返回的数字 id 或 uuid |

**返回**：单条进口器械完整字段（同 search 字段集，含注册人/代理人/规格型号/储存条件/变更情况等）。

## 22. search_seller_filed — 搜索备案医疗器械经营企业

按关键词搜索**备案**医疗器械经营企业（数据源 `nmpa_e_seller_b_info`，100.9 万条）。与许可基表 `nmpa_e_seller_info` 同构（16 列相同），故复用同一字段集；两者 uuid 重叠为 0（许可 vs 备案互补）。要查全量经营者需分别调用两套工具。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 企业名/法人/负责人/地址/经营范围/备案号关键词（如"大药房""体外诊断试剂"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：备案经营企业摘要数组，字段（与 search_seller 完全一致）：

| id | 记录 ID（get_seller_filed_detail 用此值） | 1 |
| uuid | 记录 UUID | "3caa8ea8…" |
| code | 备案号（code2） | "皖马食药监械经营备20140017号" |
| name | 企业名称（name） | "马鞍山市川洋大药房连锁有限公司年陡店" |
| legal_person | 法定代表人（legal_person） | "苏锦" |
| host_person | 企业负责人（host_person） | "" |
| address1 / address2 / address3 | 注册/经营/仓库地址 | "马鞍山市…" |
| model | 经营方式（model，备案多为空） | "" |
| scope | 经营范围（limited） | "Ⅱ类6801基础外科器械；6803神经外科手术器械…" |
| license_office | 备案机关（license_office） | "马鞍山市食品药品监督管理局" |
| begin_date / end_date | 有效期起 / 止（备案多为空） | "" / "" |

示例调用：`search_seller_filed(keyword="大药房")` / `search_seller_filed(keyword="体外诊断试剂")`

## 23. get_seller_filed_detail — 备案经营企业详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|
| seller_id | string | 是 | search_seller_filed 返回的数字 id 或 uuid |

**返回**：单条备案经营企业完整字段（同 search 字段集，含地址/经营范围/备案机关等）。

## 24. search_drug_import — 搜索进口药品

按关键词搜索 **NMPA 进口药品注册/备案**信息（数据源 `nmpa_drug_info_f_20240116`，3147 条）。与国产药品基表 `nmpa_drug_info` 字段不同（含境外持有人/生产厂商/本位码），故为独立工具。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 产品名/通用名/商品名/公司/持有人/生产厂商/注册证号/本位码关键词（如"阿司匹林""拜耳"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：进口药品摘要数组，主要字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_drug_import_detail 用此值） | 977 |
| uuid | 记录 UUID | "26d6be87…" |
| code | 进口药品注册证号（code / code_old） | "H20130339" |
| product | 产品名称（product） | "阿司匹林肠溶片" |
| goods | 商品名（goods） | "拜阿司匹灵" |
| holder | 上市许可持有人（holder，多为境外，中文可能为空） | "Bayer Vital GmbH" |
| company | 企业名称（company，可能为空） | "" |
| productor | 生产厂商（productor，多为境外） | "Bayer AG" |
| productor_region | 生产国/地区（productor_region） | "德国" |
| type | 剂型（type） | "片剂" |
| size | 规格（size） | "100mg" |
| package | 包装（package） | "10片，30片/盒" |
| product_category | 药品类别（product_category） | "化学药品" |
| barcode | 本位码（barcode） | "86978271002224" |
| begin_date / end_date | 注册有效期起 / 止 | "2018-11-08" / "2023-11-07" |

示例调用：`search_drug_import(keyword="阿司匹林")` / `search_drug_import(keyword="拜耳")`

## 25. get_drug_import_detail — 进口药品详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| drug_import_id | string | 是 | search_drug_import 返回的数字 id 或 uuid |

**返回**：单条进口药品完整字段（同 search 字段集，含 holder/holder_address/company/address/region/product/productor/productor_address/productor_region/size/package/barcode/product_category/begin_date/end_date 等）。holder/company 中文为空时返回其英文/地址字段（holder_en/company_en/holder_address_en 等）。

## 26. search_pharmacist — 搜索执业药师

按关键词搜索 **执业药师注册**信息（数据源 `nmpa_drug_pharmaceutist_info_20231218`，158 万条；注意真实表名含 "pharmace**ut**ist"，用户 SQL 曾误写为 pharmacist）。实名数据，同名极多。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 姓名/执业单位/省市/注册证号/执业范围/执业类别关键词（如"张""杭州仁泰"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：执业药师摘要数组，字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_pharmacist_detail 用此值） | 8 |
| uuid | 记录 UUID | "7647966b…" |
| code | 注册证编号（code2） | "331216018614" |
| name | 姓名（name） | "张丽娜" |
| province | 省市（privence 字段） | "浙江" |
| category | 执业类别（type，如 中药学/药学） | "中药学" |
| scope | 执业范围（fanwei） | "零售" |
| company | 执业单位（company） | "杭州仁泰医药连锁有限公司" |
| end_date | 注册有效期（end_date） | "2019-10-08" |

> 同姓名药师极多（如"张丽"在库内有多条），搜索建议同时传省市/执业单位缩小范围。示例调用：`search_pharmacist(keyword="张")` / `search_pharmacist(keyword="九州通")`

## 27. get_pharmacist_detail — 执业药师详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pharmacist_id | string | 是 | search_pharmacist 返回的数字 id 或 uuid |

**返回**：单条执业药师完整字段（同 search 字段集，含 code/name/province/category/scope/company/end_date）。

## 28. search_drug_productor — 搜索药品生产企业

按关键词搜索 **药品（非医疗器械）生产企业**（数据源 `nmpa_drug_productor_info`，8820 条；注意与服务端 `nmpa_e_productor_info` 医疗器械生产企业是不同数据域）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 企业名/法定代表人/企业负责人/住所/生产地址/生产范围/许可证号关键词（如"国药""中药配方颗粒"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：药品生产企业摘要数组，字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_drug_productor_detail 用此值） | 310 |
| uuid | 记录 UUID | "2a1468d6…" |
| code | 许可证编号（code2） | "川20170465" |
| name | 企业名称（name） | "四川国药天江药业有限公司" |
| province | 省份（province） | "四川省" |
| id_code | 统一社会信用代码（id_code） | "91511900MA62D5RP00" |
| category | 分类（category） | "Ay" |
| legal_person | 法定代表人（legal_person） | "黄吉东" |
| address | 住所（address） | "巴中市巴州区…" |
| scope | 生产范围（scope） | "颗粒剂(中药配方颗粒)…" |
| license_office | 发证机关（license_office） | "四川省药品监督管理局" |
| begin_date / end_date | 有效期起 / 止 | "2022-04-21" / "2022-11-20" |

示例调用：`search_drug_productor(keyword="国药")` / `search_drug_productor(keyword="颗粒剂")`

## 29. get_drug_productor_detail — 药品生产企业详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| drug_productor_id | string | 是 | search_drug_productor 返回的数字 id 或 uuid |

**返回**：单条药品生产企业完整字段（同 search 字段集，含 code/name/province/id_code/category/legal_person/company_person/qa_person/address/scope/address2/audit_office/audit_phone/license_office/license_person/begin_date/end_date/comments）。

## 30. search_drug_nation — 搜索国家基本药物

按关键词搜索 **国家基本药物目录**（数据源 `nmpa_drug_nation_info`，685 条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 通用名/英文名/分类关键词（如"阿莫西林""青霉素"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：国家基本药物摘要数组，字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_drug_nation_detail 用此值） | 6 |
| uuid | 记录 UUID | "a70d9918…" |
| code | 代码/通用名（code） | "阿莫西林" |
| name | 名称（name） | "阿莫西林" |
| name_en | 英文名（name_en） | "Amoxicillin" |
| category1 | 一级分类（category1） | "化学药品和生物制品" |
| category2 | 二级分类（category2） | "抗微生物药" |
| category3 | 三级分类（category3） | "青霉素类" |
| size | 剂型规格（size） | "片剂、胶囊、颗粒剂…" |

示例调用：`search_drug_nation(keyword="阿莫西林")` / `search_drug_nation(keyword="青霉素")`

## 31. get_drug_nation_detail — 国家基本药物详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| drug_nation_id | string | 是 | search_drug_nation 返回的数字 id 或 uuid |

**返回**：单条国家基本药物完整字段（同 search 字段集，含 code/name/name_en/category1/category2/category3/size/remark）。

## 32. search_yibao_drug — 搜索医保药品目录

按关键词搜索 **医保报销药品目录**（数据源 `bmfw_www_gov_cn_yibaodrug`，4545 条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 药品名称/类别/报销类别关键词（如"布洛芬""西药""甲"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：医保药品摘要数组，字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_yibao_drug_detail 用此值） | 1293 |
| uuid | 记录 UUID | "30112c20…" |
| code | 序号/编码（code） | "5368" |
| drug_type | 药品类型（drug_type，1/2…） | "1" |
| drug_type_name | 药品类型名称（drug_type_name） | "西药" |
| medicine_name | 药品名称（medicine_name） | "布洛芬" |
| medicament_type | 剂型（medicament_type） | "口服常释剂型" |
| category1 | 一级分类（category1） | "肌肉-骨骼系统药物" |
| category2 | 二级分类（category2） | "抗炎和抗风湿药" |
| reimbur_type | 报销类别（reimbur_type，甲/乙） | "甲" |

示例调用：`search_yibao_drug(keyword="布洛芬")` / `search_yibao_drug(keyword="甲")`

## 33. get_yibao_drug_detail — 医保药品详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| yibao_drug_id | string | 是 | search_yibao_drug 返回的数字 id 或 uuid |

**返回**：单条医保药品完整字段（同 search 字段集，含 code/drug_type/drug_type_name/medicine_name/paystandard/medicament_type/category1/category2/reimbur_type/remark）。

## 34. search_medical_supplies — 搜索医用耗材

按关键词搜索 **医保医用耗材**（数据源 `fuwu_nhsa_gov_cn_medical_supplies`，7.8 万条）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| keyword | string | 否 | "" | 耗材名称/通用名/材质/分类/生产企业关键词（如"支架""椎体成形""聚合物"） |
| limit | int | 否 | 20 | 返回条数，1–20 |

**返回**：医用耗材摘要数组，字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| id | 记录 ID（get_medical_supplies_detail 用此值） | 1484 |
| uuid | 记录 UUID | "a2191d4c…" |
| code | 医保耗材编码（code） | "C0331151010200006388" |
| name | 耗材名称（name） | "椎体成形工具" |
| generic_name | 通用名（generic_name） | "椎体成形工具" |
| material | 材质（material，可能为空） | "聚合物" |
| spec | 规格（spec） | "常规" |
| category1 | 一级分类（category1） | "骨科材料" |
| category2 | 二级分类（category2） | "椎体成形系统" |
| category3 | 三级分类（category3） | "支架充盈系统" |
| producer | 生产企业（producer，可能为空） | "上海三友医疗器械股份有限公司" |

示例调用：`search_medical_supplies(keyword="支架")` / `search_medical_supplies(keyword="骨科")`

## 35. get_medical_supplies_detail — 医用耗材详情

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| medical_supplies_id | string | 是 | search_medical_supplies 返回的数字 id 或 uuid |

**返回**：单条医用耗材完整字段（同 search 字段集，含 code/name/generic_name/material/spec/category1/category2/category3/producer）。
