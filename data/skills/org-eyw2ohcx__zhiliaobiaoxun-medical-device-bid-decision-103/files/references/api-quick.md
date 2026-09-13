# 工具速查（决策分析所用子集）

> 与 zlbx-bidding SKILL 同一套 api_v2 接口，此处只收录本 SKILL 用到的 9 个工具的关键参数。
> `POST https://mcp-server.zhiliaobiaoxun.com/api_v2/{工具名}`，Header 带 `X-API-Key` + `X-Client: bid-decision/1.0.3`。

## 通用概念

**match_modes**（关键词在哪个字段匹配，精确查询的关键）：

| 值 | 含义 | 决策分析中的用途 |
|---|------|-----------------|
| `caller` | 招标方/采购单位 | 查采购方的历史采购 |
| `winner` | 中标方 | 查某公司中标实力 |
| `tender` | 投标方 | 查某公司投标记录 |
| `winner_tender` | 中标或投标 | 查参与史 |
| `sm` / `title` / `brand` / `fulltext` | 标的物/标题/品牌/全文 | 标的物过滤 |

**bid_process 公告阶段**：1=采购意向 2=预招标 4=招标 7=中标结果 8=合同。查历史成交用 `[7,8]`。

**组合逻辑**（仅 `query_bids_advanced` / `aggregate_bids_advanced` 支持 keyword_groups）：
- `keywords`（OR） AND `keyword_groups` 每组（组内 OR） AND NOT `exclude_keywords`
- 例·采购方×供应商交集：`{"keywords": ["采购方全称"], "match_modes": ["caller"], "keyword_groups": [{"keywords": ["供应商全称"], "match_modes": ["winner","tender"]}]}`

**响应**：`{"success": true, "data": {...}, "meta": {"cost_units": 1}}`；分页 `page`/`page_size`（默认20，最大50）。

**金额参数名差异**：search_bids 用 `min_amount/max_amount`；query_bids_advanced 与 aggregate 的 filters 用 `min_money/max_money`；价格类工具用 `min_price/max_price`。单位都是元。

## 工具清单

### get_bid_detail — 标讯详情+原文
`{"bid_id": 123}` 或 `{"bid_url": "https://www.zhiliaobiaoxun.com/content/xxx/b1"}`。响应含 `fulltext`（公告原文）、`service_end_date`、`agency_name`。

### search_bids — 常规搜索
`keywords`(必填) + `match_modes` + `bid_type`(招标/中标/全部) + `bid_process` + `begin_date/end_date` + `provinces/cities` + `min_amount/max_amount`。

### query_bids_advanced — 高级搜索
search_bids 全参数 + `keyword_groups` + `exclude_keywords` + `sort_field/sort_order`。金额参数为 `min_money/max_money`。

### search_company — 公司名称解析
`{"company_name": "简称", "page_size": 20}` → 总部+分子公司全量列表。采购方/竞争者名称对不上时先用它扩全名。

### get_company_profile — 公司画像
`{"company": "全称或ID"}` → 工商信息、行业、`caller_count`（招标次数）、`winner_count`（中标次数）。

### get_company_partners — 客户与供应商
`{"company": "...", "partner_type": "客户|供应商|全部"(必填), "keywords": [标的物过滤], "limit": 20}` → 合作次数/金额/最近合作时间/products。

### find_potential_bidders — 潜在投标者预测
行业示例：`{"project_title": "XX市人民医院重症监护设备采购项目"}` → 返回历史参与同类项目的器械经销商。
`{"bid_id": 123}` 或 `{"project_title": "..."}`，`limit` 默认10 → `caller_history_count`（与采购方合作史）、`region_win_count`（区域中标）、`matched_products`。

### find_competitors — 竞争对手（投标重叠度）
`{"company": "...", "limit": 10}` → `co_bid_count`（共同投标次数）、`top_co_bid_products/callers/provinces`。

### get_price_trends — 品牌型号历史成交单价
行业示例：`{"brand": "迈瑞", "model": "SV300", "product": "呼吸机"}`
`{"brand": "必填", "model": "...", "product": "...", "exclude_keywords": ["维保","耗材"]}` → `price_stats`(min/max/avg/median) + 逐条成交记录。

### aggregate_bids_advanced — 聚合统计
`{"filters": {keywords/match_modes/keyword_groups/bid_type(1招标|2中标)/begin_date/provinces/min_money...}, "group_by": ["month|quarter|year|province|brand|company_type"], "compare_with": "yoy|qoq"}` → buckets（count/sum_amount/avg_amount/同比）。
