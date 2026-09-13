/**
 * 叙事素材与平行病历Word文档生成脚本 v2.0
 * 按照《叙事素材模板.docx》标准格式生成文档
 * 
 * 用法: node create_narrative_doc.js <输出路径> [配置JSON]
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak, Header, Footer, PageNumber
} = require('docx');

// ============== 默认配置 ==============
const defaultConfig = {
  // 基本信息
  title: '叙事素材',
  category: '平行病历',
  materialType: '疾病叙事',
  timeWindow: '治疗中',
  genre: '回忆录',
  keywords: [],
  difficulty: '中级',
  scenario: '',
  targetObject: '患者',
  diagnosis: '',
  narrativePopulation: '慢性病患者',
  narrativeClosure: '疑虑型',
  checkType: '',
  drugType: '',
  treatmentType: '',
  nursingProject: '',
  personality: '',
  symptoms: '',
  
  // 叙事结构
  narrativeType: '旅程式叙事',
  rhythm: { start: '悬念设置', development: '线性推进', climax: '戏剧冲突', ending: '开放' },
  coreConflict: '医患冲突',
  tension: '高',
  emotion: '矛盾',
  metaphor: '',
  culturalElement: '',
  focus: '患者中心',
  focusShift: '',
  consistency: '基本一致',
  empathyPath: '分别人认知共情、情感共情、行为共情三方面提出共情路径方法与注意事项。',
  
  // 时间节点
  timeline: [],
  
  // 内容
  materialContent: '',
  parallelContent: {}
};

// ============== 工具函数 ==============

// 加载配置
function loadConfig(configPath) {
  if (configPath && fs.existsSync(configPath)) {
    const configStr = fs.readFileSync(configPath, 'utf-8');
    return { ...defaultConfig, ...JSON.parse(configStr) };
  }
  return defaultConfig;
}

// 边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: '999999' };
const borders = { top: border, bottom: border, left: border, right: border };

// 创建单元格
function createCell(text, width, options = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: options.fill ? { fill: options.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: options.alignment || AlignmentType.LEFT,
      spacing: { before: 0, after: 0 },
      children: [new TextRun({ 
        text: text || '', 
        bold: options.bold || false, 
        size: options.size || 21,
        font: 'Microsoft YaHei',
        color: options.color || '000000'
      })]
    })]
  });
}

// ============== 表格生成函数 ==============

// 基本信息表格
function createBasicInfoTable(config) {
  const rows = [
    ['【叙事素材标题】', config.title || '叙事素材'],
    ['【素材来源】', config.category || '平行病历'],
    ['【素材类型】', config.materialType || '疾病叙事'],
    ['【叙事时间窗】', config.timeWindow || '治疗中'],
    ['【素材文学体裁】', config.genre || '回忆录'],
    ['【关键词】', config.keywords?.join('、') || '[3-5个关键词]'],
    ['【难度等级】', config.difficulty || '中级'],
    ['【适用场景】', config.scenario || ''],
    ['【适用对象】', config.targetObject || '患者'],
    ['【适用诊断】', config.diagnosis || ''],
    ['【适用叙事人群分类】', config.narrativePopulation || ''],
    ['【适用叙事闭锁分类】', config.narrativeClosure || '老年型'],
    ['【适用检查类型】', config.checkType || ''],
    ['【适用药物类型】', config.drugType || ''],
    ['【适用治疗类型】', config.treatmentType || ''],
    ['【适用护理项目】', config.nursingProject || ''],
    ['【适用关联性格】', config.personality || ''],
    ['【适用临床症状表现】', config.symptoms || '']
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: rows.map(row => new TableRow({
      children: [
        createCell(row[0], 2800, { fill: 'D5E8F0', bold: true, size: 21 }),
        createCell(row[1], 6560, { size: 21 })
      ]
    }))
  });
}

// 叙事结构表格
function createNarrativeStructureTable(config) {
  const rows = [
    ['【叙事类型】', config.narrativeType || '旅程式叙事'],
    ['【叙事节奏】', `开头：${config.rhythm?.start || '悬念设置'}；发展：${config.rhythm?.development || '线性推进'}；高潮：${config.rhythm?.climax || '戏剧冲突'}；结局：${config.rhythm?.ending || '开放'}`],
    ['【核心冲突】', config.coreConflict || '医患冲突'],
    ['【叙事张力】', config.tension || '高'],
    ['【情感基调】', config.emotion || '矛盾'],
    ['【主题隐喻】', config.metaphor || ''],
    ['【文化元素】', config.culturalElement || ''],
    ['【叙事焦点】', config.focus || '患者中心'],
    ['【叙事焦点转移】', config.focusShift || ''],
    ['【叙事一致性】', config.consistency || '基本一致'],
    ['【共情路径】', config.empathyPath || '分别人认知共情、情感共情、行为共情三方面提出共情路径方法与注意事项。']
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: rows.map(row => new TableRow({
      children: [
        createCell(row[0], 2800, { fill: 'FFF3E0', bold: true, size: 21 }),
        createCell(row[1], 6560, { size: 21 })
      ]
    }))
  });
}

// 关键时间节点
function createTimelineSection(timeline) {
  const defaultTimeline = 'T0：疾病发现与诊断\nT1：治疗体验与反应\nT2：情绪与情感表达\nT3：医患互动与沟通\nT4：反思与感悟';
  
  const text = timeline && timeline.length > 0 
    ? timeline.map(t => `${t.time || 'T' + timeline.indexOf(t)}：${t.event}`).join('\n')
    : defaultTimeline;

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          createCell(text, 9360, { size: 21 })
        ]
      })
    ]
  });
}

// ============== 内容生成函数 ==============

// 素材原文部分
function createMaterialContent(config) {
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 400, after: 200 },
      children: [new TextRun({ text: '【素材原文】', bold: true, size: 32, font: 'Microsoft YaHei', color: '1F4E79' })]
    }),
    new Paragraph({
      spacing: { after: 300 },
      children: [new TextRun({ text: '文字不少于1500字，紧密按照上述要求及用户提出的主题进行素材撰写', size: 20, color: '666666', font: 'Microsoft YaHei' })]
    }),
    new Paragraph({
      spacing: { after: 400, line: 360 },
      children: [new TextRun({ text: config.materialContent || '[请在此处撰写叙事素材原文]', size: 24, font: 'Microsoft YaHei' })]
    })
  ];
}

// 平行病历七部分
function createParallelRecord(config) {
  const p = config.parallelContent || {};
  
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 400, after: 200 },
      children: [new TextRun({ text: '平行病历正文', bold: true, size: 32, font: 'Microsoft YaHei', color: '1F4E79' })]
    }),
    new Paragraph({
      spacing: { after: 300 },
      children: [new TextRun({ text: '正文须严格遵循以下七部分结构展开：', bold: true, size: 24, font: 'Microsoft YaHei' })]
    }),
    
    // 1. 疾病发现与诊断
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '1. 疾病发现与诊断', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.discovery || '【描述疾病发现的过程、症状体验、初次就医经历】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 2. 治疗体验与反应
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '2. 治疗体验与反应', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.treatment || '【描述治疗过程中的身体感受、心理变化、不良反应】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 3. 情绪与情感表达
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '3. 情绪与情感表达', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.emotion || '【记录患者及家属的情绪波动、情感表达、心理诉求】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 4. 家庭与社会支持
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '4. 家庭与社会支持', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.family || '【家庭关系、社会支持、经济状况对疾病的影响】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 5. 医患互动与沟通
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '5. 医患互动与沟通', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.doctor || '【医患沟通情况、信任关系、决策过程、期望匹配】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 6. 重要转折与意义
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '6. 重要转折与意义', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 250, line: 360 },
      children: [new TextRun({ text: p.turning || '【叙事中的关键转折点及其对患者和医生的意义】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    }),
    
    // 7. 反思与感悟
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 150 },
      children: [new TextRun({ text: '7. 反思与感悟', bold: true, size: 26, font: 'Microsoft YaHei', color: '2E75B6' })]
    }),
    new Paragraph({
      spacing: { after: 400, line: 360 },
      children: [new TextRun({ text: p.reflection || '【患者的反思、成长或困惑，医生的反思、洞察或困惑】', size: 24, font: 'Microsoft YaHei', color: '333333' })]
    })
  ];
}

// ============== 主文档生成 ==============

async function generateDocument(config, outputPath) {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: 'Microsoft YaHei', size: 21 }
        }
      },
      paragraphStyles: [
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 32, bold: true, font: 'Microsoft YaHei', color: '1F4E79' },
          paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 }
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 26, bold: true, font: 'Microsoft YaHei', color: '2E75B6' },
          paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 }
        }
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '2E75B6', space: 4 } },
            children: [new TextRun({ text: '叙事医学素材', color: '666666', size: 18, font: 'Microsoft YaHei' })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 4 } },
            children: [
              new TextRun({ text: '第 ', size: 18, color: '666666', font: 'Microsoft YaHei' }),
              new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
              new TextRun({ text: ' 页', size: 18, color: '666666', font: 'Microsoft YaHei' })
            ]
          })]
        })
      },
      children: [
        // 标题
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, after: 400 },
          children: [new TextRun({ text: '叙事素材', bold: true, size: 40, font: 'Microsoft YaHei', color: '1F4E79' })]
        }),
        
        // 基本信息表格
        createBasicInfoTable(config),
        
        new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }),
        
        // 关键时间节点
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 0, after: 150 },
          children: [new TextRun({ text: '【关键时间节点】', bold: true, size: 24, font: 'Microsoft YaHei', color: '333333' })]
        }),
        createTimelineSection(config.timeline),
        
        new Paragraph({ spacing: { before: 300, after: 200 }, children: [] }),
        
        // 叙事结构表格
        createNarrativeStructureTable(config),
        
        new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }),
        
        // 分隔线
        new Paragraph({
          border: { bottom: { style: BorderStyle.DASHED, size: 6, color: 'AAAAAA', space: 4 } },
          spacing: { after: 200 },
          children: [new TextRun({ text: '' })]
        }),
        
        // 素材原文
        ...createMaterialContent(config),
        
        // 分页
        new Paragraph({ children: [new PageBreak()] }),
        
        // 平行病历
        ...createParallelRecord(config)
      ]
    }]
  });

  // 生成文件
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(outputPath, buffer);
  console.log(`文档已生成: ${outputPath}`);
  return outputPath;
}

// ============== 主函数 ==============

async function main() {
  const args = process.argv.slice(2);
  const outputPath = args[0] || './叙事素材.docx';
  const configPath = args[1];
  
  const config = loadConfig(configPath);
  await generateDocument(config, outputPath);
}

// 运行
main().catch(console.error);

// 导出供外部调用
module.exports = { generateDocument, defaultConfig };
