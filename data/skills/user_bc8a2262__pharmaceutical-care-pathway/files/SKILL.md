---
name: pharmaceutical-care-pathway-generator
description: >
  通用药学监护路径模板生成器。支持多临床指南交叉参考，可接受任意疾病名称，自动生成完整的药学监护路径文档套件（HTML+JSON+XML+DOC）。
  支持院前-院中-院后全周期时序规划，适用于长疗程患者的全程药学监护管理。支持单病种生成和批量多病种生成。
  触发词：生成药学监护、药学监护模板、批量生成药学监护路径、为XX疾病生成药学监护、多指南药学监护、院前院中院后药学监护。
agent_created: true
---

# 通用药学监护路径模板生成器

## 技能概述

本技能为任意临床诊断/病种一键生成完整的药学监护路径文档套件，支持**多临床指南交叉参考**和**院前-院中-院后全周期时序规划**，包含四大类共7个文件：
1. **HTML 药学监护计划** — 综合监护计划文档（含三阶段时序线图、10个PC子类表单、监护要点）
2. **HTML 治疗路径线图** — 独立时序可视化页面（院前/院中/院后三阶段高亮）
3. **JSON 监护路径** — 结构化路径数据（三阶段、节点、优先级、多指南来源标注）
4. **JSON 药学服务表单** — PC-01到PC-10结构化表单定义
5. **JSON 监测项目** — 药品/检验/检查/注意事项四大类
6. **XML 药学监护模板** — 结构化XML数据（含内联样式标签，参照PharmaceuticalCareTemplate标准）
7. **HTML 药学监护章节** — 书籍格式三章文档

### 核心能力升级

- **多指南支持**：可同时引用多个临床指南（如NCCN+CSCO+国家临床路径），自动交叉校验并标注证据来源
- **全周期时序**：针对长疗程患者，时序覆盖院前（入院前评估与用药准备）、院中（住院治疗全程）、院后（出院随访计划）三大阶段
- **XML结构化输出**：生成符合PharmaceuticalCareTemplate标准的XML文件，含内联样式标签、DRG编码、药物相互作用、每日监护节点

## 触发条件

- 用户指定疾病名称生成药学监护路径
- 批量生成多个病种的药学监护路径
- 需要药学监护HTML模板/JSON数据/XML数据/DOC文档
- 用户指定多个临床指南进行交叉参考
- 涉及长疗程（住院>14天或需长期随访）患者的药学监护规划
- 需要院前-院中-院后全周期药学监护计划

---

## 核心执行流程（7步法）

### 第0步：输入确认与解析

接收用户输入后，提取以下信息：
- **疾病名称**（必需）：中文通用名，支持多个病种批量输入
- **ICD-10编码**（可选，如未提供则自动推断）
- **就诊科室**（可选，如未提供则根据疾病自动匹配）
- **标准住院日**（可选，如未提供则使用通用框架）
- **临床指南列表**（可选）：用户可指定一个或多个指南来源
  - 单指南：如"依据《2024 CSCO胰腺癌诊疗指南》"
  - 多指南：如"依据《NCCN指南2025》和《CSCO指南2024》及国家临床路径"
- **疗程类型判定**（自动）：根据疾病特征和住院天数判定是否需要全周期时序
  - **标准疗程**（住院<=14天）：仅生成院中时序
  - **长疗程**（住院>14天，或慢性病/肿瘤/需长期随访）：自动启用院前-院中-院后三阶段时序
- **是否批量**：检查输入是否包含多个病种

**多指南解析规则：**
- 用户指定多个指南时，逐一提取每个指南的：名称、发布机构、发布年份、证据等级
- 按优先级排序：国家级规范 > 学会指南 > 专家共识
- 多指南冲突时，在文档中标注分歧点并给出推荐方案

**全周期时序阶段定义：**
```
院前阶段（Pre-hospital）：
  - 时间范围：入院前1-7天（或入院当日评估）
  - 核心内容：既往用药梳理、用药重整预备、风险评估、入院用药准备
  - 药学监护：PC-02（患者分组预评估）、PC-03预备（既往用药清单）

院中阶段（In-hospital）：
  - 时间范围：入院D1至出院DN
  - 核心内容：全程住院治疗与药学监护
  - 药学监护：PC-01至PC-09全部子类

院后阶段（Post-hospital / Follow-up）：
  - 时间范围：出院后7天/14天/30天/3个月/6个月/12个月
  - 核心内容：用药依从性随访、疗效评估、不良反应监测、用药调整
  - 药学监护：PC-07（出院用药教育）、PC-10（药学随访）
```

**输出目录规则：**
- 单病种：`药学监护路径/{疾病名称}/`
- 多病种：每个病种独立子目录

### 第1步：临床路径与指南信息采集

**信息采集优先级（按顺序尝试，高优先级来源优先，低优先级仅在缺失时补充）：**

**优先级1（最高）：用户指定来源 — 多指南/药品说明书/诊疗指南**

用户可通过以下方式指定来源：
- **上传文件**：药品说明书（PDF/Word/图片）、诊疗指南全文或节选、临床路径文档
  - 药品说明书：直接提取适应症、用法用量、禁忌症、不良反应、药物相互作用、特殊人群用药、药动学参数
  - 诊疗指南：提取治疗原则、推荐方案（证据等级）、药物选择逻辑、监护要点、随访建议
  - 临床路径文档：提取标准住院日、时间节点、诊疗流程、用药节点
  - **多文件支持**：可同时上传多个指南文件，系统逐一解析并交叉校验
