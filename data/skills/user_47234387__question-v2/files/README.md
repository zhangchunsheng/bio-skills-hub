# Health Question Generator - README

## 概述

这是一个生成客户健康问题的 OpenClaw Skill，帮助理解用户对各项身体指标的常见疑问。

## 功能

根据触发词（BMI、体脂率等10个健康指标）生成客户可能提出的问题，包括：
- 数值理解
- 改善方法
- 风险评估
- 对比分析
- 误区澄清

## 目录结构

```
health-question-generator/
├── SKILL.md                      # 主文件，包含触发词和工作流程
├── references/                   # 每个指标的详细知识库
│   ├── BMI.md
│   ├── body-fat.md
│   ├── skeletal-muscle.md
│   ├── lean-body-mass.md
│   ├── resting-heart-rate.md
│   ├── hydration.md
│   ├── protein.md
│   ├── bone-mineral.md
│   ├── BMR.md
│   └── body-age.md
├── assets/                       # 模板和资源
│   ├── customer-personas.md      # 客户画像
│   └── question-templates.md     # 问题生成示例
├── scripts/                      # 辅助脚本
│   ├── README.md
│   └── validate.py               # 技能验证脚本
└── README.md                     # 本文件
```

## 使用方法

### 1. 触发 Skill

用户提及任意触发词即可：
- "帮我生成一些关于体脂率的客户问题"
- "客户会对BMI有什么疑问？"
- "静态心率相关的问题有哪些？"

### 2. 输出格式

问题会按分类输出：
```markdown
# {指标名称} - 客户问题

## 理解类
- 问题1
- 问题2

## 改善类
- 问题1
- 问题2

...
```

### 3. 自定义选项（可选）

可以指定客户画像：
```
"生成减脂新手对体脂率的问题"
"健身爱好者会问哪些关于BMR的问题？"
```

## 验证 Skill

运行验证脚本检查完整性：

```bash
cd ~/.openclaw/workspace/agent-78045a6f/skills/health-question-generator
python3 scripts/validate.py
```

## 注意事项

- ⚠️ 生成的问题仅反映客户常见疑问，不构成医疗建议
- ⚠️ 输出中应包含免责声明，建议用户咨询专业医疗人员
- ⚠️ 避免生成关于严重健康条件的问题，除非有明确上下文

## 扩展建议

- **新增指标**：在 `references/` 添加新文件
- **调整问题风格**：修改 `assets/question-templates.md`
- **优化客户画像**：在 `assets/customer-personas.md` 添加新类型