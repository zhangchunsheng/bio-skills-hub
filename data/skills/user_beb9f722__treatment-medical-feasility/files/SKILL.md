---
name: "treatment-feasibility"
description: "Analyzes treatment feasibility for a diagnosed disease. Invoke when user mentions a confirmed disease name and asks about treatment options, whether it's curable, or wants hospital/doctor recommendations for a specific condition."
---

# 疾病治疗可行性分析 (Treatment Feasibility Analysis)

## Overview

This skill helps patients and their families understand the current state of treatment for a diagnosed disease. Given a confirmed diagnosis and relevant examination materials (CT, lab results, MRI, etc.), it provides: treatment feasibility assessment, multiple treatment plans, and recommendations for leading hospitals, departments, and doctors in mainland China.

## When to Invoke

- User mentions a specific diagnosed disease and asks "能治吗", "怎么治", "有什么治疗方案"
- User uploads medical examination reports (CT, MRI, pathology, blood tests) and asks for treatment analysis
- User asks "哪个医院看这个病好", "推荐什么医生", "这个病去哪里看"
- User wants a second opinion on treatment options for a confirmed condition

## CRITICAL: Scope Limitation

**This skill provides INFORMATION ONLY, not medical advice.** It helps users understand the treatment landscape so they can have more informed conversations with their doctors. ALL treatment decisions must be made by qualified physicians.

## Input Requirements

### Essential Information (must request if not provided):
- **Disease name**: The confirmed diagnosis (e.g., "肺腺癌 IIIA期", "特发性肺纤维化")
- **Stage/Severity** (if applicable): Disease stage, grade, or severity classification
- **Patient basic info**: Age, gender (relevant for treatment selection)

### Supplementary Information (helpful if provided):
- Examination reports: CT, MRI, pathology reports, blood test results, etc.
- Current symptoms
- Previous treatments (if any)
- Other medical conditions / comorbidities
- Allergies or contraindications

### How to Handle Uploaded Medical Documents:
- If user uploads images (CT/MRI photos, lab report photos): Read and extract key findings
- If user uploads PDF files: Extract text and analyze key data points
- If user only describes in text: Work with the description provided
- ALWAYS note: "以下分析基于您提供的信息，具体诊疗方案请以主治医生意见为准"

## Analysis Workflow

### Step 1: Disease Overview & Treatment Feasibility Assessment

Search the web for the latest information on the disease and provide:

**1.1 Disease Summary (in plain language)**
- What is this disease? (用通俗语言解释，比如"肺腺癌就是肺部出现的一种恶性肿瘤")
- What causes it? (简要说明)
- How common is it? (发病率/患病率的通俗描述)

**1.2 Treatment Feasibility Verdict**

Provide a clear, honest assessment:

| Category | Description |
|----------|-------------|
| **可治愈** | 通过现有医疗手段可以完全治愈或长期缓解 |
| **可控制** | 不能完全治愈，但可以有效控制病情、延长生存期、提高生活质量 |
| **难治疗** | 目前缺乏有效治疗手段，以姑息治疗和症状管理为主 |
| **新兴疗法** | 传统治疗效果有限，但有新的临床试验或前沿疗法在探索中 |

**Be honest but hopeful.** If a disease is difficult to treat, say so clearly, but also mention any emerging treatments or clinical trials.

**Important**: The feasibility may depend on the stage/severity. If stage information is available, give stage-specific feasibility.

### Step 2: Treatment Plans (Multiple Options)

Search for the latest treatment guidelines and clinical evidence, then present N feasible treatment options.

**For each treatment plan, provide:**

| Field | Content |
|-------|---------|
| 方案名称 | e.g., "手术治疗", "靶向药物治疗", "免疫治疗" |
| 适用条件 | 哪些患者适合这个方案（分期、体质、基因突变等） |
| 治疗原理 | 用通俗语言解释这个方案是怎么起作用的 |
| 治疗流程 | 大致的治疗过程和时间线 |
| 有效率/预后 | 查找最新的临床数据（如5年生存率、缓解率等） |
| 优点 | 这个方案的好处 |
| 缺点/风险 | 可能的副作用、并发症、局限性 |
| 费用估算 | 大致费用范围（如"约5-15万元"，标注仅供参考） |
| 医保覆盖 | 是否纳入医保/医保报销比例大致情况 |

**Search strategy for treatment options:**
1. Search for "最新 [疾病名] 治疗指南 2025 2026" to find official guidelines
2. Search for "[疾病名] 治疗方案 临床研究 最新进展"
3. Search for "[疾病名] NCCN指南 CSCO指南" (key clinical guideline sources in China)
4. Cross-reference multiple sources for accuracy