- **指定网址**：用户提供具体URL（支持多个），使用WebFetch抓取页面内容
- **指定指南名称**：如"依据《2024 CSCO胰腺癌诊疗指南》和《NCCN Pancreatic Cancer Guidelines 2025》"，使用WebSearch定向搜索每个指南

**多指南交叉校验规则：**
1. 逐一提取每个指南的：治疗原则、推荐方案、药物选择、监护要点、随访建议
2. 建立对比矩阵：对每个关键决策点（如一线用药、疗程、监测频次）逐一对比各指南推荐
3. 冲突处理：
   - 优先级：国家级规范（卫健委临床路径）> 国际指南（NCCN/ESC/KDIGO等）> 国内学会指南（CSCO/中华医学会等）> 专家共识
   - 同级别冲突：以最新版本为准，并在文档中标注分歧
   - 药品用法用量：始终以药品说明书为最终依据
4. 输出统一推荐方案，并标注每个建议的来源指南和证据等级

**处理规则：**
- 用户提供药品说明书时，所有药品的用法用量、注意事项、监护要点**必须以说明书为准**，不得被其他来源覆盖
- 用户提供诊疗指南时，治疗原则、药物选择、监护要点**以指南为准**，网络搜索仅补充指南未覆盖的细节
- 多个用户来源之间存在冲突时，以**最新版本**或**发布机构级别更高**者为准（国家级 > 学会级 > 专家共识）
- 用户来源覆盖的信息项，**跳过**对应网络搜索步骤

**优先级2：内置参考模板**

当用户来源未覆盖某些信息项时，参考以下内置资源：
- `references/pathway_templates.md` — 常见疾病临床路径时序框架（含5个常见病种完整路径 + 通用模板 + 院前/院中/院后框架）
- `references/pharmacy_care_forms.md` — PC-01到PC-10表单字段定义标准
- `references/chaa_standards.md` — 中国医院协会药事管理委员会团体标准（SOAP格式、用药重整规范、处方审核规范等）
- `assets/care_plan_template.html` — HTML文档结构模板
- `assets/pathway_timeline.html` — 时序线图模板
- `assets/pharmaceutical_care_template.xml` — XML药学监护模板（含内联样式标签规范）

**优先级3（最低）：联网检索权威网站**

仅在用户来源和内置模板**均未覆盖**的信息项时，才执行网络搜索。搜索策略如下：

**搜索指令（并行执行）：**
- `"{疾病名称} 临床路径 标准住院流程"` — 标准住院天数、诊疗流程
- `"{疾病名称} 诊疗指南 2024/2025 治疗方案 用药"` — 治疗原则和用药方案
- `"{疾病名称} 药品说明书 用法用量 监护"` — 药品详细信息
- `"{疾病名称} 围术期 用药方案"` — 手术相关用药（手术病种）
- `"{疾病名称} 药物治疗 监护要点 不良反应"` — 药物监护要点
- `"{疾病名称} 院前评估 用药准备 入院前管理"` — 院前阶段信息（长疗程病种）
- `"{疾病名称} 出院随访 用药依从性 长期管理"` — 院后随访信息（长疗程病种）

**权威网站优先级（搜索结果筛选）：**
1. **国家卫生健康委员会**（nhc.gov.cn）— 临床路径、诊疗规范
2. **NMPA药品审评中心**（cde.org.cn）— 药品说明书数据库
3. **中华医学会/中国医师协会** — 各专科诊疗指南
4. **CSCO/NCCN**（csco.org.cn / nccn.org）— 肿瘤诊疗指南
5. **KDIGO/KDOQI**（kdigo.org）— 肾脏病/内分泌指南
6. **ESC/AHA/ACC** — 心血管疾病指南
7. **国家药监局**（nmpa.gov.cn）— 药品批准信息
8. **药智网/丁香园用药助手**（yaozh.com / dxy.cn）— 药品说明书查询

**病种类型扩展搜索关键词：**
- 手术病种：加搜"围术期抗菌药物预防""术后并发症用药"
- 肿瘤病种：加搜"NCCN/CSCO指南""化疗方案""靶向治疗""免疫治疗""长期随访方案"
- 内科慢性病：加搜"KDIGO/KDOQI指南""长期用药管理""药物剂量调整""出院后随访计划"
- 感染病种：加搜"抗菌药物治疗方案""PK/PD优化""疗程指南"
- 妇科病种：加搜"妊娠期用药安全分级""哺乳期用药"
- **长疗程病种（自动检测）**：加搜"院前用药评估""出院后药学随访""长期用药管理""药物重整院外衔接"

**多指南来源标注规则：**
生成所有文档时，必须标注每项信息的数据来源：
- 来自用户上传文件：标注 `[来源：用户提供的XX说明书/指南]`
- 来自内置模板：标注 `[来源：内置临床路径模板]`
- 来自网络检索：标注 `[来源：XX指南(年份)]` 或 `[来源：XX药品说明书]`
- 多源交叉验证：标注 `[来源：用户指南 + 网络检索交叉验证]`
- **多指南交叉**：标注 `[来源：指南A(年份) + 指南B(年份) 交叉验证]`，并注明证据等级
- **指南冲突项**：标注 `[注意：指南A推荐X，指南B推荐Y，本方案采用X，理由：...]`

