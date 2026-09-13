---
name: 医疗数据查询
description: "医疗数据查询 Skill。驱动 medmcp MCP 连接器查询中国医疗数据资源：医院、药店、药品（说明书要点）、医生简介、医师执业注册、DRG 分组标杆、ICD 诊断名词、医疗器械（国产注册/备案、进口、生产企业、经营企业/备案）、进口药品、执业药师、药品生产企业、国家基本药物、医保药品目录、医用耗材及区域分布统计。适用场景：按城市/关键词找医院或药店并看详情（查医院/药店）；按药品名查说明书要点（适应症/用法用量/禁忌/不良反应，当前为示例数据）；按姓名/擅长/医院/科室搜医生并看简介（查医生/擅长/出诊）；查医师执业注册（证书编号/机构/类别）；查 DRG 权重/费用/住院日、诊断名词查 ICD 编码；查医疗器械产品/生产/经营企业及进口器械（查医疗器械/血糖仪/迈瑞/九州通/奥林巴斯）；查进口药品持有人与厂商、执业药师注册、药品生产企业、国家基本药物、医保报销类别、医用耗材材质规格；按省/市统计医院/药店数量及分布（含省→市下钻）。使用前需在连接器管理页启用 medmcp 连接器。"
agent_created: true
---

# 医疗数据查询（medmcp）

## Overview

This skill provides procedural knowledge for using the **medmcp** MCP connector, which exposes 35 tools backed by the nmpa medical database (~600k hospitals, ~462k pharmacies, ~937k doctors, ~4.5M physician registrations, 1.6k DRG benchmarks, 22k ICD diagnosis terms, ~157k NMPA drugs, ~113k domestic medical devices, ~17k imported medical devices, ~18k device producers, ~452k licensed device sellers, ~1.0M filed device sellers, 3.1k imported drugs, ~1.58M licensed pharmacists, 8.8k drug production enterprises, 685 national essential drugs, 4.5k medical-insurance drugs, ~78k medical consumables). 药品类工具（`search_drugs` / `get_drug_detail`）现已切换为返回**药品说明书要点**（适应症/用法用量/禁忌/不良反应/价格），但当前底层为示例/种子数据，并非真实生产数据——详见"已知数据局限 #1"。It covers when to use each tool, how to map natural-language requests to tool calls, how to interpret results, and the known data limitations.

## 前置条件

1. **medmcp 连接器必须已启用**。若未启用，引导用户前往"连接器管理 → 自定义连接器"，找到 `medmcp`，点击"信任"。连接器在线（server 运行中）工具才能调用成功。
2. 该连接器默认对接 medmcp server（HTTP streamable 传输）。连接器配置地址为 **`https://mcp.zhifeitech.com`**（MCP 客户端会自动补默认端点路径 `/mcp`；公网 443 经 nginx/反代 HTTPS 转发到后端 4998）。手动验证/直连时用完整端点 **`https://mcp.zhifeitech.com/mcp`**；若服务器未配置 443 反代、仅直连，则改用 `http://<服务器IP>:4998/mcp`。
3. **连接器工具不可用时可通过 MCP 协议直连验证**：POST `initialize` → `notifications/initialized` → `tools/call` 到 `https://mcp.zhifeitech.com/mcp`，请求头需含 `Accept: application/json, text/event-stream` 与响应返回的 `mcp-session-id`。响应为 SSE 流（`data: ` 行），工具返回的 JSON 字符串在 `result.structuredContent.result` 中，需二次 `json.loads`。

## 工具选择决策表

将用户意图映射到工具，避免选错：

