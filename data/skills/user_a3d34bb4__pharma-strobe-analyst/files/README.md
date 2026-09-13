# 药学数据分析助手

## 简介

面向药学真实世界研究的 STROBE 规范完整数据分析技能。输入一份多 sheet 的 Excel 研究数据，一键产出包含三线表、PSM 匹配报告、KM 曲线、森林图、中介效应分析的格式化 Word 报告。

## 适用场景

- 药学真实世界研究的回顾性队列分析
- 药物安全性/有效性的观察性研究
- STROBE 规范报告撰写
- 培训班/学习班的数据分析作业
- 多中心 HIS 数据二次分析

## 核心能力

| 步骤 | 内容 |
|:---|:---|
| 数据体检 | 缺失值分析、异常值识别、日期格式检查、单位统一检查 |
| 数据清洗 | 日期统一、性别编码标准化、血肌酐单位换算、异常值处理 |
| Table 1 | 三线表基线特征（Mann-Whitney U / t检验 / χ²检验） |
| 主要结局 | 组间比较 + 效应量 + 95%CI |
| PSM | 倾向性评分匹配 + 协变量平衡性报告 |
| 图表 | KM生存曲线、森林图、箱线图、相关性热力图 |
| 中介效应 | Bootstrap 5000次、HOMA-IR / hs-CRP 中介通路 |
| Word报告 | docx-js 生成，药学期刊风格，含全部三线表与图表 |

## 药学专属规则

- 血肌酐单位自动检测与换算（mg/dL → µmol/L ×88.4）
- MoCA 认知量表评分异常检测（>30分标记）
- HOMA-IR 胰岛素抵抗指标
- hs-CRP 炎症指标

## 依赖

```bash
pip install pandas openpyxl matplotlib seaborn scipy statsmodels lifelines scikit-learn
npm install docx
```

## 使用方式

在 WorkBuddy 中直接上传 Excel 数据文件并说：
"请帮我做数据分析" / "生成 STROBE 报告" / "做基线特征三线表"

## 参考

- STROBE Statement: https://www.strobe-statement.org/
- MoCA 量表: https://www.mocatest.org/
