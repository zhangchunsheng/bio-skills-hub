# 自主学习效果量化评估系统（医药版）

## 概述
这是「医药财务总监·战略顾问」技能包中的自主学习效果量化评估模块。基于通用版评估系统改造，全部指标替换为医药行业专用维度。

## 医药版量化指标

### 1. 核心能力评估维度（医药化）

| 核心能力维度 | 医药版评估指标 | 评分标准（1-10分） |
|---|---|---|
| **任务规划能力** | 管线BD评估分解能力 | 能否将"评估XX管线BD价值"分解为：靶点分析→竞争格局→临床数据提取→rNPV建模→交易结构建议 |
| **任务规划能力** | 市场准入路径规划 | 能否为不同产品规划合理的准入路径（国谈/集采/挂网/自费） |
| **任务规划能力** | 临床里程碑规划 | 能否识别关键临床里程碑及对应的财务需求 |
| **工具使用能力** | 医药数据库检索 | 能否正确检索CDE数据库、药智数据、ClinicalTrials.gov、PubMed |
| **工具使用能力** | 模型参数准确性 | rNPV模型参数（成功率、折现率）是否有文献支撑 |
| **工具使用能力** | 政策解读准确性 | 能否正确解读NRDL谈判规则、集采文件、CDE指导原则 |
| **多轮对话理解** | 管线上下文记忆 | 能否在讨论"PD-1集采影响"时关联前文"公司管线中3个PD-1品种的毛利率" |
| **多轮对话理解** | 跨场景关联 | 能否从"临床费用超支"关联到"入组速度→CRO合同条款→方案设计"的逻辑链 |
| **多轮对话理解** | 对话连贯性 | 在讨论BLA策略时能否自然引入专利悬崖、NRDL时间窗口等关联话题 |
| **代码生成与调试** | 医药模型代码 | 能否生成rNPV模型、患者流模型、蒙特卡洛模拟代码 |
| **代码生成与调试** | 敏感性分析代码 | 能否生成定价策略的龙卷风图数据代码 |
| **代码生成与调试** | 编码规范性 | 医药模型代码是否清晰、参数可读、假设有注释 |
| **知识应用准确性** | CDE政策准确性 | CDE指导原则引用是否准确、是否为最新版本 |
| **知识应用准确性** | 临床数据准确性 | 流行病学参数（发病率、诊断率）引用来源是否权威 |
| **知识应用准确性** | 行业知识更新 | NRDL/集采知识是否更新到最新年份 |

### 2. 每日学习记录模板（医药版）

```json
{
  "date": "YYYY-MM-DD",
  "learning_time_hours": 2.0,

  "new_policies_tracked": 3,
  "policies_list": [
    "2026年第一批国采规则：允许1-3家中标",
    "CDE《生物类似药临床试验设计指导原则》更新",
    "NRDL 2026年谈判规则新增'创新药快速通道'"
  ],

  "pipeline_analysis_cases": 2,
  "pipeline_analysis_list": [
    "PD-L1/TIGIT双抗竞争格局分析（5个竞品临床进度+估值对标）",
    "GLP-1口服制剂中国患者流模型（肥胖人群→治疗率→市场份额）"
  ],

  "model_assumption_revisions": 2,
  "assumption_revisions_list": [
    "修正：中国胃癌年新发病例从47.8万→39.7万（2026年肿瘤登记年报）",
    "修正：Phase II→III成功率从40%→35%（参考NRDD 2025统计）"
  ],

  "learning_effectiveness_score": 8,
  "learning_ROI": 165,

  "core_ability_scores": {
    "task_planning": {
      "bd_deal_decomposition": 8.5,
      "market_access_planning": 8.0,
      "milestone_planning": 9.0,
      "total": 8.5
    },
    "tool_usage": {
      "database_retrieval": 8.0,
      "model_parameter_accuracy": 8.5,
      "policy_interpretation": 9.0,
      "total": 8.5
    },
    "multi_turn_dialogue": {
      "pipeline_context_memory": 9.0,
      "cross_scenario_linking": 8.5,
      "dialogue_coherence": 9.0,
      "total": 8.8
    },
    "code_generation": {
      "pharma_model_code": 8.5,
      "sensitivity_code": 8.0,
      "coding_standard": 9.0,
      "total": 8.5
    },
    "knowledge_accuracy": {
      "cde_policy_accuracy": 9.0,
      "clinical_data_accuracy": 8.5,
      "industry_knowledge_freshness": 9.0,
      "total": 8.8
    }
  },

  "core_ability_total_score": 8.6,
  "summary": "今日重点跟踪了3项政策变化，完成2个管线竞争格局分析，修正了2个模型假设。"
}
```

