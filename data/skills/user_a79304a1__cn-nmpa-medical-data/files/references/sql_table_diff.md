# medmcp 数据表 / SQL 接口差异分析

> 分析依据：服务端权威源码 `src/medmcp/data/mysql_provider.py`（`_tables` 映射）与
> `src/medmcp/config.py`（默认表名）；SQL 语句来自用户提供的接口定义。
> 生成时间：2026-08-25。

## 结论速览

- 用户 SQL 接口共涉及 **31 张去重表**（跨 医院 / 药店 / 药品 / 医生 / DRG / ICD /
  医疗器械 / 集采 / 医保 / 耗材 / 台湾 / 微信 等约 14 个主题）。
- 当前 medmcp 服务端**实际暴露 18 个逻辑表、35 个工具**（2026-08-24 在原有 12 逻辑表/23 工具基础上，新增 6 个药品补充域：进口药品/执业药师/药品生产企业/国家基本药物/医保药品目录/医用耗材）。
- 31 张 SQL 表中：
  - **8 张**对应已实现的域（已通过 `.env` 的 `MYSQL_TABLE_*` 对齐到 SQL 同名快照，或确认有意不切换——详见第 3 节）；
  - **17 张**完全未被任何工具暴露（缺口，较原分析减少 6 张因本轮已实现）。
- 另有一处 SQL 语法错误（文末 `weixin_mp_article` 连续两条 SELECT 拼接，无法执行）。

---

## 1. 当前 medmcp 实际暴露的表（服务端默认值）

| 逻辑键 | 默认表名（config.py / .env） | 对应工具 |
|---|---|---|
| hospitals | `fuwu_nhsa_gov_cn_hospital_20230814` | search_hospitals / get_hospital_detail |
| pharmacies | `fuwu_nhsa_gov_cn_yibiaoyaodian` | search_pharmacies / get_pharmacy_detail |
| drugs | `nmpa_drug_info_20240116` | search_drugs / get_drug_detail |
| doctors | `hdf_doctor_20250110` | search_doctors / get_doctor_detail |
| doctor_registration | `credit_jdzx_net_cn_doctor` | search_doctor_registration |
| drg | `drg_biaogan_info` | search_drg |
| icd | `drg_words_info` | search_icd_diagnosis |
| equipment | `nmpa_e_equipment_info_20240116` | search_equipment / get_equipment_detail |
| productor | `nmpa_e_productor_info` | search_productor / get_productor_detail |
| seller | `nmpa_e_seller_info_20240116` | search_seller / get_seller_detail |
| equipment_import | `nmpa_e_equipment_info_f_20240116` | search_equipment_import / get_equipment_import_detail |
| seller_filed | `nmpa_e_seller_b_info` | search_seller_filed / get_seller_filed_detail |
| drug_import | `nmpa_drug_info_f_20240116` | search_drug_import / get_drug_import_detail |
| pharmacist | `nmpa_drug_pharmaceutist_info_20231218` | search_pharmacist / get_pharmacist_detail |
| drug_productor | `nmpa_drug_productor_info` | search_drug_productor / get_drug_productor_detail |
| drug_nation | `nmpa_drug_nation_info` | search_drug_nation / get_drug_nation_detail |
| yibao_drug | `bmfw_www_gov_cn_yibaodrug` | search_yibao_drug / get_yibao_drug_detail |
| medical_supplies | `fuwu_nhsa_gov_cn_medical_supplies` | search_medical_supplies / get_medical_supplies_detail |

> 表名均可通过 `.env` 的 `MYSQL_TABLE_*` 覆盖为带日期后缀的快照表（如 `nmpa_drug_info_20240116`）。2026-08-24 已将 `drugs`/`equipment`/`seller`/`equipment_import` 默认指向 SQL 同名快照表；`productor`（器械生产）与 `hospital` 因日期后缀表结构不兼容/不同源，仍用基表/专有表。

---

## 2. SQL 语句涉及的 31 张表逐表对照

图例：✅ 域已实现（含工具）｜⚠️ 同域不同源 / 表名或快照不一致｜❌ 未暴露

