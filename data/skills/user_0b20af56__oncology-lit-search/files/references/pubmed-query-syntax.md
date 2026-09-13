# PubMed 查询语法参考

## 布尔运算符

PubMed 支持 AND、OR、NOT 三个布尔运算符，**必须大写**。

- `AND`：同时满足两个条件（缩小结果）
- `OR`：满足任一条件（扩大结果）
- `NOT`：排除含某条件的文献

运算优先级：`NOT` > `AND` > `OR`。使用括号 `()` 控制优先级。

```
(lung cancer OR pulmonary neoplasms) AND immunotherapy NOT case reports
```

## 通配符与短语搜索

- **通配符 `*`**：匹配词根，至少 4 个字符。`immuno*` 匹配 immunotherapy, immunology, immunotherapy 等
- **短语搜索**：用双引号精确匹配短语。`"immune checkpoint inhibitor"` 精确匹配该短语

## 字段标签速查表

| 字段标签 | 说明 | 示例 |
|----------|------|------|
| `[MeSH]` | MeSH 主题词（自动扩展下位词） | `"Lung Neoplasms"[MeSH]` |
| `[MeSH:NoExp]` | MeSH 词不扩展下位词 | `"Breast Neoplasms"[MeSH:NoExp]` |
| `[Title/Abstract]` | 标题或摘要中搜索 | `immunotherapy[Title/Abstract]` |
| `[Title]` | 仅标题中搜索 | `pembrolizumab[Title]` |
| `[Author]` | 作者（姓 + 名首字母） | `Smith J[Author]` |
| `[Journal]` | 期刊名称 | `"J Clin Oncol"[Journal]` |
| `[Publication Type]` | 文献类型 | `clinical trial[Publication Type]` |
| `[Date - Publication]` | 发表日期 | `"2024/01/01"[Date - Publication]` |
| `[Publication Year]` | 发表年份 | `2024[Publication Year]` |
| `[Affiliation]` | 作者单位 | `MD Anderson[Affiliation]` |
| `[Filter]` | 通用过滤器 | `humans[Filter]`、`english[Filter]` |
| `[DOI]` | DOI 号 | `10.1200/JCO.2024.001[DOI]` |
| `[Language]` | 语言 | `english[Language]` |
| `[Affiliation]` | 机构 | `"Dana-Farber"[Affiliation]` |

## 日期范围语法

### 精确日期范围

```
("2023/01/01"[Date - Publication] : "2024/12/31"[Date - Publication])
```

### 按年份

```
2024[Publication Year]
```

### 相对日期

```
"last 1 year"[Date - Publication]
"last 6 months"[Date - Publication]
```

## 文献类型速查

| 查询 | 类型 |
|------|------|
| `clinical trial[Publication Type]` | 临床试验 |
| `randomized controlled trial[Publication Type]` | 随机对照试验（RCT） |
| `meta-analysis[Publication Type]` | 荟萃分析 |
| `review[Publication Type]` | 综述 |
| `systematic review[Publication Type]` | 系统综述 |
| `case reports[Publication Type]` | 病例报告 |
| `practice guideline[Publication Type]` | 实践指南 |
| `clinical trial, phase iii[Publication Type]` | III 期临床试验 |
| `comparative study[Publication Type]` | 比较研究 |

## 肿瘤学常用 MeSH 词表

### 癌种

| MeSH 词 | 中文 |
|---------|------|
| Lung Neoplasms | 肺肿瘤 |
| Breast Neoplasms | 乳腺肿瘤 |
| Colorectal Neoplasms | 结直肠肿瘤 |
| Prostatic Neoplasms | 前列腺肿瘤 |
| Ovarian Neoplasms | 卵巢肿瘤 |
| Stomach Neoplasms | 胃肿瘤 |
| Pancreatic Neoplasms | 胰腺肿瘤 |
| Liver Neoplasms | 肝肿瘤 |
| Esophageal Neoplasms | 食管肿瘤 |
| Bladder Neoplasms | 膀胱肿瘤 |
| Kidney Neoplasms | 肾肿瘤 |
| Head and Neck Neoplasms | 头颈部肿瘤 |
| Thyroid Neoplasms | 甲状腺肿瘤 |
| Leukemia | 白血病 |
| Lymphoma | 淋巴瘤 |
| Multiple Myeloma | 多发性骨髓瘤 |
| Melanoma | 黑色素瘤 |
| Sarcoma | 肉瘤 |
| Neoplasms | 肿瘤（总称） |

### 治疗方式

| MeSH 词 | 中文 |
|---------|------|
| Immunotherapy | 免疫治疗 |
| Targeted Therapy | 靶向治疗 |
| Chemotherapy, Adjuvant | 辅助化疗 |
| Radiotherapy | 放疗 |
| Precision Medicine | 精准医学 |
| Drug Therapy | 药物治疗 |
| Gene Therapy | 基因治疗 |

### 药物 / 靶点

新药和新靶点可能尚无 MeSH 词，建议用 `[Title/Abstract]` 搜索。常用搜索词：

- **免疫检查点抑制剂**：pembrolizumab, nivolumab, atezolizumab, durvalumab, ipilimumab, tremelimumab
- **靶向药物**：osimertinib, gefitinib, erlotinib, crizotinib, sotorasib, adagrasib
- **HER2 靶向**：trastuzumab, pertuzumab, T-DXd, trastuzumab deruxtecan, T-DM1
- **CDK4/6 抑制剂**：palbociclib, ribociclib, abemaciclib
- **PARP 抑制剂**：olaparib, niraparib, rucaparib, talazoparib
- **CAR-T**：CAR-T, chimeric antigen receptor, tisagenlecleucel, axicabtagene ciloleucel
- **ADC**：antibody-drug conjugate, enfortumab vedotin, sacituzumab govitecan

## 查询构建示例

### 示例 1：查找特定癌种的免疫治疗 RCT

```
"Lung Neoplasms"[MeSH] AND immunotherapy[Title/Abstract] AND randomized controlled trial[Publication Type]
```

### 示例 2：查找某作者的临床试验

```
Smith J[Author] AND clinical trial[Publication Type]
```

### 示例 3：查找近 2 年综述

```
("Lung Neoplasms"[MeSH]) AND review[Publication Type] AND ("2024/01/01"[Date - Publication] : "2025/12/31"[Date - Publication])
```

### 示例 4：查找特定期刊文章

```
"J Clin Oncol"[Journal] AND breast cancer[Title/Abstract]
```

### 示例 5：排除病例报告

```
melanoma[Title/Abstract] NOT case reports[Publication Type]
```

### 示例 6：多癌种 + 多治疗方式

```
("Lung Neoplasms"[MeSH] OR "Breast Neoplasms"[MeSH]) AND (immunotherapy[Title/Abstract] OR "targeted therapy"[Title/Abstract])
```

### 示例 7：查找特定药物的临床试验

```
pembrolizumab[Title/Abstract] AND clinical trial[Publication Type] AND ("2023/01/01"[Date - Publication] : "2024/12/31"[Date - Publication])
```

### 示例 8：仅限英文文献

```
"Colorectal Neoplasms"[MeSH] AND english[Language]
```

### 示例 9：查找某机构的研究

```
"MD Anderson"[Affiliation] AND "Breast Neoplasms"[MeSH]
```

### 示例 10：通过 DOI 精确查找

```
10.1200/JCO.2024.001[DOI]
```
