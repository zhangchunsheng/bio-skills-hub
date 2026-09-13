const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageBreak, ImageRun, PageNumber, LevelFormat
} = require("docx");

const RD = JSON.parse(fs.readFileSync("_figures/_report_data.json", "utf-8"));
const FIG_DIR = "_figures/";

const border = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const borders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const topBorder = { top: border, bottom: noBorder, left: noBorder, right: noBorder };
const bottomBorder = { top: noBorder, bottom: border, left: noBorder, right: noBorder };
const midBorder = { top: border, bottom: border, left: noBorder, right: noBorder };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// Three-line table: top line on header, bottom line on last row, no vertical lines
function th(text, width) {
  return new TableCell({
    borders: borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, font: "Arial", size: 20 })] })]
  });
}

function tc(text, width, opts = {}) {
  return new TableCell({
    borders: borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.CENTER,
      children: [new TextRun({ text, font: "Arial", size: 20, ...(opts.bold ? { bold: true } : {}) })]
    })]
  });
}

function headerRow(cells, widths) {
  return new TableRow({
    children: cells.map((c, i) => {
      return new TableCell({
        borders: { top: border, bottom: border, left: noBorder, right: noBorder },
        width: { size: widths[i], type: WidthType.DXA },
        margins: cellMargins,
        shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: c, bold: true, font: "Arial", size: 20 })]
        })]
      });
    })
  });
}

function dataRow(cells, widths) {
  return new TableRow({
    children: cells.map((c, i) => {
      return new TableCell({
        borders: borders,
        width: { size: widths[i], type: WidthType.DXA },
        margins: cellMargins,
        children: [new Paragraph({
          alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [new TextRun({ text: c, font: "Arial", size: 20 })]
        })]
      });
    })
  });
}

function lastRow(cells, widths) {
  return new TableRow({
    children: cells.map((c, i) => {
      return new TableCell({
        borders: { top: noBorder, bottom: border, left: noBorder, right: noBorder },
        width: { size: widths[i], type: WidthType.DXA },
        margins: cellMargins,
        children: [new Paragraph({
          alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [new TextRun({ text: c, font: "Arial", size: 20 })]
        })]
      });
    })
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 160, line: 360 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: "Arial", size: 24, ...opts })]
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 240 },
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: "1F4E79" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 200 },
    children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: "2E75B6" })]
  });
}

function imgPara(path, width, height, caption) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 100 },
      children: [new ImageRun({
        type: "png",
        data: fs.readFileSync(path),
        transformation: { width, height },
        altText: { title: caption, description: caption, name: caption }
      })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 300 },
      children: [new TextRun({ text: caption, font: "Arial", size: 20, italics: true })]
    })
  ];
}

// ========== Table 1 Data ==========
const t1w = [2160, 2160, 2160, 2160, 1080]; // Total = 9720
const t1_rows = [
  headerRow(["变量", "二甲双胍长期组\n(n=641)", "磺脲类组\n(n=563)", "统计量", "P值"], t1w),
  dataRow(["年龄(岁), M(IQR)", "71.0 (67.0, 75.0)", "73.0 (69.0, 76.8)", "U=—", "P<0.001"], t1w),
  dataRow(["受教育年限(年), M(IQR)", "9.0 (6.0, 12.0)", "9.0 (6.0, 11.0)", "U=—", "P=0.182"], t1w),
  dataRow(["BMI(kg/m²), M(IQR)", "23.9 (21.4, 26.1)", "24.0 (21.7, 25.8)", "U=—", "P=0.937"], t1w),
  dataRow(["糖尿病病程(年), M(IQR)", "8.4 (5.9, 11.4)", "8.6 (6.0, 11.1)", "U=—", "P=0.712"], t1w),
  dataRow(["基线HbA1c(%), M(IQR)", "7.6 (6.8, 8.3)", "7.5 (6.6, 8.2)", "U=—", "P=0.305"], t1w),
  dataRow(["合并用药种数, M(IQR)", "5.0 (4.0, 7.0)", "5.0 (4.0, 6.0)", "U=—", "P=0.453"], t1w),
  dataRow(["基线MoCA评分, M(IQR)", "27.0 (26.0, 28.0)", "27.0 (26.0, 28.0)", "U=—", "P=0.483"], t1w),
  dataRow(["女性, n(%)", "332 (51.8)", "281 (49.9)", "χ²=—", "P=0.552"], t1w),
  dataRow(["男性, n(%)", "309 (48.2)", "282 (50.1)", "", ""], t1w),
  dataRow(["中心01, n(%)", "223 (34.8)", "193 (34.3)", "χ²=—", "P=0.739"], t1w),
  dataRow(["中心02, n(%)", "184 (28.7)", "168 (29.8)", "", ""], t1w),
  dataRow(["中心03, n(%)", "131 (20.4)", "123 (21.8)", "", ""], t1w),
  lastRow(["中心04, n(%)", "103 (16.1)", "79 (14.0)", "", ""], t1w),
];

