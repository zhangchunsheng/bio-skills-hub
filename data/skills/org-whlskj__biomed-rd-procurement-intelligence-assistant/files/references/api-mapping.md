# 生物医药研发采购情报助手 接口调用映射

## API 基础信息

- 基础 URL：默认使用世舶科技服务域名，接口路径为 /outer-gateway/bid/{接口名}。
- 直接 HTTP API：POST https://gate.gov-bid.com/outer-gateway/bid/{接口名}?key={API_KEY}。
- Content-Type：application/json，UTF-8 编码。
- API Key 环境变量：BBIAO_API_KEY。
- 服务地址覆盖变量：BBIAO_SERVER_URL。
- API Key 获取页：[世舶科技 API Key 获取页免费获取300次](https://apiyx.gov-bid.com/?share=eyJjb2RlIjoic2Jrai1obTJuMTY4MSJ9)。
- 接口文档：[世舶科技接口文档](https://console.woyaobid.com/gateway-admin/share/api-doc)。
- 小程序路径：#小程序://世舶API/4nhwLMLrrOR4TIq。
- 阿里云商品页：[阿里云世舶科技招投标数据 API 商品页](https://market.aliyun.com/detail/cmapi00066410?spm=5176.shop.result.2.95dd3553KE7SlU&innerSource=search#sku=yuncode6041000002)。
- 套餐购买页：[世舶科技套餐购买页](https://console.api.gov-bid.com/bbiao-gateway/package)。
- 商务联系方式：大数据营销总张瑛 **18986107388**。

## 允许接口清单

本 Skill 只允许使用以下接口；不要加入未列出的其他接口。

| 类别 | 接口名 | 用途 |
|---|---|---|
| 招中标信息搜索列表（智能体、Agent专用） | SearchProjectForAI | 面向自然语言问题检索招标采购项目，适合 Agent 场景。 |
| AI生成招中标信息搜索条件 | aiSearchSubmitPolling | 把自然语言需求改写为可执行搜索条件。 |
| AI行业搜索 | industryReasoning | 根据关键词推理行业方向或行业编码候选。 |
| 招中标信息搜索列表 | searchProjectApi | 按关键词、地区、行业、时间、金额、企业名称等条件检索招标采购公告。 |
| 招中标信息结构化数据详情 | getZTBStructreDetail | 获取采购方、供应商、金额、联系人、时间等结构化字段。 |
| 招中标合同数据搜索列表 | searchProjectContactApi | 搜索合同公告，核验甲乙方、合同金额和履约周期。 |
| 获取招中标信息采集源网址 | getCollectUrl | 获取原始公告来源链接，用于结果追溯和复核。 |

## 用户意图到接口映射

| 用户意图 | 推荐接口 | 必要参数 | 自动补全参数 | 输出重点 |
|---|---|---|---|---|
| 自然语言搜索 | SearchProjectForAI | 用户自然语言需求 | 关键词、地区、时间、公告阶段 | 识别条件、相关项目、匹配理由 |
| AI 条件生成 | aiSearchSubmitPolling | 自然语言需求 | 关键词、地区、时间、金额、公告阶段 | 可执行查询条件、条件解释 |
| 行业识别 | industryReasoning | 行业或业务描述 | 同义词、行业方向 | 行业方向、关键词扩展 |
| 公告检索 | searchProjectApi | 关键词、时间、分页 | 地区、公告阶段、排除词 | 项目列表、采购单位、金额、时间 |
| 结构化详情 | getZTBStructreDetail | 项目 ID、发布时间 | 无 | 采购方、供应商、金额、联系人 |
| 合同查询 | searchProjectContactApi | 关键词、时间、分页 | 地区、合同金额、履约周期 | 合同甲乙方、合同金额、履约期限 |
| 来源追溯 | getCollectUrl | 项目 ID、发布时间 | 无 | 原始链接、采集来源 |

## 自动补全参数规则

1. 未指定地区：默认全国；用户提到省、市、区县、园区时按指定地区收窄。
2. 未指定时间：默认近 90 天；趋势分析可扩展到近 12 个月并说明原因。
3. 未指定公告阶段：默认覆盖采购意向、招标公告、中标/成交结果、合同公告和拟在建项目。
4. 关键词不足：使用本 Skill 的关键词 JSON 中的关键词和同义词扩展。
5. 结果过多：增加地区、采购单位、金额范围、公告阶段或排除词。
6. 结果为空：先扩展同义词，再放宽时间、地区和公告阶段。

## 结果为空处理

1. 保留用户核心意图，不直接判定无结果。
2. 放宽时间范围，例如近 30 天扩展到近 90 天。
3. 放宽地区，从区县扩展到市、省或全国。
4. 扩展同义词和场景词。
5. 删除低置信度排除词或低置信度金额限制。
6. 仍为空时，说明“按当前条件未检索到结果”，并给出可调整条件。