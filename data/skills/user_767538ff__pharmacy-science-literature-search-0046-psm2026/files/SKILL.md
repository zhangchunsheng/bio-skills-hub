---
name: pharmacy-science-literature-search-0046-psm2026
description: 药学科普文写作前的文献检索策略生成工具。当用户给出科普选题（如他汀伤肝伤肌肉、感冒药叠吃伤肝等），同时生成 PubMed（英文）和 CNKI 知网（中文）的三档梯度检索式，含 MeSH 映射、同义词扩展、批量爬摘要指引。三甲医院药师专用，聚焦用药安全、合理用药、ADR 方向的药学科普。触发词：检索式、文献检索、PubMed检索式、知网检索式、查文献、科普文检索、中英文文献检索。
agent_created: true
---

# 科普文的中英文文献检索

## Overview

为药学科普选题**同步生成** PubMed 与 CNKI 两套三档梯度检索式。学员（药师）只需给出科普选题方向，AI 自动完成课题拆解、MeSH 映射、同义词扩展、检索式组配，并附批量爬摘要 4 步指引。复制粘贴即可跑通。

核心流程：**课题拆解 → 概念提取 → 双平台并行构建 → 合并输出**

---

## When to Use

触发场景：
- 药师给出一个科普选题，要求「生成检索式」或「帮我查文献」
- 用户需要 PubMed 或 CNKI 的检索策略来支撑科普文写作
- 用户提到「文献检索」「查文献」「检索式」「中英文文献检索」等关键词
- 与 `药学文献检索-PubMed` 不同，本 skill 专注**科普方向**且**同时覆盖中英文双平台**

---

## Step 1：课题解构与核心概念提取

**原则**：忽略方法论修饰词，提取 2–4 个实质性核心概念。

**操作**：从科普选题中识别：
- 目标药物/药物类别
- 目标疾病/症状/器官系统
- 关注维度（安全性、副作用、有效性、相互作用等）

**示例**：

| 科普选题 | 核心概念 |
|:---|:---|
| 他汀类降脂药"伤肝伤肌肉"？药师带你正确认识副作用 | ①他汀类药物 ②肝损伤/肝毒性 ③肌病/肌痛 |
| 感冒药叠着吃，当心对乙酰氨基酚超量伤肝 | ①复方感冒药 ②对乙酰氨基酚 ③肝损伤 ④过量/重复用药 |
| 吃这些药时千万别碰西柚——药食相克实用清单 | ①CYP3A4底物药物 ②西柚 ③药物相互作用 |
| 抗生素"见好就收"到底行不行 | ①抗生素 ②疗程 ③细菌耐药 ④用药依从性 |
| 血压正常了就停药？降压药吃吃停停比不吃更危险 | ①降压药 ②停药 ③反跳性高血压 ④心血管事件 |

---

## Step 2：PubMed 检索式构建

### 2.1 MeSH 主题词映射

根据核心概念，在以下速查表中定位 MeSH 词：

**药学概念 MeSH 速查表（核心）**

| 概念 | MeSH 主题词 |
|:---|:---|
| 他汀类 | `"Hydroxymethylglutaryl-CoA Reductase Inhibitors"[Mesh]` |
| 二甲双胍 | `"Metformin"[Mesh]` |
| 质子泵抑制剂 | `"Proton Pump Inhibitors"[Mesh]` |
| 万古霉素 | `"Vancomycin"[Mesh]` |
| 对乙酰氨基酚 | `"Acetaminophen"[Mesh]` |
| 抗生素 | `"Anti-Bacterial Agents"[Mesh]` |
| 抗凝药 | `"Anticoagulants"[Mesh]` |
| 降压药 | `"Antihypertensive Agents"[Mesh]` |
| 药物不良反应 | `"Drug-Related Side Effects and Adverse Reactions"[Mesh]` |
| 肝损伤（药物性） | `"Chemical and Drug Induced Liver Injury"[Mesh]` |
| 肝功能 | `"Liver Function Tests"[Mesh]` |
| 肌痛 | `"Myalgia"[Mesh]` |
| 肌炎 | `"Myositis"[Mesh]` |
| 横纹肌溶解 | `"Rhabdomyolysis"[Mesh]` |
| 急性肾损伤 | `"Acute Kidney Injury"[Mesh]` |
| 药物相互作用 | `"Drug Interactions"[Mesh]` |
| 用药依从性 | `"Medication Adherence"[Mesh]` |
| 细菌耐药 | `"Drug Resistance, Bacterial"[Mesh]` |
| 多重用药 | `"Polypharmacy"[Mesh]` |
| 老年 | `"Aged"[Mesh]` |
| 儿童 | `"Child"[Mesh]` |
| 心血管事件 | `"Cardiovascular Diseases"[Mesh]` |
| 高血压 | `"Hypertension"[Mesh]` |

**个体药品 MeSH**：常见药品均有独立 MeSH 词，如 `"Atorvastatin"[Mesh]`、`"Simvastatin"[Mesh]`、`"Warfarin"[Mesh]` 等，建议与类别 MeSH 同步覆盖。

