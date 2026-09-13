---
name: medical-symptom-analyzer
description: "Medical symptom analysis skill that searches authoritative medical resources to analyze user-described symptoms, matches them with possible conditions, and provides inferences with recommendations. Use when: (1) user describes symptoms and asks for possible causes or conditions, (2) user asks what disease they might have based on symptoms, (3) user wants to know which medical department/specialty to consult, (4) user asks for analysis of symptoms like '头痛 发热 可能是什么病', '我这些症状是什么病', '应该挂什么科', (5) explicitly asked to analyze medical symptoms or provide medical information."
---

# Medical Symptom Analyzer

Analyze user-described symptoms by searching authoritative medical resources, provide possible condition inferences, recommendations, and always include appropriate medical disclaimers.

## Workflow

### 1. Receive and Parse Symptoms

Extract from user's description:
- **Main symptoms**: Primary complaints (e.g., 头痛, 发热, 咳嗽)
- **Symptom details**: Onset, duration, severity, progression
- **Associated symptoms**: Secondary symptoms that may be related
- **Patient context**: Age, gender, medical history (if provided)
- **Severity indicators**: Emergency symptoms (胸痛, 呼吸困难, etc.)

If symptoms are vague or incomplete, ask for clarification before proceeding.

### 2. Check for Emergency Symptoms

**Before analysis, check if user described emergency symptoms:**
- 胸痛或胸闷 (chest pain or tightness)
- 呼吸困难 (difficulty breathing)
- 意识丧失或晕厥 (loss of consciousness or fainting)
- 严重头痛伴呕吐 (severe headache with vomiting)
- 肢体无力或言语不清 (limb weakness or slurred speech - suspected stroke)
- 严重腹痛 (severe abdominal pain)
- 高热伴意识改变 (high fever with altered consciousness)
- 外伤后症状 (symptoms after trauma)

**If emergency symptoms present**: Start response with:
> 🚨 **紧急提醒**：您描述的症状可能需要立即医疗关注，请尽快就医或拨打急救电话。

### 3. Search Authoritative Medical Resources

**Read references/medical_resources.md** for complete list of resources and search strategies.

**Search workflow:**
1. Use `web_fetch` to retrieve information from authoritative medical websites
2. Use `online-search` skill (if available) for broader searches
3. Prioritize Chinese medical resources for Chinese-speaking users:
   - 丁香医生 (dxy.com)
   - 好大夫在线 (haodf.com)
   - Mayo Clinic 中文版 (mayoclinic.org/zh-hans/)
4. Cross-reference with international resources:
   - Mayo Clinic (mayoclinic.org)
   - WebMD (webmd.com)
   - MedlinePlus (medlineplus.gov)

**Search queries to use:**
- "[症状1] [症状2] 可能是什么病"
- "[symptom1] [symptom2] possible causes"
- "[symptom1] [symptom2] differential diagnosis"

### 4. Analyze and Match Symptoms

Based on retrieved information:
1. **List possible conditions** sorted by likelihood
2. **Match symptoms** to condition presentations
3. **Note key differentiators** between similar conditions
4. **Identify red flags** requiring immediate medical attention

### 5. Structure the Response

Provide analysis in this format:

```
## 症状分析

### 可能的原因

1. **[疾病名称]** (可能性：高/中/低)
   - 典型症状：...
   - 为什么匹配：...
   
2. **[疾病名称]** (可能性：高/中/低)
   - 典型症状：...
   - 为什么匹配：...

### 建议就诊科室

- **推荐科室**：[科室名称]
- **其他选择**：[其他相关科室]

### 建议采取的措施

1. 尽快就医，寻求专业诊断
2. [具体的自我护理建议，如适用]
3. 注意观察症状变化

---
[医疗免责声明]
```

### 6. Include Medical Disclaimer

**Read references/medical_disclaimer.md** for the complete disclaimer template.

**Always include the medical disclaimer at the end of the response.**

For first analysis in a conversation, use the full disclaimer.
For subsequent messages, can use shortened version:
> ⚠️ 提醒：以上分析仅供参考，请务必咨询专业医生获取准确诊断。

## Important Guidelines

### DO:
- ✅ Search multiple authoritative sources before making inferences
- ✅ Cite the medical resources used in analysis
- ✅ Include appropriate medical disclaimers
- ✅ Ask for clarification if symptoms are vague
- ✅ Recommend consulting healthcare professionals
- ✅ Provide emergency warnings when symptoms suggest urgency

### DON'T:
- ❌ Provide definitive diagnosis (always state it's speculative)
- ❌ Recommend specific medications without professional guidance
- ❌ Ignore emergency symptoms
- ❌ Skip the medical disclaimer
- ❌ Rely on single source for analysis
- ❌ Provide analysis for serious conditions without emphasizing need for immediate medical attention

## References

This skill includes the following reference files:

- **references/medical_disclaimer.md**: Complete medical disclaimer template with Chinese and English versions. **MUST be included in every analysis.**

- **references/medical_resources.md**: List of authoritative medical resources (Chinese and international), search strategies, and source quality assessment guidelines.

## Example Interactions

**Example 1: Simple symptom inquiry**
```
User: 我头痛、发热、咳嗽，可能是什么病？

Assistant: [Searches dxy.com and mayoclinic.org]
          [Provides analysis of possible conditions: cold, flu, COVID-19, etc.]
          [Recommends internal medicine department]
          [Includes medical disclaimer]
```

**Example 2: Asking for department recommendation**
```
User: 小孩发烧38.5度，流鼻涕，应该挂什么科？

Assistant: [Searches for pediatric fever symptoms]
          [Recommends pediatric department]
          [Provides home care suggestions]
          [Includes medical disclaimer]
```

**Example 3: Emergency symptoms**
```
User: 我胸痛，呼吸困难，左臂发麻

Assistant: [Immediately warns about emergency]
          [Suggests possible causes (heart attack, etc.)]
          [Strongly recommends immediate ER visit]
          [Includes medical disclaimer]
```

## Search and Resource Usage

When searching for medical information:

1. **Start with web_fetch** for specific medical websites
2. **Use online-search skill** for broader searches if web_fetch is insufficient
3. **Cross-reference** findings across multiple authoritative sources
4. **Extract relevant information**: possible conditions, typical symptoms, when to see doctor, recommended specialty
5. **Cite sources** in the analysis

For severe or complex symptoms, also consider searching PubMed or medical literature databases.

## Limitations

This skill:
- Does NOT replace professional medical diagnosis
- Can ONLY provide reference information based on symptoms described
- Relies on available online medical resources
- Should NOT be used for self-diagnosis or treatment decisions

Always emphasize the importance of consulting healthcare professionals.
