/**
 * 真实世界研究（RWS）方案 Word 文档生成模板（空白占位版）
 *
 * 与 generate_protocol_template.js 平行：本模板用于"前瞻性/回顾性观察性真实世界研究
 * （含目标试验模拟 TTE、IPTW/重叠权重、登记研究）"类方案，区别于解释性 RCT / 实用性
 * pRCT。如需生成 RCT/pRCT 方案，请使用 generate_protocol_template.js。
 *
 * 用法：
 *   node generate_rws_protocol_template.js                 → 默认：前瞻性、加权（IPTW/重叠权重）
 *   node generate_rws_protocol_template.js --retrospective → 回顾性 RWS（ETL 提取 + 伦理豁免 + RECORD）
 *   node generate_rws_protocol_template.js --psm           → PSM 模拟 RCT（1:1 匹配 + caliper + SMD 平衡表）
 *   node generate_rws_protocol_template.js --cer           → 比较效果研究 CER（效应修饰 + 亚组分析）
 *   可组合：node generate_rws_protocol_template.js --retrospective --psm --cer
 * 填写：将所有 {{PLACEHOLDER}} 与【】替换为实际内容；不适用的章节注明 N/A，保留框架。
 *
 * 子类型决策（对应 SKILL.md 阶段三与 study-design-guide.md §2.6）：
 *   --retrospective  数据来自 HIS/EHR/登记库，提取而非录入，知情同意多依豁免
 *   --psm            混杂控制以 1:1 倾向评分匹配为首要方法（模拟 RCT 报告范式）
 *   --cer            目的标签为比较效果研究，强调效应修饰与亚组
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// ---- RWS 子类型开关（使前瞻/回顾/PSM/CER 成为一等公民，而非手动改占位符）----
const IS_RETRO = process.argv.includes('--retrospective');
const IS_PSM = process.argv.includes('--psm');
const IS_CER = process.argv.includes('--cer');
const designLabel = (IS_RETRO ? '回顾性' : '前瞻性') + '、多中心、观察性真实世界队列研究（目标试验模拟）' + (IS_CER ? ' / 比较效果研究 CER' : '');
const psMethod = IS_PSM
  ? 'PSM 1:1 最近邻匹配（caliper 0.2×SD、无放回）'
  : 'IPTW/重叠权重/PSM';
const statMethod = IS_PSM
  ? '{{倾向评分 1:1 最近邻匹配（caliper 0.2×SD、无放回）；匹配前后各协变量 SMD<0.1 平衡诊断；条件 Logistic/Cox 报 aOR/aHR + 95%CI}}'
  : '{{基线均衡 SMD<0.1；IPTW/重叠权重 + 加权回归/边际结构模型；敏感性分析 E-value；缺失 MICE}}';

const F = { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" };
const S24 = { font: F, size: 24 };
const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };

function p(text, opts = {}) {
  return new Paragraph({ spacing: { before: 60, after: 60, line: 360 }, ...opts,
    children: [new TextRun({ text, ...S24, ...opts.run })] });
}
function pB(text, opts = {}) { return p(text, { ...opts, run: { bold: true, ...opts.run } }); }
function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 },
  children: [new TextRun({ text, font: F, size: 32, bold: true })] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 },
  children: [new TextRun({ text, font: F, size: 28, bold: true })] }); }
function h3(text) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 },
  children: [new TextRun({ text, font: F, size: 26, bold: true })] }); }
function bullet(text) { return new Paragraph({ numbering: { reference: "bullets", level: 0 },
  spacing: { before: 40, after: 40, line: 360 }, children: [new TextRun({ text, ...S24 })] }); }
function pb() { return new Paragraph({ children: [new PageBreak()] }); }
function empty() { return new Paragraph({ children: [new TextRun({ text: "", ...S24 })] }); }

function tc(text, opts = {}) {
  return new TableCell({ borders, width: { size: opts.width || 4680, type: WidthType.DXA },
    shading: opts.shade ? { fill: "D5E8F0", type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ spacing: { before: 20, after: 20 },
      children: [new TextRun({ text, ...S24, bold: opts.bold || false, size: opts.size || 24 })] })] });
}
function makeTable(rows, colWidths, opts = {}) {
  const tableRows = rows.map((r, i) => {
    const cells = r.map((t, j) => tc(t, { width: colWidths[j], bold: i === 0, shade: i === 0, size: opts.size }));
    return new TableRow({ cantSplit: true, children: cells });
  });
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, columnWidths: colWidths, rows: tableRows });
}

const c = [];

// -------- 封面页 --------
c.push(empty(), empty(), empty(), empty());
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 200 },
  children: [new TextRun({ text: "{{研究题目全称：评价【暴露/干预】对比【对照】用于【人群/适应症】的真实世界【有效性/安全性】}}", font: F, size: 30, bold: true })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
  children: [new TextRun({ text: "{{设计类型短描述，如：" + designLabel + "}}", font: F, size: 26, bold: true, color: "555555" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 600 },
  children: [new TextRun({ text: "临床研究方案", font: F, size: 36, bold: true })] }));
c.push(empty(), empty());
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 60 },
  children: [new TextRun({ text: "研究方案编号：{{编号}}", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "研究阶段：{{如：IIT-RWS / 观察性真实世界研究 / 登记研究}}", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "版本号：V1.0", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 400 },
  children: [new TextRun({ text: "版本日期：{{日期}}", font: F, size: 24 })] }));
c.push(pb());

// -------- 保密声明 --------
c.push(pB("保密声明", { alignment: AlignmentType.CENTER, run: { size: 28 } }));
c.push(empty());
c.push(p("本方案属于保密性文件，其中所包含的所有信息的所有权归申办者，仅提供给本项目研究者、合作研究者、伦理委员会和监督管理部门等相关机构和人员审阅。在未得到书面批准情况下，切勿传播和外泄。"));
c.push(pb());

// -------- 签字页 --------
c.push(pB("临床研究方案确认签字页", { alignment: AlignmentType.CENTER, run: { size: 28 } }));
c.push(empty());
c.push(pB("{{研究题目全称}}"));
c.push(empty());
c.push(pB("主要研究者关于方案的同意书："));
c.push(p("我已经认真阅读过本方案，我同意方案中包括的所有用来进行研究的必要的信息，并且我同意按方案所描述的内容执行。我明白缺少伦理委员会批准的情况下，试验不得启动，并且要完全遵守本单位的相关规定。"));
c.push(empty());
c.push(p("研究组长单位：【填写组长单位全称】"));
c.push(p("主要研究者签字：________________    日期：____年__月__日"));
c.push(pb());

// -------- 缩略语表 --------
c.push(h1("缩略语表"));
const abbrData = [
  ["英文缩写", "英文全称", "中文全称"],
  ["RWS", "Real-World Study", "真实世界研究"],
  ["TTE", "Target Trial Emulation", "目标试验模拟"],
  ["IPTW", "Inverse Probability of Treatment Weighting", "逆概率治疗加权"],
  ["OW", "Overlap Weighting", "重叠权重"],
  ["PS", "Propensity Score", "倾向评分"],
  ["SMD", "Standardized Mean Difference", "标准化均数差"],
  ["STROBE", "STrengthening the Reporting of OBservational studies in Epidemiology", "加强观察性流行病学研究报告"],
  ["RECORD", "REporting of studies Conducted using Routine collected Data", "常规收集数据研究报告"],
  ["eCRF", "electronic Case Report Form", "电子病例报告表"],
  // ... 按研究领域补充更多缩略语
];
c.push(makeTable(abbrData, [1600, 5200, 2800], { size: 22 }));
c.push(pb());

// -------- 方案摘要 --------
c.push(h1("方案摘要"));
const summaryData = [
  ["研究名称", "{{研究题目全称}}"],
  ["研究方案编号", "{{编号}}"],
  ["版本号/版本日期", "V1.0 / {{日期}}"],
  ["研究设计", "{{" + (IS_RETRO ? "回顾性" : "前瞻性") + "/单/多中心、观察性真实世界队列；是否遵循 TTE；混杂控制方法（" + psMethod + "）" + (IS_CER ? "；目的：比较效果研究 CER" : "") + "}}"],
  ["研究对象", "{{目标人群}}"],
  ["样本量", "{{N}}例（暴露组{{n1}}例，对照组{{n2}}例）"],
  ["研究目的", "主要目的：{{主要目的}}\n次要目的：{{次要目的}}"],
  ["研究分组", "{{暴露组 vs 对照组；说明是否随机（RWS 通常非随机，按真实处方/实践分组）}}"],
  ["干预/暴露措施", "{{暴露（真实世界用药/措施）}}"],
  ["对照措施", "{{对照（真实世界对照用药/措施/无干预）}}"],
  ["入选标准", "{{主要入选标准摘要}}"],
  ["排除标准", "{{主要排除标准摘要}}"],
  ["研究终点", "主要终点：{{主要终点}}\n次要终点：{{次要终点}}"],
  ["分析方法", "{{加权/回归方法；平衡诊断 SMD<0.1；敏感性分析（E-value 等）}}"],
];
c.push(makeTable(summaryData, [2200, 7400], { size: 22 }));
c.push(pb());

// -------- 1 研究背景 --------
c.push(h1("1 研究背景"));
c.push(h2("1.1 临床需求与现状")); c.push(p("{{第一段：疾病/诊疗现状、未满足需求}}"));
c.push(h2("1.2 对照现状与局限")); c.push(p("{{第二段：对照用药/措施现状与已知局限性}}"));
c.push(h2("1.3 研究暴露特性")); c.push(p("{{第三段：研究暴露（药物/措施）的特性与差异化}}"));
c.push(h2("1.4 研究暴露真实世界证据")); c.push(p("{{第四段：已有 RWS/观察性证据，按证据等级}}"));
c.push(h2("1.5 研究空白与立题依据")); c.push(p("{{第五段：明确 RWS 证据缺口，提出科学问题（PICO）}}"));
c.push(pb());

// -------- 2 研究目的 --------
c.push(h1("2 研究目的"));
c.push(pB("（1）主要研究目的：")); c.push(p("{{主要目的}}" + (IS_CER ? "（比较效果研究 CER：在真实临床决策下比较两干预的实效差异）" : "")));
c.push(pB("（2）次要研究目的：")); c.push(p("{{次要目的}}"));

// -------- 3 研究假设 --------
c.push(h1("3 研究假设"));
c.push(p("（1）{{主要假设}}"));
c.push(p("（2）{{次要假设}}"));
c.push(pb());

// -------- 4 研究设计 --------
c.push(h1("4 研究设计"));
c.push(h2("4.1 整体设计和计划（目标试验模拟 / TTE）"));
c.push(p("{{说明本研究为观察性 RWS；显式映射 TTE 七要素：①目标人群 ②治疗策略 ③分配 ④随访 ⑤结局 ⑥因果对比 ⑦分析；引用 Hernán 等（PMID:26994063, 36508210）}}"));
c.push(makeTable([
  ["TTE 要素", "本研究对应定义"],
  ["① 目标人群（Eligibility）", "{{}}"],
  ["② 治疗策略（Treatment strategy）", "{{}}"],
  ["③ 分配（Assignment）", "{{非随机；以真实处方/实践为暴露；借 PS 加权模拟随机化}}"],
  ["④ 随访（Follow-up）", "{{}}"],
  ["⑤ 结局（Outcome）", "{{}}"],
  ["⑥ 因果对比（Causal contrast）", "{{ATE/ATT；aOR/aHR 及 95%CI}}"],
  ["⑦ 分析（Analysis）", "{{IPTW/重叠权重 + 回归；SMD<0.1；E-value}}"],
], [2600, 7000], { size: 22 }));
c.push(h3("4.1.1 与 RCT、实用性 RCT（pRCT）的区分"));
c.push(p("{{说明本研究属于观察性 RWS，与解释性 RCT / pRCT 在分配、人群、干预、设盲、偏倚控制上的区别（见 study-design-guide.md 2.4）}}"));
c.push(h2("4.2 分组与暴露定义（替代“随机化与设盲”）"));
c.push(p("（1）暴露定义：{{以真实处方/实践判定暴露组与对照组的时点与规则}}"));
c.push(p("（2）非随机说明：{{说明为何不随机、组间失衡如何用加权控制}}"));
c.push(p("（3）盲法：{{RWS 通常开放；说明如何降低评估偏倚}}"));
c.push(p("（4）研究登记：{{ChiCTR/国际观察性登记预注册；遵循 STROBE/RECORD}}"));
c.push(pb());

// -------- 5 研究人群 --------
c.push(h1("5 研究人群"));
c.push(h2("5.1 数据来源与人群界定")); c.push(p(IS_RETRO ? "{{真实世界数据来源：HIS/EHR/登记库等既有结构化数据；通过 ETL 按预设字段集提取历史就诊记录；人群依诊疗记录界定（回顾性）}}" : "{{真实世界数据来源：自建 eCRF 前瞻录入；人群界定}}"));
c.push(h2("5.2 入选标准")); c.push(p("（1）{{入选标准1}}"));
c.push(h2("5.3 排除标准")); c.push(p("（1）{{排除标准1（安全性排除优先）}}"));
c.push(h2("5.4 退出、剔除与中止标准")); c.push(p("{{}}"));
c.push(pb());

// -------- 6 研究干预/暴露 --------
c.push(h1("6 研究暴露 / 干预措施"));
c.push(h2("6.1 暴露（研究药物/措施）")); c.push(p("{{真实世界暴露定义、剂量范围}}"));
c.push(h2("6.2 对照（对照药物/措施）")); c.push(p("{{真实世界对照定义}}"));
c.push(h2("6.3 合并用药/措施与混杂因素")); c.push(p("{{允许真实临床联用；记录为混杂校正候选}}"));
c.push(h2("6.4 暴露/药品数据管理")); c.push(p("{{真实世界数据溯源与采集}}"));
c.push(pb());

// -------- 7 研究方法 --------
c.push(h1("7 研究方法及步骤"));
c.push(h2("7.1 数据收集期（" + (IS_RETRO ? "数据提取（ETL）" : "基线/筛选（eCRF 录入）") + "）")); c.push(p(IS_RETRO ? "{{从 HIS/EHR 按预设字段集提取历史就诊数据；记录提取时点、窗口与溯源}}" : "{{前瞻录入基线协变量与暴露}}"));
c.push(h2("7.2 暴露/治疗期")); c.push(p("{{真实世界暴露实施与监测}}"));
c.push(h2("7.3 随访期")); c.push(p("{{随访时点（如术后 24/48/72h、30天）}}"));
c.push(h2("7.4 研究程序与评估时间表")); c.push(p("{{评估时间表表格（前瞻 eCRF 时点 / 回顾提取字段）}}"));
c.push(pb());

// -------- 8 研究终点 --------
c.push(h1("8 研究终点"));
c.push(h2("8.1 主要终点指标")); c.push(p("{{主要终点定义（直接回答科学问题）}}"));
c.push(h2("8.2 次要终点指标")); c.push(p("（1）{{次要终点1}}"));
c.push(h2("8.3 需要重点关注的安全性指标")); c.push(p("{{安全性指标}}"));
c.push(pb());

// -------- 9 安全性监测 --------
c.push(h1("9 安全性监测与报告"));
c.push(h2("9.1 不良事件的定义")); c.push(p("{{AE 定义}}"));
c.push(h2("9.2 严重不良事件的定义")); c.push(p("{{SAE 定义}}"));
c.push(h2("9.3 不良事件记录、收集、报告和处理")); c.push(p("{{报告流程（RWS 多依真实世界安全信号）}}"));
c.push(pb());

// -------- 10-11 --------
c.push(h1("10 试验终止 / 暂停标准")); c.push(p("{{}}"));
c.push(h1("11 临床试验结束的规定")); c.push(p("{{数据库锁定与结果更新}}"));
c.push(pb());

// -------- 12 数据管理 --------
c.push(h1("12 数据管理"));
c.push(h2("12.1 数据管理总体方案")); c.push(p(IS_RETRO ? "{{数据来源：HIS/EHR/登记库；ETL 流程、字段映射与溯源（遵循 RECORD 报告规范）}}" : "{{数据来源、eCRF 构建与调查员培训、溯源}}"));
c.push(h2("12.2 数据记录与文件保存")); c.push(p("{{}}"));
c.push(h2("12.3 数据库建立与数据锁定")); c.push(p("{{}}"));
c.push(h2("12.4 缺失数据处理（真实世界关键控制）")); c.push(p("{{完整性预查；MCAR/MAR 用完整病例或 MICE；系统性缺失触发方案修订；" + (IS_RETRO ? "回顾性数据遵循 RECORD 缺失报告" : "前瞻 eCRF 设必填校验降低缺失；遵循 STROBE 缺失报告") + "}}"));
c.push(pb());

// -------- 13 统计分析 --------
c.push(h1("13 统计分析"));
c.push(h2("13.1 样本量确定")); c.push(p("{{RWS 以效应精度 + 加权后有效样本量为原则；给出公式与参数}}"));
c.push(h2("13.2 分析人群的定义和选择")); c.push(p("{{观测队列全分析集 / 加权分析集 / 敏感性子集}}"));
c.push(h2("13.3 统计方法")); c.push(p(statMethod));
c.push(h2("13.4 统计软件与一般要求")); c.push(p("{{R（MatchIt/WeightIt/survey/mice）或 SAS}}"));
if (IS_CER) {
  c.push(h2("13.5 效应修饰与亚组分析（CER）")); c.push(p("{{按年龄/肾功能/术式/基线严重程度分层的效果修饰；交互项检验；亚组森林图；与对照的因果对比一致性}}"));
}
c.push(pb());

// -------- 14 试验管理 --------
c.push(h1("14 试验管理"));
c.push(h2("14.1 质量管理原则")); c.push(p("{{观察性研究参照 GCP 原则；统一 eCRF 培训}}"));
c.push(h2("14.2 参与者的隐私保护")); c.push(p("{{编码、加密、《个人信息保护法》}}"));
c.push(h2("14.3 质量控制和质量保证")); c.push(p("{{逻辑核查、SDV、协调会}}"));
c.push(h2("14.4 监查与稽查")); c.push(p("{{}}"));
c.push(h2("14.5 临床试验预期的进度和完成日期")); c.push(p("{{}}"));
c.push(h2("14.6 各方职责")); c.push(p("{{}}"));
c.push(pb());

// -------- 15 伦理学 --------
c.push(h1("15 试验相关的伦理学"));
c.push(h2("15.1 伦理委员会")); c.push(p("{{}}"));
c.push(h2("15.2 知情同意")); c.push(p(IS_RETRO ? "{{回顾性研究依伦理委员会豁免或宽泛同意，不触及受试者前瞻性操作；隐私去标识化}}" : "{{前瞻性研究需受试者签署知情同意；提供退出权利}}"));
c.push(h2("15.3 受试者权益保护")); c.push(p("{{}}"));
c.push(h2("15.4 临床研究注册")); c.push(p("{{ChiCTR / 观察性登记；锁定分析计划}}"));
c.push(pb());

// -------- 16 参考文献 --------
c.push(h1("16 参考文献"));
const refs = [
  // "[1] 作者. 题名[J]. 期刊名, 年份. （RWS 须引用 TTE 与 STROBE/RECORD/NMPA 指导原则）"
];
refs.forEach(r => c.push(new Paragraph({ spacing: { before: 40, after: 40, line: 320 },
  indent: { left: 480, hanging: 480 }, children: [new TextRun({ text: r, ...S24, size: 22 })] })));
c.push(pb());

// -------- 17 修订历史 --------
c.push(h1("17 方案修订历史"));
c.push(makeTable([["版本", "日期", "修订内容", "修订人"], ["V1.0", "{{日期}}", "首版 RWS 方案", "{{姓名}}"]], [1200, 1800, 4400, 2200], { size: 22 }));
c.push(pb());

// -------- 附录 --------
c.push(h1("附录1 重点关注安全性事件 / 终点的操作性定义"));
c.push(makeTable([["事件", "操作性定义"], ["{{事件}}", "{{定义}}"]], [2600, 7000], { size: 22 }));
c.push(pb());
c.push(h1("附录2 评估量表 / 问卷"));
c.push(p("{{NRS/VAS、镇静评分、QoR-15、因果判定量表等}}"));
c.push(pb());

// ==================== 文档组装 ====================
const doc = new Document({
  styles: {
    default: { document: { run: { font: F, size: 24 }, paragraph: { spacing: { line: 360 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: F }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0, keepNext: false, keepLines: false } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: F }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1, keepNext: false, keepLines: false } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: F }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2, keepNext: false, keepLines: false } },
    ]
  },
  numbering: { config: [ { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] } ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "{{研究方案简称}}", font: F, size: 18, color: "999999" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "第 ", font: F, size: 18 }), new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18 }), new TextRun({ text: " 页", font: F, size: 18 })] })] }) },
    children: c
  }]
});

const outPath = "{{输出路径}}.docx";
Packer.toBuffer(doc).then(buffer => { fs.writeFileSync(outPath, buffer); console.log("SUCCESS: " + outPath + " (" + (buffer.length / 1024).toFixed(1) + " KB)"); })
  .catch(err => { console.error("ERROR:", err.message); process.exit(1); });
