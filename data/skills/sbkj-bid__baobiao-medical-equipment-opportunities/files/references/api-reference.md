# 接口参考

依据用户提供的《接口文档_2026-09-07.md》v1.94，2026-09-08读取快照编写。正文实际10个接口，原文顶部的21为未同步元数据。本文件只摘录本行业需要的接口请求与响应表；不包含旧版已删除接口和原始业务示例。参数表“默认值”含演示值，不能作为真实查询条件直接复用。

## 调用与鉴权

调用方式、环境变量读取顺序、密钥获取、长期安全保存和充值指引统一以 [SKILL.md](../SKILL.md) 中的“调用方式”和“密钥APIkey获取使用与API服务地址”为准，首次调用前读取。
使用平台现有HTTP能力，UTF-8 JSON POST，Content-Type: application/json; charset=utf-8，无需安装本地脚本或CLI。
服务地址从 BBIAO_SERVER_URL 读取，默认 https://gate.gov-bid.com；规范化为唯一的 /outer-gateway 前缀后拼接接口路径。下文完整URL仅表示默认服务地址，配置服务地址时替换服务部分。
密钥优先从 BBIAO_API_KEY 读取，再按主文件规则复用已安全保存的凭据；仅发送给用户配置或本 Skill 默认的服务地址。表中***是脱敏标记，不能实际发送。无密钥或无HTTP能力时停止对应调用并说明原因，不把示例当实际结果。
密钥仅按主文件规则存入安全凭据库、用户级环境变量或权限受限的凭据文件，不进入Skill、普通查询状态、结果、日志或报错。

## 接口调用频率

接口调用频率上限为 **60次/分钟**。按 [SKILL.md](../SKILL.md) 的“接口调用频率”章节统一执行：同一Key下所有接口、分页和重试保守合并计数，任意连续60秒内不超过60次，默认串行且请求发起间隔至少1.1秒；多个任务共享限流队列。

## 请求构造
- SearchProjectForAI仅允许：startDate、endDate、pageId、pageNumber、keyword、excludeKW、inCludeKW、className、areaName、companyName、OrderByType。保留大小写。
- className仅使用：全部信息、招标信息、中标信息、合同信息、采购意向、拍租信息。多个大类用英文逗号；细分类在响应与正文核验。
- 未指定地区时智能体搜索省略areaName；指定地区用名称。CompanySearchProject不接受日期、地区和企业角色参数。
- 搜索排序用 OrderByType="发布时间"；分页默认20，智能体与企业搜索最大100。pageNumber=0仅取候选数量，不得同时期待项目列表。
- 日期基于当前用户时区；最近30个自然日从当天前29天00:00:00到当天23:59:59。详情用来源记录的真实发布时间。
- 不支持的金额、行业、角色等条件不能塞入请求；在候选数据上核验，并说明结果覆盖范围。
- JSON关键词中的竖线不加Markdown转义反斜杠；URL查询值正确编码；文档示例日期、企业名和ID均不作为默认数据。

## 响应与失败处理
先检查HTTP成功、可解析JSON及 code=200。存在 subCode 时核对成功值0000000000，若code、subCode、msg矛盾则视为待确认错误，不当空结果。某些企业接口不返回subCode，不强制要求该字段。
鉴权、权限或额度错误停止对应调用，告诉用户发生什么、需要配置或由账户管理员处理；不重复轰炸。网络超时和临时5xx最多重试2次，遵守有效的Retry-After并采用短退避，所有重试进入同一限流队列。HTTP 429或明确的频率限制提示按主文件限流规则暂停：有有效Retry-After时遵守，未提供时至少等待60秒，最多重试2次；限流不等于额度不足。持续失败或平台不能等待时保留断点与已取结果，说明未完成。
列表：data.data、data.total、data.pageId、data.hasNext。企业联系人及关系：data.records、data.pagination，其中hasNext、totalPages等以实际返回为准（关系接口示例含这些字段）。hasNext缺失但存在可信totalPages可据其翻页；都缺失时标记不能确认全量，不猜测完成。
联系人默认pageNo=1、pageSize=5，最大5；客户与供应商默认pageNo=1、pageSize=20，最大20。按每个接口自身返回分页，不用其他接口的总数决定结束。