### 3. 核心能力评估报告模板（医药版）

```json
{
  "assessment_date": "YYYY-MM-DD",
  "assessment_period": "月度",

  "task_planning": {
    "bd_deal_decomposition": {
      "score": 8.5,
      "description": "能够将BD交易分析分解为结构化步骤，识别关键交易要素",
      "improvement": "可增加可比交易对标分析步骤"
    },
    "market_access_planning": {
      "score": 8.0,
      "description": "能够为不同产品规划合理的准入路径",
      "improvement": "DRG/DIP影响分析可更深入"
    },
    "milestone_planning": {
      "score": 9.0,
      "description": "能够准确识别关键临床里程碑并规划对应的财务资源",
      "improvement": "保持"
    },
    "total": 8.5
  },

  "knowledge_accuracy": {
    "cde_policy_accuracy": {
      "score": 9.0,
      "description": "CDE政策引用准确，版本及时",
      "improvement": "可增加CDE政策的国际对标分析（FDA/EMA对比）"
    },
    "clinical_data_accuracy": {
      "score": 8.5,
      "description": "流行病学数据引用有权威来源支撑",
      "improvement": "发病率数据应标注年份，因数据每年更新"
    },
    "industry_knowledge_freshness": {
      "score": 9.0,
      "description": "NRDL/集采知识及时更新，竞品情报跟综到位",
      "improvement": "保持"
    },
    "total": 8.8
  },

  "core_ability_total_score": 8.67,
  "assessment": "整体优秀。医药行业专业知识准确性高、政策跟踪及时。可加强BD交易的系统化分析和医药数据可视化能力。"
}
```

## 评估标准（沿用通用版）

### 学习效率评分标准
- 10分：高效学习，产出价值显著
- 8-9分：良好学习，产出价值明显
- 6-7分：中等学习，产出价值一般
- 5分及以下：需要改进

### ROI评估标准
- ROI > 200%：极高ROI
- ROI > 150%：高ROI
- ROI > 100%：中等ROI
- ROI > 50%：需优化
- ROI < 50%：需调整方向

## 实施流程

### 每日流程：
1. **学习前**：记录开始时间 + 今日学习主题（如"GLP-1赛道竞争格局"）
2. **学习中**：记录新跟踪政策、管线分析案例、模型假设修正
3. **学习后**：记录结束时间，评估学习效率，更新每日记录

### 每周流程：
1. **周日晚上**：汇总一周数据
2. **生成周报**：新政策跟踪数、管线分析案例数、核心能力评分变化趋势
3. **识别瓶颈**：哪些维度评分持续偏低？需要补充什么知识？

### 每月流程：
1. **月底**：汇总月度数据
2. **生成本月报告**：完整核心能力评估报告
3. **深度分析**：本月学习ROI、知识盲区识别、下月学习计划

## 医药行业持续学习资源推荐

| 类别 | 来源 | 频率 |
|------|------|------|
| 药政法规 | CDE官网（cde.org.cn）"法规文件" | 每周扫描 |
| 医保政策 | 国家医保局官网"政策解读" | 每月跟踪 |
| 集采信息 | 各省药品采购平台公告 | 批次跟进 |
| 管线情报 | ClinicalTrials.gov + 药智数据 + 医药魔方 | 持续监控 |
| 学术进展 | PubMed + NEJM + Lancet Oncology | 每周 |
| 行业研报 | 券商医药行业周报 | 每周 |
| BD交易 | 医药魔方/药智BD交易数据库 | 每月汇总 |
