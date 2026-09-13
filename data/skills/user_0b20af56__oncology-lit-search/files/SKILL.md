---
name: oncology-lit-search
version: "V1.1.2"
description: "肿瘤学文献与会议摘要检索技能（V1.1.2，固定报告格式）。支持 PubMed 文献检索（MeSH 词、作者、期刊、日期范围、布尔运算、临床试验筛选）以及 ASCO、ESMO、CSCO、AACR、WCLC 几大肿瘤学年会会议摘要检索。药物/靶点专题报告固定格式 V1.1.2：封面 6 要素 → 一、背景与流行病学 → 二、临床数据汇总表（按临床阶段降序，多瘤种分表）→ 三、重点药物临床数据详情（按临床阶段降序，III期布局固定，含耐药机制研究）→ 四、非主流开发方向 → 五、会议数据汇总 → 六、总结与趋势判断（7 个固定子目录：治疗格局/疗效梯队/竞争态势/差异化策略/耐药挑战与应对/监管进展(注册策略)/临床意义与展望）→ 参考文献（置于最后，原 PubMed 文献列表以参考文献方式列出）。由 scripts/gen_drug_target_report.py（JSON 驱动）生成标准 .docx。适用于：查找肿瘤相关文献/研究/临床试验报告、检索特定年会会议摘要、按癌种/药物/靶点/试验名称检索文献、药物/靶点全景进展调研、文献综述准备、竞品/管线追踪、NCCN/ESMO/CSCO 指南相关文献追踪等场景。当用户提及 PubMed、ASCO、ESMO、CSCO、AACR、WCLC 肿瘤文献、会议摘要、临床试验文献、靶点药物、管线、临床数据、cancer literature、oncology abstract、查文献、搜文献、文献检索、年会摘要、meeting abstract 等关键词时触发本 skill。PubMed 检索使用 scripts/pubmed_search.py 脚本调用 NCBI E-utilities API；会议摘要检索使用 WebSearch + site: 站内搜索策略；专题报告导出使用 scripts/gen_drug_target_report.py。"
agent_created: true
---

# Oncology Literature Search — 肿瘤文献检索

## 概述

在 PubMed（NCBI E-utilities API）和 ASCO / ESMO / CSCO / AACR / WCLC几大肿瘤学年会检索文献与会议摘要。PubMed 检索通过 Python 脚本调用官方 API 获取结构化数据；会议摘要检索通过 WebSearch 站内搜索策略 + WebFetch 全文抓取完成。

## 触发场景

| 场景 | 示例提问 |
|------|----------|
| PubMed 文献检索 | "帮我查一下非小细胞肺癌免疫治疗的最新文献" |
| ASCO 会议摘要 | "2024 ASCO 有哪些关于 HER2 阳性乳腺癌的重磅研究" |
| ESMO 会议摘要 | "ESMO 2023 关于 CAR-T 疗法的摘要" |
| CSCO 会议摘要 | "CSCO 2024 年会有哪些关于胃癌靶向治疗的进展" |
| 多源综合检索 | "帮我收集卵巢癌 PARP 抑制剂的文献和会议摘要" |
| 临床试验文献 | "找一下 KEYNOTE-858 试验的 PubMed 文献" |

## 使用教程（面向用户）

本技能开箱即用，无需任何配置。你只需用自然语言描述需求，WorkBuddy 会自动判断走 PubMed 还是会议摘要检索，并按规范格式输出结果。

**三步上手：**
1. 直接说需求，例如："帮我查 KRAS G12D 胰腺癌的最新临床数据"（自动触发本技能）。
2. 指定来源更精准，例如："2024 ASCO 关于 HER2 阳性乳腺癌的重磅研究"（自动走 ASCO 会议摘要检索）。
3. 需要留存时，说"导出成 Word 报告"，自动生成带检索时间、范围、关键词等元数据的 `.docx`。