| 用户意图 | 调用工具 | 关键参数 |
|---|---|---|
| 按城市/关键词找医院 | `search_hospitals` | keyword, city, limit |
| 看某家医院详情 | `get_hospital_detail` | hospital_id |
| 按城市/关键词找药店 | `search_pharmacies` | keyword, city, limit |
| 看某家药店详情 | `get_pharmacy_detail` | pharmacy_id |
| 搜药品（说明书要点：适应症/用法/禁忌/不良反应） | `search_drugs` | keyword, limit |
| 看某药品说明书详情（精确匹配完整品名） | `get_drug_detail` | drug_name |
| 按姓名/擅长/医院/科室找医生 | `search_doctors` | keyword, city, hospital, department, limit |
| 看某医生完整简介（擅长/成就/简介） | `get_doctor_detail` | doctor_id |
| 查医师执业注册（证书编号/机构/类别） | `search_doctor_registration` | name, hospital, category, limit |
| 查 DRG 分组标杆（权重/费用/住院日） | `search_drg` | code, keyword, drg_type, category, limit |
| 诊断名词查 ICD 编码 | `search_icd_diagnosis` | keyword, limit |
| 统计各省医院数量 | `count_hospitals_by_region` | scope=province, limit |
| 下钻某省各市医院数量 | `count_hospitals_by_region` | scope=city, province, limit |
| 统计各省药店数量 | `count_pharmacies_by_region` | scope=province, limit |
| 下钻某省各市药店数量 | `count_pharmacies_by_region` | scope=city, province, limit |
| 搜医疗器械产品（名称/企业/类别/注册证号） | `search_equipment` | keyword, limit |
| 看某医疗器械详情 | `get_equipment_detail` | equipment_id |
| 搜医疗器械生产企业（名称/法人/范围/许可证） | `search_productor` | keyword, limit |
| 看某生产企业详情 | `get_productor_detail` | productor_id |
| 搜医疗器械经营企业/销售商 | `search_seller` | keyword, limit |
| 看某经营企业详情 | `get_seller_detail` | seller_id |
| 搜进口医疗器械（注册人/代理人/境外厂） | `search_equipment_import` | keyword, limit |
| 看某进口医疗器械详情 | `get_equipment_import_detail` | equipment_id |
| 搜备案医疗器械经营企业 | `search_seller_filed` | keyword, limit |
| 看某备案经营企业详情 | `get_seller_filed_detail` | seller_id |
| 搜进口药品（产品名/注册证号/持有人/厂商） | `search_drug_import` | keyword, limit |
| 看某进口药品详情 | `get_drug_import_detail` | drug_import_id |
| 搜执业药师（姓名/单位/省市/范围/类别） | `search_pharmacist` | keyword, limit |
| 看某执业药师详情 | `get_pharmacist_detail` | pharmacist_id |
| 搜药品生产企业（名称/法人/范围） | `search_drug_productor` | keyword, limit |
| 看某企业详情 | `get_drug_productor_detail` | drug_productor_id |
| 搜国家基本药物（通用名/分类） | `search_drug_nation` | keyword, limit |
| 看某基药详情 | `get_drug_nation_detail` | drug_nation_id |
| 搜医保药品目录（药名/类别/报销类别） | `search_yibao_drug` | keyword, limit |
| 看某医保药品详情 | `get_yibao_drug_detail` | yibao_drug_id |
| 搜医用耗材（名称/材质/分类/企业） | `search_medical_supplies` | keyword, limit |
| 看某耗材详情 | `get_medical_supplies_detail` | medical_supplies_id |

完整参数定义、返回字段与调用示例见 `references/tools_reference.md`。

## 执行规范