**采集输出格式（结构化提取）：**

从搜索结果中提取并结构化为以下字段：
```
疾病信息：
  - 名称（中/英文）
  - ICD-10编码
  - 就诊科室
  - 标准住院天数
  - 疗程类型（标准疗程/长疗程）
  - 治疗原则摘要
  - 诊断要点（3-5条核心要点）
  - 主要检查/检验项目列表
  - 常见合并疾病列表
  - 指南参考文献列表（至少3条，标注来源指南和证据等级）
  - 多指南对比矩阵（如适用）

药物清单：
  每个药品包含：
  - 通用名（中文）+ 英文INN
  - 剂型规格
  - 单次剂量
  - 频次
  - 给药途径
  - 起止时间（Day X - Day Y，或院前/院中/院后阶段标注）
  - 使用原因
  - 注意事项
  - 监护要点
  - 风险等级（高/中/低）
  - 推荐等级（一线/二线/备选）+ 来源指南标注

药物相互作用清单：
  每对相互作用包含：
  - 药物A名称
  - 药物B名称
  - 相互作用机制
  - 临床后果
  - 严重程度（severe/moderate/mild）
  - 处理建议

时间轴节点（三阶段）：
  每个节点包含：
  - 阶段（院前/院中/院后）
  - Day编号（院前用Pre-D1~D0，院中用D1~DN，院后用Post-D7~D365）
  - 阶段名称（入院前评估/入院/术前/手术/术后/出院/随访等）
  - 诊疗行为
  - 护理操作
  - 用药事件
  - 药学监护事件（PC-XX代码）
  - 关键行动标注
```

### 第2步：生成HTML文件

#### 2.1 [病种名]_药学监护计划.html

使用以下完整HTML模板生成（将所有占位符替换为实际内容）：

**HTML结构规范：**

```
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{疾病名称}药学监护计划</title>
  <style>
    /* === 统一医疗蓝绿主题CSS === */
    :root {
      --primary-color: #0B7A75;
      --primary-light: #F0F9F8;
      --primary-dark: #065F5B;
      --accent-color: #17A89D;
      --warning-color: #E85D04;
      --danger-color: #D62828;
      --text-primary: #1A1A2E;
      --text-secondary: #4A4A6A;
      --border-color: #B2DFDB;
      --table-header: #004D40;
      --table-alt: #E0F2F1;
      --phase-pre: #6A1B9A;       /* 院前阶段色 */
      --phase-in: #0B7A75;        /* 院中阶段色 */
      --phase-post: #1565C0;      /* 院后阶段色 */
    }
    /* ... 完整CSS见下方 ... */
  </style>
</head>
<body>
  <!-- 1. 文档头部（封面区）— 含多指南依据标注 -->
  <!-- 2. 患者基本信息区 -->
  <!-- 3. 诊断信息区 -->
  <!-- 4. 治疗方案区（含用药清单表格，含推荐等级标签） -->
  <!-- 5. 多指南依据对照区（如适用） -->
  <!-- 6. 治疗路径时序线图区（三阶段：院前/院中/院后） -->
  <!-- 7. 药学监护计划总览表（三阶段） -->
  <!-- 8. 重点药学监护要点区 -->
  <!-- 9. 药学监护子类表单区（10个可折叠details/summary） -->
  <!-- 10. 药师签名区 -->
</body>
</html>
```

**CSS样式规范（必须内联在`<style>`标签中）：**

以下CSS必须包含在每个HTML文件中（不依赖外部文件）：

- body: font-family "Microsoft YaHei", 微软雅黑, "Heiti SC", 黑体, sans-serif; font-size 12pt; color #1A1A2E
- .page-wrapper: max-width 210mm; margin 0 auto; background white; padding 20px
- .doc-header: border 2.5px solid #065F5B; border-radius 4px
- .doc-header-top: background #065F5B; color white; flex justify-between; padding 10px 16px
- .doc-header-title: background #17A89D; color white; text-align center; font-size 18pt; font-weight bold; padding 12px
- .section: margin-bottom 14px; border 1px solid #B2DFDB; border-radius 4px
- .section-header: background #004D40; color white; padding 7px 14px; font-weight bold
- .section-body: padding 12px 14px; background #F8FDFC
- table: width 100%; border-collapse collapse; font-size 10.5pt
- thead th: background #004D40; color white; padding 7px 10px; text-align center
- tbody tr:nth-child(even): background #E0F2F1
- tbody td: padding 7px 10px; border 1px solid #B2DFDB; vertical-align top
- .info-grid: display grid; grid-template-columns repeat(3, 1fr); border 1px solid #B2DFDB
- .info-cell: padding 7px 12px; border-right/bottom 1px solid #B2DFDB
- .info-cell-label: font-size 9pt; color #4A4A6A
- .info-cell-value: font-size 11pt; font-weight 600; border-bottom 1px dashed #ccc; min-height 20px
- .care-card summary: background #0B7A75; color white; padding 8px 14px; cursor pointer; font-weight bold
- .care-card[open] summary::after: content "▲ 收起"
- .alert-box: padding 10px 14px; border-radius 4px; margin 8px 0
- .alert-warning: background #FFF8E1; border-left 4px solid #E85D04
- .alert-danger: background #FFEBEE; border-left 4px solid #D62828
- .alert-info: background #F0F9F8; border-left 4px solid #17A89D
- .badge: display inline-block; padding 2px 8px; border-radius 12px; font-size 9pt
- .badge-high-risk: background #FFEBEE; color #D62828
- .badge-pending: background #FFF3E0; color #E65100
- .signature-section: border 1px solid #B2DFDB; border-radius 4px; display grid; grid-template-columns repeat(3, 1fr)
- **.phase-pre-header**: background #6A1B9A; color white; padding 5px 14px; font-weight bold（院前阶段标题）
- **.phase-in-header**: background #0B7A75; color white; padding 5px 14px; font-weight bold（院中阶段标题）
- **.phase-post-header**: background #1565C0; color white; padding 5px 14px; font-weight bold（院后阶段标题）
- **.phase-pre-row**: background rgba(106,27,154,0.06)（院前行高亮）
- **.phase-post-row**: background rgba(21,101,192,0.06)（院后行高亮）
- **.recommend-tag**: display inline-block; padding 2px 12px; border-radius 4px; font-weight 600; font-size 12px（推荐等级标签）
- **.recommend-first**: background #e74c3c; color white（一线用药标签）
- **.recommend-second**: background #3498db; color white（二线用药标签）
- **.recommend-alt**: background #95a5a6; color white（备选用药标签）
- **.guideline-source**: font-size 8.5pt; color #4A4A6A; font-style italic（指南来源标注）
- @media print: body background white; .page-wrapper padding 10px; @page size A4; margin 2cm 2.5cm