**常用触发词（说其中任意一个即可唤起）：**
`PubMed`、`ASCO`、`ESMO`、`CSCO`、`AACR`、`WCLC`、`肿瘤文献`、`会议摘要`、`临床试验文献`、`查文献`、`搜文献`、`文献检索`、`年会摘要`、`cancer literature`、`oncology abstract`

**能力速览：**
- **PubMed 检索**：支持 MeSH 主题词 / 作者 / 期刊 / 日期范围 / 布尔运算 / 临床试验筛选，结构化返回 PMID、DOI、摘要全文、文献类型。
- **会议摘要检索**：ASCO / ESMO / CSCO / AACR / WCLC 五大年会官方摘要库站内检索 + 全文抓取，标注 Oral / Poster / Plenary 专场。
- **药物 / 靶点专题**：多源并行综合检索（PubMed + WebSearch + 五大会议 `site:` 搜索 + 管线全景核查），输出「品种 / 企业 / 进展 / 瘤种 / 有效性 / 安全性」汇总表。
- **Word 报告导出**：一键生成，含检索元数据，适合立项调研、医学信息、竞品追踪留存。

## 检索源路由策略

| 用户需求 | 检索源 | 方法 |
|----------|--------|------|
| 已发表文献、综述、临床试验 | PubMed | 执行 scripts/pubmed_search.py |
| ASCO 年会摘要 | ASCO | WebSearch + `site:meetinglibrary.asco.org` |
| ESMO 年会摘要 | ESMO | WebSearch + `site:esmo.org` |
| CSCO 年会摘要 | CSCO | WebSearch + 中文关键词 |
| AACR 年会摘要 | AACR | WebSearch + `site:aacr.org` 或 `AACR <年份> <关键词>` |
| WCLC 年会摘要 | WCLC | WebSearch + `WCLC <年份> <关键词>` |
| 某靶点/药物全景进展 | 多源综合 | PubMed + 多角度 WebSearch 并行（见"多源综合检索流程"） |
| 需要导出 Word 报告 | 全部来源 | 检索完成后用 python-docx 生成（见"Word 文档导出"） |
| 不确定来源 | 先 PubMed，再按需补充会议摘要 + WebSearch |

当用户未指定来源时，默认先检索 PubMed（覆盖面最广），再补充会议摘要和 WebSearch。当用户提到特定会议名称（ASCO / ESMO / CSCO / AACR / WCLC）时，直接使用对应的检索策略。

**默认时间范围**：不指定时默认覆盖最近 3 年至检索日当天。当检索靶点/药物专题时，必须确保覆盖到检索日当月的最新会议和文献，执行补充检索（见下文）。

## PubMed 检索流程

### 第一步：构建查询语句

将用户的自然语言需求转化为 PubMed 查询语法。参考 references/pubmed-query-syntax.md 了解完整查询语法。

常用查询模式：

- **癌种 + 治疗**：`lung cancer[Title/Abstract] AND immunotherapy[Title/Abstract]`
- **MeSH 主题词**：`"Lung Neoplasms"[MeSH] AND "Immunotherapy"[MeSH]`
- **作者 + 关键词**：`Smith J[Author] AND targeted therapy[Title/Abstract]`
- **日期范围**：`AND ("2024/01/01"[Date - Publication] : "2024/12/31"[Date - Publication])`
- **临床试验筛选**：`AND clinical trial[Publication Type]`
- **随机对照试验**：`AND randomized controlled trial[Publication Type]`
- **综述**：`AND review[Publication Type]`
- **排除病例报告**：`NOT case reports[Publication Type]`

注意事项：
- 布尔运算符 AND / OR / NOT 必须大写
- MeSH 词用双引号包裹并加 `[MeSH]` 标签
- 新药 / 新靶点可能尚无 MeSH 词，改用 `[Title/Abstract]` 搜索
- 使用括号 `()` 控制运算优先级

### 第二步：执行检索脚本

脚本路径相对于本 skill 目录：`scripts/pubmed_search.py`