| # | SQL 表名 | 数据域 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `hospital` | 医院 | ⚠️ | 服务端表名为 `fuwu_nhsa_gov_cn_hospital_20230814`，非裸名 `hospital` |
| 2 | `nmpa_drug_seller_info_20240116` | 药店(NMPA经营) | ⚠️ | 药店域已实现，但服务端用 `fuwu_nhsa_gov_cn_yibiaoyaodian`（医保定点库），**数据源不同** |
| 3 | `hdf_doctor_20170901` | 医生 | ❌ | 旧快照；服务端用 `hdf_doctor_20250110` |
| 4 | `hdf_doctor_20230809` | 医生 | ❌ | 旧快照；服务端用 `hdf_doctor_20250110` |
| 5 | `nmpa_drug_info_20240116` | 药品 | ✅ | 域已实现；2026-08-24 起 `MYSQL_TABLE_DRUGS` 默认指向该快照 |
| 6 | `nmpa_drug_info_f_20240116` | 进口药品 | ✅ | 2026-08-24 新增 `search_drug_import` / `get_drug_import_detail` |
| 7 | `dingdang_20220831_info` | 叮当商品 | ❌ | 电商商品库，未暴露 |
| 8 | `drg_biaogan_info` | DRG 标杆 | ✅ | 精确匹配 `search_drg` 底表 |
| 9 | `drg_words_info` | 临床名词/ICD | ✅ | 精确匹配 `search_icd_diagnosis` 底表 |
| 10 | `nmpa_e_equipment_info_20240116` | 国产器械 | ✅ | 域已实现；2026-08-24 起 `MYSQL_TABLE_EQUIPMENT` 默认指向该快照 |
| 11 | `nmpa_drug_internet_info` | 互联网药品信息 | ❌ | 互联网药品信息服务资格，未暴露 |
| 12 | `nmpa_drug_pharmaceutist_info_20231218` | 执业药师 | ✅ | 2026-08-24 新增 `search_pharmacist`；注意用户 SQL 误写为 `nmpa_drug_pharmacist_info`（缺 "eu"） |
| 13 | `nmpa_drug_productor_info` | 药品生产企业 | ✅ | 2026-08-24 新增 `search_drug_productor`；与器械生产企业 `nmpa_e_productor_info` 是不同域 |
| 14 | `nmpa_drug_clinical_trial_institution_info` | 临床试验机构 | ❌ | 药物临床试验机构，未暴露 |
| 15 | `nmpa_e_equipment_info_f_20240116` | 进口器械 | ✅ | 域已实现；2026-08-24 起 `MYSQL_TABLE_EQUIPMENT_IMPORT` 默认指向该快照 |
| 16 | `nmpa_e_productor_info_20240116` | 器械生产企业 | ⚠️ | 域已实现（基表 `nmpa_e_productor_info`）；日期后缀表列不兼容，**有意不切换** |
| 17 | `pharnexcloud_jicai` | 集采 | ❌ | 药品集中采购，未暴露 |
| 18 | `fuwu_nhsa_gov_cn_medical_supplies` | 医用耗材 | ✅ | 2026-08-24 新增 `search_medical_supplies` / `get_medical_supplies_detail` |
| 19 | `fuwu_nhsa_gov_cn_disease_catalog` | 疾病诊断目录 | ❌ | 医保诊断目录，未暴露 |
| 20 | `fuwu_nhsa_gov_cn_sugical_catalog` | 手术操作目录 | ❌ | 医保手术目录，未暴露 |
| 21 | `fuwu_nhsa_gov_cn_service_facilities` | 诊疗项目 | ❌ | 医疗服务设施/诊疗项目，未暴露 |
| 22 | `fuwu_nhsa_gov_cn_local_optin` | 医保定点机构 | ❌ | 医保定点机构，未暴露 |
| 23 | `nmpa_e_seller_info_20240116` | 器械经营企业 | ✅ | 域已实现；2026-08-24 起 `MYSQL_TABLE_SELLER` 默认指向该快照 |
| 24 | `fuwu_nhsa_gov_cn_med_ins_org` | 医保医疗机构 | ❌ | 定点医疗机构（与 #1 同源不同表），未暴露 |
| 25 | `fuwu_nhsa_gov_cn_med_ins_org_pharmacy` | 医保药店(旧) | ❌ | **已废弃旧表**，服务端 2026-08-21 已切到 `fuwu_nhsa_gov_cn_yibiaoyaodian`；勿用 |
| 26 | `bmfw_www_gov_cn_yibaodrug` | 医保药品目录 | ✅ | 2026-08-24 新增 `search_yibao_drug` / `get_yibao_drug_detail` |
| 27 | `bmfw_www_gov_cn_hesuan` | 核酸检测机构 | ❌ | 核酸采样机构，未暴露 |
| 28 | `nmpa_drug_nation_info` | 国家基本药物 | ✅ | 2026-08-24 新增 `search_drug_nation` / `get_drug_nation_detail` |
| 29 | `ma_mohw_gov_tw_masearch` | 台湾医疗机构 | ❌ | 台湾地区医疗院所，未暴露 |
| 30 | `ma_mohw_gov_tw_phmacy` | 台湾药店 | ❌ | 台湾地区药局，未暴露 |
| 31 | `weixin_mp_article` | 微信文章 | ❌ | 公众号文章；且文末 SQL 存在语法错误（两条 SELECT 拼接） |