**Present options from most conservative to most aggressive (or vice versa), and clearly recommend which is most suitable based on the patient's specific situation.**

**Number of options**: Provide at least 2-3 feasible options. For complex diseases, provide up to 5 options if applicable.

### Step 3: Hospital & Department Recommendations

Search for leading hospitals in mainland China that specialize in treating this disease.

**Search strategy:**
1. Search for "[疾病名] 最好的医院", "[疾病名] 重点专科医院"
2. Search for "复旦版 中国医院专科排名 [相关科室]" for authoritative rankings
3. Search for "[疾病名] 临床试验 医院" for hospitals conducting cutting-edge research
4. Search for "国家临床重点专科 [相关科室] 名单"

**For each hospital recommendation, provide:**

| Field | Content |
|-------|---------|
| 医院名称 | Full name |
| 所在城市 | Location |
| 相关科室 | The specific department to visit |
| 专科排名/荣誉 | e.g., "复旦版专科排名全国第X", "国家临床重点专科" |
| 擅长领域 | Specific strengths related to this disease |
| 是否有临床试验 | Any ongoing clinical trials for this condition |

**Recommended top hospitals to consider (disease-dependent):**
- For cancer: 中国医学科学院肿瘤医院、复旦大学附属肿瘤医院、中山大学肿瘤防治中心、四川省肿瘤医院等
- For neurological: 北京天坛医院、宣武医院、华山医院等
- For cardiovascular: 阜外医院、安贞医院、中山医院等
- Always search for the specific disease's top hospitals rather than assuming

### Step 4: Doctor Recommendations

Search for leading doctors who specialize in this disease.

**Search strategy:**
1. Search for "[疾病名] 知名专家 主任医师"
2. Search for "好大夫在线 [疾病名] 推荐医生" (haodf.com is a major Chinese doctor review platform)
3. Search for "[医院名] [科室名] 专家介绍"

**For each doctor, provide:**

| Field | Content |
|-------|---------|
| 姓名 | Doctor's name |
| 职称 | e.g., 主任医师、教授 |
| 所在医院/科室 | Hospital and department |
| 擅长方向 | Specific expertise relevant to this disease |
| 学术背景 | Key qualifications (院士、学会主委、博导等) |
| 患者评价 | If available from haodf.com or similar platforms |

**Limit**: Recommend 3-5 leading doctors. Do not claim to have exhaustive knowledge — always suggest the user verify on official hospital websites.

### Step 5: Practical Guidance

Provide actionable next steps for the patient:

1. **就诊准备**: What to bring (medical records, imaging CDs, pathology slides, etc.)
2. **挂号建议**: How to register at recommended hospitals (app, website, phone)
3. **转诊/会诊**: If a second opinion is needed, how to get one
4. **临床试验**: If applicable, how to find and enroll in clinical trials (e.g., 中国临床试验注册中心)
5. **医保/费用**: Tips on medical insurance coverage and financial assistance

### Step 6: Output the Full Report

The report MUST be delivered in **two formats simultaneously**:

1. **Markdown text in chat** — for immediate reading and review
2. **PDF file** — for saving, printing, and sharing with family/doctors

#### 6.1 Markdown Output Structure (in chat)

Structure the final output in chat:

```
# [疾病名] 治疗可行性分析报告

## 一、患者信息与检查结果汇总
## 二、疾病概述
## 三、治疗可行性评估
## 四、当务之急
## 五、可选治疗方案（N种）
### 方案一：...
### 方案二：...
### 方案三：...
## 六、方案选择建议
## 七、推荐医院与科室
## 八、推荐专家
## 九、就诊建议与下一步行动
## 十、重要提醒

> ⚠️ 免责声明：本报告仅供参考，不构成医疗建议。具体诊疗方案请遵医嘱。
```

#### 6.2 PDF Export (MUST generate)

After completing the markdown report in chat, **ALWAYS generate a PDF file** using Python `reportlab`.

**Workflow:**

1. Write a Python script in the temp working directory (`c:\Users\Michael XUE\.trae-cn\work\...`) to generate the PDF
2. Run the script to produce the PDF
3. Save the final PDF to the final workspace folder:
   ```
   C:\Users\Michael XUE\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a5f0217599cc8d94824d568\[疾病名]_治疗可行性分析报告.pdf
   ```
4. Provide the PDF file link to the user using `computer://` protocol

**PDF Content Requirements:**
- Must contain ALL sections from the markdown report
- Must include a cover page with title, report date, and medical disclaimer
- Must use styled tables for data presentation
- Must be readable in both print and digital formats
- File name should be descriptive and include the disease name