## 字段衔接与证据
- 招中标列表id + publishTime → getZTBStructreDetail / getZTBProjectDetailForAI。
- 企业关系relatedProjectId + projectPublishTime → 招中标详情，先验证ID可无损转integer。
- 结构化数据的partyAInfo / partyBInfo / agencyInfo与列表partAInfo / partBInfo / agencyInfo不同；不混用字段名。
- 结构化预算budgetMoney、中标bidMoney的单位为元，数组含多金额，按正文确定归属；列表projectMoney是带单位的展示字符串，性质未必明确。
- companyProfileSummary.dataStatus表示资料是否命中，false不代表企业没有对应业务。
- 原始来源使用真实collectUrl，不用sbkjBidUrl冒充。详情失败仍保留成功列表并说明，缺失信息不推测。
- 公告去重使用数据集类型 + id + publishTime。实体、标段和项目统计需要另外核验关联，不仅按标题去重。

## 接口目录
- 企业招中标信息搜索列表：`CompanySearchProject`
- 招中标信息结构化数据详情：`getZTBStructreDetail`
- 招中标信息详情（智能体、Agent专用）：`getZTBProjectDetailForAI`
- 招中标信息搜索列表（智能体、Agent专用）：`SearchProjectForAI`
- 企业基本信息：`companyProfileSummary`
- 企业联系电话：`companyProfileContacts`
- 企业合作客户：`companyProfileCustomers`
- 企业供应商：`companyProfileSuppliers`



## POST 企业招中标信息搜索列表

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/CompanySearchProject?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| companyName | string | 是 | 华中科技大学 | 参与招投标活动的企业名字，可以是甲方、乙方、代理机构 |
| pageId | integer | 是 | 1 | 当前页码 |
| pageNumber | integer | 否 | 20 | 每页记录数，此值不要超过100,设为0时仅返回结果数量，即total值 |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口统一响应码 |
| msg | string | 解析响应信息 |
| subCode | string | 业务侧code |
| data | object | 业务数据结果 |
| data.costTime | string | 搜索耗费时长，单位，毫秒 |
| data.total | integer | 搜索结果总数 |
| data.pageId | integer | 当前页码 |
| data.pageNumber | integer | 每页记录数量 |
| data.startDate | string | 搜索开始时间(格式：yyyy-MM-dd HH:mm:ss) |
| data.endDate | string | 搜索结束时间(格式：yyyy-MM-dd HH:mm:ss) |
| data.hasNext | boolean | 是否还有下一页 |
| data.data | array | 记录集合 |
| data.data[].id | integer | 项目ID |
| data.data[].newsTypeName | string | 信息类别 |
| data.data[].title | string | 信息标题 |
| data.data[].publishTime | string | 项目发布时间(格式:YYYY-MM-DD HH:mm:ss) |
| data.data[].content | string | 搜索高亮内容（截取部分） |
| data.data[].areaName | string | 项目信息归属地名称 |
| data.data[].score | number | 搜索引擎对文章相关度打分 |
| data.data[].projectMoney | string | 项目金额(带单位，如”54.38万”) |
| data.data[].projectClass | string | 项目子分类名称 |
| data.data[].purchaseType | string | 项目采购分类名称 |
| data.data[].siginUpStopDate | string | 报名截止时间(格式：yyyy-MM-dd) |
| data.data[].bidStartAddress | string | 开标地点 |
| data.data[].bidStartDate | string | 开标时间(格式：yyyy-MM-dd) |
| data.data[].collectUrl | string | 内容采集原网址 |
| data.data[].sbkjBidUrl | string | 世舶科技内容地址 |
| data.data[].partAIndustryList | array | 甲方行业，数组 |
| data.data[].subMatIndustryList | array | 标的物行业，数组 |
| data.data[].partAInfo | array | 甲方信息 |
| data.data[].partAInfo[].name | string | 甲方名称 |
| data.data[].partAInfo[].contactPhone | string | 甲方联系电话，多个用顿号间隔 |
| data.data[].partAInfo[].email | string | 甲方联系邮箱，多个用顿号间隔 |
| data.data[].partBInfo | array | 乙方信息 |
| data.data[].partBInfo[].name | string | 乙方名称 |
| data.data[].partBInfo[].contactPhone | string | 乙方联系电话，多个用顿号问隔 |
| data.data[].partBInfo[].email | string | 乙方联系邮箱，多个用顿号间隔 |
| data.data[].agencyInfo | array | 代理机构信息 |
| data.data[].agencyInfo[].name | string | 代理机构名称 |
| data.data[].agencyInfo[].contactPhone | string | 代理机构联系电话，多个用顿号间隔 |
| data.data[].agencyInfo[].email | string |  代理机构联系邮箱，多个用顿号间隔 |

