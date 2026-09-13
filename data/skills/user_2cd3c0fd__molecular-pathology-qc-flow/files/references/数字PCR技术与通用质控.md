# 数字 PCR 技术与通用质控

作者：WangYunL  
更新日期：2026-08-27

## 一、技术是什么

数字 PCR（dPCR）把一个反应划分为大量独立分区，终点读取每个分区的阳性或阴性状态，并依据阳性分区比例和统计模型估计目标核酸数量。常见形式包括芯片或微流控分区和液滴数字 PCR（ddPCR）。

## 二、常见读数

- 总分区数、有效分区数和无效分区数。
- 阳性、阴性及中间液滴或分区的分布。
- 阈值线或聚类边界及其人工调整记录。
- 阳性分区比例、拷贝数、浓度、置信区间。
- 空白限、检出限、定量限或线性范围，仅在方法验证已定义时使用。
- 阳性、阴性、无模板和过程对照结果。

## 三、通用质控节点

1. 样本、核酸完整性、抑制物和输入量是否满足方法要求。
2. 分区生成是否成功，有效分区数量是否满足匹配平台和 SOP。
3. 空白和阴性对照是否满足污染或背景接受规则。
4. 阳性对照是否落在验证范围内。
5. 阳性、阴性及中间分区群是否可分辨，阈值或聚类设置是否可追溯。
6. 反应是否出现饱和、过度稀释或超出动态范围。
7. 重复孔或重复测量的一致性是否满足方法规则。
8. 统计模型、分区体积、稀释倍数和结果单位是否正确。
9. 结果是否进入通过、复检、稀释重测、重提或人工复核路径。

## 四、不可通用化的内容

- 最低有效分区数和中间液滴接受范围。
- 阈值线、聚类算法、补偿或串色规则。
- 空白限、检出限、定量限、线性范围和最低变异频率。
- 分区体积、稀释策略、重复数和报告单位。

这些数值必须绑定具体平台、试剂、分析软件版本、SOP 和验证报告。

## 五、来源

- NIST Digital PCR：<https://www.nist.gov/programs-projects/digital-pcr>
- dMIQE Guidelines（NIST publication）：<https://www.nist.gov/publications/guidelines-minimum-information-publication-quantitative-digital-pcr-experiments>
- NIST，The Application of Digital PCR as a Reference Measurement Procedure：<https://www.nist.gov/publications/application-digital-pcr-reference-measurement-procedure-support-accuracy-quality>