### 2.2 同义词与自由词扩充

针对每个核心概念，以 `[tiab]` 字段补充同义词、缩写、变体：

- 药品名：通用名 + 商品名 + 化学名
- 症状/疾病：英式/美式拼写、缩写-全称对
- 通配符规则：`*` 前词干 ≥ 4 字符，如 `prescrib*` ✓、`pr*` ✗

**药学高频自由词速查**：

| 概念 | `[tiab]` 自由词 |
|:---|:---|
| 药品不良反应 | `adverse drug reaction*`、`adverse drug event*`、`ADR[tiab]`、`side effect*`、`drug-related problem*` |
| 肝损伤 | `hepatotox*`、`liver injur*`、`liver damage*`、`hepatic injur*`、`liver enzyme*`、`transaminase*`、`DILI[tiab]`、`drug-induced liver injury` |
| 肌病 | `myopath*`、`myalgi*`、`rhabdomyolysis`、`muscle pain*`、`muscle symptom*`、`creatine kinase`、`CK elevation`、`SAMS[tiab]`、`statin-associated muscle symptom*`、`statin intolerance` |
| 药物相互作用 | `drug interaction*`、`CYP3A4`、`drug-drug interaction*`、`DDI[tiab]` |
| 用药依从性 | `medication adherence`、`medication compliance`、`treatment adherence`、`persistence` |
| 细菌耐药 | `antimicrobial resistance`、`antibiotic resistance`、`AMR[tiab]`、`drug resistance` |
| 真实世界 | `real-world`、`routine care`、`electronic health record*`、`claims data` |

### 2.3 检索式组配规则

**运算符**：

| 符号 | 含义 | 示例 |
|:---|:---|:---|
| `AND` | 同时满足 | `metformin AND cognition` |
| `OR` | 任一满足 | `elderly OR older OR aged` |
| `NOT` | 排除 | `NOT (rats[tiab] OR mice[tiab])` |
| `()` | 分组优先级 | `(A OR B) AND C` |
| `*` | 截词（词干≥4） | `prescrib*` |

**双通道原则（核心，不可遗漏）**：

每个核心概念组必须同时包含：
- ① **MeSH 通道**：`"Concept"[Mesh]` — PubMed 自动扩展下位词，保证查全
- ② **自由词通道**：`synonym[tiab]` — 捕获尚未标引的最新文献

### 2.4 生成三档检索式

**【宽档 · 摸底】**：核心概念 AND 全部同义词，不限动物/细胞

```
预期：3,000–8,000 条 | 用途：看总量
```

**【中档 · 主文献池】** ★ 推荐：宽档 + NOT 动物/细胞 + AND Humans

```text
NOT ("Animals"[Mesh:NoExp] OR rats[tiab] OR mice[tiab] OR "in vitro"[tiab])
AND ("Humans"[Mesh])
```

```
预期：600–1,500 条 | 用途：今天爬摘要就是这条
```

**【窄档 · 精筛】**：中档 + 证据等级限定

```text
AND (systematic review[pt] OR meta-analysis[pt] OR randomized controlled trial[pt])
```

```
预期：80–300 条 | 用途：量太大时降噪，全是高等级证据
```

**补充过滤片段（按需追加到中档末尾）**：

```text
# 近 5 年
AND ("2021"[Date - Publication] : "3000"[Date - Publication])

# 限定英语
AND (english[lang])
```

---

## Step 3：CNKI 知网检索式构建

### 3.1 CNKI 专业检索语法

| 符号 | 含义 | 示例 |
|:---|:---|:---|
| `*` | AND（与） | `SU='他汀' * '肝损伤'` |
| `+` | OR（或） | `'肝损伤' + '肝毒性'` |
| `-` | NOT（非） | `-'大鼠'` |
| `SU` | 主题（题名+关键词+摘要） | 默认字段，覆盖面最均衡 |
| `TI` | 篇名 | 精确命中，适合窄档 |
| `KY` | 关键词 | 作者标引词 |
| `AB` | 摘要 | 比 SU 略宽 |
| `SU %` | 模糊匹配 | `SU % '他汀'` 匹配变体 |
| `''` | 字符串字面量 | 含特殊字符的词须加单引号 |
| `()` | 分组 | 控制运算优先级 |

> ⚠️ CNKI 专业检索单次上限约 **500 字符**，构建时控制 OR 词条数。

### 3.2 中文同义词扩展

根据核心概念映射为中文检索词，注意覆盖：
- 通用名 + 商品名（如「阿托伐他汀」+「立普妥」）
- 学术术语 + 通俗说法（如「药物性肝损伤」+「药物伤肝」）
- 缩写 + 全称（如「DILI」+「药物性肝损伤」）
- 不同表述变体（如「横纹肌溶解」+「横纹肌溶解症」）

### 3.3 生成三档检索式

**【宽档 · 摸底】**：SU 字段 + 全量同义词，不限时间