## POST 招中标信息结构化数据详情

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/getZTBStructreDetail?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 332023653 | 项目ID |
| publishTime | string | 是 | 2026-06-08 14:30:30 | 项目发布时间，yyyy-MM-dd HH:mm:ss； |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 解析响应信息 |
| subCode | string | 业务侧 code |
| subMsg | string | 业务侧 msg |
| data | object | 业务数据结果 |
| data.projectID | integer | 项目ID |
| data.publishTime | string | 项目发布时间 格式：yyyy-MM-dd HH:mm:ss |
| data.sbkjBidUrl | string | 世舶科技项目信息地址 |
| data.collectUrl | string | 项目源网址 |
| data.projectName | string | 项目名称 |
| data.projectNumber | array | 项目编号（支持多编号） |
| data.projectSectionCode | array | 项目标段编号（支持多标段） |
| data.budgetMoney | array | 预算金额（支持多金额，如：[100, 200]）单位：元 |
| data.bidMoney | array | 中标金额（支持多金额，如：[100, 200]）单位：元 |
| data.siginUpStopDate | string | 报名截止日期（null表示无）格式：yyyy-MM-dd HH:mm:ss |
| data.bidStartDate | string | 开标日期（null表示无）格式：yyyy-MM-dd HH:mm:ss |
| data.bidStartAddress | array | 开标地点（支持多地点） |
| data.partyAInfo | array | 甲方信息列表 |
| data.partyAInfo[].name | string | 主体名称（甲方/乙方/代理机构） |
| data.partyAInfo[].contactName | array | 联系人列表（支持多人） |
| data.partyAInfo[].contactPhone | array | 联系电话列表（支持多号码） |
| data.partyAInfo[].address | array | 地址列表（支持多地址） |
| data.partyAInfo[].email | array | 邮箱列表（支持多邮箱，null表示无） |
| data.partyBInfo | array | 乙方信息列表 |
| data.agencyInfo | array | 代理机构信息列表 |
| data.bidCompany | array | 投标企业列表（支持多家） |

## POST 招中标信息详情（智能体、Agent专用）

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/getZTBProjectDetailForAI?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 337580128 | 项目ID |
| publishTime | string | 是 | 2026-07-06 18:11:40 | 项目发布时间，格式： yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss； |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 解析响应信息 |
| subCode | string | 业务侧 code |
| subMsg | string | 业务侧 msg |
| data | object | 业务数据结果 |
| data.id | integer | 项目ID |
| data.newsTypeName | string | 项目信息类别ID（老版分类）：招标信息，中标信息，采购合同，采购意向，拍卖信息 |
| data.title | string | 项目信息标题 |
| data.content | string | 项目信息内容，已清除html标签（标讯信息正文内容） |
| data.proviceName | string | 项目信息省名称 |
| data.cityName | string | 项目信息市名称 |
| data.countyName | string | 项目信息区/县名称 |
| data.projectMoney | string | 项目金额 |
| data.projectClassName | string | 2025版14个项目子分类名称 |
| data.purchaseType | string | 采购类别名称 |
| data.partAIndustryName | array | 甲方行业，数组 |
| data.subMatIndustryName | array | 标的物行业，数组 |
| data.partAName | array | 甲方名称，数组 |
| data.partBName | array | 乙方名称，数组 |
| data.agentName | array | 代理机构名称，数组 |
| data.publishTime | string | 项目发布时间 格式：yyyy-MM-dd HH:mm:ss |
| returnValue | string | 单个值响应结果 |

