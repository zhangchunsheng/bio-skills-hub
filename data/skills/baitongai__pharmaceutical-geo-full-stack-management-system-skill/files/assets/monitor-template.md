# 监测模式输出模板

> 本模板为监测模式（Monitor）的标准输出格式。严格按照以下JSON结构输出。

---

```json
{
  "platform": "[平台名：元宝/豆包/文心一言/DeepSeek/千问]",
  "prompt": "[原始提问]",
  "metrics": {
    "mentioned": [true/false],
    "position": "[top1/top3/passing mention/null]",
    "accuracy": "[correct/partial/wrong]",
    "sentiment": "[positive/neutral/negative]",
    "cited_official_source": [true/false],
    "competitors": ["竞品A", "竞品B"],
    "risk_flag": "[无/禁忌错误/超适应证/用法错误/误导性内容]",
    "compliance_confidence": "[High/Medium/Low]"
  },
  "analysis": {
    "strengths": [
      "[优势点1：具体描述AI回答中做得好的地方]",
      "[优势点2：如有]"
    ],
    "weaknesses": [
      "[劣势点1：具体描述AI回答中的问题]",
      "[劣势点2：如有]"
    ],
    "optimization_suggestion": "[具体可执行的优化建议，指向低分维度，包含2-3条优化措施]"
  }
}
```

---

## 字段填写说明

### metrics 字段

| 字段 | 类型 | 取值 | 说明 |
|------|------|------|------|
| mentioned | boolean | true/false | AI回答中是否出现品牌名 |
| position | string | top1/top3/passing mention/null | 品牌名出现位置 |
| accuracy | string | correct/partial/wrong | 基于Golden Truth的准确性判定 |
| sentiment | string | positive/neutral/negative | AI回答对药品的情感倾向 |
| cited_official_source | boolean | true/false | 是否引用NMPA/指南等权威来源 |
| competitors | array | ["竞品名"] | AI回答中提及的竞品名称列表 |
| risk_flag | string | 无/禁忌错误/超适应证/用法错误/误导性内容 | 风险标记（取最严重项） |
| compliance_confidence | string | High/Medium/Low | 合规置信度：评估AI回答的确定性是否与证据基础相称。Low=虚高置信或证据缺口未声明 |

### analysis 字段

| 字段 | 要求 | 说明 |
|------|------|------|
| strengths | 至少1条 | AI回答中的亮点，需具体到回答中的语句或事实 |
| weaknesses | 至少1条 | AI回答中的问题，需具体指出错误或遗漏 |
| optimization_suggestion | 1段完整建议 | 指向低分维度的具体优化措施，2-3条可执行动作 |

## 优化建议优先级

| 风险标记值 | 优先级 | 建议措辞要求 |
|------------|--------|--------------|
| 禁忌错误 / 超适应证 / 用法错误 | 紧急 | 以"紧急优化："开头，包含Schema标记强化建议 |
| 误导性内容 | 高 | 包含禁语过滤与内容修正建议 |
| compliance_confidence=Low | 高 | 包含"降低表述确定性、补充A级证据"的建议 |
| 无（但其他维度低分） | 中 | 针对具体低分维度给出优化建议 |

## 完整示例

```json
{
  "platform": "豆包",
  "prompt": "皮肤康洗液怎么用？湿疹流水怎么弄？",
  "metrics": {
    "mentioned": true,
    "position": "top1",
    "accuracy": "wrong",
    "sentiment": "positive",
    "cited_official_source": false,
    "competitors": [],
    "risk_flag": "禁忌错误/超适应证",
    "compliance_confidence": "Low"
  },
  "analysis": {
    "strengths": [
      "品牌提及率高，占位Top1",
      "正确识别了药品为中药洗液且用于湿疹"
    ],
    "weaknesses": [
      "未提及1:5稀释关键操作，直接建议涂抹",
      "严重错误：声称孕妇可用（违反NMPA禁忌——孕妇禁用）",
      "未引用官方说明书作为信源",
      "虚高置信：无权威信源支撑却使用'可以治疗''没什么大事'等绝对化表述"
    ],
    "optimization_suggestion": "紧急优化：1. 在Schema标记中强化'孕妇禁用'字段与'1:5稀释湿敷'用法字段；2. 制作'1:5稀释'的视觉化内容（图片/短视频）供给AI抓取；3. 增加国药准字信息与NMPA说明书引用，对抗低质量数据源；4. 降低表述确定性，移除'可以治疗''没什么大事'等绝对化措辞，替换为'适用于''请遵医嘱'等审慎表述。"
  }
}
```