1. **参数默认值**：用户未指定 limit 时，搜索类工具默认取 20（医院搜索上限 50，其余上限 20），统计类默认取 20（最多 100）。
2. **两步模式**：搜索返回的是摘要列表；要完整字段必须用对应 `get_*_detail` 二次查询。用户问"XX医院怎么样"时，先 search 拿到 id，再 get_detail 取详情。**注意 `get_hospital_detail` 的参数是 `hospital_id`（search 返回的数字 id），不是医院名称**。
3. **药品名称匹配（说明书要点）**：`search_drugs` / `get_drug_detail` 现返回**药品说明书要点**（适应症 indications / 用法用量 dosage / 禁忌 contraindications / 不良反应 side_effects / 价格 price），数据来自说明书库而非原 NMPA 注册基础表。`get_drug_detail` 的 `drug_name` 为**精确匹配**（如"布洛芬缓释胶囊"能命中、"布洛芬片"返回空），需用户提供完整品名；`search_drugs` 的 keyword 为模糊匹配，可按通用名检索返回列表。**重要：当前说明书数据为示例/种子数据**（生产厂家均为"示例制药有限公司"、批准文号为占位号、price 恒为 null），并非真实生产数据，回答时须明确告知用户"以下为示意数据，不可作为用药依据"。
4. **统计下钻一致性**：scope=city 时必须传 province；省份名用简称（如"广东""四川"），无需带"省/市"后缀。下钻结果的 total 应与省级统计中该省的 count 一致，可用于校验。**注意：统计工具返回结构为 `{data: [{kind, scope, total, rows}], count: 1, hint}`，统计数据嵌套在 `data[0]` 中**。
5. **城市名等价性**：`search_hospitals` 的 city 参数为模糊匹配（`LIKE '%city%'`），"上海"与"上海市"、"北京"与"北京市"等价，无需带后缀。`search_doctors` 的 city 同理匹配省份字段，也支持"广东"等省名。
6. **医生搜索字段**：`search_doctors` 的 keyword 同时匹配姓名/擅长/医院名（如"肺栓塞"能搜到擅长该病的医生）；排序为主任/副主任医师优先、问诊量降序。`get_doctor_detail` 参数是 `doctor_id`（search 返回的数字 id 或 uuid），不是姓名。
7. **执业注册与医生简介是两类数据**：`search_doctor_registration`（credit_jdzx，451 万条）返回执业证书编号/执业机构/类别/注册日期，是官方注册信息；`search_doctors`（hdf_doctor，93.7 万条）返回职称/擅长/科室等出诊简介。查"某医生有没有执业资格/在哪个机构执业"用前者，查"某医生擅长什么/哪个科室"用后者。
8. **DRG 版本**：`search_drg` 的 drg_type 只接受 `CN`（国家版）或 `CHS`（CHS-DRG），大小写敏感；不传则返回全部版本。code 支持前缀模糊（如 `OZ` 命中 OZ15 等）。
9. **结果呈现**：搜索结果以表格或列表呈现关键字段；统计结果按数量降序列出并附占比；详情结果逐字段列出，跳过空值字段。

## 已知数据局限（务必向用户说明）

