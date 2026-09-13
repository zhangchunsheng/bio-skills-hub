# ClinicalTrials.gov API v2 文档

## 概述

ClinicalTrials.gov API v2 提供对 ClinicalTrials.gov 数据库的编程访问，该数据库包含临床试验的注册和结果信息。

- **Base URL**: `https://clinicaltrials.gov/api/v2`
- **Documentation**: https://clinicaltrials.gov/data-api/api
- **速率限制**: 每秒 10 次请求

## 身份验证

无需 API 密钥，该 API 可公开访问。

## 主要端点

### 搜索研究
```
GET /studies
```

查询参数：
- `pageSize`：结果数量（1-1000）
- `query.term`：自由文本搜索
- `filter`：结构化过滤器

过滤器选项：
- `sponsor:SponsorName` - 按申办方筛选
- `condition:ConditionName` - 按适应症筛选
- `overallStatus:STATUS` - 按状态筛选
- `phase:PHASE` - 按阶段筛选

### 获取研究详情
```
GET /studies/{nctId}
```

返回特定试验的完整方案和结果部分。

## 响应结构

### 研究对象
```json
{
  "protocolSection": {
    "identificationModule": {
      "nctId": "NCT05108922",
      "briefTitle": "Study Title",
      "officialTitle": "Official Study Title"
    },
    "statusModule": {
      "overallStatus": "RECRUITING",
      "startDateStruct": {"date": "2022-01-15"},
      "completionDateStruct": {"date": "2024-12-31"},
      "statusVerifiedDate": "2024-01-15"
    },
    "sponsorCollaboratorsModule": {
      "leadSponsor": {"name": "Pfizer"}
    },
    "conditionsModule": {
      "conditions": ["Diabetes Mellitus", "Type 2"]
    },
    "designModule": {
      "phases": ["PHASE2", "PHASE3"],
      "enrollmentInfo": {"count": 500}
    }
  }
}
```

## 速率限制

- 最大：每秒 10 次请求
- 建议请求间隔：100-150 毫秒
- 超出限制将返回 HTTP 429

## 错误代码

| 代码 | 含义 |
|------|---------|
| 200 | 成功 |
| 400 | 错误请求 |
| 404 | 研究未找到 |
| 429 | 超出速率限制 |
| 500 | 服务器错误 |
