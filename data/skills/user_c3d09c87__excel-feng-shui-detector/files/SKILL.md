---
name: excel-feng-shui-detector
description: Perform a read-only structural audit of local .xlsx workbooks for merged-cell hazards, hidden sheets, rows and columns, formula errors, full-column formulas, numeric values stored as text, duplicate or blank headers, style fragmentation, bloated used ranges, missing freeze panes, and other maintainability risks; then produce a humorous but evidence-backed Excel feng shui report and prioritized repair plan. Use when users ask to Excel风水检测, 检查表格混乱, 查找公式煞气, 分析隐藏列, 清理工作簿, 审计Excel质量, or understand why a workbook is hard to filter, calculate, print, or maintain.
---

# Excel 风水检测器

检查财位、煞气、隐藏空间和祖传公式。笑点用于报告包装；风险判断必须给出工作表、单元格或范围证据。

## 工作流

1. 接收 `.xlsx` 文件，默认只读分析，不修改原文件。
2. 运行结构检查：

```bash
python scripts/inspect_excel_fengshui.py --input <workbook.xlsx> --output <report.json> --pretty
```

3. 按 `references/fengshui-rules.md` 复核发现。合并单元格、隐藏列和多种样式可能有合理用途，不能机械判错。
4. 必要时视觉渲染所有相关工作表，检查标题、表头、截断、空白、图表遮挡和打印布局。结构脚本不能替代视觉检查。
5. 按 `assets/fengshui-report-template.md` 输出：
   - 总体气运；
   - 财位；
   - 主要煞气；
   - 隐藏空间；
   - 祖传法器；
   - 化煞顺序。
6. 只有用户明确要求修复时，才另存新工作簿；保留原有格式和公式，修改后检查关键范围、公式错误并渲染复核。

## 必须输出

- 风水分数、等级和一句话诊断；
- 每条发现的工作表、单元格或范围证据；
- 区分确定错误、维护风险和人工复核候选；
- 按“先防数据错误、再防误操作、最后改善可读性”排序；
- 说明每项修复的影响和可能副作用；
- 无法通过静态结构判断的内容，例如外部链接、宏、计算结果和业务口径。

## 约束

- 不自动删除、取消隐藏、拆分合并单元格、修改公式或覆盖原文件。
- 合并单元格适合标题和展示区，不适合明细计算区；必须结合位置判断。
- 数字样式文本可能是订单号、邮编或账号，只能标为人工复核候选。
- 修改时间、缓存结果和静态 XML 不能证明公式当前计算正确。
- `.xls`、`.xlsb`、含宏 `.xlsm` 和受密码保护文件超出本脚本范围，要明确提示。
- 不声称静态扫描已经完成业务数据正确性审计。