**PDF Technical Implementation (reportlab):**

Use the following pattern (adapt content to the specific disease):

```python
import os, platform
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak, KeepTogether
from reportlab.lib import colors

# 1. Register CJK font (critical for Chinese)
system = platform.system()
font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"]
cjk_font = None
for fp in font_paths:
    if os.path.exists(fp):
        pdfmetrics.registerFont(TTFont("CJKFont", fp, subfontIndex=0))
        cjk_font = "CJKFont"
        break

# 2. Define professional styles
styles = {
    'title': ParagraphStyle('Title', fontName=cjk_font, fontSize=22, leading=28,
        textColor=HexColor('#1a365d'), spaceAfter=14, alignment=1, wordWrap='CJK'),
    'subtitle': ParagraphStyle('Subtitle', fontName=cjk_font, fontSize=12, leading=16,
        textColor=HexColor('#4a5568'), spaceAfter=20, alignment=1, wordWrap='CJK'),
    'warning': ParagraphStyle('Warning', fontName=cjk_font, fontSize=10, leading=14,
        textColor=HexColor('#c53030'), spaceAfter=16, alignment=1, wordWrap='CJK'),
    'h1': ParagraphStyle('H1', fontName=cjk_font, fontSize=16, leading=22,
        textColor=HexColor('#1a365d'), spaceBefore=20, spaceAfter=10, wordWrap='CJK'),
    'h2': ParagraphStyle('H2', fontName=cjk_font, fontSize=13, leading=18,
        textColor=HexColor('#2b6cb0'), spaceBefore=14, spaceAfter=6, wordWrap='CJK'),
    'body': ParagraphStyle('Body', fontName=cjk_font, fontSize=10, leading=15,
        textColor=HexColor('#2d3748'), spaceBefore=0, spaceAfter=8, wordWrap='CJK'),
    'caption': ParagraphStyle('Caption', fontName=cjk_font, fontSize=8, leading=11,
        textColor=HexColor('#718096'), alignment=1, spaceBefore=4, spaceAfter=8, wordWrap='CJK'),
}

# 3. Styled table helper
def styled_table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), cjk_font),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f7fafc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f7fafc'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
    ])
    return t

# 4. Document setup
doc = SimpleDocTemplate(
    output_pdf_path, pagesize=A4,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.6*inch, bottomMargin=0.6*inch
)

# 5. Build story
story = []
# Cover page
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph("[疾病名]", styles['title']))
story.append(Paragraph("治疗可行性分析报告", styles['title']))
story.append(Paragraph(f"报告日期：{today}", styles['subtitle']))
story.append(Paragraph("<b>免责声明：本报告仅供参考，不构成医疗建议。具体诊疗方案请以主治医生意见为准。</b>", styles['warning']))
story.append(PageBreak())

# Content sections...
# Use KeepTogether([styled_table(...)]) for small tables to keep them on one page
# Use Paragraph(text, styles['body']) for body text
# Use styles['h1'] and styles['h2'] for headings
# Let content flow naturally — avoid excessive PageBreak and KeepTogether

doc.build(story)
```

**PDF Pagination Rules:**
- Use `PageBreak()` ONLY once after the cover page
- Let headings and paragraphs flow naturally across pages
- Use `KeepTogether([...])` only for small tables and image+caption pairs
- Use `LongTable(..., repeatRows=1)` for large tables that may span multiple pages
- Never add `PageBreak()` before every section — this wastes paper

**User Delivery:**
After PDF is generated, present it to the user like:
```
报告已完成，PDF文件已生成，点击即可下载：
[[疾病名] 治疗可行性分析报告](computer://...)
```

## Important Rules

- **ALWAYS search the web for the latest information** — medical knowledge changes rapidly, do not rely solely on training data
- **ALWAYS include the medical disclaimer** at the top and bottom of every response
- **Use plain language (通俗版)** — explain medical terms when they first appear, use analogies when helpful
- **Be honest about uncertainties** — if evidence is limited, say so
- **Never guarantee outcomes** — use language like "根据临床数据, 大约X%的患者...", not "一定能治好"
- **Never recommend against following the current doctor's advice** — frame this as supplementary information for a more informed discussion
- **Cite sources** — include URLs for all web-sourced medical information
- **Note data freshness** — medical guidelines are updated periodically; note the most recent guideline version referenced
- **If the disease is a medical emergency** (e.g., acute conditions requiring immediate treatment), strongly advise the user to seek immediate medical attention
- **Respect patient privacy** — do not store or share any patient-specific medical information