**各区块内容规范：**

**文档头部：**
```
- 医院名称占位符：××医院
- 文档标题：{疾病名称} 药学监护计划
- 文档编号：PHAR-{YYYYMMDD}-001
- 版本号：V1.0
- 制定日期：当前日期
- 指南依据：列出所有引用的指南名称和年份（多指南时逐一列出）
```

**患者基本信息区（6-9字段网格）：**
```
| 患者姓名 | 性别 | 年龄 |
| 住院号 | 科室/床位号 | 入院日期 |
| 体重/身高 | 肾功能(eGFR) | 过敏史 |
```
所有值为占位符（_______），过敏史标注为红色文字"无/_______"。

**诊断信息区：**
```
| 主要诊断（span 2列，大号字） | ICD-10编码 |
| 次要诊断/合并症（span 3列） | |
| 特殊状态 | 监护分级 | 预期住院天数 |
| 疗程类型（标准疗程/长疗程） | 时序范围（院前/院中/院后） | DRG编码（如适用）|
```

**治疗方案区：**
- 先显示治疗原则摘要（蓝色提示框，含多指南来源标注）
- 然后是药品清单表格，列：序号|药品通用名(INN)|剂型规格|单次剂量|频次|给药途径|开始|预计停用|推荐等级|备注
- 推荐等级使用彩色标签：一线(红色)/二线(蓝色)/备选(灰色)，并标注来源指南

**多指南依据对照区（仅多指南时显示）：**
```
| 决策点 | 指南A推荐 | 指南B推荐 | 本方案采用 | 理由 |
```
逐一列出各指南在关键决策点上的推荐差异和最终选择。

**治疗路径时序线图区（三阶段）：**
使用 `<div class="timeline-diagram">` 包裹，包含：
- 图例（药学监护=绿色、医疗=蓝色、护理=紫色、院前=紫色底、院后=蓝色底）
- **三阶段分区标题**：院前阶段 | 院中阶段 | 院后随访阶段
- 时序内容：每行一个类别（诊疗/护理/用药/药学监护），每列一个Day
- 院前阶段节点使用 `.phase-pre-row` 高亮，院后阶段使用 `.phase-post-row` 高亮

**药学监护计划总览表（三阶段）：**
```
| 阶段 | 时间节点 | 药学监护活动 | 子类代码 | 优先级 | 责任药师 | 计划完成时间 | 完成状态 |
```
按时序从院前到院后排列所有PC活动，阶段列用三色标识，优先级用彩色徽章。

**重点药学监护要点区：**
按疾病特点列出3-8个监护要点，每个用提示框包裹，标注风险等级。长疗程病种须包含院前和院后监护要点。

**药学监护子类表单区（10个可折叠卡片）：**
使用 `<details class="care-card"><summary>PC-XX {名称}</summary><div class="care-card-body">...内容...</div></details>` 结构。10个子类固定为：

| 代码 | 名称 | 卡片内必须包含的疾病特异性内容 |
|------|------|------|
| PC-01 | 药学查房记录表 | SOAP格式框架，列出该病种需重点关注的DTP |
| PC-02 | 患者分组评估表 | 风险评分字段，标注该病种常见高风险因素（含院前预评估） |
| PC-03 | 用药重整表（入院） | BPMH清单模板+差异核对+重点关注药物（衔接院前用药） |
| PC-04 | 用药重整表（转科） | 转科用药差异（如适用） |
| PC-05 | 处方审核记录表 | 四适宜核查要点+该病种特殊审核关注 |
| PC-06 | 处方精简评估表 | 精简原则+该病种可精简药品示例 |
| PC-07 | 出院用药教育记录表 | 出院带药清单+重点教育药品+TEACH-BACK+院后用药衔接指导 |
| PC-08 | 药学综合评估表 | 多维度评估（肾功能/肝功能/营养/依从性等）+院前/院中/院后三次评估 |
| PC-09 | 药学会诊记录表 | 会诊框架+该病种常见会诊问题示例 |
| PC-10 | 药学随访记录表 | 院后随访时间节点（7d/14d/30d/3m/6m/12m）+该病种专项随访内容 |

