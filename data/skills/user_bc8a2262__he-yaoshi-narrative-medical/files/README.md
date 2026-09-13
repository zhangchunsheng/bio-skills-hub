# 叙事医学SKILL使用说明

## 概述

叙事医学SKILL用于根据用户的医疗相关提问，生成规范化的叙事医学素材与平行病历Word文档。

## 快速开始

### 触发条件

当用户提问涉及以下内容时，技能将自动激活：
- 药物相关：用药咨询、药物不良反应、用药体验
- 治疗相关：治疗方案、治疗体验、康复过程
- 诊断相关：确诊经历、症状描述、检查体验
- 检验检查：各项检查的感受、等待结果的心理

### 工作流程

1. **收集用户问题** - 识别核心主题和关键信息
2. **文献检索** - 调用Medical Advice和PubMed技能获取循证依据
3. **叙事人群分类** - 根据参考文献进行分类
4. **生成文档** - 输出Word格式叙事素材和平行病历

## 文件结构

```
narrative-medicine/
├── SKILL.md                    # 主技能文件
├── scripts/
│   └── create_narrative_doc.js # Word文档生成脚本
├── references/
│   ├── narrative_taxonomy.md   # 叙事人群分类详表
│   ├── medical_keywords.md     # 医学关键词映射
│   └── evidence_levels.md      # 循证医学证据分级
└── assets/
    ├── 叙事素材模板.docx        # 标准输出模板
    └── example_config.json     # 示例配置
```

## 使用示例

### 基本使用

```
用户: 我想了解糖尿病患者的用药体验故事
↓
Skill自动识别主题 → 收集问题 → 文献检索 → 分类 → 生成文档
↓
输出: G:\claw\叙事医学\output\叙事素材_[日期]_[序号].docx
```

### 自定义配置

可以通过JSON配置文件自定义输出：

```javascript
const config = {
  title: '自定义标题',
  narrativePopulation: '肿瘤患者',
  narrativeType: '成长式叙事',
  // ... 其他配置
};
```

## 配置项说明

| 配置项 | 说明 | 示例 |
|-------|------|-----|
| title | 叙事素材标题 | 糖尿病患者用药体验 |
| materialType | 素材类型 | 药学叙事/疾病叙事 |
| narrativePopulation | 叙事人群分类 | 慢性病患者/肿瘤患者 |
| narrativeClosure | 叙事闭锁类型 | 疑虑型/老年型 |
| narrativeType | 叙事类型 | 旅程式/成长式/告别式 |
| materialContent | 素材原文 | 不少于1500字 |
| parallelContent | 平行病历正文 | 七部分结构，不少于1400字 |

## 注意事项

1. 生成的叙事素材应为虚构或已脱敏
2. 引用文献时确保医学准确性
3. 注意文化敏感性和情感适度性
