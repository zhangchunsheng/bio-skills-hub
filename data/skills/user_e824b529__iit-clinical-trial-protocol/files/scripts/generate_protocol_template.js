/**
 * 临床研究方案 Word 文档生成模板
 *
 * 使用方法：
 * 1. 将此文件复制到工作目录
 * 2. 根据研究方案内容，替换所有 {{PLACEHOLDER}} 占位符
 * 3. 运行: node generate_protocol_template.js
 * 4. 清理: python scripts/sanitize.py output.docx
 *
 * 此模板基于 docx-js 库，生成符合临床研究方案通用模板结构的 Word 文档。
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// ==================== 字体与样式常量 ====================
const F = { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" };
const S24 = { font: F, size: 24 };
const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };

// ==================== 辅助函数 ====================
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

// ==================== 文档内容构建 ====================
const c = [];

// -------- 封面页 --------
c.push(empty(), empty(), empty(), empty());
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 200 },
  children: [new TextRun({ text: "{{研究题目全称}}", font: F, size: 32, bold: true })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 600 },
  children: [new TextRun({ text: "{{设计类型描述}}", font: F, size: 32, bold: true })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 200 },
  children: [new TextRun({ text: "临床研究方案", font: F, size: 36, bold: true })] }));
c.push(empty(), empty());
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 60 },
  children: [new TextRun({ text: "研究方案编号：{{编号}}", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "研究阶段：{{阶段}}", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "版本号：V1.0", font: F, size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 400 },
  children: [new TextRun({ text: "版本日期：{{日期}}", font: F, size: 24 })] }));
c.push(pb());

// -------- 保密声明 --------
c.push(pB("保密声明", { alignment: AlignmentType.CENTER, run: { size: 28 } }));
c.push(empty());
c.push(p("本方案属于保密性文件，其中所包含的所有信息的所有权归申办者，仅提供给本项目研究者、合作研究者、伦理委员会和监督管理部门等相关机构和人员审阅。在未得到申办者书面批准情况下，切勿传播和外泄。"));
c.push(pb());

// -------- 签字页 --------
c.push(pB("临床试验方案确认签字页", { alignment: AlignmentType.CENTER, run: { size: 28 } }));
c.push(empty());
c.push(pB("{{研究题目全称}}"));
c.push(empty());
c.push(pB("主要研究者关于方案的同意书："));
c.push(p("我已经认真阅读过本方案，我同意方案中包括的所有用来进行研究的必要的信息，并且我同意按方案所描述的内容执行。我明白缺少伦理委员会批准的情况下，试验不得启动，并且要完全遵守本单位的相关规定。"));
c.push(empty());
c.push(p("研究组长单位：{{单位全称}}"));
c.push(p("主要研究者签字：________________    日期：____年__月__日"));
c.push(pb());

// -------- 缩略语表 --------
c.push(h1("缩略语表"));
// TODO: 按研究领域补充缩略语，格式：[英文缩写, 英文全称, 中文全称]
const abbrData = [
  ["英文缩写", "英文全称", "中文全称"],
  ["AE", "Adverse Event", "不良事件"],
  ["SAE", "Serious Adverse Event", "严重不良事件"],
  ["GCP", "Good Clinical Practice", "药物临床试验质量管理规范"],
  ["CRF", "Case Report Form", "病例报告表"],
  ["FAS", "Full Analysis Set", "全分析集"],
  ["PPS", "Per-Protocol Set", "符合方案集"],
  ["SS", "Safety Set", "安全性分析集"],
  // ... 补充更多缩略语
];
c.push(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  columnWidths: [1800, 4500, 3300],
  rows: abbrData.map((r, i) => new TableRow({ cantSplit: true, children: r.map((t, j) =>
    tc(t, { width: [1800, 4500, 3300][j], bold: i === 0, shade: i === 0 })) }))
}));
c.push(pb());

// -------- 方案摘要 --------
c.push(h1("方案摘要"));
// TODO: 填写摘要表内容
const summaryData = [
  ["研究名称", "{{研究题目全称}}"],
  ["研究方案编号", "{{编号}}"],
  ["版本号/版本日期", "V1.0 / {{日期}}"],
  ["研究设计", "{{设计类型}}"],
  ["研究对象", "{{目标人群}}"],
  ["样本量", "{{N}}例（试验组{{N/2}}例，对照组{{N/2}}例）"],
  ["研究目的", "主要研究目的：{{主要目的}}\n次要研究目的：{{次要目的}}"],
  ["研究分组", "{{试验组}}与{{对照组}}，按1:1比例随机分配"],
  ["干预措施", "{{试验药物及用法}}"],
  ["对照措施", "{{对照药物及用法}}"],
  ["入选标准", "{{主要入选标准摘要}}"],
  ["排除标准", "{{主要排除标准摘要}}"],
  ["研究终点", "主要终点指标：{{主要终点}}\n次要终点指标：{{次要终点}}"],
  ["分析方法", "{{统计方法概述}}"],
];
c.push(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  columnWidths: [2200, 7400],
  rows: summaryData.map(r => new TableRow({ cantSplit: true, children: [
    tc(r[0], { width: 2200, bold: true, shade: true }), tc(r[1], { width: 7400 })
  ]}))
}));
c.push(pb());

// -------- 1 研究背景 --------
// TODO: 按五段式结构撰写，每段标注文献引用编号
// 参见 references/background-writing-guide.md
c.push(h1("1 研究背景"));
c.push(h2("1.1 {{临床需求与现状}}"));
c.push(p("{{第一段内容，引用文献[1]...}}"));
c.push(h2("1.2 {{对照药物现状与局限}}"));
c.push(p("{{第二段内容...}}"));
c.push(h2("1.3 {{研究药物特性}}"));
c.push(p("{{第三段内容...}}"));
c.push(h2("1.4 {{研究药物临床证据}}"));
c.push(p("{{第四段内容...}}"));
c.push(h2("1.5 研究空白与立题依据"));
c.push(p("{{第五段内容，提出科学问题...}}"));
c.push(pb());

// -------- 2 研究目的 --------
c.push(h1("2 研究目的"));
c.push(pB("（1）主要研究目的："));
c.push(p("{{主要目的}}"));
c.push(pB("（2）次要研究目的："));
c.push(p("{{次要目的}}"));

// -------- 3 研究假设 --------
c.push(h1("3 研究假设"));
c.push(p("（1）{{主要假设}}"));
c.push(p("（2）{{次要假设}}"));
c.push(pb());

// -------- 4 研究设计 --------
c.push(h1("4 研究设计"));
c.push(h2("4.1 整体设计和计划"));
c.push(p("{{研究设计描述}}"));
c.push(h2("4.2 随机化和设盲"));
c.push(p("{{随机化方法}}"));
c.push(p("{{盲法设计}}"));
c.push(pb());

// -------- 5 研究人群 --------
c.push(h1("5 研究人群"));
c.push(h2("5.1 诊断标准"));
c.push(p("{{诊断标准}}"));
c.push(h2("5.2 入选标准"));
c.push(p("（1）{{入选标准1}}"));
// ... 补充入选标准
c.push(h2("5.3 排除标准"));
c.push(p("（1）{{排除标准1}}"));
// ... 补充排除标准
c.push(h2("5.4 退出、剔除与中止标准"));
c.push(p("{{退出标准}}"));
c.push(pb());

// -------- 6 研究用药 --------
c.push(h1("6 研究用药/干预措施"));
c.push(h2("6.1 试验用药品"));
// TODO: 试验药物信息表
c.push(h2("6.2 对照药物"));
// TODO: 对照药物信息表
c.push(h2("6.3 合并用药与禁用药物"));
c.push(p("{{合并用药说明}}"));
c.push(h2("6.4 试验用药品管理"));
c.push(p("{{药品管理说明}}"));
c.push(pb());

// -------- 7 研究方法 --------
c.push(h1("7 研究方法及步骤"));
c.push(h2("7.1 筛选期"));
c.push(p("{{筛选期内容}}"));
c.push(h2("7.2 治疗期"));
c.push(p("{{治疗期给药方案与监测}}"));
c.push(h2("7.3 随访期"));
c.push(p("{{随访期内容}}"));
c.push(h2("7.4 研究程序与评估时间表"));
// TODO: 评估时间表表格
c.push(pb());

// -------- 8 研究终点 --------
c.push(h1("8 研究终点"));
c.push(h2("8.1 主要终点指标"));
c.push(p("{{主要终点定义}}"));
c.push(h2("8.2 次要终点指标"));
c.push(p("（1）{{次要终点1}}"));
// ... 补充次要终点
c.push(h2("8.3 需要重点关注的安全性指标"));
c.push(p("{{安全性指标}}"));
c.push(pb());

// -------- 9 安全性监测 --------
c.push(h1("9 安全性监测与报告"));
c.push(h2("9.1 不良事件的定义"));
c.push(p("{{AE定义}}"));
c.push(h2("9.2 严重不良事件的定义"));
c.push(p("{{SAE定义}}"));
c.push(h2("9.3 不良事件记录、收集、报告和处理"));
c.push(p("{{报告流程}}"));
c.push(pb());

// -------- 10-11 终止与结束 --------
c.push(h1("10 试验终止/暂停标准"));
c.push(p("{{终止标准}}"));
c.push(h1("11 临床试验结束的规定"));
c.push(p("{{结束规定}}"));
c.push(pb());

// -------- 12 数据管理 --------
c.push(h1("12 数据管理"));
c.push(h2("12.1 数据管理"));
c.push(p("{{数据管理说明}}"));
c.push(h2("12.2 数据记录与文件保存"));
c.push(p("{{记录保存说明}}"));
c.push(h2("12.3 数据库建立与数据锁定"));
c.push(p("{{数据库说明}}"));
c.push(pb());

// -------- 13 统计分析 --------
c.push(h1("13 统计分析"));
c.push(h2("13.1 样本量确定"));
// TODO: 完整的样本量计算，参见 references/sample-size-guide.md
c.push(p("{{样本量计算}}"));
c.push(h2("13.2 分析人群的定义和选择"));
c.push(p("{{分析人群定义}}"));
c.push(h2("13.3 统计方法"));
c.push(p("{{统计方法}}"));
c.push(h2("13.4 统计软件与一般要求"));
c.push(p("{{软件说明}}"));
c.push(pb());

// -------- 14 试验管理 --------
c.push(h1("14 试验管理"));
c.push(h2("14.1 遵从GCP的要求"));
c.push(p("{{GCP说明}}"));
c.push(h2("14.2 参与者的隐私保护"));
c.push(p("{{隐私保护}}"));
c.push(h2("14.3 质量控制和质量保证"));
c.push(p("{{质控说明}}"));
c.push(h2("14.4 监查与稽查"));
c.push(p("{{监查与稽查说明}}"));
c.push(h2("14.5 临床试验预期的进度和完成日期"));
c.push(p("{{进度安排}}"));
c.push(h2("14.6 各方职责"));
c.push(p("{{职责说明}}"));
c.push(pb());

// -------- 15 伦理学 --------
c.push(h1("15 试验相关的伦理学"));
c.push(h2("15.1 伦理委员会"));
c.push(p("{{伦理说明}}"));
c.push(h2("15.2 知情同意"));
c.push(p("{{知情同意说明}}"));
c.push(h2("15.3 受试者权益保护"));
c.push(p("{{受试者保护说明}}"));
c.push(h2("15.4 临床试验注册"));
c.push(p("{{注册说明}}"));
c.push(pb());

// -------- 16 参考文献 --------
// TODO: 按 GB/T 7714 格式列出所有参考文献
// 严禁编造文献，只列出实际检索到的
c.push(h1("16 参考文献"));
const refs = [
  // "[1] 作者. 题名[J]. 期刊名, 年份, 卷(期): 页码."
];
refs.forEach(r => c.push(new Paragraph({ spacing: { before: 40, after: 40, line: 320 },
  indent: { left: 480, hanging: 480 }, children: [new TextRun({ text: r, ...S24, size: 22 })] })));
c.push(pb());

// -------- 17 修订历史 --------
c.push(h1("17 方案修订历史"));
// TODO: 修订历史表格

// -------- 附录 --------
c.push(pb());
c.push(h1("附录1 重点关注安全性事件/终点的操作性定义"));
// TODO: 安全性事件定义表格

c.push(pb());
c.push(h1("附录2 评估量表/问卷"));
// TODO: 评估量表（MOAA/S、Aldrete、VAS、MMSE等）

// ==================== 文档组装 ====================
const doc = new Document({
  styles: {
    default: { document: { run: { font: F, size: 24 }, paragraph: { spacing: { line: 360 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: F },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0, keepNext: false, keepLines: false } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: F },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1, keepNext: false, keepLines: false } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: F },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2, keepNext: false, keepLines: false } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },  // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "{{研究方案简称}}", font: F, size: 18, color: "999999" })] })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "第 ", font: F, size: 18 }),
          new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18 }),
          new TextRun({ text: " 页", font: F, size: 18 })] })] })
    },
    children: c
  }]
});

// ==================== 生成文件 ====================
const outPath = "{{输出路径}}.docx";

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log("SUCCESS: Document generated at " + outPath);
  console.log("File size: " + (buffer.length / 1024).toFixed(1) + " KB");
  console.log("NEXT: Run sanitize.py to clean up the document:");
  console.log("  python scripts/sanitize.py " + outPath);
}).catch(err => {
  console.error("ERROR: Failed to generate document");
  console.error("REASON: " + err.message);
  console.error("HINT: Check that all placeholder values are valid strings and docx module is installed (npm install docx)");
  process.exit(1);
});