```text
SU=('核心词1'+'同义词1a'+'同义词1b')*(('概念2a'+'概念2b')+('概念3a'+'概念3b'))
```

```
预期：1,500–3,000 条 | 用途：摸底
```

**【中档 · 主文献池】** ★ 推荐：同宽档表达式，筛选在结果页面左侧栏完成

进入结果页后手动勾选：
- 发表时间 → 「近 5 年」
- 来源类型 → ✅ 学术期刊 ✅ 学位论文
- 来源类别 → ✅ 北大核心 ✅ CSCD

```
预期：300–800 条 | 用途：今天用这条
```

> ⚠️ CNKI 来源类别无法在检索式内指定，必须在结果页左侧栏手动过滤。

**【窄档 · 精筛】**：切换为 TI（篇名）字段，去除商品名

```text
TI=('核心词1'+'核心词1a')*(('概念2a'+'概念2b')+('概念3a'+'概念3b'))
```

```
预期：100–300 条 | 用途：高度相关、免二次筛选
```

---

## Step 4：输出模板

每次完成一个选题的检索式构建后，按以下模板交付：

```markdown
# 【选题名称】中英文文献检索策略

## 一、核心概念提取
| # | 核心概念 | 角色 |
|---|---|---|
| C1 | ... | ... |

## 二、PubMed 三档检索式

### 【宽档 · 摸底】
(检索式)
> 预期: XXXX 条 | 用途: 摸底

### 【中档 · 主文献池】★ 推荐
(检索式)
> 预期: XXX 条 | 用途: 爬摘要写科普

### 【窄档 · 精筛】
(检索式)
> 预期: XX 条 | 用途: 证据等级限缩

## 三、CNKI 知网三档检索式

### 【宽档 · 摸底】
(检索式)
> 预期: XXXX 条 | 用途: 摸底

### 【中档 · 主文献池】★ 推荐
(检索式)
> 预期: XXX 条 | 用途: 结果页左侧栏手动过滤
> 筛选建议: 近5年 + 学术期刊 + 北大核心/CSCD

### 【窄档 · 精筛】
(检索式)
> 预期: XX 条 | 用途: 篇名精确命中

## 四、批量爬摘要指引

### PubMed（4 步）
1. 复制中档检索式到 https://pubmed.ncbi.nlm.nih.gov/ 搜索框
2. 点 Save → Selection 选 All results（或输入 100）
3. Format 必须选 **Abstract**（⚠️ 选 Summary 只有标题）
4. 点 Create file 下载 .txt

### CNKI（4 步）
1. 打开 https://kns.cnki.net/kns8s/AdvSearch → 切换到「专业检索」
2. 粘贴中档检索式 → 检索
3. 左侧栏过滤：近5年 + 学术期刊 + 北大核心/CSCD
4. 勾选目标文献 → 导出与分析 → 查新（自定义）→ 勾选摘要 → 导出

## 五、不理想怎么办
| 问题 | 对策 |
|:---|:---|
| 太多 | 换窄档，或加时间限定 |
| 太少 | 换宽档，检查括号/引号 |
| 0 条 | 逐段排查，只跑核心概念确认能出结果 |

## 六、中英文互补提示
| | CNKI 独有 | PubMed 独有 |
|:---|:---|:---|
| 内容 | 中国人群数据、中文综述、硕博论文 | 国际 RCT、大规模荟萃分析、全球指南 |
| 科普价值 | 本土案例 + 中国指南���读者代入感强 | 全球共识声明，证据等级高 |

> 建议 PubMed 中档 + CNKI 中档同时跑，各取前 50 条摘要合并。
```

---

## Step 5：输出前自检清单

交付检索式前逐项确认：

- [ ] 每个核心概念都覆盖了 PubMed `[Mesh]` + `[tiab]` 双通道？
- [ ] `[Mesh]` 中双引号已保留（PubMed 语法要求）？
- [ ] PubMed 自由词**未**加双引号（会破坏自动词汇映射）？
- [ ] 通配符 `*` 前词干 ≥ 4 字符？
- [ ] CNKI 检索式总字符数 ≤ 500？
- [ ] CNKI 检索式中括号配对正确（半角符号）？
- [ ] 三档都给出了预期命中量级？
- [ ] 三档都标注了用途说明？
- [ ] 批量爬摘要操作指引已附上？
- [ ] 中英文互补提示已附上？

**任一项为否 → 补充完整再输出。**

---

## Notes

- 本 skill 聚焦**药学科普**方向（用药安全、合理用药、ADR），若课题偏向科研设计（如「基于真实世界数据的 XX 研究」），建议优先使用 `药学文献检索-PubMed` skill 单独构建英文检索式，再用 `cnki-search-builder` 补充中文端。
- 科普选题通常**不需要**过于复杂的检索策略——中档足以覆盖高质量证据池。优先保证查全率和可复现性，而非极致的查准率。
- 药品商品名（如立普妥、可定）在 CNKI 中可显著提高召回，但在 PubMed 中贡献有限（英文文献通常用通用名）。
