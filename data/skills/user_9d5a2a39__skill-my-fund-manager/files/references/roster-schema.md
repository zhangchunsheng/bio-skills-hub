# 数据文件结构

## roster.json（基金经理名单）

```json
{
  "meta": {
    "version": 1,
    "last_update": "2026-07-23 17:02",
    "count": 1,
    "max": 100,
    "description": "已蒸馏基金经理名单 - 最多100名（支持知名经理种子库一键导入）"
  },
  "managers": [
    {
      "id": "30189744",
      "name": "张坤",
      "company": "易方达基金",
      "fund_count": 4,
      "tenure_return": "308.10%",
      "scale": "322.85亿元",
      "add_date": "2026-07-23",
      "last_refresh": "2026-07-23 17:30",
      "status": "distilled",
      "manager_type": "公募"
    }
  ]
}
```

| 字段 | 说明 | 状态值 |
|------|------|--------|
| status | 经理状态 | active=已加入待蒸馏 / distilled=已蒸馏 / stale=数据过期 |
| manager_type | 经理类型 | 公募 / 私募 / QDII |
| max | 名单上限 | 100（原50，v1.2.0扩容） |

## famous_managers_2025_2026.json（知名经理种子库）

```json
{
  "meta": {
    "version": 1,
    "updated": "2026-07-26",
    "description": "2025-2026年知名基金经理种子库 - 按需导入到 roster.json",
    "categories": ["公募明星", "私募百亿", "QDII海外", "当红经理"],
    "total": 80,
    "note": "id 为空的条目，导入时通过 manager_search 按姓名+公司自动补全"
  },
  "managers": [
    {
      "name": "张坤",
      "company": "易方达基金",
      "manager_type": "公募",
      "category": "公募明星",
      "id": "30189744",
      "representative_fund": "005827",
      "tags": ["价值", "消费", "港股"],
      "note": "易方达蓝筹精选，长期重仓白酒+港股，价值投资代表"
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| category | 分类标签（公募明星/私募百亿/QDII海外/当红经理） |
| id | 东方财富经理ID（公募/QDII）或 amac_ 前缀ID（私募）；为空时导入时自动搜索补全 |
| representative_fund | 代表基金代码（用户参考，不影响导入） |
| tags | 风格标签数组 |

**种子库分类容量：** 公募明星30 / 私募百亿20 / QDII海外15 / 当红经理15 = 共80位（留20名额给用户自定义）

## managers/{id}.json（单经理完整档案）

```json
{
  "id": "30189744",
  "name": "张坤",
  "company": "易方达基金",
  "fund_codes": ["005827", "110011", ...],
  "fund_names": ["易方达蓝筹精选混合", ...],
  "tenure_return": "308.10%",
  "scale": "322.85亿元",

  "bio": "我是张坤，易方达基金基金经理...",
  "specialty": "消费、科技",
  "style_tags": ["价值", "高度集中"],
  "style_code": "VALUE-MED_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-HK_STOCK",
  "industry_preference": ["消费", "科技"],
  "viewpoint_human": "我认为当前消费板块...",
  "style_dna": "### 1. 投资决策框架\n...",

  "top_holdings": [
    {"code": "00700", "name": "腾讯控股", "total_ratio": 15.32, "appear_count": 3, "fund_count": 3}
  ],
  "holdings_report_date": "2026-06-30",

  "strategy_texts": ["【易方达蓝筹精选混合】投资目标：..."],
  "latest_reports": [{"title": "...", "date": "...", "pdf_url": "..."}],

  "performance": {
    "summary": {"avg_returns": {"近1年": -18.92}},
    "funds": [{"fund_code": "005827", "fund_name": "...", "returns": {...}}]
  },

  "distill_engine": "rules",
  "distill_date": "2026-07-23 17:30",
  "holdings_updated": "2026-07-23 17:30",
  "reports_updated": "2026-07-23 17:30",
  "performance_updated": "2026-07-23 17:30",

  "_v2_comment": "以下 5 个字段为 v2.0.0 新增，每次 smart_update 自动写入"
}
```

### v2.0.0 新增字段

```json
{
  "speech_fingerprint": {
    "avg_sentence_len": 28.5,
    "first_person_density": 0.08,
    "data_driven_score": 0.65,
    "certainty_score": 0.32,
    "dominant_style": "数据驱动+适度确定性",
    "sample_quotes": ["...", "..."],
    "computed_at": "2026-08-07 12:30"
  },

  "capability_scores": {
    "选股": 78,
    "择时": 62,
    "风控": 71,
    "稳定": 85,
    "composite": 74,
    "weights": {"选股": 0.35, "择时": 0.25, "风控": 0.20, "稳定": 0.20},
    "computed_at": "2026-08-07 12:30",
    "data_window": "近1年+3年"
  },

  "attribution": {
    "total_return": -18.92,
    "industry_exposure": -3.5,
    "stock_selection": -12.4,
    "timing": -3.0,
    "summary": "本期亏损主要来自选股贡献...",
    "method": "simplified_brinson_v1",
    "computed_at": "2026-08-07 12:30"
  },

  "risk_metrics": {
    "max_drawdown_pct": -22.5,
    "annual_volatility_pct": 18.3,
    "downside_volatility_pct": 14.7,
    "sharpe_ratio": 0.93,
    "calmar_ratio": -0.84,
    "sortino_ratio": 1.16,
    "risk_level": "中",
    "computed_at": "2026-08-07 12:30"
  },

  "style_radar": {
    "value_growth": {"value": 75, "growth": 25},
    "market_cap": {"large": 80, "mid": 20},
    "momentum": {"high": 30, "low": 70},
    "quality": {"high": 85, "low": 15},
    "concentration": {"high": 70, "low": 30},
    "turnover": {"high": 20, "low": 80},
    "computed_at": "2026-08-07 12:30"
  }
}
```

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `speech_fingerprint` | dict | speech_fingerprint.build_fingerprint() | 6 维言论指纹 |
| `capability_scores` | dict | capability_score.compute_scores() | 4 维评分 + composite |
| `attribution` | dict | performance_attribution.attribute_performance() | 简化 Brinson 归因 |
| `risk_metrics` | dict | risk_metrics.compute_risk_metrics() | 风险调整收益 5 指标 |
| `style_radar` | dict | style_radar.compute_radar() | 6 维风格雷达 |

## change_log/YYYY-MM-DD.json（smart_update 变化日志）

```json
{
  "date": "2026-07-26",
  "runs": [
    {
      "run_time": "2026-07-26 09:00",
      "engine": "auto",
      "managers": [
        {
          "name": "张坤",
          "manager_id": "30189744",
          "changed": true,
          "reasons": ["新季报：2026-03-31 -> 2026-06-30", "重仓变动：新增1只/退出1只"],
          "details": {
            "report_date_change": {"old": "2026-03-31", "new": "2026-06-30"},
            "holdings_change": {"added": ["600519"], "removed": ["000858"]}
          }
        },
        {
          "name": "萧楠",
          "manager_id": "30298742",
          "changed": false,
          "reasons": []
        }
      ]
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| runs | 当天多次运行 smart_update 的记录数组 |
| changed | 该经理是否检测到变化 |
| reasons | 变化原因数组（规模/重仓/季报/业绩四维度） |
| details | 变化详情（old/new/diff 等结构化字段） |

## 数据时效说明

| 数据类型 | 实际滞后 | 更新频率 |
|---------|---------|---------|
| 基金净值 | T+1~T+2 | 每日 |
| 十大重仓 | 季度末后4-8周 | 每季度 |
| 投资策略 | 基金合同，极少变 | 静态 |
| 季报正文 | 季度末后4-8周 | 每季度 |
| 经理档案 | 实时 | 任职/离职时 |
| 业绩数据 | T+1~T+2 | 每日 |