1. **药品说明书为示例数据（已纠正旧版"无说明书"局限）**：`search_drugs` / `get_drug_detail` 现已接入药品说明书库，返回 适应症/用法用量/禁忌/不良反应/价格 等要点；但**当前底层为示例/种子数据**（生产厂家均为"示例制药有限公司"、批准文号为占位号如 `国药准字H00000001`、price 恒为 null），并非真实 NMPA 注册或生产数据。**严禁将此类数据当作权威用药依据**，正式回答须标注"以下为示意数据"。原 NMPA 注册基础字段（剂型、规格、审核日期等）已不再由药品工具返回。
2. **医院经纬度脏数据**：hospital 表的 lnt/lat 部分值格式异常（如 `"116.367587;1"`），直接用于地图标注前需清洗。
3. **历史快照表**：底层数据库存在多个日期版本的同名表（如 `nmpa_drug_info_20240116`）。当前 .env 指向的是主表；如数据明显滞后，可建议切换到更新版本快照表（修改 `MYSQL_TABLE_DRUGS` 等环境变量）。
4. **药店区域字段**：药店表（`fuwu_nhsa_gov_cn_yibiaoyaodian`）有独立的 `privence` 省份字段，按省统计直接精确分组；按市统计从地址中提取"XX市"（直辖市直接用省名），地址未含市名的记录归并为该省名。
5. **数据覆盖范围**：医院与药店均为医保定点机构数据，不含未纳入医保的民营/非定点机构。药店表覆盖全国 31 省级（共 46.2 万家，上海 1555 家、北京 730 家、广东 36012 家）；**此前误用 19.4 万行的旧表 `fuwu_nhsa_gov_cn_med_ins_org_pharmacy` 导致上海/北京/广东等省为 0，2026-08-21 已切换为完整表**，旧表字段（hisCode/hisName/contactAddress/areaName 等）已废弃勿再用。**若线上查询上海等省药店为空或报 `Unknown column 'rtalPhacCode'/'privence'`，说明服务器 .env 的 `MYSQL_TABLE_PHARMACIES` 仍是旧表名，需改为 `fuwu_nhsa_gov_cn_yibiaoyaodian` 并重启服务**（deploy.bat 对已存在的 .env 会跳过更新，需手动改）。药品为 NMPA 注册基础信息（9.2 万条）。
6. **医院 cityName 字段脏数据**：部分记录的 cityName 与实际所在地不符（如"绍兴上虞复大口腔医院"cityName 记为"杭州市"）。按城市搜索时结果可能混入周边城市机构，需结合 address/province 字段人工核验。
7. **服务端排序改进待部署**：2026-08-20 已修改 `mysql_provider.py` 的 search_hospitals 排序（三级>二级>其他、同级按床位降序），避免按城市搜索时返回的全是 id 靠前的村卫生室。若线上仍出现旧排序（基层机构优先），说明云端服务器尚未重新部署本地代码。
8. **医生姓名重名**：hdf_doctor（93.7 万条）与 credit_jdzx（451 万条）均为实名数据，同姓名医生极多（如"王辰"在两个库各有 3+ 条），必须结合医院/科室/执业机构字段区分；搜索时建议同时传 hospital/city 缩小范围。医生姓名/擅长搜索在 93 万行上为全表扫描，单次约 1-5 秒，属正常。
9. **执业注册数据时效**：credit_jdzx 医师执业注册的注册日期（reg）集中为 2019 年前后，为信用中国某时段快照，不代表最新执业状态；官方最新信息以国家卫健委医师电子化注册系统为准。
10. **DRG 数据量有限**：drg_biaogan_info 仅 1608 条（CN 1017 + CHS 591），覆盖常见专业（普通外科/骨科/心内等）；未覆盖的 DRG 编码查询会返回空。临床名词 drg_words_info（2.2 万条）来自《常用临床医学名词》（2019 版）等词典，非全量 ICD-10 字典。
11. **医疗器械三类表（2026-08-24 新增）**：`nmpa_e_equipment_info`（9.6 万，国产注册/备案产品）、`nmpa_e_productor_info`（1.8 万，生产企业）、`nmpa_e_seller_info`（28.3 万，许可经营企业）均为 NMPA 政务抓取快照，字段含注册证号/企业名/法人/经营范围/有效期等，但**无说明书文本、无实时变更**（有效期字段为快照时点）。nmpa 库另有带日期后缀的快照表（如 `nmpa_e_seller_info_20250715`、`nmpa_e_equipment_info_20240116`），若需更新数据可在 `.env` 用 `MYSQL_TABLE_EQUIPMENT/PRODUCTOR/SELLER` 指向更新快照。器械查询均为 id 排序全表扫描，单次约 1-3 秒属正常。
12. **医疗器械补充表（与基表互斥互补，2026-08-24 新增）**：`nmpa_e_equipment_f_info`（1.9 万，**进口**医疗器械，23 列，含注册人/代理人/境外生产地址/规格型号/储存条件/变更情况，与国产基表字段不兼容，单独工具 `search_equipment_import`/`get_equipment_import_detail`）+ `nmpa_e_seller_b_info`（100.9 万，医疗器械**备案**经营企业，16 列，与许可基表 `nmpa_e_seller_info` 同构，单独工具 `search_seller_filed`/`get_seller_filed_detail`）。三对基表/补充表 uuid 重叠均为 0：**国产 vs 进口**、**许可 vs 备案**各覆盖一半，要查全量医疗器械/经营者需分别调用两套工具（如进口器械只搜 `search_equipment_import`，国内备案经营企业只搜 `search_seller_filed`）。
13. **药品补充域（2026-08-24 新增 6 个工具）**：进口药品（`nmpa_drug_info_f_20240116`，3147 条）、执业药师（`nmpa_drug_pharmaceutist_info_20231218`，158 万条）、药品生产企业（`nmpa_drug_productor_info`，8820 条）、国家基本药物（`nmpa_drug_nation_info`，685 条）、医保药品目录（`bmfw_www_gov_cn_yibaodrug`，4545 条）、医用耗材（`fuwu_nhsa_gov_cn_medical_supplies`，7.8 万条）。其中**执业药师为实名数据、同名极多**（如"张丽"在库内有多条），搜索建议加省市/执业单位缩小范围；医用耗材的 `producer`（生产企业）与 `material`（材质）字段可为空，查询时需注意。这些表与器械类表（nmpa_e_*）是不同数据域，请勿混用。
14. **"线上查不到数据"几乎都是部署/连通问题，不是数据缺失**：底层数据库（nmpa）数据是齐全的——例如搜"九州通"在医疗器械经营许可表（`nmpa_e_seller_info`）与备案表（`nmpa_e_seller_b_info`）中各返回 100+ 条，且存在"九州通医疗器械集团有限公司"等实体。skill 中凡提到"线上为空 / 报 Unknown column / 排序仍是旧的"，都指向**云端 medmcp 服务（mcp.zhifeitech.com）未重新部署本地最新代码，或云端 .env 的 `MYSQL_TABLE_*` 仍指向旧表名**，并非数据不存在。本地代码已验证可用（35 工具、`create_server()` 实枚举通过、各表真实库均返回数据）。排查顺序：① 确认连接器已信任且服务在线——`curl -m 10 https://mcp.zhifeitech.com/mcp` 应返回 HTTP 状态码（如 400 属正常，表示 DNS 已解析、服务存活），而非"Could not resolve host / 超时"；② 确认云端已跑最新代码（新 6 工具是否出现在连接器工具列表）；③ 确认云端 .env 已把 `MYSQL_TABLE_DRUGS/EQUIPMENT/SELLER` 切到日期快照并补上 6 个新表映射（drug_import/pharmacist/drug_productor/drug_nation/yibao_drug/medical_supplies）；④ 重启云端服务使 .env 与代码生效（deploy.bat 对已存在的 .env 会跳过覆盖，需手动改云端 .env）。