```bash
# 基本检索（默认返回 5 篇，含摘要全文）
python scripts/pubmed_search.py --query "lung cancer AND immunotherapy"

# 带日期范围（自动追加日期过滤）
python scripts/pubmed_search.py -q "breast cancer[MeSH] AND trastuzumab" --year-from 2023 --year-to 2024 -m 10

# summary 模式（仅元数据，速度快，不含摘要全文）
python scripts/pubmed_search.py -q "CAR-T AND lymphoma" --mode summary -m 15

# 按发表日期排序（最新优先）
python scripts/pubmed_search.py -q "colorectal cancer AND targeted therapy" --sort pub_date

# 分页（获取第 6-10 条）
python scripts/pubmed_search.py -q "ovarian cancer AND PARP inhibitor" --start 5 -m 5
```

参数说明：

| 参数 | 说明 |
|------|------|
| `-q / --query` | PubMed 查询语句（必填） |
| `-m / --max-results` | 最大返回数量（1-200，默认 5） |
| `-s / --start` | 分页起始位置（默认 0） |
| `--mode` | `abstract`（含摘要全文，较慢）或 `summary`（仅元数据，较快） |
| `--sort` | `relevance` / `pub_date` / `author` / `journal` |
| `--year-from` | 起始年份 |
| `--year-to` | 结束年份 |
| `--api-key` | NCBI API Key（可选，提升限速至 10 req/s） |

### 第三步：解读与展示结果

脚本输出 JSON，结构如下：

```json
{
  "query": "lung cancer AND immunotherapy",
  "total_results": 1234,
  "returned": 5,
  "start": 0,
  "mode": "abstract",
  "articles": [
    {
      "pmid": "12345678",
      "title": "Article title...",
      "authors": ["Smith J", "Doe A", "Lee K"],
      "journal": "Journal of Clinical Oncology",
      "pub_date": "2024 Jan 15",
      "abstract": "Background: ... Methods: ... Results: ... Conclusion: ...",
      "doi": "10.1200/JCO.2024.001",
      "mesh_terms": ["Lung Neoplasms/drug therapy", "Immunotherapy", "Pembrolizumab"],
      "publication_types": ["Clinical Trial", "Phase III"],
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    }
  ]
}
```

按 references/output-format-guide.md 规范展示结果给用户：
- **第一步**：展示概览表格（# | PMID | 英文标题 | 第一作者 | 期刊 | 年份 | DOI | 文献类型）
- **第二步**：逐篇展开详情，包含英文完整标题、中文摘要概括（100-200字核心要点）、MeSH 主题词、DOI、文献类型
- **摘要语言**：标题保留英文原文，摘要用中文概括核心要点（研究目的→方法→结果→结论），关键数据保留原始数字
- **默认数量**：5 篇
- 大量结果时提示总数并建议缩小范围或翻页

## 会议摘要检索流程

### ASCO 检索

参考 references/conference-search-guide.md 了解详细策略。

1. **站内搜索**：用 WebSearch 执行 `site:meetinglibrary.asco.org <关键词> <年份>`
   - 示例：`site:meetinglibrary.asco.org HER2 breast cancer 2024`
2. **筛选结果**：从搜索结果中筛选相关摘要条目，提取标题、作者、摘要编号
3. **全文抓取**：用 WebFetch 抓取具体摘要页面，提取摘要正文
4. **专场标注**：标注 Oral / Poster / Plenary 等专场类型

### ESMO 检索

1. **站内搜索**：`site:esmo.org <关键词> <年份> congress abstract`
   - 或：`annalsofoncology.org ESMO congress <年份> <关键词>`
2. **结果解析**：提取标题、作者、摘要编号（LBA / O / P 前缀代表不同专场）
3. **全文抓取**：用 WebFetch 获取摘要全文

### CSCO 检索

1. **中文搜索**：`CSCO 年会 <年份> <关键词> 摘要`
   - 示例：`CSCO 年会 2024 胃癌 靶向治疗 摘要`
2. **多源整合**：结果可能来自医学媒体（丁香园、肿瘤资讯）、CSCO 官网、论文数据库
3. **全文抓取**：用 WebFetch 获取中文页面内容