**药师签名区：**
三列签名：制定药师/上级药师审核/患者知情确认

#### 2.2 [病种名]_治疗路径线图.html

独立时序线图HTML页面，包含：
- 页面头部（疾病名称+版本+日期+多指南依据）
- **三阶段分区标识**：院前（紫色）、院中（绿色）、院后（蓝色）
- 图例（诊疗=蓝色、护理=橙色、药学监护=紫色高亮、用药=青色、院前节点=紫色框、院后节点=蓝色框）
- 时序表格：横轴覆盖院前Pre-D1到院后Post-D365，纵轴4行（诊疗/护理/用药/药学监护）
- 院前阶段列使用紫色渐变背景，院后阶段列使用蓝色渐变背景
- 药学监护行使用高亮背景色标记
- @media print 支持

### 第3步：生成JSON文件

#### 3.1 [病种名]_监护路径.json

标准JSON结构（含三阶段时序和多指南标注）：
```json
{
  "disease_name": "疾病中文名",
  "disease_name_en": "English Name",
  "icd_code": "ICD-10编码",
  "standard_stay_days": N,
  "course_type": "standard | long_term",
  "department": "就诊科室",
  "treatment_principle": "治疗原则摘要",
  "guideline_sources": [
    {
      "name": "指南名称",
      "organization": "发布机构",
      "year": "发布年份",
      "evidence_level": "证据等级"
    }
  ],
  "care_pathway": {
    "pre_hospital": {
      "phase": "院前阶段",
      "days": "Pre-D7 ~ D0",
      "care_activities": [
        {
          "code": "PC-XX",
          "name": "活动名称",
          "time": "触发时间",
          "priority": "高/中/低",
          "content": "具体工作内容描述",
          "notes": "注意事项",
          "guideline_source": "来源指南标注"
        }
      ]
    },
    "in_hospital": {
      "phases": [
        {
          "phase": "阶段名称",
          "days": "D1-D2",
          "care_activities": [
            {
              "code": "PC-XX",
              "name": "活动名称",
              "time": "触发时间",
              "priority": "高/中/低",
              "content": "具体工作内容描述",
              "notes": "注意事项",
              "guideline_source": "来源指南标注"
            }
          ]
        }
      ]
    },
    "post_hospital": {
      "phase": "院后随访阶段",
      "follow_up_schedule": [
        {
          "timepoint": "出院后7天",
          "care_activities": [
            {
              "code": "PC-10",
              "name": "药学随访",
              "content": "随访内容",
              "guideline_source": "来源指南标注"
            }
          ]
        },
        {
          "timepoint": "出院后30天",
          "care_activities": ["..."]
        },
        {
          "timepoint": "出院后3个月",
          "care_activities": ["..."]
        },
        {
          "timepoint": "出院后6个月",
          "care_activities": ["..."]
        },
        {
          "timepoint": "出院后12个月",
          "care_activities": ["..."]
        }
      ]
    }
  },
  "medications": [
    {
      "generic_name_cn": "中文通用名",
      "generic_name_inn": "英文INN",
      "specification": "剂型规格",
      "dose": "单次剂量",
      "frequency": "频次",
      "route": "给药途径",
      "start_day": "开始时间",
      "end_day": "结束时间",
      "phase": "院前/院中/院后",
      "indication": "使用原因",
      "precautions": "注意事项",
      "monitoring_points": ["监护要点1", "监护要点2"],
      "risk_level": "高/中/低",
      "recommend_level": "一线/二线/备选",
      "guideline_source": "来源指南标注"
    }
  ],
  "drug_interactions": [
    {
      "drug_a": "药物A",
      "drug_b": "药物B",
      "mechanism": "相互作用机制",
      "consequence": "临床后果",
      "severity": "severe/moderate/mild",
      "action": "处理建议"
    }
  ],
  "monitoring_points": [
    {
      "category": "分类名称",
      "items": ["要点1", "要点2"],
      "risk_level": "info/warning/danger"
    }
  ],
  "guideline_references": [
    {
      "title": "指南名称(年份版)",
      "organization": "发布机构",
      "evidence_level": "证据等级"
    }
  ]
}
```

#### 3.2 [病种名]_药学服务表单.json

标准JSON结构：
```json
{
  "disease_name": "疾病名称",
  "forms": [
    {
      "form_code": "PC-01",
      "form_name_cn": "药学查房记录表",
      "form_name_en": "Pharmacy Ward Round Record",
      "applicable_phase": "全程住院期",
      "trigger_condition": "每日/隔日查房",
      "disease_specific_notes": "该病种专项说明",
      "fields": [
        {
          "field_name": "字段名称",
          "field_type": "text/select/radio/textarea/date/number",
          "options": ["选项1", "选项2"] | null,
          "required": true/false,
          "risk_flag": "none/warning/danger",
          "disease_specific_note": "该病种填写指导"
        }
      ]
    }
  ]
}
```
共10个form (PC-01到PC-10)。PC-03和PC-07须包含院前用药衔接字段，PC-08和PC-10须包含院后随访字段。

#### 3.3 [病种名]_监测项目.json

