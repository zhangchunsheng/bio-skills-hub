---
name: med-ppt-ai-eval
description: 医学生 AI 辅助医学小讲课 PPT 的鼓励性评价技能。当教师需要评价学生提交的医学小讲课 PPT 作业（含 PPT 成品与 AI 交互记录）时使用；支持 zip 压缩包（先解压并全面阅读全部文件）、单个或多个学生作业；每名学生输出一份独立互动 HTML 评估报告，含学生姓名、能力维度雷达图、具体修改意见及理由。触发词：评价PPT、医学小讲课评价、AI辅助PPT评分、批改医学PPT作业、评估学生PPT、PPT评价标准。
agent_created: true
---

# 医学生 AI 辅助医学小讲课 PPT 评价

## Overview

本技能用于"AI 素养提升探索性评价"：同时评估学生的 **PPT 成品质量（55 分）** 与 **AI 交互能力（45 分）**，以鼓励性语言输出每名学生一份的独立互动 HTML 评估报告。**严禁出现"不及格"等负面表述**，全部采用正向激励语言。

## 核心原则（不可违背）

1. **先读后评**：必须全面阅读作业包内所有文件（PPT、AI 交互记录、披露单、核验表、反思等）后方可评分，禁止只看 PPT 就下结论。
2. **鼓励性评价**：严格遵守 `references/rubric.md` 第六节"反馈语言规范"——先亮点后建议，每条建议含"建议+理由+可操作做法+改写示范"，禁用否定性词汇。
3. **每生一份报告**：每位学生输出一份独立 HTML 报告，命名为 `评估报告_<姓名>.html`，可独立打开、方便教师转发。
4. **发现真实患者隐私信息**：立即停止该生评价，不生成学生版报告，仅向教师提示需先完成脱敏处置。

## 工作流程

### 第 1 步：接收与解压

- 若收到 zip 文件，用脚本解压（自动修复中文文件名乱码）：

```bash
python scripts/unzip_assignment.py <zip路径>
```

- 若收到文件夹或散文件，直接进入第 2 步。
- 若一个 zip 内含多名学生的子文件夹，逐一处理，每名学生生成一份独立报告。

### 第 2 步：清点文件并识别角色

阅读解压后的文件清单，为每份文件标注角色：

| 角色 | 常见形态 |
|---|---|
| PPT 成品 | .pptx / .ppt / .pdf |
| AI 交互记录 | 对话导出 txt/md/html/json、截图、链接清单 |
| AI 使用披露单 | docx/md/txt |
| 主张-证据核验表 | xlsx/docx/md |
| 反思文档 | docx/md/txt |
| 其他素材 | 图片、讲稿、大纲 |

### 第 3 步：全面阅读全部材料

- **PPT**：用脚本提取全部幻灯片文本（含表格与备注页），再通读提取结果：

```bash
python scripts/extract_pptx.py <pptx路径> <输出md路径>
```

如需查看版式、配色、图文比例等视觉信息，按可用性依次选择：
   - 环境有 LibreOffice 时：`soffice --headless --convert-to pdf` 后转图片逐页查看；
   - 无 LibreOffice 时：pptx 本质是 zip，可解压后读取 `ppt/theme/theme1.xml` 中的主题配色（`a:accent1`–`a:accent6` 的 srgbClr 值）判断配色是否克制统一，并结合提取结果中的 `[图片 xN]` 标记与文字量评估图文比例；
   - 视觉信息确实无法获取时，依据文本层级与版式一致性按锚定中间等级评分，并在证据中注明"视觉维度基于结构信息评估"。
- **AI 交互记录**：逐份完整阅读，统计总轮数与有效轮数（引发实质修改/核验/新增素材的轮次），标记纠错实例与递进式提问。
- **docx/xlsx/pdf**：用 python-docx / openpyxl / PyMuPDF 等提取文本后阅读。
- **截图类记录**：逐张查看图片内容。

### 第 4 步：加载评分规则并逐项评分

阅读 `references/rubric.md`，按其标准执行：