## POST 招中标信息搜索列表（智能体、Agent专用）

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/SearchProjectForAI?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| startDate | string | 是 | 2026-06-03 | 起始日期(格式:yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss) |
| endDate | string | 是 | 2026-09-05 | 结束日期(格式:yyyy-MM-dd 或 yyyy-MM-dd HH:mm:ss) |
| pageId | integer | 是 | 1 | 当前页码 |
| pageNumber | integer | 是 | 10 | 每页记录数，此值不要超过100,设为0时仅返回结果数量，即total值 |
| keyword | string | 否 | 工程\|空调 | 搜索关键词： - 多个关键词”同时出现”用空格分隔 - 多个关键词”或关系”用竖线分隔 |
| excludeKW | string | 否 | - | 排除关键词，多个用竖线分隔 |
| inCludeKW | string | 否 | - | 必须包含关键词： - 多个关键词”或关系”用竖线分隔 |
| className | string | 否 | 招标信息 | 项目信息类别： 全部信息，招标信息，中标信息，合同信息，采购意向，拍租信息 多个类别用英文逗号分隔 |
| areaName | string | 否 | 武汉 | 地区名称 |
| companyName | string | 否 | 华中科技大学 | 参与招投标活动的企业名字，可以是甲方、乙方、代理机构 |
| OrderByType | string | 否 | 发布时间 | 结果排序方式，相关性：按得分降序排序，发布时间：按发布时间降序排序 |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口统一响应码 |
| msg | string | 解析响应信息 |
| subCode | string | 业务侧code |
| subMsg | string | 业务侧msg |
| data | object | 业务数据结果 |
| data.costTime | string | 搜索耗费时长，单位，毫秒 |
| data.total | integer | 搜索结果总数 |
| data.pageId | integer | 当前页码 |
| data.pageNumber | integer | 每页记录数量 |
| data.startDate | string | 搜索开始时间(格式：yyyy-MM-dd HH:mm:ss) |
| data.endDate | string | 搜索结束时间(格式：yyyy-MM-dd HH:mm:ss) |
| data.hasNext | boolean | 是否还有下一页 |
| data.seKeyWords | string | Ui标红用的关键词 |
| data.data | array | 记录集合 |
| data.data[].id | integer | 项目ID |
| data.data[].newsTypeName | string | 信息类别 |
| data.data[].title | string | 信息标题(包含HTML高亮标签) |
| data.data[].publishTime | string | 项目发布时间(格式:YYYY-MM-DD HH:mm:ss) |
| data.data[].content | string | 招中标信息内容 |
| data.data[].areaName | string | 项目信息归属地名称 |
| data.data[].score | number | 搜索引擎对文章相关度打分 |
| data.data[].projectMoney | string | 项目金额(带单位，如”54.38万”) |
| data.data[].projectClass | string | 项目子分类名称 |
| data.data[].purchaseType | string | 项目采购分类名称 |
| data.data[].partAInfo | array | 甲方信息 |
| data.data[].partAInfo[].name | string | 甲方名称 |
| data.data[].partAInfo[].contactPhone | string | 甲方联系电话，多个用顿号间隔 |
| data.data[].partAInfo[].email | string | 甲方联系邮箱，多个用顿号间隔 |
| data.data[].partBInfo | array | 乙方信息 |
| data.data[].partBInfo[].name | string | 乙方名称 |
| data.data[].partBInfo[].contactPhone | string | 乙方联系电话，多个用顿号间隔 |
| data.data[].partBInfo[].email | string | 乙方联系邮箱，多个用顿号间隔 |
| data.data[].agencyInfo | array | 代理机构信息 |
| data.data[].agencyInfo[].name | string | 代理机构名称 |
| data.data[].agencyInfo[].contactPhone | string | 代理机构联系电话，多个用顿号间隔 |
| data.data[].agencyInfo[].email | string | 代理机构联系邮箱，多个用顿号间隔 |
| data.data[].siginUpStopDate | string | 报名截止时间(格式：yyyy-MM-dd) |
| data.data[].bidStartAddress | string | 开标地点 |
| data.data[].bidStartDate | string | 开标时间(格式：yyyy-MM-dd) |
| data.data[].collectUrl | string | 内容采集原网址 |
| data.data[].sbkjBidUrl | string | 世舶科技内容地址 |
| data.data[].partAIndustryList | array | 甲方行业，数组 |
| data.data[].subMatIndustryList | array | 标的物行业，数组 |

