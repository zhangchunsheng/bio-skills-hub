---
name: pharma-rnpv-valuation
description: >
  医药股 rNPV（风险调整净现值）估值流水线。输入任意 A股/港股医药股名称或代码，
  自动执行：财务快照 → 管线映射 → 逐管线 rNPV 建模（含 license-out 六件套）→
  分部加总 → ⭐市场隐含成功率反推 → 产出 Excel 模型 + Markdown 报告 + 结构化 JSON。
  回答"以当前价格买入这只医药股，相当于押注了什么样的管线成功率？市场是太乐观还是太悲观"。
  触发词：rNPV分析、医药股估值、管线估值、创新药估值、pipeline valuation、pharma rnpv、市场隐含成功率。
---

# 医药股 rNPV 估值流水线

## 概述

输入一只医药股（创新药 Biotech / 中型 Pharma），完整执行 [`pipeline.md`](pipeline.md) 的 **9 个 Stage（Stage 0–8）**，产出可审计的 Excel rNPV 模型 + 8 章分析报告 + 结构化 JSON（条件校验，见产出文件节）。

**核心问题：** 如果以当前价格买入这只医药股，我相当于押注了什么样的管线成功率？市场是太乐观还是太悲观？

**双引擎哲学（缺一不可）：**
1. **正向估值** — 算"值多少"：管线 PoS × 峰值销售 × 折现，逐管线 rNPV 分部加总
2. **⭐反向市场隐含反推** — 算"市场押注了什么"：拆解市值 → 反推隐含折扣因子 λ → 对比行业 PoS 基准 → 判读低估/高估

> 与普通 rNPV 计算器的区别：本系统不只正向算"值多少"，更反推"市场押注了什么"——这是最有洞察价值的环节。

## 输入规范

| 参数 | 必填 | 说明 | 示例 |
|---|---|---|---|
| 股票名称或代码 | ✅ | 中文名、A股代码（600276.SH）、港股代码（01093.HK） | "恒瑞医药"、"01093.HK" |
| 市场 | 自动识别 | A股 / 港股，从代码后缀推断 | .SS/.SZ = A股，.HK = 港股 |

**适用范围：** ✅ 管线驱动型 Biotech、创新药企业、中型 Pharma；⚠️ 不适合纯 CRO/CDMO、仿制药、医疗器械（详见 pipeline.md 末节）。

## 执行流程

**完整执行 [`pipeline.md`](pipeline.md) 的 9 个 Stage（Stage 0–8），不可跳步：**

Stage 0 输入初始化 → Stage 1 财务快照 → Stage 2 管线映射 → Stage 3 逐管线 rNPV（PoS 赋值/峰值估算/现金流/折现）→ Stage 4 分部加总 → Stage 5 ⭐市场隐含反推 → Stage 6 风险与催化剂 → Stage 7 质量自检 gate → Stage 8 产出文件

方法论细节按 pipeline.md 的索引查阅 `references/` 对应文件。

### 5 条核心纪律（不可妥协）

1. **费用率加法** `(1-cogs-sga)*(1-tax)`，不用乘法
2. **λ 双报判读**：同时报告 λ 和 λ/加权PoS（λ 绝对值无判读意义）
3. **partnered 资产六件套逐项建模**（首付+里程碑+royalty+供货+海外），不简化为单一 royalty
4. **区间优先**：关键参数用区间 + 悲观/基准/乐观三情境，禁止虚假精度单点
5. **卖方共识不能作中性标尺**反推模型

## 产出文件

保存至 `output/[ticker]_[YYYY-MM-DD]/`（相对当前任务目录）：

| 文件 | 内容 |
|---|---|
| `[ticker]_rNPV_model.xlsx` | 6 Sheet：Summary / Pipeline / rNPV Detail / Implied PoS / Assumptions / Sensitivity（蓝=输入、黑=公式、绿=跨表引用，关键数字附来源注释） |
| `[ticker]_rNPV_report.md` | 8 章报告（按 `templates/report-template.md`），核心是第 6 章"市场隐含视角" |
| `[ticker]_implied.json` | 结构化输出（条件交付，适用规则见下） |