## 常见请求映射示例

**医院 / 药店**
- "北京有哪些三甲医院" → `search_hospitals(keyword="", city="北京")`，再按等级字段过滤"三级"
- "上海主要医院" → `search_hospitals(city="上海", limit=50)`（新排序下三级医院优先返回）
- "这家医院有多少科室和床位" → `get_hospital_detail(hospital_id="<search 返回的 id>")`
- "国大药房在沈阳有几家" → `search_pharmacies(keyword="国大药房", city="沈阳")`
- "这家药店能刷医保电子凭证吗" → `get_pharmacy_detail(pharmacy_id="<search 返回的 id>")`

**药品（说明书要点 = 示例数据，见局限 #1）**
- "布洛芬缓释胶囊的适应症和用法用量" → `get_drug_detail(drug_name="布洛芬缓释胶囊")`（精确匹配完整品名，如"布洛芬片"反而不命中）
- "布洛芬类药品有哪些" → `search_drugs(keyword="布洛芬")`（模糊匹配通用名，返回列表）

**医生 / 执业注册**
- "北京擅长肺栓塞的主任医师" → `search_doctors(keyword="肺栓塞", city="北京", limit=20)`（高级职称自动优先）
- "这位医生的擅长和简介" → `get_doctor_detail(doctor_id="<search 返回的 id 或 uuid>")`
- "王辰医生在哪个医院执业" → `search_doctor_registration(name="王辰")`（可加 hospital 缩小范围）

**DRG / ICD**
- "OZ15 这个 DRG 组的平均费用和权重" → `search_drg(code="OZ15")`
- "糖尿病的 ICD 编码是什么" → `search_icd_diagnosis(keyword="糖尿病")`

**区域统计**
- "全国药店最多的省是哪些" → `count_pharmacies_by_region(scope="province")`
- "广东省各市医院分布" → `count_hospitals_by_region(scope="city", province="广东")`

**医疗器械（国产 / 进口 / 生产 / 经营 / 备案）**
- "血糖仪有哪些注册产品" → `search_equipment(keyword="血糖仪")`
- "这个血糖仪产品的适用范围和结构组成" → `get_equipment_detail(equipment_id="<search 返回的 id 或 uuid>")`
- "迈瑞生产哪些医疗器械" → `search_productor(keyword="迈瑞")`
- "这家器械企业详情" → `get_productor_detail(productor_id="<search 返回的 id 或 uuid>")`
- "九州通是不是医疗器械经营公司" → `search_seller(keyword="九州通")`
- "某经营企业许可证范围" → `get_seller_detail(seller_id="<search 返回的 id 或 uuid>")`
- "奥林巴斯进口的碎石器注册信息" → `search_equipment_import(keyword="碎石器")`（进口器械，含注册人/代理人）
- "这个进口器械的注册人和代理人" → `get_equipment_import_detail(equipment_id="<search 返回的 id 或 uuid>")`
- "某备案医疗器械经营店经营范围" → `search_seller_filed(keyword="大药房")`（备案经营者，100 万+ 条）
- "这个备案经营店的备案机关" → `get_seller_filed_detail(seller_id="<search 返回的 id 或 uuid>")`

