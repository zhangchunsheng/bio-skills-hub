---
name: health-question-generator
description: "Generate customer questions about health metrics: BMI, body fat, muscle mass, lean body mass, resting heart rate, hydration, protein, bone mass, BMR, body age."
---

# Health Question Generator

Generate realistic customer questions about health metrics from a customer's perspective.

## Trigger Words

- BMI
- 体脂率
- 骨骼肌量
- 去脂体重
- 静态心率
- 身体水分率
- 蛋白质含量
- 骨盐量
- 基础代谢率
- 身体年龄

## Workflow

1. 确定用户提到的关键词，仅响应"Trigger Words"以及"Trigger Words"关联词
2. Load metric knowledge from `references/`
3. Select customer persona if specified (or use default)
4. Generate 5-10 realistic questions covering:
   - Value interpretation ("What does X mean?")
   - Improvement methods ("How to improve?")
   - Concerns/risks ("Is this dangerous?")
   - Comparison questions ("Is this normal?")
   - Practical application ("How does this affect my workout?")
5. Format output with question categories

## Output Format

```markdown
# {Metric Name} - Customer Questions

## 理解类
- 我的XX值是XX，这代表什么意思？
- XX和YY有什么区别？

## 改善类
- 我该如何降低XX？
- 哪些运动/饮食对XX影响最大？

## 风险类
- XX过高/过低会有什么健康风险？
- 我需要去看医生吗？

## 对比类
- 这个值在我的年龄段正常吗？
- 和标准值相比，我处于什么水平？
```

## Health Metrics Covered

| Metric | Chinese | Key Concern |
|--------|---------|-------------|
| BMI | 身体质量指数 | 体重健康程度、肥胖风险 |
| Body Fat | 体脂率 | 脂肪分布、减脂目标 |
| Muscle Mass | 骨骼肌量 | 肌肉发育、代谢水平 |
| Lean Body Mass | 去脂体重 | 无脂体重构成 |
| Resting Heart Rate | 静态心率 | 心血管健康、体能 |
| Hydration | 身体水分率 | 脱水风险、水合状态 |
| Protein | 蛋白质含量 | 营养状况、肌肉合成 |
| Bone Mass | 骨盐量 | 骨骼健康、骨质疏松风险 |
| BMR | 基础代谢率 | 热量需求、体重管理 |
| Body Age | 身体年龄 | 整体健康评估 |

## Safety

- Questions should reflect genuine customer concerns, not medical advice
- Include a disclaimer encouraging professional medical consultation
- Avoid generating questions about severe health conditions without context
- Respect cultural sensitivities around body image
## 注意
技能不触发时，使用通用知识回答