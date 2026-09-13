# 数据源 API 端点详解

> 本文件详列本 skill 使用的所有数据源 API，供调试和扩展参考。

## 一、东方财富 / 天天基金（主数据源，无需 API Key）

### 1. 全市场基金经理列表
```
GET https://fund.eastmoney.com/Data/FundDataPortfolio_Interface.aspx
参数: dt=14, ft=all, pn={每页数}, pi={页码}, sc=abbname, st=asc, mc=returnjson
返回: var returnjson={data:[["经理ID","姓名","公司ID","公司","基金代码","基金名称","任职天数","任职回报","代表基金代码","代表基金名称","规模","代表回报"],...]}
分页: pn 最大 500，全市场约 4273 人，需 9 页
缓存: data/manager_index.json，有效期 7 天
反爬: 仅需 User-Agent + Referer
```

### 2. 基金经理详情页
```
GET https://fundf10.eastmoney.com/Manager/MangerInfo/{manager_id}
解析: HTML 正则提取姓名、公司、投资理念、简历、任职时间
```

### 3. 基金十大重仓
```
GET https://fundf10.eastmoney.com/FundArchivesDatas.aspx
参数: type=jjcc(股票)/zqcc(债券)/jjcc_2(基金), code={基金代码}, topline=10
返回: var apidata={content:"<table>...</table>", arryear:["2026-06-30",...]}
编码: UTF-8
反爬: 仅需 User-Agent + Referer，无需签名
注意: content 含多个报告期表格，只取第一个（最新）
```

### 4. 基金基本概况（投资策略）
```
GET https://fundf10.eastmoney.com/jbgk_{fund_code}.html
解析: HTML 正则提取"投资目标""投资范围""投资策略""投资理念""业绩比较基准""风险收益特征"
```

### 5. 基金业绩数据
```
GET https://fund.eastmoney.com/pingzhongdata/{fund_code}.js
返回: JS 变量格式
关键变量:
  fS_name = "基金名称"
  syl_1y = 近1月收益率(%)
  syl_6y = 近6月收益率(%)
  syl_1n = 近1年收益率(%)
  syl_3n = 近3年收益率(%)
  syl_jin = 今年以来(%)
  fund_sourceRate = 管理费率(%)
  Data_netWorthTrend = [{x:时间戳, y:净值, equityReturn:日涨幅}, ...]
  Data_rateInSimilarPersent = [{x:时间戳, y:同类排名百分位}, ...]
```

### 6. 基金定期报告公告
```
GET https://api.fund.eastmoney.com/f10/JJGG
参数: fundcode={基金代码}, pageIndex=1, pageSize=10, type=3(定期报告)
Header: Referer: https://fundf10.eastmoney.com/
返回: JSON {Data:[{TITLE, PUBLISHDATEDesc, ID, ...}]}
季报PDF: https://pdf.dfcfw.com/pdf/H2_{ID}_1.pdf
```

## 二、AMAC 中国证券投资基金业协会（私募基金数据源，无需 API Key）

### 1. 私募基金产品搜索
```
POST https://gs.amac.org.cn/amac-infodisc/api/pof/fund
Header: Content-Type: application/json, Referer: https://gs.amac.org.cn/amac-infodisc/res/pof/fund/fundList.html
Body: {"keyword": "搜索词", "primaryInvestType": "ALL", "page": 1, "size": 20}
返回: JSON {content: [{fundName, managerName, managersInfo: [{managerId, managerName}], ...}], totalElements}
覆盖: 全市场约24万+只私募基金产品
反爬: 仅需 User-Agent + Referer + Content-Type
```

### 2. 私募基金管理人详情
```
GET https://gs.amac.org.cn/amac-infodisc/res/pof/manager/{managerId}.html
注意: 页面为JS渲染，人员信息通过AJAX加载
managerId 来源: 基金产品搜索结果中的 managersInfo[0].managerId
```

### 3. 私募搜索局限性
- AMAC 搜索的是**基金产品名**和**管理人名**，非基金经理个人名
- 若用户提供私募基金经理个人名（如"邓晓峰"），需提示提供管理人名称（如"高毅资产"）
- 私募基金不公开持仓和季报，蒸馏主要基于管理人信息和互联网公开资料
- 私募管理人ID格式：`amac_{managerId}`（避免与公募ID冲突）

## 三、ttfund 官方 API（可选增强，需 API Key）

```
POST https://skills.tiantianfunds.com/ai-smart-skill-service/openapi/skill/invoke
Header: X-API-Key: $TTFUND_APIKEY
基金经理查询: skill_id=FUND_MANAGER_INFO, manager_name={姓名} 或 manager_id={ID}
持仓查询: skill_id=FUND_HOLDING_INFO, fund_id={代码}, report_period=2025-Q4, holding_type=stock/bond/all
```

## 三、反爬处理

| 数据源 | 反爬手段 | 处理 |
|--------|---------|------|
| 东方财富 fundf10 | User-Agent + Referer | 随机 UA 池 + `Referer: https://fund.eastmoney.com/` |
| 东方财富列表 | 随机延迟 | 每页间隔 0.3-0.8s |
| 东方财富公告 | Referer 校验 | `Referer: https://fundf10.eastmoney.com/` |
| ttfund API | API Key | Header `X-API-Key` |

## Edge Cases

- 基金代码为空或无效：返回空数据，跳过该基金
- 东方财富返回 403：检查 User-Agent 和 Referer，增加延迟
- 经理无管理产品：无法获取重仓和业绩，只蒸馏投资策略
- 港股代码（5位数字如 00700）：正常处理，不影响解析
- 债券型/货币型基金：无股票重仓，持仓为债券/存款
