---
name: clinical-pharmacy-newsletter-0012-psm2026
description: 月度临床药讯生成器。当需要编写、整理、汇总临床科室药讯、用药指南更新摘要、药物安全通报、季度药学通讯时使用。覆盖抗感染为主，可扩展抗凝、肿瘤支持治疗、疼痛管理等领域。输出符合科室排版规范的Word文档。触发词：药讯、用药指南更新、科室药讯、月度药讯、季度药讯、pharmacy newsletter、guideline digest、药物安全通报、药讯排版、药讯模板、药学通讯。
---

# 临床药讯生成器

## 概述

月度临床药讯生成器。固定5大栏目（卷首语/指南更新/药物安全警示/文献速递/新药速览），输出符合科室排版规范的.docx文件。AI生成初稿，药师审核签字后发布。

## 工作流程

### Step 1: 确认本期参数

向用户确认：
- 本期月份与覆盖时间范围（默认上月1日至本月1日）
- 是否设专题（如"碳青霉烯耐药时代"专题）
- 关注领域（默认抗感染，可叠加抗凝/肿瘤支持/疼痛管理）
- 院内素材是否就绪（ADR案例、新药清单）

### Step 2: 素材收集

按栏目分头收集：

- **指南更新**：按 `references/guide_sources.md` 中列出的权威来源检索近30天更新
- **药物安全警示**：用户提供本期院内ADR案例（脱敏后）+ 国家药品不良反应监测中心通报 + FDA/EMA安全警示
- **文献速递**：PubMed检索本期高影响文献（IF>5或被指南引用），CNKI检索中文核心
- **新药速览**：用户提供本期新引进药品清单

### Step 3: 内容撰写

每个栏目按以下规则撰写：

- 每条更新写明：**关键变更点** + **与旧版/既往做法差异** + **临床影响** + **证据等级** + **来源与发布日期**
- 翻译内容标注"机翻待药师校对"
- 严重ADR/新的ADR标注上报时限（死亡/危及生命24h，新的严重15d，一般30d）
- 文献摘要标注PMID/DOI与证据等级（按OCEBM或GRADE）

### Step 4: 生成Word文档

运行 `scripts/generate_newsletter.py`：

```bash
"C:/Users/HUAWEI/.workbuddy/binaries/python/envs/default/Scripts/python.exe" scripts/generate_newsletter.py --input content.json --output 药讯_YYYY年MM月.docx
```

输入JSON结构见 `references/content_schema.md`。脚本自动生成封面、目录、页眉页脚、栏目分节。

### Step 5: 药师审核与发布

- AI生成初稿 → 药师逐栏目审核 → 必要时人工校对翻译 → 签字发布
- 严重安全警示需科室主任复核
- 发布前再次确认患者信息已脱敏

## 栏目结构（5大固定栏目）

| 栏目 | 内容要点 | 篇幅建议 |
|------|----------|----------|
| 卷首语 | 本期主题、3-5条要点提示 | 100-200字 |
| 指南更新 | 国内外指南变更点摘要+临床影响 | 800-1500字 |
| 药物安全警示 | 院内ADR案例+国家通报+风险提示 | 600-1000字 |
| 文献速递 | 3-5篇高影响文献摘要 | 每篇200-300字 |
| 新药速览 | 新引进药品的适应症/用法/注意事项/医保属性 | 每药200-300字 |

## 数据来源

权威指南库、数据库、期刊清单见 `references/guide_sources.md`。按治疗领域分类，含URL与检索要点。

## 脱敏与合规（硬约束）

1. **患者脱敏**：ADR案例剥离姓名、住院号、床号、身份证、电话；保留年龄、性别、诊断、用药史、ADR表现、转归
2. **翻译校对**：所有外文翻译标注"机翻待药师校对"，发布前必须人工校对
3. **上报时限标注**：严重ADR/新的ADR按国家ADR监测中心要求标注上报时限
4. **引用规范**：所有指南/文献/通报标注来源全称、版本号、发布日期；网页内容标注访问日期
5. **不替代临床决策**：药讯为科室内部学习材料，不作为临床用药唯一依据

## 内容JSON Schema

详见 `references/content_schema.md`。核心结构：

```json
{
  "issue": {"year": 2026, "month": 8, "topic": "碳青霉烯耐药时代"},
  "sections": {
    "preface": "...",
    "guideline_updates": [{"title":"...","changes":"...","impact":"...","evidence_level":"A","source":"..."}],
    "safety_alerts": [{"title":"...","case":"...","national_alert":"...","risk":"...","report_deadline":"15d"}],
    "literature": [{"title":"...","journal":"...","pmid":"...","summary":"...","evidence_level":"B"}],
    "new_drugs": [{"name":"...","indication":"...","dosage":"...","cautions":"...","insurance":"..."}]
  }
}
```

## 依赖

- Python 3.13+（使用managed环境 `C:/Users/HUAWEI/.workbuddy/binaries/python/envs/default/`）
- python-docx（pip install python-docx）
- 字体：宋体（正文）、黑体（标题）、Times New Roman（英文/数字）

## 共享与部署（分发给其他药师/科室）

本 skill 设计原则：**skill 是模板，邮箱与自动化是各使用者的实例配置，不随 skill 分发。**

### 为什么邮箱不能写进 skill

`.skill` 文件会原样分发给他人。若把邮箱硬编码进 SKILL.md 或脚本，别人一运行药讯就会发到你的邮箱，且暴露你的地址。因此本 skill **只负责生成 docx，发送动作作为运行时参数**，由触发方在对话或自动化 prompt 中指定目标邮箱。

### 接收方部署步骤

1. **安装 skill**：导入 `clinical-pharmacy-newsletter.skill`（WorkBuddy 左侧「技能」→ 导入）
2. **连接邮箱 connector**：左侧「连接器」连一个可发外部邮件的通道 —— QQ邮箱 / 网易邮箱 / IMAP 其一（连接后点「信任」）；仅用智能体内部收件箱则连 agent-mail 即可
3. **自建每月自动化**（关键，无法分发）：在 WorkBuddy 创建一个 recurring 自动化，例如
   - 名称：月度临床药讯
   - 调度：每月 1 号
   - prompt：`调用 clinical-pharmacy-newsletter skill，检索近30天抗感染指南更新/国家ADR通报/PubMed-CNKI文献，生成5栏目药讯Word（院内ADR案例与新药速览留空标"待药师补充"），保存后通过已连邮箱connector发送到 <接收方自己的邮箱>`
4. 接收方把 `<接收方自己的邮箱>` 换成自己的地址即可，无需改 skill 源码

### 邮箱模式选择

- **个人邮箱**：每人自动化填自己邮箱，私密、各管各的。适合各药师在自己科室独立出刊。
- **科室公共邮箱**（如 `pharmacy@hospital.com`）：统一发公共箱、轮值查看。适合药学部统一出刊、多人共享。

无论哪种，邮箱都只出现在各人本地自动化配置里，**不进 skill 文件**，分发安全。