标准JSON结构：
```json
{
  "disease_name": "疾病名称",
  "monitoring_categories": {
    "drug_monitoring": [
      {
        "drug_name_cn": "药品中文名",
        "drug_name_inn": "英文INN",
        "specification": "剂型规格",
        "monitoring_items": [
          {
            "item": "监测项目名称",
            "frequency": "监测频次",
            "target_range": "目标范围（如适用）",
            "action_threshold": "异常处理阈值（如适用）"
          }
        ],
        "risk_level": "高/中/低",
        "precautions": "该药使用注意事项"
      }
    ],
    "lab_monitoring": [
      {
        "item": "检验项目名称",
        "frequency": "监测频次",
        "purpose": "监测目的",
        "phase": "院前/院中/院后（标注适用阶段）"
      }
    ],
    "exam_monitoring": [
      {
        "item": "检查项目名称",
        "frequency": "检查频次",
        "purpose": "检查目的",
        "phase": "院前/院中/院后（标注适用阶段）"
      }
    ],
    "precautions": [
      "注意事项1",
      "注意事项2"
    ]
  }
}
```

### 第4步：生成XML文件（新增）

#### [病种名]_药学监护模板.xml

生成符合PharmaceuticalCareTemplate标准的XML文件，参照 `assets/pharmaceutical_care_template.xml` 模板样式。

**XML结构规范：**

```xml
<?xml version="1.0" encoding="utf-8"?>
<PharmaceuticalCareTemplate version="1.0" generated_at="{生成日期时间}">
  <!--药学监护路径模板 - {疾病名称}-->
  <TemplateInfo>
    <Name>{疾病名称}药学监护路径</Name>
    <Code>{疾病代码}</Code>
    <DRGCode>{DRG编码（如适用）}</DRGCode>
    <DRGName>{DRG名称（如适用）}</DRGName>
    <Description>{模板描述，包含适用人群和核心内容}</Description>
    <EstimatedDays>{预计住院天数}</EstimatedDays>
    <CourseType>{疗程类型：standard/long_term}</CourseType>
    <IsActive>1</IsActive>
    <GuidelineSources>
      <Guideline name="{指南名称}" organization="{发布机构}" year="{年份}" evidence_level="{证据等级}" />
      <!-- 多指南时逐一列出 -->
    </GuidelineSources>
  </TemplateInfo>

  <DrugTreatments>
    <!--标准药物治疗方案（含推荐等级样式化标签）-->
    <Drug>
      <Phase>{阶段：院前/治疗初期/巩固期/全疗程/院后随访}</Phase>
      <DayRange>{时间范围，如D1-D3或Post-D7~D30}</DayRange>
      <DrugName>{药品通用名}</DrugName>
      <DrugNameEN>{英文INN}</DrugNameEN>
      <Specification>{剂型规格}</Specification>
      <Dosage>{单次剂量}</Dosage>
      <Frequency>{频次}</Frequency>
      <Route>{给药途径}</Route>
      <Indication>{使用原因}</Indication>
      <Notes>{注意事项}</Notes>
      <Priority>{优先级数字}</Priority>
      <RecommendLevel style="color:#fff;background:{颜色};padding:2px 12px;border-radius:4px;display:inline-block;font-weight:600;font-size:12px;margin:0 2px;">{一线用药/二线用药/备选用药}</RecommendLevel>
      <GuidelineSource>{来源指南标注}</GuidelineSource>
    </Drug>
    <!-- 每个药品一个<Drug>节点 -->
  </DrugTreatments>

  <LabTests>
    <!--必需的检验监测项目（含监护优先级样式化标签）-->
    <LabTest>
      <DayRange>{监测时间范围}</DayRange>
      <TestName>{检验项目名称}</TestName>
      <Purpose>{监测目的}</Purpose>
      <Frequency>{监测频次}</Frequency>
      <Notes>{注意事项}</Notes>
      <TargetRange>{目标范围（如适用）}</TargetRange>
      <ActionThreshold>{异常处理阈值（如适用）}</ActionThreshold>
      <MonitoringPriority style="color:#fff;background:{颜色};padding:2px 10px;border-radius:9999px;display:inline-block;font-weight:600;font-size:12px;">{高/中/低}</MonitoringPriority>
    </LabTest>
    <!-- 每个检验项目一个<LabTest>节点 -->
  </LabTests>

  <DrugInteractions>
    <!--重要的药物相互作用-->
    <Interaction>
      <DrugA>{药物A名称}</DrugA>
      <DrugB>{药物B名称}</DrugB>
      <Mechanism>{相互作用机制}</Mechanism>
      <Consequence>{临床后果}</Consequence>
      <Severity>{severe/moderate/mild}</Severity>
      <Action>{处理建议}</Action>
    </Interaction>
    <!-- 每对相互作用一个<Interaction>节点 -->
  </DrugInteractions>

  <Timeline>
    <!--每日监护节点（含三阶段：院前/院中/院后）-->
    <Node>
      <DayNo>{Day编号}</DayNo>
      <DayLabel>{日期标签，如"Pre-D3 院前评估"或"D1 入院"或"Post-D7 出院随访"}</DayLabel>
      <Phase>{阶段：院前/入院期/治疗初期/巩固期/出院期/随访期}</Phase>
      <PhaseCategory>{pre_hospital/in_hospital/post_hospital}</PhaseCategory>
      <MedicalActions>{诊疗行为}</MedicalActions>
      <DrugActions>{用药事件}</DrugActions>
      <PharmacyActions>{药学监护事件，含PC-XX代码}</PharmacyActions>
      <KeyActions>{关键行动标注}</KeyActions>
    </Node>
    <!-- 院前节点 -->
    <Node>
      <DayNo>Pre-D7</DayNo>
      <DayLabel>Pre-D7 院前评估</DayLabel>
      <Phase>院前期</Phase>
      <PhaseCategory>pre_hospital</PhaseCategory>
      <MedicalActions>既往用药梳理，风险评估</MedicalActions>
      <DrugActions>整理入院前用药清单</DrugActions>
      <PharmacyActions>PC-02患者分组预评估，PC-03既往用药梳理</PharmacyActions>
      <KeyActions>院前用药评估 + 风险分层</KeyActions>
    </Node>
    <!-- 院中节点 (D1 ~ DN) -->
    <!-- ... -->
    <!-- 院后随访节点 -->
    <Node>
      <DayNo>Post-D7</DayNo>
      <DayLabel>Post-D7 出院后随访</DayLabel>
      <Phase>随访期</Phase>
      <PhaseCategory>post_hospital</PhaseCategory>
      <MedicalActions>电话/门诊随访症状控制情况</MedicalActions>
      <DrugActions>评估用药依从性</DrugActions>
      <PharmacyActions>PC-10药学随访记录，用药教育强化</PharmacyActions>
      <KeyActions>出院后7天随访</KeyActions>
    </Node>
    <Node>
      <DayNo>Post-D30</DayNo>
      <DayLabel>Post-D30 1个月随访</DayLabel>
      <Phase>随访期</Phase>
      <PhaseCategory>post_hospital</PhaseCategory>
      <MedicalActions>门诊复查，疗效评估</MedicalActions>
      <DrugActions>评估用药方案是否需调整</DrugActions>
      <PharmacyActions>PC-10药学随访，疗效评估</PharmacyActions>
      <KeyActions>出院后30天随访</KeyActions>
    </Node>
    <Node>
      <DayNo>Post-D90</DayNo>
      <DayLabel>Post-D90 3个月随访</DayLabel>
      <Phase>随访期</Phase>
      <PhaseCategory>post_hospital</PhaseCategory>
      <MedicalActions>门诊复查，长期管理评估</MedicalActions>
      <DrugActions>长期用药管理评估</DrugActions>
      <PharmacyActions>PC-10药学随访，长期用药管理</PharmacyActions>
      <KeyActions>出院后3个月随访</KeyActions>
    </Node>
    <!-- 长疗程病种可追加6个月、12个月随访节点 -->
  </Timeline>
</PharmaceuticalCareTemplate>
```

