# 医药股 rNPV 价值分析系统

> 输入任意 A股/港股医药股名称或代码，自动执行：取价 → 管线映射 → 逐管线 rNPV 建模 → 市场隐含成功率反推 → 产出 Excel 模型 + Markdown 报告。

## 这是什么

一套**可复用的医药股 rNPV（Risk-Adjusted Net Present Value，风险调整净现值）估值流水线**。

rNPV 是生物科技/医药行业估值的黄金标准：每条管线药物有独立的临床阶段、成功概率（PoS）、峰值销售预期，将各管线的风险调整后现金流折现求和，即得公司内在价值。

**本系统的独特价值：** 不仅有正向 rNPV 估值，还能**反向拆解**——当前股价隐含了什么样的管线成功率？市场是太乐观还是太悲观？

## 核心公式

```
正向 rNPV 估值：
  每条管线 rNPV = PoS(阶段→获批) × Σ [ 年度FCF / (1+WACC)^t ]
  股权价值 = Σ(各管线 rNPV) + 已上市产品 DCF + 净现金
  每股价值 = 股权价值 / 总股本

反向隐含分析（核心洞察）：
  市场隐含管线价值 = 当前市值 - 已上市产品NPV - 净现金
  λ = 市场隐含管线价值 / Σ无风险PV
  判读：λ/加权PoS（非 λ 绝对值）→ <0.7 悲观 / ~1.0 合理 / >1.5 乐观
  结论：隐含 PoS vs 基准 PoS → 低估 / 合理 / 高估
```

## 使用方法

对本 agent 说：
- "分析 **恒瑞医药**" 或 "分析 **01093.HK**"
- 触发词：`rNPV分析 [股票]`、`医药股估值 [股票]`、`pipeline valuation [ticker]`

### 产出

每次分析在 `output/[ticker]_[YYYY-MM-DD]/` 下产出：

| 文件 | 内容 |
|---|---|
| `[ticker]_rNPV_model.xlsx` | 6 个 Sheet 的完整 rNPV 估值模型 |
| `[ticker]_rNPV_report.md` | 结构化分析报告（执行摘要 → 管线 → rNPV → 市场隐含 → 结论）|
| `[ticker]_implied.json` | 结构化输出（成熟标的 reverse 场景适用，过 schema 校验；pre-revenue 标的可选）|

## Excel 模型结构（6 个 Sheet）

| Sheet | 内容 |
|---|---|
| **Summary** | 公司信息、当前价/市值、rNPV 汇总、每股价值、市场隐含 λ、低估/高估判断 |
| **Pipeline** | 管线总览表：每条一行（药物/靶点/适应症/阶段/PoS/峰值销售/rNPV 贡献）|
| **rNPV Detail** | 逐年现金流：收入、成本、FCF、折现因子、PV、rNPV（每条管线一个区块）|
| **Implied PoS** | 市场隐含成功率反推：市值拆解、隐含管线价值、λ 求解、vs 基准对比 |
| **Assumptions** | PoS 基准表、折现率、治疗费用、患者人数、渗透率假设（蓝字输入，附来源注释）|
| **Sensitivity** | 敏感性分析：WACC×峰值销售、PoS×峰值销售、PoS×折现率 三张表 |

## 方法论体系

本系统包含 **7 篇 references**，构成完整方法论闭环。入口文档 `00-methodology-overview.md` 串联全部。

### 方法论来源

**PoS 基准（BIO/BioMedTracker 2011-2020）**：
- Phase 1 → 获批：~7.9%
- Phase 2 → 获批：~15.1%（Phase 2 是死亡之谷）
- Phase 3 → 获批：~52.4%
- NDA → 获批：~90.6%

**核心参考文献**：
- BIO/BioMedTracker, *Clinical Development Success Rates 2011-2020*
- Wong, Siah & Lo (2019), *Estimation of Clinical Trial Success Rates*, Nature Biotechnology
- Analysis Group (2024), *Biotech Asset Valuation Methods: A Practitioner's Guide*

## 免责声明

⚠️ 本系统产出的所有估值结论**仅供研究参考，不构成投资建议**。PoS 基准和峰值销售估算具有高度主观性，报告中会标注每个假设的来源和置信度。投资决策请咨询持牌专业人士。