---

## 3. 差异汇总

### 3.1 已覆盖域名（8 张同域对齐 + 6 张新增，共 14 张 SQL 表）

| 数据域 | SQL 表（用户） | 服务端实际表（2026-08-24） | 对齐动作 |
|---|---|---|---|
| 医院 | `hospital` | `fuwu_nhsa_gov_cn_hospital_20230814` | **有意不切换**：裸名 `hospital` 字段结构与服务端完全不同 |
| 药店 | `nmpa_drug_seller_info_20240116` | `fuwu_nhsa_gov_cn_yibiaoyaodian` | **有意不切换**：SQL 表在库中不存在，且数据源不同，保留医保定点药店 |
| 药品 | `nmpa_drug_info_20240116` | `nmpa_drug_info_20240116` | ✅ 已对齐（`MYSQL_TABLE_DRUGS`） |
| 国产器械 | `nmpa_e_equipment_info_20240116` | `nmpa_e_equipment_info_20240116` | ✅ 已对齐（`MYSQL_TABLE_EQUIPMENT`） |
| 进口器械 | `nmpa_e_equipment_info_f_20240116` | `nmpa_e_equipment_info_f_20240116` | ✅ 已对齐（`MYSQL_TABLE_EQUIPMENT_IMPORT`） |
| 器械生产 | `nmpa_e_productor_info_20240116` | `nmpa_e_productor_info` | **有意不切换**：日期后缀表列结构与基表不兼容 |
| 器械经营 | `nmpa_e_seller_info_20240116` | `nmpa_e_seller_info_20240116` | ✅ 已对齐（`MYSQL_TABLE_SELLER`） |
| DRG / ICD | `drg_biaogan_info` / `drg_words_info` | 同名 | ✅ 已精确匹配 |
| 进口药品 | `nmpa_drug_info_f_20240116` | `nmpa_drug_info_f_20240116` | ✅ 新增工具 `search_drug_import` |
| 执业药师 | `nmpa_drug_pharmacist_info_20231218`（误写） | `nmpa_drug_pharmaceutist_info_20231218` | ✅ 新增工具；用户 SQL 表名拼写缺 "eu" |
| 药品生产企业 | `nmpa_drug_productor_info` | `nmpa_drug_productor_info` | ✅ 新增工具 `search_drug_productor` |
| 国家基本药物 | `nmpa_drug_nation_info` | `nmpa_drug_nation_info` | ✅ 新增工具 `search_drug_nation` |
| 医保药品目录 | `bmfw_www_gov_cn_yibaodrug` | `bmfw_www_gov_cn_yibaodrug` | ✅ 新增工具 `search_yibao_drug` |
| 医用耗材 | `fuwu_nhsa_gov_cn_medical_supplies` | `fuwu_nhsa_gov_cn_medical_supplies` | ✅ 新增工具 `search_medical_supplies` |