**药品补充域（进口药 / 执业药师 / 药品生产 / 基药 / 医保 / 耗材，2026-08-24 新增）**
- "进口阿司匹林在国内的持有人和生产厂商" → `search_drug_import(keyword="阿司匹林")`
- "某进口药品的注册证号和有效期" → `get_drug_import_detail(drug_import_id="<search 返回的 id 或 uuid>")`
- "张伟是执业药师吗，在哪执业" → `search_pharmacist(keyword="张伟")`（实名库同名极多，建议加省份缩小范围）
- "某执业药师的注册证号和执业范围" → `get_pharmacist_detail(pharmacist_id="<search 返回的 id 或 uuid>")`
- "国药集团生产哪些药品" → `search_drug_productor(keyword="国药集团")`
- "某药品生产企业的生产范围" → `get_drug_productor_detail(drug_productor_id="<search 返回的 id 或 uuid>")`
- "阿莫西林是不是国家基本药物" → `search_drug_nation(keyword="阿莫西林")`
- "某基药的剂型和备注" → `get_drug_nation_detail(drug_nation_id="<search 返回的 id 或 uuid>")`
- "布洛芬在医保目录里吗，甲类还是乙类" → `search_yibao_drug(keyword="布洛芬")`
- "某医保药品的支付标准和报销类别" → `get_yibao_drug_detail(yibao_drug_id="<search 返回的 id 或 uuid>")`
- "冠脉支架是什么耗材，什么材质" → `search_medical_supplies(keyword="冠脉支架")`
- "某耗材的材质和规格" → `get_medical_supplies_detail(medical_supplies_id="<search 返回的 id 或 uuid>")`

## 数据表 / SQL 接口差异（已分析）

用户侧存在一套更完整的 SQL 接口定义（共 **31 张去重表**，覆盖医院/药店/药品/医生/DRG/ICD/医疗器械/集采/医保/耗材/台湾/微信等约 14 个主题）。经与服务端权威源码（`mysql_provider.py` 的 `_tables` + `config.py` 默认值）逐表核对：

- 当前服务端**实际暴露 18 个逻辑表 / 35 个工具**（2026-08-24 在原有 12 逻辑表/23 工具基础上新增 6 个药品补充域：进口药品/执业药师/药品生产企业/国家基本药物/医保药品目录/医用耗材）。
- **8 张"同域但表名/日期不一致"表的对齐结论**：4 张已通过 `.env` 的 `MYSQL_TABLE_*` 切到 SQL 同名快照（`drugs`→`nmpa_drug_info_20240116`、`equipment`→`nmpa_e_equipment_info_20240116`、`seller`→`nmpa_e_seller_info_20240116`、`equipment_import`→`nmpa_e_equipment_info_f_20240116`）；3 张**有意未切换**——`hospital` 裸名与服务端 `fuwu_nhsa_gov_cn_hospital_20230814` 字段结构完全不同、带日期后缀的 `nmpa_e_productor_info_20240116` 与基表列不兼容（productor 仍用基表）、`nmpa_drug_seller_info_20240116` **在库中不存在**（药店仍用 `fuwu_nhsa_gov_cn_yibiaoyaodian`）。
- **用户 SQL 自身两处问题**（已实现时暴露）：① `nmpa_drug_pharmacist_info_20231218` 拼写错误，**真实表名为 `nmpa_drug_pharmaceutist_info_20231218`**（含 "pharmace**ut**ist"），已按真实表名实现；② 文末 `weixin_mp_article` 两条 SELECT 拼接的语法错误；③ `drg_biaogan_info` 详情 SQL 中 `quantile_time_75` 注释误写为"70分位"。
- 关键同名不同源：`nmpa_drug_seller_info_*`（NMPA 经营药店，且库里并不存在）与服务端 `fuwu_nhsa_gov_cn_yibiaoyaodian`（医保定点药店）是**不同数据源**。
- 废弃表 `fuwu_nhsa_gov_cn_med_ins_org_pharmacy` 已在 2026-08-21 切换为 `fuwu_nhsa_gov_cn_yibiaoyaodian`，SQL 中勿再引用。

完整逐表对照表、差异汇总与新增工具优先级建议见 `references/sql_table_diff.md`（处理"覆盖度/表名对齐/功能缺口"问题时加载）。该文档已同步更新为 2026-08-24 实现后的状态。

## Resources

### references/
- `tools_reference.md` — 35 个工具的完整参数定义、返回字段清单与调用示例，处理具体调用细节时加载。
- `sql_table_diff.md` — 用户 SQL 接口（31 张表）与服务端实际暴露表（18 逻辑表/35 工具）的逐表对照、差异汇总与功能缺口规划。