1. **前置合规确认**：脱敏 / AI 披露 / 引用可定位 / 素材来源，四项逐一检查（不扣分，缺失写入"温馨提示"）。
2. **9 个子维度逐项评级（0–4）**：P1–P5（PPT 成品，55 分）与 A1–A4（AI 交互，45 分），每项记录评分证据（页码 / 对话轮次）。
3. **换算得分**：子维度得分 = 权重 × 等级 ÷ 4，保留 1 位小数；总分 = 各子维度之和。
4. **确定成长树等级**：🌳 硕果累累(90–100) / 🌲 枝繁叶茂(80–89) / 🌿 茁壮成长(70–79) / 🌱 破土新苗(55–69) / 🌰 蓄力种子(<55)。

### 第 5 步：生成互动 HTML 报告

1. 将评估数据整理为下述 JSON，保存为临时文件（如 `data_<姓名>.json`）。
2. 用脚本将 JSON 注入模板，生成独立报告（自动处理转义，避免手工替换出错）：

```bash
python scripts/fill_report.py assets/report_template.html data_<姓名>.json 评估报告_<姓名>.html
```

JSON 结构：

```json
{
  "student_name": "张三",
  "topic": "作业主题",
  "date": "YYYY-MM-DD",
  "total_score": 82.5,
  "ppt_score": 44.0,
  "ai_score": 38.5,
  "level": {"emoji": "🌲", "name": "枝繁叶茂", "comment": "表现优秀，距示范仅一步之遥"},
  "impression": "2-3句正向开场，点名最值得肯定的具体之处",
  "dimensions": [
    {"id": "P1", "name": "核心知识与内容表达", "weight": 15, "grade": 3, "score": 11.3, "evidence": "评分依据，引用页码/轮次"},
    {"id": "P2", "name": "循证引用与来源可靠性", "weight": 12, "grade": 3, "score": 9.0, "evidence": "..."},
    {"id": "P3", "name": "学术风格与教学规范", "weight": 10, "grade": 3, "score": 7.5, "evidence": "..."},
    {"id": "P4", "name": "文字量与图文比例", "weight": 10, "grade": 3, "score": 7.5, "evidence": "..."},
    {"id": "P5", "name": "配色与视觉呈现", "weight": 8, "grade": 3, "score": 6.0, "evidence": "..."},
    {"id": "A1", "name": "对话逻辑与提问质量", "weight": 12, "grade": 3, "score": 9.0, "evidence": "..."},
    {"id": "A2", "name": "错误识别与纠正能力", "weight": 15, "grade": 3, "score": 11.3, "evidence": "..."},
    {"id": "A3", "name": "对话轮数记录与效率", "weight": 8, "grade": 3, "score": 6.0, "evidence": "总X轮/有效Y轮"},
    {"id": "A4", "name": "多任务协同利用", "weight": 10, "grade": 3, "score": 7.5, "evidence": "..."}
  ],
  "highlights": [{"title": "亮点标题", "detail": "具体证据（页码/轮次）"}],
  "suggestions": [{"dimension": "P2", "title": "建议标题", "reason": "理由说明", "action": "可操作做法", "example_before": "修改前示例", "example_after": "修改后示范"}],
  "notices": ["温馨提示（合规缺失项，如无则留空数组）"],
  "closing": "一句鼓励性寄语"
}
```

要求：亮点 ≥3 条；成长建议 3–6 条，按优先级排序；`example_before`/`example_after` 必须来自该生作业的真实片段与针对性改写。

### 第 6 步：自检与交付

1. 对照 `references/rubric.md` 第六节通读报告全文，清除任何否定性表述。
2. 在浏览器中打开报告确认渲染正常（雷达图、折叠面板、"另存为 PDF"按钮可生成下载）。
3. 向用户交付报告文件（每生一份），并简述总体评价结果。

## Resources

- `references/rubric.md` — 完整评分规则：权重、0–4 级行为锚定、成长树等级、反馈语言规范、评分流程。**评分前必读**。
- `assets/report_template.html` — 自包含互动报告模板（内嵌 SVG 雷达图、折叠面板、"另存为 PDF"一键下载按钮，已内嵌 html2canvas+jsPDF，离线可用，无外部依赖），替换 `__REPORT_DATA__` 即可生成报告。
- `scripts/unzip_assignment.py` — 解压作业 zip，自动修复中文文件名乱码，输出文件清单。
- `scripts/extract_pptx.py` — 提取 PPTX 全部文本（标题/正文/表格/备注），依赖 python-pptx。
- `scripts/fill_report.py` — 将评估 JSON 注入报告模板生成独立 HTML（自动安全转义），用法：`python scripts/fill_report.py <模板> <数据json> <输出html>`。