**XML样式标签规范（内联style属性）：**

| 标签 | 用途 | 高优先级(红) | 中优先级(橙/蓝) | 低优先级(绿/灰) |
|------|------|-------------|----------------|---------------|
| RecommendLevel | 推荐等级 | 一线: `background:#e74c3c` | 二线: `background:#3498db` | 备选: `background:#95a5a6` |
| MonitoringPriority | 监测优先级 | 高: `background:#e74c3c` | 中: `background:#f39c12` | 低: `background:#27ae60` |

所有样式标签统一格式：`style="color:#fff;background:{颜色};padding:2px 10px;border-radius:{圆角};display:inline-block;font-weight:600;font-size:12px;"`
- RecommendLevel: `border-radius:4px; margin:0 2px;`
- MonitoringPriority: `border-radius:9999px;`

**XML生成规则：**
1. 编码：UTF-8（`<?xml version="1.0" encoding="utf-8"?>`）
2. 根元素：`<PharmaceuticalCareTemplate version="1.0" generated_at="{YYYY-MM-DD HH:MM:SS}">`
3. 所有文本内容须进行XML转义（`&` -> `&amp;`, `<` -> `&lt;`, `>` -> `&gt;`, `"` -> `&quot;`, `'` -> `&apos;`）
4. 药品推荐等级和监测优先级使用内联style属性呈现彩色标签
5. 三阶段时序节点必须完整覆盖（院前 + 院中 + 院后），标准疗程可省略院前/院后
6. 多指南信息在 `<GuidelineSources>` 中逐一列出
7. XML注释用于分区说明（如 `<!--院前节点-->`、`<!--院中节点-->`、`<!--院后随访节点-->`）

### 第5步：生成DOC文件

#### [病种名]_药学监护章节.doc

使用HTML格式保存（兼容浏览器查看和打印），书籍章节结构：

```
# 第X章 {疾病名称}药学监护

## 一、疾病概述
### 1.1 疾病特点
（流行病学、发病率、好发人群、病理生理简述，200-400字）

### 1.2 诊断要点
（临床表现、诊断标准、辅助检查、鉴别诊断要点）

### 1.3 治疗原则
（治疗目标、治疗策略分层、手术/药物/综合治疗选择原则，含多指南对比）

### 1.4 监护要点
（核心药学监护要点列表，按重要性排序，含院前/院中/院后三阶段要点）

### 1.5 合并疾病
（常见合并症列表及处理注意事项）

### 1.6 指南及相关文献
（列出3-8条权威指南和参考文献，含发布机构、年份和证据等级）

## 二、药学治疗与监护要点
（表格形式，列为：药品名称、剂型规格、用法用量、起止时间、阶段(院前/院中/院后)、使用原因、推荐等级、注意事项、监护要点）
（列出该病种所有相关药品，每药一行，用法用量需标注剂型/规格/单次剂量/频次/途径）

### 2.1 药物相互作用
（表格形式，列为：药物A、药物B、机制、后果、严重程度、处理建议）

## 三、药学监护服务
### 3.1 院前阶段药学服务
（表格形式，列为：时间节点、药学服务类型、工作内容、注意事项）

### 3.2 院中阶段药学服务
（表格形式，列为：住院天数、时间节点、药学服务类型、工作内容、注意事项）
（从入院Day1到出院，每种药学服务类型结合该病种具体用药详细展开）

### 3.3 院后随访阶段药学服务
（表格形式，列为：随访时间(7d/14d/30d/3m/6m/12m)、药学服务类型、工作内容、注意事项）
```