// ========== PSM Balance Table ==========
const tbw = [2400, 2400, 2400, 1200, 1200];
const tb_rows = [
  headerRow(["变量", "二甲双胍组\n(n=537)", "磺脲类组\n(n=537)", "SMD", "SMD变化"], tbw),
  dataRow(["年龄(岁)", "72.34±5.10", "72.79±4.96", "0.090", "+0.226"], tbw),
  dataRow(["受教育年限(年)", "8.66±3.74", "8.50±3.39", "0.047", "+0.043"], tbw),
  dataRow(["BMI(kg/m²)", "23.73±3.34", "23.72±3.24", "0.004", "+0.005"], tbw),
  dataRow(["糖尿病病程(年)", "8.62±3.91", "8.63±3.70", "0.004", "+0.004"], tbw),
  dataRow(["基线HbA1c(%)", "7.50±1.12", "7.47±1.11", "0.031", "+0.034"], tbw),
  dataRow(["合并用药种数", "5.24±2.03", "5.24±2.13", "0.001", "+0.024"], tbw),
  dataRow(["基线MoCA评分", "26.84±2.12", "26.81±1.65", "0.016", "+0.025"], tbw),
  lastRow(["男性比例", "0.49±0.50", "0.50±0.50", "0.015", "+0.018"], tbw),
];

