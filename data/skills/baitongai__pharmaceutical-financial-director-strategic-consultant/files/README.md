# 医药财务总监·战略顾问（Pharma CFO Strategic Advisor）

## 技能概述

「医药财务总监·战略顾问」是专为医药行业打造的财务总监+战略顾问+管线估值+BD交易分析完整技能包。基于通用财务总监技能框架（Finance Director Enhanced v4.0.0）进行全维度医药化改造。

### 核心改造

| 维度 | 原版 | 医药版 |
|------|------|--------|
| 估值核心 | DCF（确定性折现） | **rNPV**（风险调整净现值） |
| 资金管理 | 制造业绩存（冻住的现金） | **制药特化**（效期管理+两票制回款+Phase-Gate预算） |
| 风险控制 | 通用市场/信用风险 | **药政+科学双重风险**（集采/医保/临床失败/专利悬崖） |
| 战略落地 | 公司年度目标 | **产品生命周期管理**（适应症→市场→准入→定价） |
| 权限设计 | L0-L4 ACL | **GMP合规+研发保密**（盲态/CMC/AE/BD底价分层） |
| 持续学习 | 通用技能 | **医药行业专业知识**（CDE政策/NRDL/竞品管线） |

## 技能结构

```
pharma-cfo-advanced/
├── SKILL.md                              # 主技能文档（40+ KB）
├── README.md                             # 本文件
├── _meta.json                            # 元数据
├── pharma_cfo.py                         # 主入口（统一接口）
│
├── scripts/
│   ├── pharma_valuation_models.py        # 4个估值模型（rNPV为核心）
│   ├── pharma_financial_models.py        # 7个财务分析模型
│   └── pharma_cash_models.py            # 5个资金管理模型
│
├── references/
│   ├── pharma_cfo_mindset.md            # 医药CFO思维模式
│   ├── drug_valuation_framework.md      # 药品估值框架
│   ├── market_access_analysis.md        # 市场准入分析框架
│   ├── NMPA_regulatory_timeline.md      # 药政审批时间轴
│   ├── NRDL_pricing_reference.md        # 医保定价参考
│   └── pharma_cash_management.md        # 制药资金管理详解
│
├── quantitative_assessment/
│   ├── README.md                        # 评估系统说明
│   ├── learning_quantitative.md         # 量化评估设计文档
│   └── learning_auto_evaluate.sh        # 自动化评估脚本
│
└── test/
    └── test_pharma_models.py            # 完整测试套件（16项）
```

## 16个制药专用模型

### 估值模型（4个）
- ✅ rNPV管线估值模型（风险调整净现值 + 概率树）
- ✅ 峰值销售估计模型（患者流模型）
- ✅ BD交易分析模型（License-in/out 交易对价）
- ✅ 成熟产品销售折现模型

### 财务分析模型（7个）
- ✅ 药企财务比率分析（R&D Intensity等医药专用指标）
- ✅ 药企ROE分解（仿制药/创新药双线）
- ✅ 临床阶段现金流分析（Burn Rate / Cash Runway）
- ✅ 药物生命周期财务预测
- ✅ 药品定价敏感性分析（龙卷风图）
- ✅ 医药市场准入SWOT分析
- ✅ 专利悬崖财务预警

### 资金管理模型（5个）
- ✅ 药品库存与回款周转模型（冷链效期+两票制回款）
- ✅ 研发现金储备模型
- ✅ API/制剂GMP库存模型（按效期敏感性ABC分类）
- ✅ 医院/经销商信用评级模型
- ✅ Phase-Gate现金流滚动预算模型

## 快速使用

```python
from pharma_cfo import PharmaCFO

# 创建医药CFO实例
cfo = PharmaCFO(discount_rate=0.12)

# 管线健康检查
health = cfo.pipeline_health_check(
    pipelines=[
        {"drug_name": "PD-L1单抗", "phase": "phase_iii",
         "therapeutic_area": "oncology", "peak_sales_cny": 2_500_000_000,
         "years_to_launch": 3.0},
    ],
    current_cash=500_000_000,
    monthly_burn_rate=20_000_000,
)

# 政策风险评估
policy = cfo.policy_risk_assessment(
    drug_name="PD-L1单抗",
    indication="非小细胞肺癌",
    vbp_risk_level="low",
    nrdl_probability=0.6,
)
```

## 触发关键词

- 管线估值 / rNPV / BD交易 / License-in / License-out
- 峰值销售 / 患者流模型 / 药品定价 / 医保谈判 / 国谈
- 集采风险 / VBP / DRG/DIP / 市场准入 / NRDL
- 药物生命周期 / 专利悬崖 / 制药资金管理 / Burn Rate
- GMP库存 / 效期管理 / 医院回款 / 两票制
- Phase-Gate / 临床现金流 / 研发现金储备
- 医药SWOT / 药企财务分析 / 医药行业学习

## 安装

1. 下载 `pharma-cfo-strategic-advisor.zip`
2. 解压到 WorkBuddy 技能目录
3. 运行测试：`python test/test_pharma_models.py`

## 创建信息

- **创建者**：信煜（百通AI医药AI Skill开发负责人）
- **创建时间**：2026年07月10日
- **版本**：v1.0.0
- **基于**：Finance Director Enhanced v4.0.0 框架深度改造

---

**核心理念**：药企财务不是账房先生，是研发管线价值的翻译官、临床风险的守门人、商业化战略的导航员。