### 会议摘要检索通用流程

1. 用 WebSearch 执行站内搜索，获取摘要列表
2. 从搜索结果中筛选相关条目
3. 用 WebFetch 抓取具体摘要页面全文
4. 提取结构化信息：标题、作者、专场、摘要编号、摘要正文
5. 按 references/output-format-guide.md 规范展示，按会议分组

## 多源综合检索流程

当用户要求全面检索某靶点、某药物或某瘤种的进展时，必须执行多源并行检索，确保覆盖到检索日当天。

### 检索步骤

**第一步：PubMed 并行检索（2-3 个查询同时执行）**

```bash
# 查询1：聚焦临床试验和药物
python scripts/pubmed_search.py -q "<靶点/药物> AND (inhibitor OR drug OR therapy) AND (clinical trial[pt] OR clinical trial[ti])" -m 10 --year-from <当前年-2> --sort pub_date

# 查询2：宽泛检索，覆盖所有相关文献
python scripts/pubmed_search.py -q "<靶点/药物>" -m 10 --year-from <当前年-2> --sort pub_date

# 查询3（可选）：聚焦当年最新文献
python scripts/pubmed_search.py -q "<靶点/药物>" -m 20 --year-from <当前年> --sort pub_date
```

**第二步：WebSearch 多角度并行检索（4-6 个查询同时执行）**

用不同关键词角度确保不遗漏在研管线：
- `"<靶点/药物> inhibitor clinical trial <当前年> <当前年-1> ASCO meeting abstract"` — 会议数据
- `"<靶点/药物> targeted therapy latest clinical progress <当前年> <当前年-1>"` — 总体进展
- `"<靶点/药物> inhibitor FDA approval clinical trial update <当前年>"` — 监管动态
- `"<靶点/药物> <当前年> latest news results"` — 最新新闻
- `"<靶点/药物>抑制剂 临床试验 <当前年> 最新数据"` — 中文来源
- `"<具体药物代号> <会议名> <年份> phase results"` — 按已知药物代号逐一搜索

**第三步：五大会议 site: 站内搜索（关键！不可省略）**

对 ASCO / ESMO / CSCO / AACR / WCLC 逐一执行 site: 站内搜索，确保系统性覆盖所有会议数据：
- `site:meetinglibrary.asco.org <关键词> <年份>` — ASCO 年会 + ASCO GI
- `site:esmo.org <关键词> <年份>` — ESMO 年会 + ESMO GI
- `site:csco.org.cn <关键词> <年份>` — CSCO 年会 + CSCO BOC/指南会
- `site:aacr.org <关键词> <年份>` — AACR 年会
- `site:iaslc.org OR WCLC <年份> <关键词>` — WCLC 年会

**注意**：此步骤不可用通用 WebSearch 替代。通用搜索只能获取二手媒体报道，site: 搜索能直接命中会议官方摘要库。ASCO 2026 等最新会议摘要通常未被 PubMed 索引（延迟 1-3 个月），必须通过此步骤覆盖。

**第四步：补充检索（关键！）**

首轮检索完成后，检查是否有遗漏品种：
- 根据已找到的药物列表，逐一用药物代号做补充 WebSearch（如 `"<药物代号> <会议> <年份> results"`）
- 搜索该靶点领域的最新 FDA/NMPA 批准动态
- 搜索中文医学媒体（丁香园、肿瘤资讯、医药魔方、动脉网）的会议报道
- 搜索 ClinicalTrials.gov 和中国临床试验注册中心（chinadrugtrials.org.cn）的注册试验
- 如果当前年份有刚结束的年会（ASCO 5-6月、AACR 4月、ASCO GI 1月、ESMO 10月、CSCO 9月），必须专门搜索该会议

**第五步：管线全景核查（关键！防止遗漏品种）**