**DOC文件CSS要求：**
- font-family: 微软雅黑/黑体; font-size: 11pt; line-height: 1.8
- h1: font-size 18pt; color #065F5B; border-bottom 2px solid #0B7A75; padding-bottom 6px
- h2: font-size 14pt; color #0B7A75; margin-top 24px
- h3: font-size 12pt; color #1A1A2E; margin-top 16px
- table: width 100%; border-collapse collapse; font-size 10pt
- th: background #004D40; color white; padding 6px 8px
- td: padding 6px 8px; border 1px solid #B2DFDB
- tr:nth-child(even): background #F0F9F8
- **.phase-pre**: color #6A1B9A; font-weight bold（院前阶段标题）
- **.phase-post**: color #1565C0; font-weight bold（院后阶段标题）
- @media print: @page size A4; margin 2cm 2.5cm; body font-size 10pt

---

## 批量生成协议

当用户输入包含多个病种时：

1. **解析病种列表** — 识别输入中提到的所有疾病名称
2. **解析多指南列表** — 识别每个病种对应的临床指南（可共用或独立指定）
3. **并行信息采集** — 对所有病种同时执行第1步（网络搜索+指南解析），每个病种独立搜索
4. **多指南交叉校验** — 对每个病种的多指南信息进行交叉对比，生成统一推荐方案
5. **并行文件生成** — 使用Task子代理并行生成各病种文件，每个子代理负责1个病种的全部7个文件
6. **进度报告** — 每完成1个病种向用户报告进度
7. **最终汇总** — 列出所有病种的文件清单和摘要

**子代理调度规范：**
- 每个子代理接收完整指令（含CSS规范、JSON结构、XML结构、DOC结构、疾病特定数据、多指南信息）
- 子代理输出7个文件到指定子目录
- 子代理返回文件路径清单和内容摘要

**长疗程病种自动检测规则：**
- 住院天数 > 14天 -> 启用三阶段时序
- 疾病类型为肿瘤/慢性病/移植后/结核/罕见病 -> 启用三阶段时序
- 用户明确要求"院前院中院后"或"全周期"或"长期随访" -> 启用三阶段时序
- 标准疗程病种（如单纯阑尾炎LC手术）-> 仅生成院中时序，院前/院后可省略或简化

---

## 质量标准

### 内容质量
- 所有药品名称必须使用**通用名（中文）+ 英文INN**格式
- 用法用量必须标注：剂型、规格、单次剂量、频次、给药途径
- 监护要点必须引用循证依据（标注指南级别）
- 药物治疗表格中"起止时间"必须标注具体天数（如"Day1-Day3"或"术前30min-术后24h"或"Post-D7~D30"）
- 多指南交叉项必须标注分歧点和选择理由
- 长疗程病种必须包含完整的院前/院中/院后三阶段时序

### 技术质量
- HTML文件：**完整内联CSS**，不依赖任何外部CSS/JS文件
- HTML文件：必须包含 `@media print` 打印适配
- JSON文件：必须为**合法JSON格式**，UTF-8编码，无语法错误
- **XML文件：必须为合法XML格式**，UTF-8编码，符合PharmaceuticalCareTemplate schema
- **XML文件：所有特殊字符必须正确转义**（&, <, >, ", '）
- **XML文件：内联style属性格式统一**，推荐等级和监测优先级标签样式一致
- DOC文件：HTML格式保存，打印友好样式

### 安全规范
- 所有患者个人信息字段使用占位符（`_______`）
- 不填入任何真实患者数据
- 过敏史字段默认显示"无"，红色标注

### 视觉规范
- 统一配色方案：主色 #0B7A75，辅色 #F0F9F8，表头 #004D40
- 字体：微软雅黑/黑体
- 风险标注：高(红色)/中(橙色)/常规(黑色)
- 高风险药品/监测项使用 `.alert-danger` 样式标注
- **三阶段配色**：院前(紫色#6A1B9A)、院中(绿色#0B7A75)、院后(蓝色#1565C0)
- **推荐等级标签**：一线(红色#e74c3c)、二线(蓝色#3498db)、备选(灰色#95a5a6)

---

## 参考资源

- `references/pathway_templates.md` — 常见疾病临床路径时序框架参考（含院前/院中/院后通用框架）
- `references/pharmacy_care_forms.md` — 10个PC子类表单模板详细字段定义
- `references/chaa_standards.md` — 中国医院协会药事管理委员会团体标准要点
- `assets/care_plan_template.html` — HTML药学监护计划综合模板
- `assets/pathway_timeline.html` — 治疗路径时序线图HTML模板
- `assets/form_styles.css` — 统一CSS样式表
- `assets/pharmaceutical_care_template.xml` — XML药学监护模板（含内联样式标签规范）
