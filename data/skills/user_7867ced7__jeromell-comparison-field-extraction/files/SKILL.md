---
slug: jeromell-comparison-field-extraction
displayName: "可比公司字段提取"
version: 1.0.0
summary: "为横向对比表提取单只标的的固定字段，输出结构统一、口径带年份的可比行，适合快速搭同业对比表。"
license: MIT
name: comparison-field-extraction
description: Extract a stock's comparable fields for a horizontal comparison table in a fixed schema (前瞻PE / 乐观空间 / 壁垒层级 / 份额 / $per-unit / 参考设计 / 验证态), each cell carrying source+date+证据态, by READING the 主文件 header rather than re-deriving. Use when building or refreshing a 横向对比 cluster table (see 横向对比框架_v0.1), or when adding a stock to an existing comparison. Skill spec is shared with AlphaClaw — write once, sync over.
---

# 横向对比抽取 (comparison-field-extraction)

把一只票抽成横向对比表里的一行，字段口径固定、cell 带证据态。**READ 主文件头部，不重录数据**（主文件是唯一真相源）。

## 何时用
- 建/刷新某 cluster 的横向对比表。
- 给已有对比表加一只票，或加一列新维度。

## 步骤
1. 读标的「主文件」头部：stance / 乐观情景 / 🎯验证表 / 分部指标。**缺的字段才去取数**（免费源优先）。
2. 按三层维度填：
   - **通用**：前瞻 PE(27E/28E) / 乐观空间(vs现价) / 增长 / 毛利质量 / 市值 / stance+验证进度。
   - **行业特化**（最有区分度）：该 cluster 的特化列（如 AI 电力链：$/MW、是否进 NVIDIA 参考设计、链上份额、电源 vs 液冷敞口、商品化程度）。
   - **用户自定义**：用户提的对比角度列。
3. 每 cell 标证据态 ✅/🔵/—；关键数走 `sellside-claim-triangulation` 核过才标 ✅。
4. 主文件已有数**引用**即可，不重录。

## 输出 schema
一行 = `{标的 | 层级 | 前瞻估值 | 乐观空间 | 行业特化字段… | stance+验证 | 一句话}`。横向比较导出出版级 SVG（无竖线、分组表头、克制灰阶）；不要用 `render_excel_table.py` 画红蓝 Excel 网格。

## 接口
- 喂 research_os(L4) 排 top-10；新维度 → 回填整列；用户提对比角度 → 加列（每表底「自定义对比角度」区登记口径）。