> **JSON 校验的适用条件**：`output_schema.json` 的硬校验字段（PE 基准、卖方一致预期、reverse-DCF 双读数）面向**有已上市产品、可做市场隐含反推的成熟标的**——此类标的产出 JSON 时必须过 `validate_output.py` 校验（`python validate_output.py <json>`，PASS 该环节才算完成）。对 **pre-revenue 管线型 Biotech**（无 PE、无一致预期覆盖），JSON 为可选增强、不强求 PASS——以 Excel 模型 + 报告为交付完成标准，并在报告中注明"未做 JSON 硬校验（标的无 PE/一致预期基准）"。

## 运行环境与降级

- **Python 3.10+**。`validate_output.py` / `render_report.py` 纯标准库，任何环境可跑。
- **Excel 生成**调 `templates/rNPV_excel_template.py`（依赖 openpyxl）。**若环境无 openpyxl 或安装失败：降级为 Markdown 报告 + CSV 数据表**（用标准库 csv 把 6 个 Sheet 内容平铺输出，文件名 `[ticker]_rNPV_data_*.csv`），**不阻塞交付**，并在报告中注明"Excel 模型因环境缺库降级为 CSV"。
- **行情数据**：优先 yfinance（如环境可用），不可用时用网络搜索获取股价/市值/股本，并在报告中标注数据口径与日期。
- **管线与财务信息**：网络搜索（公司年报/IR/ClinicalTrials.gov/CDE 公开信息），多源交叉验证，禁止未经验证的数字。
- **数据可得性三态**：数据齐备 → 完整执行；部分可得 → 降级执行并在报告标注缺失项；不可得 → 该 Stage 显式标注「数据不可得」后继续后续 Stage，不静默中止。
- **进度汇报**：这是深度分析任务（通常数分钟）。执行中每个 Stage 完成时向用户简报进度（如「Stage 2 管线映射完成：共 6 条管线」），管理等待预期。
- **无 Python 运行时环境**：若运行环境无法执行 Python 脚本，校验/渲染/Excel 环节由 Agent 手工执行等效计算与自查，交付物降级为 Markdown 报告 + 数据表，报告标注「⚠️ 未过脚本校验（环境无 Python）」。

## 免责声明（每份报告必须包含）

> ⚠️ 本报告基于公开信息与模型假设产出，仅供研究参考，不构成投资建议；数据可能滞后或不完整，rNPV 估值对 PoS 和峰值销售假设高度敏感，实际结果可能与预测存在重大差异。投资决策请咨询持牌专业人士。

## 参考文件索引

| 文件 | 用途 | 何时查阅 |
|---|---|---|
| **`pipeline.md`** | **9-Stage 完整流水线（执行入口）** | **每次执行必读** |
| `references/00-methodology-overview.md` | 方法论总纲：双引擎哲学 + 5 条纪律 | 首次使用必读 |
| `references/rNPV-methodology.md` | rNPV 六步法 + 费用率口径 + 区间纪律 | Stage 3 自营管线 |
| `references/partnered-asset-valuation.md` | license-out 六件套建模 | Stage 3 遇 license-out |
| `references/clinical-trial-POS-benchmarks.md` | BIO 行业 PoS 基准 + 情境微调 | Stage 3a 查 PoS |
| `references/peak-sales-framework.md` | 峰值销售漏斗（8 层流行病学） | Stage 3b 估峰值 |
| `references/discount-rate-guide.md` | 折现率选取 + 全参数敏感性 | Stage 3d 选 WACC |
| `references/reverse-rnpv-method.md` | ⭐市场隐含反推 + λ 判读 | Stage 5 |
