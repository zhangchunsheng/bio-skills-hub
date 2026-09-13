---
name: ecg-electrode-patent-finder
description: "This skill helps find, organize, and analyze patents related to ECG (electrocardiogram) electrode module manufacturing processes in both Chinese and English. It should be used when the user needs to search for ECG electrode production patents, compare manufacturing process patents, conduct patent landscape analysis, or identify innovation opportunities in the medical electrode field. Trigger scenarios include searching for heart electrode manufacturing patents, comparing electrode fabrication methods, patent novelty assessment, and patent infringement risk analysis for ECG electrode production. Keywords (CN): 心电电极, 电极模块, 制作工艺, 专利搜索, 专利对比, 创新性分析. Keywords (EN): ECG electrode, electrode module, manufacturing process, patent search, patent comparison, innovation analysis."
---

# ECG Electrode Patent Finder

## Overview

This skill provides a structured workflow for finding and analyzing ECG (electrocardiogram) electrode module manufacturing process patents across Chinese and international patent databases. It covers bilingual keyword searching, IPC/CPC classification-based retrieval, patent comparison, and innovation opportunity identification.

## Trigger Words (触发词)

### Chinese Triggers (中文触发词)

Any of the following terms in a user request should activate this skill:

- 心电电极 / 心电图电极 / 心脏电极
- 电极模块 / 电极片
- 制作工艺 / 生产工艺 / 制造方法 / 加工流程
- 电极专利 / 心电电极专利
- 专利搜索 / 专利检索 / 专利对比 / 专利分析
- 创新性 / 新颖性 / 侵权分析
- 生物电极 / 医用电极 / 一次性电极
- 导电凝胶 / 银氯化银 / AgCl
- 干电极 / 湿电极 / 固态电极
- 电极贴片 / 电极扣 / 电极连接器

### English Triggers (英文触发词)

- ECG electrode / EKG electrode / heart electrode
- electrode module / electrode pad / electrode patch
- manufacturing process / fabrication method / production process
- patent search / patent retrieval / patent comparison / patent analysis
- innovation / novelty / infringement analysis
- bioelectrode / medical electrode / disposable electrode
- conductive gel / Ag/AgCl / silver-silver chloride
- dry electrode / wet electrode / solid-state electrode
- biopotential electrode / surface electrode
- electrode connector / snap electrode

## Execution Workflow

### Step 1: Determine Search Scope

Clarify the user's specific needs before searching:

1. **Target electrode type**: dry electrode, wet electrode, solid-state, disposable, reusable, implantable, or surface electrode
2. **Process focus**: material preparation, electrode fabrication, gel application, connector assembly, packaging, or full process chain
3. **Geographic scope**: China only, international, or global
4. **Time range**: recent 5 years, 10 years, or all available
5. **Purpose**: novelty assessment, infringement risk, competitive landscape, or technology trend analysis

Ask the user for clarification on any unspecified dimension. If the user provides a general request like "find ECG electrode manufacturing patents," default to a broad search covering all electrode types and the last 10 years.

### Step 2: Generate Search Queries

Load `references/keyword_glossary.md` to access the bilingual keyword matrix and IPC/CPC classification codes. Construct search queries by combining:

1. **Core subject keywords**: electrode type (Chinese + English)
2. **Process keywords**: manufacturing method terms (Chinese + English)
3. **Classification filters**: relevant IPC/CPC codes

For each search, generate at minimum:
- 3-5 Chinese keyword combination queries
- 3-5 English keyword combination queries
- 2-3 classification-based queries (by IPC/CPC code)

Optionally, run `scripts/generate_search_queries.py` to automatically generate ready-to-use search URLs for each patent database.

### Step 3: Search Across Patent Databases

Load `references/patent_databases.md` for the complete database list with URLs and search syntax. Execute searches across:

**Chinese Databases:**
1. Google Patents (Chinese subset) - `patents.google.com` with `country=CN` filter
2. CNIPA (国家知识产权局) - patent search portal
3. SooPAT / 智慧芽 / 佰腾网 - Chinese commercial platforms

**International Databases:**
4. Google Patents (global) - `patents.google.com`
5. Espacenet (EPO) - `worldwide.espacenet.com`
6. WIPO Patentscope - `patentscope.wipo.int`
7. USPTO Patent Full-Text and Image Database

For each database:
- Use the generated queries from Step 2
- Apply the time range and geographic filters from Step 1
- Record: patent number, title, applicant, filing date, abstract, IPC/CPC codes

### Step 4: Organize and Filter Results

Compile all retrieved patents into a structured comparison table. For each patent, capture:

| Field | Description |
|---|---|
| Patent Number | Patent ID (e.g., CN123456A, US20230123456A1) |
| Title | Full title (Chinese and/or English) |
| Applicant | Assignee / patent holder |
| Filing Date | Application date |
| Publication Date | Publication / grant date |
| IPC/CPC | Classification codes |
| Abstract | Condensed abstract |
| Process Type | Manufacturing process category (see `references/manufacturing_processes.md`) |
| Key Materials | Primary materials used |
| Key Innovation | Distinguishing technical feature |
| Status | Granted, pending, withdrawn |

Filter out clearly irrelevant results (e.g., electrode for non-ECG applications, pure software patents without hardware manufacturing claims).

### Step 5: Patent Comparison and Innovation Analysis

Load `references/innovation_analysis.md` for the detailed analysis framework. Perform:

1. **Process Comparison Matrix**: Compare manufacturing processes across key dimensions (material preparation, electrode body formation, conductive layer application, gel dispensing, connector attachment, packaging)
2. **Technology Trend Map**: Plot patents on a timeline to identify technology evolution
3. **Applicant Landscape**: Identify key players and their patent portfolios
4. **Innovation Gap Analysis**: Identify under-explored process steps or material combinations
5. **Risk Assessment**: Flag potential infringement risks in key process areas

### Step 6: Generate Innovation Assessment

Synthesize findings into actionable insights:

1. **Technology gaps**: Under-explored manufacturing approaches that could be patentable
2. **Differentiation opportunities**: Process modifications or material substitutions that differ from existing patents
3. **Freedom-to-operop**: Areas with dense patent coverage that require careful navigation
4. **Recommendation**: Specific process innovation directions based on the analysis

## Output Format

The final output should include:

1. **Patent Summary Table** - All found patents organized by process type
2. **Process Comparison Matrix** - Side-by-side manufacturing process comparison
3. **Innovation Assessment Report** - Gap analysis and innovation recommendations
4. **Search Query Log** - All queries used (for reproducibility)

If the user requests a specific format (Excel, Word, PDF), generate the output accordingly. Default to a structured Markdown report.

## Resources

### references/

- `keyword_glossary.md` - Bilingual (Chinese-English) keyword matrix with IPC/CPC classification codes and search query templates. Load this before generating search queries in Step 2.
- `patent_databases.md` - Comprehensive guide to Chinese and international patent databases with URLs, search syntax, and tips. Load this before searching in Step 3.
- `manufacturing_processes.md` - Overview of common ECG electrode manufacturing processes, material categories, and technical parameters for comparison. Load this before organizing results in Step 4 and during comparison in Step 5.
- `innovation_analysis.md` - Framework for patent comparison, innovation gap identification, and risk assessment. Load this during Step 5 and Step 6.

### scripts/

- `generate_search_queries.py` - Automatically generates optimized search queries and ready-to-use URLs for each patent database based on the keyword glossary. Optionally run in Step 2 to speed up query construction.