## POST 企业基本信息

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/companyProfileSummary?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| companyName | string | 是 | 武汉览山科技有限公司 | 企业名称  |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 响应信息 |
| data | object | 业务数据 |
| data.companyName | string | 企业名称 |
| data.baseInfo | object | 企业基础信息 |
| data.baseInfo.enterpriseProfile | object | 企业概况 |
| data.baseInfo.enterpriseProfile.companyId | string | 企业ID |
| data.baseInfo.enterpriseProfile.companyTypeName | string | 企业类型名称 |
| data.baseInfo.enterpriseProfile.companyTypeCode | string | 企业类型编码 |
| data.baseInfo.enterpriseProfile.industryName | string | 所属行业名称 |
| data.baseInfo.enterpriseProfile.industryCode | string | 所属行业编码 |
| data.baseInfo.enterpriseProfile.registeredRegion | object | 注册地区信息 |
| data.baseInfo.enterpriseProfile.registeredRegion.areaId | integer | 地区ID |
| data.baseInfo.enterpriseProfile.registeredRegion.provinceCode | string | 省编码 |
| data.baseInfo.enterpriseProfile.registeredRegion.cityCode | string | 市编码 |
| data.baseInfo.enterpriseProfile.legalRepresentative | string | 法定代表人 |
| data.baseInfo.enterpriseProfile.establishmentDate | string | 成立日期 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.enterpriseProfile.operatingStatus | object | 经营状态 |
| data.baseInfo.enterpriseProfile.operatingStatus.statusCode | string | 经营状态编码 |
| data.baseInfo.enterpriseProfile.operatingStatus.statusName | string | 经营状态名称 |
| data.baseInfo.enterpriseProfile.historicalNames | string | 历史名称 |
| data.baseInfo.registrationInfo | object | 注册信息 |
| data.baseInfo.registrationInfo.creditCode | string | 统一社会信用代码 |
| data.baseInfo.registrationInfo.registrationNumber | string | 注册号 |
| data.baseInfo.registrationInfo.organizationCode | string | 组织机构代码 |
| data.baseInfo.registrationInfo.registrationAuthority | string | 登记机关 |
| data.baseInfo.registrationInfo.registeredCapital | object | 注册资本 |
| data.baseInfo.registrationInfo.registeredCapital.amount | number | 注册资本金额 |
| data.baseInfo.registrationInfo.registeredCapital.unitCode | string | 注册资本单位编码 |
| data.baseInfo.registrationInfo.registeredCapital.unitName | string | 注册资本单位名称 |
| data.baseInfo.registrationInfo.paidInCapital | object | 实缴资本 |
| data.baseInfo.registrationInfo.paidInCapital.amount | number | 实缴资本金额 |
| data.baseInfo.registrationInfo.paidInCapital.unitCode | string | 实缴资本单位编码 |
| data.baseInfo.registrationInfo.paidInCapital.unitName | string | 实缴资本单位名称 |
| data.baseInfo.operationInfo | object | 经营信息 |
| data.baseInfo.operationInfo.businessScope | string | 经营范围 |
| data.baseInfo.operationInfo.businessTerm | string | 营业期限 |
| data.baseInfo.operationInfo.businessTermStart | string | 营业期限开始时间 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.operationInfo.businessTermEnd | string | 营业期限结束时间 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.operationInfo.approvalDate | string | 核准日期 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.operationInfo.revocationDate | string | 吊销日期 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.operationInfo.cancellationDate | string | 注销日期 格式 yyyy-MM-dd HH:mm:ss |
| data.baseInfo.operationInfo.insuredPersonCount | string | 参保人数 |
| data.baseInfo.contactInfo | object | 联系信息 |
| data.baseInfo.contactInfo.registeredAddress | string | 注册地址 |
| data.baseInfo.contactInfo.latestAddress | string | 最新地址 |
| data.baseInfo.contactInfo.website | string | 官网地址 |
| data.baseInfo.contactInfo.contactPhones | array | 联系电话列表 |
| data.baseInfo.contactInfo.contactEmails | array | 联系邮箱列表 |
| data.projectInsights | object | 项目统计信息 |
| data.projectInsights.bidStatistics | array | 投标项目统计列表 |
| data.projectInsights.bidStatistics[].industryName | string | 行业名称 |
| data.projectInsights.bidStatistics[].projectCount | integer | 项目数量 |
| data.projectInsights.bidStatistics[].projectShare | string | 项目占比 |
| data.projectInsights.bidStatistics[].budgetAmountWan | string | 预算金额，单位万元 |
| data.projectInsights.winStatistics | array | 中标项目统计列表 |
| data.projectInsights.winStatistics[].industryName | string | 行业名称 |
| data.projectInsights.winStatistics[].projectCount | integer | 项目数量 |
| data.projectInsights.winStatistics[].projectShare | string | 项目占比 |
| data.projectInsights.winStatistics[].budgetAmountWan | string | 预算金额，单位万元 |
| data.relationshipSummary | object | 关系汇总 |
| data.relationshipSummary.contactPersonCount | string | 联系人数量 |
| data.relationshipSummary.customerProjectCount | string | 客户项目数量 |
| data.relationshipSummary.supplierProjectCount | string | 供应商项目数量 |
| data.dataStatus | object | 数据命中状态 |
| data.dataStatus.baseInfoAvailable | boolean | 是否命中企业基础信息 |
| data.dataStatus.projectStatisticsAvailable | boolean | 是否命中项目统计信息 |
| data.dataStatus.contactsAvailable | boolean | 是否命中联系人数据 |
| data.dataStatus.customersAvailable | boolean | 是否命中客户数据 |
| data.dataStatus.suppliersAvailable | boolean | 是否命中供应商数据 |