> 小结：8 张同域表中 4 张已切到 SQL 同名快照（药品/国产器械/进口器械/器械经营），3 张有意不切换（医院裸名结构不同、器械生产日期表不兼容、`nmpa_drug_seller_info` 不存在），DRG/ICD 同名无需改。另 6 张高优先缺口已在本轮新增工具覆盖。

### 3.2 完全未暴露的表（17 张缺口，按主题；较原分析减少 6 张因 2026-08-24 已实现）

- **药品域补充（仍缺口）**：互联网药品信息 `nmpa_drug_internet_info`、临床试验机构 `nmpa_drug_clinical_trial_institution_info`、集采 `pharnexcloud_jicai`、叮当商品 `dingdang_20220831_info`
  - 已在本轮实现：进口药品、执业药师、药品生产企业、国家基本药物、医保药品目录（见 3.1）
- **医生旧快照**：`hdf_doctor_20170901` / `hdf_doctor_20230809`（建议统一到 `hdf_doctor_20250110`）
- **医保局目录族（仍缺口）**：疾病诊断目录 `fuwu_nhsa_gov_cn_disease_catalog`、手术操作目录 `fuwu_nhsa_gov_cn_sugical_catalog`、诊疗项目 `fuwu_nhsa_gov_cn_service_facilities`、医保定点机构 `fuwu_nhsa_gov_cn_local_optin`、医保医疗机构 `fuwu_nhsa_gov_cn_med_ins_org`、旧医保药店 `fuwu_nhsa_gov_cn_med_ins_org_pharmacy`（废弃）
  - 已在本轮实现：医用耗材 `fuwu_nhsa_gov_cn_medical_supplies`（见 3.1）
- **核酸检测**：`bmfw_www_gov_cn_hesuan`
- **台湾**：医疗机构 `ma_mohw_gov_tw_masearch`、药店 `ma_mohw_gov_tw_phmacy`
- **内容**：微信文章 `weixin_mp_article`

### 3.3 SQL 自身问题
- 文末 `weixin_mp_article` 处出现 `select ... subtitle1 select uuid, title ...` 两条 SELECT 拼接，属语法错误，无法执行，需拆分。
- `drg_biaogan_info` 详情 SQL 中 `quantile_time_75 例均住院70分位时间` 注释写 "70分位"，应为 "75分位"，属注释笔误。
- 大量字段用 `'联系管理员'` 占位（执业编号、统一信用证号、病床数、医生数、经纬度、POI指数、是否医保、手机号、门头照、院边店等），说明这些字段在源库缺失或需后台补全，工具返回前需确认是否有真实数据。

---

## 4. 对 Skill / 服务端的建议

1. **表层差异（低成本）**：8 张"同域不同源/日期"的表，用 `.env` 的 `MYSQL_TABLE_*` 指向对应快照即可在现有工具内覆盖，无需改代码；仅 `nmpa_drug_seller_info`（NMPA 经营药店）与 `hospital` 裸名属于**表名不一致**，需在工具 SQL 或配置里对齐。
2. **功能缺口（需新增工具）**：23 张未暴露表建议按优先级分批接入：
   - 高优先（医疗核心）：进口药品、执业药师、药品生产企业、国家基本药物、医保药品目录、医用耗材；
   - 中优先（医保局目录族）：疾病/手术/诊疗项目/定点机构/医疗机构；
   - 低优先（地域/内容）：台湾机构、核酸检测、叮当商品、微信文章。
3. **废弃表下线**：`fuwu_nhsa_gov_cn_med_ins_org_pharmacy` 已废弃，SQL 中不应再引用，避免回归旧 bug（上海/北京/广东 药店为 0）。
4. **SQL 修正**：拆分文末重复 SELECT，修正 DRG 注释笔误，补全 `'联系管理员'` 占位字段的真实来源。
