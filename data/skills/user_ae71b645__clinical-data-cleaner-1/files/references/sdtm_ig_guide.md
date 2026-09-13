# CDISC SDTM 实施指南参考

## 概述

研究数据表格模型（Study Data Tabulation Model，SDTM）是一种用于组织和格式化数据的标准,旨在简化数据收集、管理、分析和报告的流程。

## 关键领域

### DM - 人口统计学
包含研究受试者的人口统计学信息。

**必需字段：**
- STUDYID: 研究标识符
- USUBJID: 唯一受试者标识符
- SUBJID: 研究内受试者标识符
- RFSTDTC: 受试者参考开始日期/时间
- RFENDTC: 受试者参考结束日期/时间
- SITEID: 研究中心标识符
- AGE: 年龄
- SEX: 性别
- RACE: 种族

### LB - 实验室检测结果
包含实验室检测结果,包括生化、血液学、尿液分析。

**必需字段：**
- STUDYID: 研究标识符
- USUBJID: 唯一受试者标识符
- LBTESTCD: 实验室检测简称
- LBCAT: 实验室检测类别
- LBORRES: 原始单位下的结果或发现
- LBORRESU: 原始单位
- LBSTRESC: 标准格式下的字符型结果/发现
- LBDTC: 标本采集日期/时间

### VS - 生命体征
包含血压、心率、体温等生命体征测量数据。

**必需字段：**
- STUDYID: 研究标识符
- USUBJID: 唯一受试者标识符
- VSTESTCD: 生命体征检测简称
- VSORRES: 原始单位下的结果或发现
- VSORRESU: 原始单位
- VSSTRESC: 标准格式下的字符型结果/发现
- VSDTC: 生命体征测量日期/时间

## 数据质量要求

1. **缺失值**：必须编码为空,而不是像 "NA" 或 "N/A" 这样的文本
2. **日期**：ISO 8601 格式（YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS）
3. **编码值**：使用受控术语
4. **单位**：统一为常规单位

## 参考资料

- CDISC SDTM Implementation Guide v3.4
- CDISC Controlled Terminology
- FDA Study Data Technical Conformance Guide