## POST 企业联系电话

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/companyProfileContacts?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| companyName | string | 是 | 武汉览山科技有限公司 | 企业名称  |
| pageNo | integer | 是 | 1 | 页码，从 1 开始 |
| pageSize | integer | 是 | 5 | 每页条数，接口内部最大按 5 处理 |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 响应信息 |
| data | object | 业务数据 |
| data.companyName | string | 企业名称 |
| data.pagination | object | 分页信息 |
| data.pagination.pageNo | integer | 当前页码 |
| data.pagination.pageSize | integer | 每页条数 |
| data.pagination.total | string | 总条数 |
| data.pagination.totalPages | integer | 总页数 |
| data.pagination.hasNext | boolean | 是否有下一页 |
| data.records | array | 联系人列表 |
| data.records[].contactName | string | 联系人姓名 |
| data.records[].contactPhones | array | 联系电话列表 |

## POST 企业合作客户

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/companyProfileCustomers?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| companyName | string | 是 | 武汉览山科技有限公司 | 企业名称 |
| pageNo | integer | 是 | 1 | 页码，从 1 开始 |
| pageSize | integer | 是 | 20 | 每页条数，接口内部最大按 20 处理 |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 响应信息 |
| data | object | 业务数据 |
| data.companyName | string | 企业名称 |
| data.pagination | object | 分页信息 |
| data.records | array | 客户关系列表 |
| data.records[].partnerCompanyName | string | 合作方企业名称 |
| data.records[].relatedProjectId | string | 关联项目ID |
| data.records[].relatedProjectName | string | 关联项目名称 |
| data.records[].projectPublishTime | string | 项目发布时间， 格式 yyyy-MM-dd HH:mm:ss |
| data.records[].relationshipType | string | 关系类型，固定为客户 |

## POST 企业供应商

**请求地址：** `https://gate.gov-bid.com/outer-gateway/bid/companyProfileSuppliers?key=***`

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| companyName | string | 是 | 武汉览山科技有限公司 | 企业名称 |
| pageNo | integer | 是 | 1 | 页码，从 1 开始 |
| pageSize | integer | 是 | 20 | 每页条数，接口内部最大按 20 处理 |

### 响应参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 接口响应状态码 |
| msg | string | 响应信息 |
| data | object | 业务数据 |
| data.companyName | string | 企业名称 |
| data.pagination | object | 分页信息 |
| data.records | array | 供应商关系列表 |
| data.records[].partnerCompanyName | string | 合作方企业名称 |
| data.records[].relatedProjectId | string | 关联项目ID |
| data.records[].relatedProjectName | string | 关联项目名称 |
| data.records[].projectPublishTime | string | 项目发布时间 |
| data.records[].relationshipType | string | 关系类型，固定为供应商 |