搜索该靶点/药物的管线综述或行业报告，逐一核对所有在研药物是否已被覆盖：
- `"<靶点> pipeline review <年份>"` / `"<靶点> 管线 综述 <年份>"`
- `"<靶点> inhibitor clinical trial pipeline overview"`
- 对照核查：将管线综述中列出的所有药物代号与已检索结果逐一比对，标记未覆盖品种
- 对未覆盖品种执行针对性补充检索（中英文双语查询）

**第六步：整合所有来源，生成结构化报告**

按 references/output-format-guide.md 中的"药物/靶点专题综合汇总表"格式整理。

### 检索充分性检查清单

在提交结果前，逐项确认：
- [ ] PubMed 查询是否覆盖了当前年份？
- [ ] 是否对 ASCO/ESMO/CSCO/AACR/WCLC 五大会议逐一执行了 site: 站内搜索？
- [ ] 是否逐一搜索了已知的药物代号/研发代号？
- [ ] 是否执行了管线全景核查（搜索管线综述，逐一比对在研品种）？
- [ ] 是否搜索了 FDA/NMPA 最新批准动态？
- [ ] 是否搜索了中文来源（CSCO 相关、药魔方、动脉网等）？
- [ ] 是否搜索了 ClinicalTrials.gov 和中国临床试验注册中心？
- [ ] 是否有遗漏的品种？（对比已有管线数据库/行业报告）
- [ ] 中文关键词查询是否充分？（中国本土企业药物可能在中文媒体首发）

## 药物/靶点专题报告（固定格式 V1.1.2）

当用户要求全面检索某靶点 / 药物 / 瘤种并导出报告时，**必须**使用 SKILL V1.1.2 的固定格式，由 `scripts/gen_drug_target_report.py`（JSON 驱动）生成。该格式以 KRAS G12D 胰腺癌检索报告（2026-07-17 v2）目录为基准，经用户多次校正固化，完整规范见 `references/drug-target-report-template.md`。

### 固定结构（封面 6 要素 + 6 章节 + 参考文献）

| 位置 | 固定标题 | 核心内容 / 规则 |
|------|----------|------------------|
| 封面 | 6 个固定要素（顺序固定） | ①检索主题 ②检索时间 ③检索数据库及数据源范围 ④文献或数据发表的时间范围 ⑤检索工具 ⑥检索关键词（**不含**"文献数量"） |
| 一 | 背景与流行病学 | 靶点生物学 / 流行病学负担 / 未满足需求（自由文本） |
| 二 | 临床数据汇总表 | 总体汇总（**按临床阶段降序**）；涉及 ≥2 瘤种时**按瘤种分表**；6 列固定 |
| 三 | 重点药物临床数据详情 | **按临床阶段降序**；III 期布局固定（已开展/计划 III 期必呈现）；末尾设「耐药机制研究」子项 |
| 四 | 非主流开发方向（不作为重点） | 非小分子模态（TCR-T/siRNA/疫苗/外泌体等）文字分析 + 可选小表 |
| 五 | 会议数据汇总 | 按 ASCO / ESMO / CSCO / AACR / WCLC 分组，5 列表格 |
| 六 | 总结与趋势判断 | **7 个固定子目录（顺序固定）**：1、治疗格局（与标准疗法对照）2、疗效梯队 3、竞争态势 4、差异化策略 5、耐药挑战与应对 6、监管进展（注册策略，内容与 V2.0 一致）7、临床意义与展望。各子目录以段落 + 要点呈现，强调归纳概括 |
| 末尾 | 参考文献 | 原 PubMed 核心文献列表移至最后，以**编号参考文献**方式列出（7 要素） |

**固定列定义**：
- 综合汇总表（6 列）：品种 | 开发企业 | 最新进展 | 瘤种 | 主要有效性结果 | 主要安全性结果
- 会议数据表（5 列）：摘要编号 | 药物/疗法 | 瘤种 | 关键数据 | 专场
- 参考文献（7 要素）：PMID | DOI | 文献类型 | 英文标题 | 第一作者 | 期刊 | 年份

