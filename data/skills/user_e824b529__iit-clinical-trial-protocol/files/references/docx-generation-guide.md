# Word文档生成技术指南

## 目录
- [1. 概述](#1-概述)
- [2. 环境准备](#2-环境准备)
- [3. 字体配置（中文文档必需）](#3-字体配置中文文档必需)
- [4. 辅助函数](#4-辅助函数)
  - [4.1 段落](#41-段落)
  - [4.2 标题](#42-标题)
  - [4.3 表格单元格](#43-表格单元格)
  - [4.4 分页符](#44-分页符)
- [5. 文档结构](#5-文档结构)
  - [5.1 样式定义](#51-样式定义)
  - [5.2 关键规则](#52-关键规则)
- [6. 完整章节生成顺序](#6-完整章节生成顺序)
- [7. 生成与清理](#7-生成与清理)
- [8. 常见问题](#8-常见问题)

## 1. 概述

使用JavaScript `docx-js` 库生成研究方案Word文档。生成后使用 `sanitize.py` 进行清理验证。

## 2. 环境准备

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');
```

## 3. 字体配置（中文文档必需）

```javascript
const F = { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" };
const S24 = { font: F, size: 24 };
```

## 4. 辅助函数

### 4.1 段落
```javascript
function p(text, opts = {}) {
  return new Paragraph({ spacing: { before: 60, after: 60, line: 360 }, ...opts,
    children: [new TextRun({ text, ...S24, ...opts.run })] });
}
function pB(text, opts = {}) { return p(text, { ...opts, run: { bold: true, ...opts.run } }); }
```

### 4.2 标题
```javascript
function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 200 },
  children: [new TextRun({ text, font: F, size: 32, bold: true })] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2,
  spacing: { before: 280, after: 160 },
  children: [new TextRun({ text, font: F, size: 28, bold: true })] }); }
```

### 4.3 表格单元格
```javascript
function tc(text, opts = {}) {
  return new TableCell({
    borders, width: { size: opts.width || 4680, type: WidthType.DXA },
    shading: opts.shade ? { fill: "D5E8F0", type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ spacing: { before: 20, after: 20 },
      children: [new TextRun({ text, ...S24, bold: opts.bold || false })] })] });
}
```

### 4.4 分页符
```javascript
function pb() { return new Paragraph({ children: [new PageBreak()] }); }
```

## 5. 文档结构

### 5.1 样式定义
```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: F, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", ..., run: { size: 32, bold: true, font: F },
        paragraph: { spacing: {...}, outlineLevel: 0, keepNext: false, keepLines: false } },
      { id: "Heading2", ..., run: { size: 28, bold: true, font: F },
        paragraph: { spacing: {...}, outlineLevel: 1, keepNext: false, keepLines: false } },
    ]
  },
  numbering: { config: [ /* bullets, numbers */ ] },
  sections: [{ /* 单一section */ }]
});
```

### 5.2 关键规则
- **使用单一section**：多section会产生空白页
- **设置keepNext: false**：避免标题与后续内容强制同页导致大量空白
- **表格双重宽度**：columnWidths和每个cell的width都要设置
- **cantSplit: true**：表格行不跨页
- **ShadingType.CLEAR**：不用SOLID（会导致黑色背景）
- **A4页面**：width: 11906, height: 16838
- **页边距**：margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }

## 6. 完整章节生成顺序

按以下顺序将内容push到children数组：

1. 封面页（标题、方案编号、版本信息）+ PageBreak
2. 保密声明 + PageBreak
3. 签字页 + PageBreak
4. 缩略语表（Table）+ PageBreak
5. 方案摘要表（Table）+ PageBreak
6. 1 研究背景（h1 + 多段p + 文献引用）
7. 2 研究目的
8. 3 研究假设
9. 4 研究设计（4.1整体设计 + 4.2随机化设盲）
10. 5 研究人群（5.1诊断标准 + 5.2入选 + 5.3排除 + 5.4退出）
11. 6 研究用药（6.1试验药表格 + 6.2对照药表格 + 6.3合并用药 + 6.4药品管理）
12. 7 研究方法（7.1筛选 + 7.2治疗期给药方案 + 7.3随访 + 7.4评估时间表）
13. 8 研究终点（8.1主要 + 8.2次要 + 8.3安全性指标）
14. 9 安全性监测（AE/SAE/SUSAR定义与报告）
15. 10 终止标准
16. 11 结束规定
17. 12 数据管理
18. 13 统计分析（13.1样本量 + 13.2分析人群 + 13.3统计方法 + 13.4软件）
19. 14 试验管理（14.1 GCP + 14.2隐私 + 14.3质控 + 14.4监查与稽查 + 14.5进度 + 14.6职责）
20. 15 伦理学（15.1伦理委员会 + 15.2知情同意 + 15.3受试者保护 + 15.4注册）
21. 16 参考文献（GB/T 7714格式）
22. 17 修订历史
23. 附录1 安全性事件定义表
24. 附录2 评估量表（MOAA/S、Aldrete、VAS、MMSE等）

## 7. 生成与清理

```bash
# 生成文档
node generate_protocol_template.js

# 清理验证（sanitize.py 位于本技能 scripts/ 目录）
python scripts/sanitize.py output.docx

# 若 sanitize.py 依赖缺失，先安装：
pip install defusedxml --break-system-packages
```

## 8. 常见问题

| 问题 | 解决方案 |
|------|---------|
| 中文显示为方框 | 配置eastAsia字体为Microsoft YaHei |
| 引号显示为乱码 | 使用JavaScript转义 \" 而非XML实体 |
| 中文文本含双引号致语法错误 | 在JS双引号字符串内使用中文引号“”而非ASCII双引号" |
| 表格列宽不对 | 同时设置columnWidths和cell width |
| 大量空白页 | 设置keepNext: false；使用单一section |
| 分页位置不对 | 在章节间使用PageBreak |
| 项目符号显示错误 | 使用LevelFormat.BULLET，不要手动输入• |
| sanitize.py 报错 | 检查defusedxml是否安装：`pip install defusedxml --break-system-packages` |
