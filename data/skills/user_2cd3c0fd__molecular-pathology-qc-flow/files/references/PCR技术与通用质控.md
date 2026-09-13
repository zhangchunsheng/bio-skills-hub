# PCR 技术与通用质控

作者：WangYunL  
核对日期：2026-08-27

## 一、技术定位

PCR（聚合酶链式反应）是在体外选择性扩增特定 DNA 片段的技术大类。qPCR、ARMS-PCR、数字 PCR 等是 PCR 下的具体方法；BRAF V600E、EGFR 等是检测项目或靶点。查询“PCR 的 BRAF”时，应同时返回 PCR 技术说明和 BRAF 项目说明，不能把 BRAF 称为一种 PCR 技术。

权威技术定义来源：

- NHGRI PCR Fact Sheet：https://www.genome.gov/about-genomics/fact-sheets/Polymerase-Chain-Reaction-Fact-Sheet
- NHGRI PCR Glossary：https://www.genome.gov/genetics-glossary/Polymerase-Chain-Reaction-PCR

## 二、方法原理

PCR 由引物界定目标区域，通过反复的变性、退火和延伸循环扩增靶序列。终点 PCR 可在扩增完成后检查产物；实时荧光 PCR 在运行过程中采集荧光信号并产生 Ct/Cq 等读数；ARMS-PCR 借助等位基因特异性扩增区分序列；数字 PCR 通过分区和计数进行定量。

上述是技术层说明，不等同于任何试剂的临床声明、靶点范围或判定算法。

## 三、通用质控阶段

| 阶段 | 需要确认的质控点 | 典型失败处置 |
| --- | --- | --- |
| 样本与接收 | 样本类型、标识、保存和肿瘤含量是否符合项目要求 | 退样、补样或病理复核 |
| 核酸提取 | 提取批次对照、核酸数量和质量是否符合 SOP | 重提取或记录偏差 |
| 反应体系 | 试剂批号、有效期、加样记录和污染控制 | 重新配制或重做 |
| 扩增运行 | 仪器状态、运行参数、阳性/阴性/空白对照 | 判定整批无效或按 SOP 调查 |
| 下机质控 | 曲线、通道、Ct/Cq、内参和软件判定状态 | 复核原始曲线、复测或重提取 |
| 结果判读 | 靶标条件、内参条件、灰区和无 Ct 分支 | 人工复核或按项目规则处置 |

## 四、关键建模要求

1. Ct/Cq、ΔCt、基线、阈值线和通道名称均需绑定具体方法。
2. 必须区分 `<`、`≤`、`>`、`≥`，不能把边界值模糊为“正常/异常”。
3. 无 Ct、Undetermined、空字符串和数值 0 不能默认视为同一种状态。
4. 阳性、阴性、空白和内参对照的接受标准要绑定试剂说明书或 SOP。
5. 灰区应建成独立分支，写明进入条件、复算或复测方式及最终处置。

## 五、项目示例边界

- BRAF：NCBI BRAF 基因记录和 FDA cobas BRAF 资料可用于核实项目与特定 PCR 产品实例；不得据此推导其他试剂的 Ct 阈值。
- EGFR：NCBI EGFR 基因记录和 FDA cobas EGFR 标签可用于核实特定项目实例；检测变异范围、样本类型和判定条件仍以匹配版本资料为准。

## 六、流程图建议

通用流程图只能写“是否满足当前项目 SOP/IFU”，不能凭经验填入数值。收到实验室资料后，再把每个指标拆成 measurement、operator、value、unit、missing_policy 和 evidence_refs。