**排序规则（降序）**：已上市 > III 期 > 注册性临床 > II 期 > I/II 期 > I 期 > IND > 临床前。每条记录带 `phase` 字段（如 `"III期"`）以保证排序稳定；缺省时从"最新进展"文本推断。

### 工作流（封装）

```
① 多源综合检索（见上「多源综合检索流程」：PubMed + WebSearch + 五大会议 site: + 管线核查 + 补充）
        ↓
② 填充 data.json —— 严格遵循模板章节与列定义；封面用 6 要素
        ↓
③ 生成报告：
   python scripts/gen_drug_target_report.py --input data.json --output <主题>_检索报告_YYYYMMDD.docx
        ↓
④ present_files 呈现
```

> 先将检索结果组织为 `data.json`，再生成报告，可保证每次输出格式完全一致、可复现、可审计。旧版 V1.1 的 `data.json` 可用 `scripts/transform_v11_to_v111.py` 一键迁移到 V1.1.1 schema；V1.1.1 → V1.1.2 仅需将 `conclusion` 由列表改为 7 键字典（见模板）。

## Word 文档导出

药物 / 靶点专题报告统一用 `scripts/gen_drug_target_report.py` 生成（固定格式 V1.1.2）；普通 PubMed / 单会议摘要导出可直接用 python-docx 自行拼装，但建议尽量复用上述固定结构。

### 依赖安装

```bash
python -m pip install python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 生成命令

```bash
# 1) 先导出一份 data.json 骨架（照模板填充）
python scripts/gen_drug_target_report.py --sample data.json

# 2) 校验数据是否符合 V1.1.2 schema
python scripts/gen_drug_target_report.py --input data.json --validate

# 3) 生成固定格式 Word 报告
python scripts/gen_drug_target_report.py --input data.json --output KRAS_G12D_临床最新进展_检索报告_20260717.docx
```

### 文件命名与保存

- 命名格式：`<主题>_检索报告_YYYYMMDD.docx`
- 保存路径：项目根目录（如 `D:\WorkBuddy\肿瘤临床开发\`）
- 生成后用 `present_files` 工具呈现给用户

## 边界情况处理

- **PubMed 无结果**：提示用户调整查询词，建议使用更宽泛的关键词、扩大日期范围、用 MeSH 词替代自由词、检查拼写
- **PubMed API 限速**：脚本内置 3 req/sec 限速控制，无需手动处理。如有 NCBI API Key 可通过 `--api-key` 参数提升至 10 req/sec
- **PubMed 网络错误**：脚本自动重试 1 次，仍失败则输出错误信息告知用户
- **会议摘要搜不到**：尝试不同关键词组合、中英文交替搜索、调整年份范围。部分年份的会议摘要可能尚未公开
- **会议年份未举行**：提示该年份会议可能尚未举行或摘要尚未发布。参考会议时间表：ASCO GI（1月）、AACR（4月）、ASCO（5-6月）、WCLC（9月）、CSCO（9月）、ESMO（10月）、ESMO GI（1月/6月）
- **大量结果**：提示总数，建议缩小查询范围或使用 `--start` 参数分页查看
- **跨会议重复**：同一试验可能在多个会议报告，注意标注并去重
- **遗漏在研品种**：药物/靶点专题检索时，仅做 1-2 次 WebSearch 容易遗漏品种。必须按"多源综合检索流程"执行：PubMed 并行 + WebSearch 多角度并行 + 五大会议 site: 站内搜索 + 逐一搜索已知药物代号 + 管线全景核查。特别注意：① 中文关键词查询不可省略（中国本土企业药物可能在中文媒体首发）；② 最新会议摘要未被 PubMed 索引时必须用 site: 搜索覆盖；③ 充分性检查必须包含管线全景核查步骤
- **最新会议数据未覆盖**：当年刚结束的年会（如 6 月检索时 ASCO 刚结束）可能未被 PubMed 收录，必须通过 WebSearch 补充。搜索时用 `<会议名> <年份> <关键词>` 而非仅 `site:` 限定
- **pip 安装超时**：国内网络环境下 pip 安装 python-docx 可能超时，使用清华镜像源 `-i https://pypi.tuna.tsinghua.edu.cn/simple` 解决

