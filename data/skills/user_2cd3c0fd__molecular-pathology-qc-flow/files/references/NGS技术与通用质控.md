# NGS 技术与通用质控

作者：WangYunL  
核对日期：2026-08-27

## 一、技术定位

NGS（下一代测序）通过并行读取大量核酸片段获得序列数据。分子病理 NGS 一般包含样本与核酸处理、文库制备、测序运行、生物信息分析和结果复核。Illumina 的技术工作流资料可用于理解这些阶段；FDA 指南强调 NGS 检测的设计、开发与分析性能验证。

来源：

- FDA NGS Analytical Validation Guidance：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-design-development-and-analytical-validation-next-generation-sequencing-ngs-based
- Illumina NGS Workflow：https://www.illumina.com/science/technology/next-generation-sequencing/beginners/ngs-workflow.html
- Illumina NGS Overview：https://www.illumina.com/science/technology/next-generation-sequencing.html
- Illumina Quality Scores：https://www.illumina.com/science/technology/next-generation-sequencing/plan-experiments/quality-scores.html

## 二、主要阶段与质控点

| 阶段 | 通用质控点 | 需要绑定的具体信息 |
| --- | --- | --- |
| 样本与核酸 | 样本身份、核酸数量、纯度、完整性和抑制风险 | 样本类型、提取方法、panel 验证 |
| 文库制备 | 文库产量、片段分布、接头或 index、污染和批次对照 | 扩增子/捕获方法、试剂版本 |
| 测序运行 | 运行状态、对照、产量、质量分数和 index 表现 | 仪器、试剂盒、run 配置 |
| 下机数据 | Q30 等碱基质量、比对、深度、覆盖度、均一性 | panel、样本类型、软件版本和阈值 |
| 变异分析 | 质控过滤、支持读数、等位基因频率、链偏倚等 | pipeline、数据库和验证范围 |
| 结果复核 | 样本一致性、变异审核、失败或补充检测规则 | 实验室 SOP 和报告政策 |

## 三、Q30 的边界

质量分数用于表达碱基判读错误概率；Q30 对应预测错误概率约为千分之一。这个定义可以通用说明，但“Q30 比例必须达到多少”不是通用阈值，必须依据平台、运行类型、项目验证和实验室 SOP。

## 四、建模规则

1. 把文库质控、运行质控和样本级数据质控分开建模。
2. 记录仪器、试剂、panel、pipeline 和参考数据库版本。
3. 不把一个 panel 的深度、覆盖度或变异频率阈值复制到另一个 panel。
4. 对 failed、warning、manual review 和 repeat 建独立终点或处置节点。
5. 若当前只有通用资料，判断条件使用 `CUSTOM`，表达式写“依据当前项目 SOP/验证规则”，不填假数字。

## 五、示例说明

`assets/NGS通用质控.json` 展示阶段泳道和通用质控关系，不是可直接用于临床项目的执行 SOP。收到具体项目参数后，应替换为经确认的 structured condition，并保留原来源和适用范围。