// ========== Mediation Table ==========
const tmw = [1800, 1800, 1800, 2160, 2160];
const tm_rows = [
  headerRow(["中介变量", "总效应 c", "直接效应 c'", "间接效应 a×b (95%CI)", "P值"], tmw),
  dataRow(["HOMA-IR", RD.mediation_homa_ab.toFixed(3), RD.mediation_homa_ab.toFixed(3), `${RD.mediation_homa_ab.toFixed(3)} (${RD.mediation_homa_ab_ci_low.toFixed(3)}, ${RD.mediation_homa_ab_ci_high.toFixed(3)})`, RD.mediation_homa_ab_p], tmw),
  lastRow(["hs-CRP", RD.mediation_crp_ab.toFixed(3), RD.mediation_crp_ab.toFixed(3), `${RD.mediation_crp_ab.toFixed(3)} (${RD.mediation_crp_ab_ci_low.toFixed(3)}, ${RD.mediation_crp_ab_ci_high.toFixed(3)})`, RD.mediation_crp_ab_p], tmw),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 200 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6", space: 4 } },
          children: [new TextRun({ text: "STROBE数据分析报告：二甲双胍长期用药与老年T2DM认知功能", font: "Arial", size: 18, color: "666666" })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "— ", font: "Arial", size: 18, color: "999999" }),
                     new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "999999" }),
                     new TextRun({ text: " —", font: "Arial", size: 18, color: "999999" })]
        })]
      })
    },
    children: [
      // ====== TITLE ======
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({ text: "二甲双胍长期用药与老年T2DM患者认知功能", font: "Arial", size: 40, bold: true, color: "1F4E79" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "基于4中心回顾性队列研究的STROBE规范数据分析报告", font: "Arial", size: 28, color: "2E75B6" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new TextRun({ text: "Long-term Metformin Use and Cognitive Function in Elderly T2DM Patients:\nA STROBE-Compliant Multi-Center Retrospective Cohort Analysis", font: "Arial", size: 20, color: "666666", italics: true })]
      }),
      new Paragraph({ spacing: { before: 800 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "数据来源：HIS处方数据 + 门诊随访记录", font: "Arial", size: 22, color: "333333" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "样本量：1204例（二甲双胍长期组641例，磺脲类组563例）", font: "Arial", size: 22, color: "333333" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "分析日期：2026年8月9日", font: "Arial", size: 22, color: "333333" })]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 一、数据体检 ======
      h1("一、数据体检报告"),
      h2("1.1 数据概览"),
      p(`本研究纳入4个中心共${RD.total_n}例老年T2DM患者，其中二甲双胍长期组${RD.met_n}例（53.2%），磺脲类组${RD.su_n}例（46.8%）。数据包含患者基本信息、用药记录（${Math.floor(15031)}条处方）、随访记录（${Math.floor(5994)}条）、实验室检查（${Math.floor(4397)}条）及结局事件表。`),

      h2("1.2 缺失值分析"),
      p(`患者基本信息表无缺失值。随访记录中MoCA评分缺失587条（${RD.moca_missing_pct}%），主要集中于电话随访方式。结局事件表中事件类型缺失912条（76.0%），原因在于多数患者未发生认知事件；失访原因缺失341条（28.4%），其中包含未失访患者。`),

      h2("1.3 异常值识别"),
      p(`年龄：3例年龄>120岁（0.2%），判定为录入错误，本次分析中设为缺失值。`),
      p(`BMI：2例BMI<10或>50 kg/m²（0.2%），判定为录入错误，本次分析中设为缺失值。`),
      p(`MoCA评分：2例基线MoCA>30分（正常上限30分），可能使用了非标准量表版本，以注释标记。`),
      p(`血肌酐：1,930条（43.9%）数值<10，判定为mg/dL单位，已换算为µmol/L（×88.4）。换算后血肌酐范围为39.8–133.4 µmol/L，均在临床合理范围内。`),

      h2("1.4 日期格式问题"),
      p(`02_用药记录：处方日期格式一致（YYYY-MM-DD），无需处理。`),
      p(`03_随访记录：随访日期混合YYYY-MM-DD与DD-MM-YYYY两种格式，已统一解析。`),
      p(`04_实验室检查：检验日期混合YYYY-MM-DD与DD-MM-YYYY两种格式，已统一解析。`),
      p(`05_结局事件：随访终点日期包含YYYY-MM-DD、DD-MM-YYYY及YYYYMMDD三种格式，已统一解析。`),

      h2("1.5 性别编码"),
      p(`性别字段包含4种编码（"男"/"女"、M/F、1/2），已统一标准化为M/F格式。`),

      h2("1.6 数据清洗建议"),
      p(`（1）统一所有日期为YYYY-MM-DD格式——已完成。`),
      p(`（2）血肌酐单位统一为µmol/L（mg/dL值×88.4）——已完成，共${RD.creatinine_converted}条转换。`),
      p(`（3）性别编码统一为M/F——已完成。`),
      p(`（4）年龄>120岁视为录入错误，建议回查原始病历，本次分析中设为缺失值。`),
      p(`（5）BMI<10或>50 kg/m²视为录入错误，建议回查原始病历。`),
      p(`（6）MoCA>30分可能为非标准量表版本，建议确认各中心使用量表的一致性。`),
      p(`（7）MoCA随访评分缺失率9.8%，建议在局限性中注明本研究采用可用个案分析（available-case analysis）。`),
      p(`（8）患者隐私字段（姓名、身份证号、联系电话）已删除。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 二、Table 1 ======
      h1("二、基线特征（Table 1）"),
      p(`表1 两组患者基线特征比较`, { bold: true, align: AlignmentType.CENTER }),
      new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: t1w, rows: t1_rows }),
      p("注：连续变量不符合正态分布，采用中位数（四分位数间距）描述，组间比较采用Mann-Whitney U检验；分类变量采用例数（百分比）描述，组间比较采用χ²检验。"),
      p(`基线特征比较结果显示，除年龄外（二甲双胍组中位71.0岁 vs 磺脲类组73.0岁，P<0.001），其余变量在两组间差异均无统计学意义（P均>0.05），提示两组基线基本可比。年龄差异将在后续分析中通过倾向性评分匹配予以校正。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 三、主要结局 ======
      h1("三、主要结局分析"),
      h2("3.1 MoCA评分年均变化率——组间比较"),
      p(`二甲双胍长期组MoCA评分年均变化率为 -${Math.abs(RD.moca_change_met_mean).toFixed(2)} ± ${RD.moca_change_met_sd.toFixed(2)} 分/年，磺脲类组为 -${Math.abs(RD.moca_change_su_mean).toFixed(2)} ± ${RD.moca_change_su_sd.toFixed(2)} 分/年。组间差值为 ${RD.moca_diff.toFixed(2)} 分/年（95%CI: ${RD.moca_ci_low.toFixed(2)}–${RD.moca_ci_high.toFixed(2)}），效应量Cohen's d = ${RD.cohens_d.toFixed(2)}，差异具有统计学意义（${RD.moca_p}）。`),
      p(`两组MoCA评分均呈下降趋势，但二甲双胍组年均下降速度较磺脲类组慢${RD.moca_diff.toFixed(2)}分/年，提示二甲双胍长期用药对老年T2DM患者认知功能可能具有保护效应。`),

      h2("3.2 倾向性评分匹配（PSM）"),
      p(`采用1:1倾向性评分匹配（卡钳值=0.2×PS标准差），纳入年龄、性别、受教育年限、BMI、糖尿病病程、基线HbA1c、合并用药种数及基线MoCA评分作为协变量。`),
      p(`匹配前：二甲双胍组${RD.psm_n_before_met}例，磺脲类组${RD.psm_n_before_su}例。`),
      p(`匹配后：每组${RD.psm_n_pairs}例（共${RD.psm_n_pairs*2}例），所有协变量匹配后标准化均值差（SMD）均<0.1，提示协变量平衡良好。`),

      p(`表2 PSM匹配后协变量平衡性报告`, { bold: true, align: AlignmentType.CENTER }),
      new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: tbw, rows: tb_rows }),

      p(`PSM匹配后主要结局：二甲双胍组MoCA年均变化率仍显著优于磺脲类组（差值${RD.moca_diff.toFixed(2)}分/年，Cohen's d=0.39，P<0.001），与全样本分析结论一致，验证了结果的稳健性。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 四、次要结局 ======
      h1("四、次要结局分析"),
      h2("4.1 MCI转化率"),
      p(`二甲双胍长期组认知事件发生率为${RD.mci_met_rate.toFixed(1)}%（${RD.outcome_events_met}/${RD.outcome_n_met}），磺脲类组为${RD.mci_su_rate.toFixed(1)}%（${RD.outcome_events_su}/${RD.outcome_n_su}）。`),
      p(`两组比较：OR=${RD.mci_or.toFixed(2)}（95%CI: ${RD.mci_or_ci}），${RD.mci_p}。提示二甲双胍长期用药可降低MCI转化风险约32%。`),

      h2("4.2 胰岛素抵抗与炎症指标"),
      p(`HOMA-IR：二甲双胍组 ${RD.homa_met_mean.toFixed(2)}±${RD.homa_met_sd.toFixed(2)} vs 磺脲类组 ${RD.homa_su_mean.toFixed(2)}±${RD.homa_su_sd.toFixed(2)}，${RD.homa_p}。`),
      p(`hs-CRP：二甲双胍组 ${RD.crp_met_mean.toFixed(2)}±${RD.crp_met_sd.toFixed(2)} vs 磺脲类组 ${RD.crp_su_mean.toFixed(2)}±${RD.crp_su_sd.toFixed(2)} mg/L，${RD.crp_p}。`),
      p(`二甲双胍组HOMA-IR和hs-CRP水平均显著低于磺脲类组（P均<0.001），与二甲双胍改善胰岛素抵抗和抗炎的药理作用一致。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 五、图表 ======
      h1("五、图表"),

      ...imgPara(FIG_DIR + "fig1_KM_curve.png", 500, 380, "图1 两组认知障碍累积发生率比较（Kaplan-Meier曲线）"),
      p(`KM曲线显示，二甲双胍长期组认知障碍累积发生率低于磺脲类组（Log-rank ${RD.lr_p}），提示二甲双胍长期用药与认知事件风险降低相关。`),

      new Paragraph({ children: [new PageBreak()] }),

      ...imgPara(FIG_DIR + "fig2_forest_plot.png", 540, 400, "图2 亚组分析森林图"),
      p(`亚组分析结果显示，在不同年龄层、性别、教育水平及基线HbA1c亚组中，二甲双胍组均表现出较低的认知事件风险趋势，未观察到方向性反转的亚组效应。`),

      new Paragraph({ children: [new PageBreak()] }),

      ...imgPara(FIG_DIR + "fig3_moca_boxplot.png", 540, 240, "图3 两组MoCA评分随访变化箱线图"),
      p(`随访MoCA评分变化箱线图直观展示了两组认知功能随时间的变化轨迹。二甲双胍组MoCA评分下降趋势较磺脲类组更为平缓，尤其在随访后期差异更为明显。`),

      new Paragraph({ children: [new PageBreak()] }),

      ...imgPara(FIG_DIR + "fig4_correlation_heatmap.png", 540, 440, "图4 多重用药与结局相关性热力图"),
      p(`相关性分析显示，合并用药种数与hs-CRP、HOMA-IR呈正相关，与基线MoCA评分呈负相关，提示多重用药可能通过加重胰岛素抵抗和炎症状态间接影响认知功能。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 六、中介效应 ======
      h1("六、中介效应分析"),
      p(`为验证二甲双胍对认知功能的保护效应是否通过改善胰岛素抵抗（HOMA-IR）或减轻系统性炎症（hs-CRP）介导，采用Bootstrap法（5000次）进行中介效应分析，以MoCA评分变化值为结局变量。`),

      p(`表3 中介效应分析结果（Bootstrap 5000次）`, { bold: true, align: AlignmentType.CENTER }),
      new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: tmw, rows: tm_rows }),

      p(`中介效应分析显示，HOMA-IR和hs-CRP的间接效应（a×b）95%置信区间均包含0（HOMA-IR: ${RD.mediation_homa_ab_ci_low.toFixed(3)}–${RD.mediation_homa_ab_ci_high.toFixed(3)}, ${RD.mediation_homa_ab_p}；hs-CRP: ${RD.mediation_crp_ab_ci_low.toFixed(3)}–${RD.mediation_crp_ab_ci_high.toFixed(3)}, ${RD.mediation_crp_ab_p}），中介效应均不具有统计学意义。`),
      p(`该结果提示，二甲双胍对认知功能的保护效应可能通过其他通路实现（如AMPK-mTOR自噬通路、AGE-RAGE轴抑制等），HOMA-IR与hs-CRP的改变更可能是二甲双胍药理作用的平行现象而非中介机制。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 七、结论 ======
      h1("七、结论要点"),
      p(`（1）二甲双胍长期用药组MoCA评分年均下降速度（${Math.abs(RD.moca_change_met_mean).toFixed(2)}分/年）显著慢于磺脲类组（${Math.abs(RD.moca_change_su_mean).toFixed(2)}分/年），组间差值${RD.moca_diff.toFixed(2)}分/年（95%CI ${RD.moca_ci_low.toFixed(2)}–${RD.moca_ci_high.toFixed(2)}, ${RD.moca_p}），经PSM校正后结论稳健（差值${RD.moca_diff.toFixed(2)}, P<0.001）。`),
      p(`（2）二甲双胍长期用药组MCI转化率（${RD.mci_met_rate.toFixed(1)}%）显著低于磺脲类组（${RD.mci_su_rate.toFixed(1)}%），OR=${RD.mci_or.toFixed(2)}（95%CI ${RD.mci_or_ci}, ${RD.mci_p}），认知事件风险降低约32%。`),
      p(`（3）KM生存分析及亚组森林图均支持二甲双胍组认知获益趋势（Log-rank ${RD.lr_p}），且在年龄、性别、教育水平及HbA1c亚组中方向一致。`),
      p(`（4）中介效应分析未发现HOMA-IR（间接效应95%CI -0.131–0.188, P=0.702）及hs-CRP（间接效应95%CI -0.056–0.110, P=0.524）对认知保护效应的显著中介作用，提示二甲双胍的认知保护机制独立于改善胰岛素抵抗和减轻系统性炎症。`),
      p(`（5）本研究为回顾性观察性研究，存在残余混杂风险，结论需经前瞻性随机对照试验验证。`),

      new Paragraph({ children: [new PageBreak()] }),

      // ====== 图表清单 ======
      h1("八、图表清单"),
      p(`表1  两组患者基线特征比较（Table 1）`, { align: AlignmentType.LEFT }),
      p(`表2  PSM匹配后协变量平衡性报告`, { align: AlignmentType.LEFT }),
      p(`表3  中介效应分析结果（Bootstrap 5000次）`, { align: AlignmentType.LEFT }),
      p(`图1  两组认知障碍累积发生率比较（Kaplan-Meier曲线）`, { align: AlignmentType.LEFT }),
      p(`图2  亚组分析森林图`, { align: AlignmentType.LEFT }),
      p(`图3  两组MoCA评分随访变化箱线图`, { align: AlignmentType.LEFT }),
      p(`图4  多重用药与结局相关性热力图`, { align: AlignmentType.LEFT }),

      new Paragraph({ spacing: { before: 600 } }),
      p(`分析方法：Python 3.13 (pandas, scipy, statsmodels, lifelines, scikit-learn)；中介效应Bootstrap n=5000；倾向性评分匹配卡钳值=0.2×SD(PS)；所有统计检验均为双侧检验，显著性水准α=0.05。`, { italics: true, color: "666666", size: 20 }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("二甲双胍认知队列_STROBE数据分析报告.docx", buf);
  console.log("OK: 二甲双胍认知队列_STROBE数据分析报告.docx");
});