## 参考文档索引

- **references/pubmed-query-syntax.md** — PubMed 查询语法、字段标签速查表、肿瘤学常用 MeSH 词表、查询构建示例
- **references/conference-search-guide.md** — ASCO / ESMO / CSCO / AACR / WCLC 详细检索策略、WebSearch 查询模板、结果解析方法、会议年份对照表
- **references/output-format-guide.md** — PubMed 文献表格+详情格式、会议摘要格式、药物/靶点专题综合汇总表格式、Word 文档导出结构、无结果提示格式、分页提示格式
- **references/drug-target-report-template.md** — 药物/靶点专题报告**固定格式 V1.1.2**规范（封面 6 要素、背景与流行病学、临床数据汇总表按阶段降序/分瘤种、重点药物详情、非主流开发方向、会议数据、总结趋势 7 子目录、参考文献；含列定义、排序规则、通用规则、工作流）
- **scripts/gen_drug_target_report.py** — JSON 驱动的通用报告生成器（固定格式 V1.1.2），支持 `--input/--output/--sample/--validate`
- **scripts/convert_docx_to_datajson.py** — 旧 docx 报告迁移工具（抽取结构 → data.json）
- **scripts/transform_v11_to_v111.py** — V1.1 → V1.1.1 schema 一键迁移工具

## 版本历史

- **V1.0** — 基础 PubMed 检索 + 五大会议摘要检索 + 多源综合检索流程（6 步）+ 初版 Word 导出结构。
- **V1.1** — 药物/靶点专题报告**固定格式**固化（6 章节 + 封面元数据 + 固定列定义），来源于 KRAS G12D 胰腺癌检索报告（2026-07-17）目录；新增 `references/drug-target-report-template.md` 规范与 `scripts/gen_drug_target_report.py` 生成器，将「检索 → 填充 data.json → 生成 docx」工作流封装进 SKILL，保证报告可复现、可审计。
- **V1.1.1** — 按用户二次校正进一步固定报告格式：① 封面固定为 **6 要素**（检索主题 / 检索时间 / 检索数据库及数据源范围 / 文献或数据发表的时间范围 / 检索工具 / 检索关键词，去掉"文献数量"）；② 新增「一、背景与流行病学」为内容首项；③ 临床数据汇总表**按临床阶段降序**，多瘤种时**按瘤种分表**；④ 重点药物详情**按临床阶段降序**，固定「III 期布局」（已开展/计划 III 期必呈现），耐药机制研究并入本节；⑤ 非主流开发方向单列（不作重点）；⑥ 会议数据汇总保留；⑦ **删除「改进措施」章节**；⑧ 总结与趋势判断保留内部子目录；⑨ 原「PubMed 核心文献列表」移至**报告最后**以「参考文献」方式列出。同步更新 `drug-target-report-template.md`、重写 `gen_drug_target_report.py`（含 `phase_rank` 阶段降序排序与瘤种分组）、新增 `transform_v11_to_v111.py` 迁移工具。
- **V1.1.2** — 重构「六、总结与趋势判断」为 **7 个固定子目录**（顺序固定）：1、治疗格局（与标准疗法对照，凸显优势）2、疗效梯队 3、竞争态势 4、差异化策略 5、耐药挑战与应对 6、监管进展（注册策略，内容与 V2.0 一致）7、临床意义与展望。要求内容具备归纳概括能力（段落 + 要点）。`conclusion` 数据由列表改为 7 键字典（`treatment_landscape / efficacy_tiers / competitive / differentiation / resistance / regulatory / outlook`，每项含 `paras` 与 `bullets`）。更新 `gen_drug_target_report.py`（新增 `CONCLUSION_SECTIONS` 与 `_render_conclusion_item`，兼容旧列表格式）、`drug-target-report-template.md` 与版本历史。
